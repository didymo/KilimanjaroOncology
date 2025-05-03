# database_service.py
import datetime
import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Dict, Optional


class DatabaseService:
    """
    Thread-safe service class for handling database operations.
    Uses connection pooling and context managers to ensure safe concurrent access.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: Optional[str] = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseService, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the database service with connection pooling."""
        if self._initialized:
            return

        self.db_path = db_path or str(
            Path.home() / "africa_oncology_settings" / "database.sqlite"
        )
        self._local = threading.local()
        self._lock = threading.Lock()
        self._initialized = True

    @contextmanager
    def get_connection(self):
        """Thread-safe context manager for database connections."""
        if not hasattr(self._local, "connection"):
            self._local.connection = sqlite3.connect(self.db_path)

        try:
            yield self._local.connection
        except Exception as e:
            self._local.connection.rollback()
            raise e
        else:
            self._local.connection.commit()

    def close_connections(self):
        """Close the connection for the current thread if it exists."""
        if hasattr(self._local, "connection"):
            self._local.connection.close()
            del self._local.connection

    def save_diagnosis_record(self, record_data) -> int:
        """
        Save a new record to the database.
        Supports data from Diagnosis, Follow Up, and Death screens.
        Returns the autoincrement ID of the inserted record.
        """

        # If record_data is a dataclass instance, convert it to a dictionary.
        if is_dataclass(record_data):
            record_data = asdict(record_data)

        with self._lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Always record the creation time.
                data = {"record_creation_datetime": datetime.datetime.now().isoformat()}

                # Mapping: canonical database column -> possible keys in record_data.
                mapping = {
                    "PatientID": ["patient_id"],
                    "Event": ["event"],
                    "Event_Date": ["event_date"],
                    "Diagnosis": ["diagnosis"],
                    "Histo": ["histo"],
                    "Grade": ["grade"],
                    "Factors": ["factors"],
                    "Stage": ["stage"],
                    "Careplan": ["careplan"],
                    "Note": ["note"],
                    "Death_Date": ["death_date"],  # if applicable
                    "Death_Cause": ["death_cause"],  # if applicable
                }

                # For each canonical column, pick the first matching key from
                # record_data.
                for col, keys in mapping.items():
                    for key in keys:
                        if key in record_data:
                            data[col] = record_data[key]
                            break
                    else:
                        # If none of the expected keys are found,
                        # default to empty string.
                        data[col] = ""

                # Build the INSERT statement dynamically.
                columns = list(data.keys())
                placeholders = ", ".join("?" for _ in columns)
                sql = (
                    f"INSERT INTO oncology_data ({', '.join(columns)}) "
                    f"VALUES ({placeholders})"
                )

                values = tuple(data[col] for col in columns)

                cursor.execute(sql, values)
                return cursor.lastrowid

    def get_diagnosis_record(self, record_id: int) -> Dict:
        """Retrieve a specific diagnosis record by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM oncology_data WHERE AutoincrementID = ?
            """,
                (record_id,),
            )

            record = cursor.fetchone()
            if record:
                # Convert tuple to dictionary using column names
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, record))
            return {}

    def get_patient_records(self, patient_id: str) -> list:
        """Retrieve all records for a specific patient."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM oncology_data
                WHERE PatientID = ?
                ORDER BY Event_Date DESC
            """,
                (patient_id,),
            )

            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def update_diagnosis_record(self, record_id: int, record_data: Dict) -> bool:
        """Update an existing diagnosis record."""
        with self._lock:  # Ensure thread-safe write operation
            with self.get_connection() as conn:
                cursor = conn.cursor()

                update_fields = []
                values = []

                # Build dynamic update statement based on provided fields
                for field, value in record_data.items():
                    if field != "AutoincrementID":  # Skip the primary key
                        update_fields.append(f"{field} = ?")
                        values.append(value)

                if not update_fields:
                    return False

                # Add record_id to values
                values.append(record_id)

                sql = f"""
                UPDATE oncology_data
                SET {', '.join(update_fields)}
                WHERE AutoincrementID = ?
                """

                cursor.execute(sql, values)
                return cursor.rowcount > 0
