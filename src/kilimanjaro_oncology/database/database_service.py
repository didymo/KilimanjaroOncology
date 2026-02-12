# database_service.py
from __future__ import annotations

import datetime
import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


class DatabaseService:
    """
    Thread-safe service class for handling database operations.
    Uses per-thread sqlite connections + a lock for writes.

    SECURITY (medical/PII posture):
    - Parameterize all *values* with sqlite placeholders.
    - Only allow SQL identifier interpolation (table/column names) from allowlists.
    - Fail closed if unknown columns are requested for update/insert.
    """

    # map db_path → instance
    _instances: dict[str, DatabaseService] = {}
    _instances_lock = threading.Lock()

    # ---- schema allowlists (explicit is safer) ----
    TABLE_ONCOLOGY = "oncology_data"

    # These are the only columns this service is allowed to write/update.
    # Keep this list in sync with your schema.
    ALLOWED_COLUMNS: set[str] = {
        "record_creation_datetime",
        "PatientID",
        "Event",
        "Event_Date",
        "Diagnosis",
        "Histo",
        "Grade",
        "Factors",
        "Stage",
        "Careplan",
        "Summary",
        "Note",
        "Death_Date",
        "Death_Cause",
    }

    def __new__(cls, db_path: str | None = None):
        key = db_path or ""
        with cls._instances_lock:
            if key not in cls._instances:
                inst = super().__new__(cls)
                inst._initialized = False
                cls._instances[key] = inst
            return cls._instances[key]

    def __init__(self, db_path: str | None = None):
        if getattr(self, "_initialized", False):
            return

        self.db_path = db_path or str(
            Path.home() / "africa_oncology_settings" / "database.sqlite"
        )
        self._local = threading.local()
        self._write_lock = threading.Lock()
        self._initialized = True

    @contextmanager
    def get_connection(self):
        """
        Thread-safe context manager for database connections.
        Each thread gets its own sqlite connection (stored in threading.local()).
        """
        if not hasattr(self._local, "connection"):
            # Each thread gets its own connection; check_same_thread=False is safe in this pattern.
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = None  # keep default tuples

            # Safer defaults for sqlite in a multi-thread desktop app
            conn.execute("PRAGMA foreign_keys = ON;")
            # Network shares are often unreliable with WAL; fall back to DELETE.
            if str(self.db_path).startswith(("\\\\", "//")):
                conn.execute("PRAGMA journal_mode = DELETE;")
            else:
                conn.execute("PRAGMA journal_mode = WAL;")
            # Reduce transient "database is locked" errors on slower storage.
            conn.execute("PRAGMA busy_timeout = 5000;")
            conn.execute("PRAGMA synchronous = NORMAL;")

            self._local.connection = conn

        try:
            yield self._local.connection
        except Exception:
            # Roll back but do not mask the original exception.
            try:
                self._local.connection.rollback()
            finally:
                raise
        else:
            self._local.connection.commit()

    def close_connections(self):
        """Close the connection for the current thread if it exists."""
        if hasattr(self._local, "connection"):
            self._local.connection.close()
            del self._local.connection

    # ---- helpers ----

    @staticmethod
    def _row_to_dict(cursor: sqlite3.Cursor, row: tuple[Any, ...]) -> dict[str, Any]:
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row, strict=False))

    # ---- CRUD ----

    def save_diagnosis_record(self, record_data: Any) -> int:
        """
        Save a new record to the database.
        Supports data from Diagnosis, Follow Up, and Death screens.
        Returns the autoincrement ID of the inserted record.
        """
        if is_dataclass(record_data) and not isinstance(record_data, type):
            record_data = asdict(record_data)

        if not isinstance(record_data, dict):
            raise TypeError("record_data must be a dict or dataclass instance")

        # Always record the creation time.
        data: dict[str, Any] = {
            "record_creation_datetime": datetime.datetime.now().isoformat()
        }

        # Mapping: canonical database column -> possible keys in record_data.
        # This mapping is an allowlist by design.
        mapping: dict[str, list[str]] = {
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
            "Death_Date": ["death_date"],
            "Death_Cause": ["death_cause"],
        }

        for col, keys in mapping.items():
            for key in keys:
                if key in record_data:
                    data[col] = record_data[key]
                    break
            else:
                data[col] = ""

        patient_id = str(data.get("PatientID", "")).strip()
        data["Summary"] = (
            self._compose_patient_summary(patient_id, data) if patient_id else ""
        )

        # Defensive: only allow known schema columns
        columns = [c for c in data if c in self.ALLOWED_COLUMNS]
        if not columns:
            raise ValueError("No valid columns to insert")

        placeholders = ", ".join("?" for _ in columns)
        col_list = ", ".join(columns)

        # Safe because TABLE_ONCOLOGY and columns are allowlisted identifiers only.
        sql = f"INSERT INTO {self.TABLE_ONCOLOGY} ({col_list}) VALUES ({placeholders})"  # noqa: S608  # nosec B608
        values = tuple(data[c] for c in columns)

        with self._write_lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, values)
            rid = cursor.lastrowid
            if rid is None:
                raise RuntimeError("Insert succeeded but lastrowid is None")
            return int(rid)

    def get_diagnosis_record(self, record_id: int) -> dict[str, Any]:
        """Retrieve a specific diagnosis record by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM oncology_data WHERE AutoincrementID = ?",
                (record_id,),
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(cursor, row)
            return {}

    def get_patient_records(self, patient_id: str) -> list[dict[str, Any]]:
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
            rows = cursor.fetchall()
            if not rows:
                return []

            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, row, strict=False)) for row in rows]

    def update_diagnosis_record(self, record_id: int, record_data: dict[str, Any]) -> bool:
        """
        Update an existing diagnosis record.

        SECURITY:
        - Only allow updates to explicitly allowlisted columns (prevents injection via field names).
        - Values remain parameterized.
        """
        if not isinstance(record_data, dict):
            raise TypeError("record_data must be a dict")

        updates: list[str] = []
        values: list[Any] = []

        for field, value in record_data.items():
            if field == "AutoincrementID":
                continue
            if field not in self.ALLOWED_COLUMNS:
                # Fail closed rather than silently ignoring unknown columns.
                raise ValueError(f"Refusing to update unknown column: {field!r}")

            updates.append(f"{field} = ?")
            values.append(value)

        if not updates:
            return False

        values.append(record_id)
        set_clause = ", ".join(updates)

        # Safe because set_clause is built only from allowlisted identifiers.
        sql = f"UPDATE {self.TABLE_ONCOLOGY} SET {set_clause} WHERE AutoincrementID = ?"  # noqa: S608  # nosec B608

        with self._write_lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, values)
            return int(cursor.rowcount) > 0

    def get_patient_summary(self, patient_id: str) -> str:
        """Return latest cumulative summary for a patient."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT Summary
                FROM oncology_data
                WHERE PatientID = ?
                ORDER BY Event_Date DESC, AutoincrementID DESC
                LIMIT 1
                """,
                (patient_id,),
            )
            row = cursor.fetchone()
            if not row:
                return ""
            return str(row[0] or "")

    @staticmethod
    def _display_date(value: Any) -> str:
        text = str(value or "").strip()
        if not text:
            return ""
        return text.split("T", 1)[0]

    @staticmethod
    def _sort_key(item: dict[str, Any]) -> tuple[str, int]:
        date = str(item.get("Event_Date", ""))
        ident = int(item.get("AutoincrementID", 0) or 0)
        return date, ident

    @staticmethod
    def _summary_block(item: dict[str, Any]) -> str:
        date_txt = DatabaseService._display_date(item.get("Event_Date")) or "unknown-date"
        pieces: list[str] = []

        diagnosis = str(item.get("Diagnosis", "") or "").strip()
        histo = str(item.get("Histo", "") or "").strip()
        grade = str(item.get("Grade", "") or "").strip()
        factors = str(item.get("Factors", "") or "").strip()
        stage = str(item.get("Stage", "") or "").strip()
        careplan = str(item.get("Careplan", "") or "").strip()
        death_cause = str(item.get("Death_Cause", "") or "").strip()

        if diagnosis:
            pieces.append(diagnosis)
        if histo:
            pieces.append(histo)
        if grade:
            pieces.append(f"G{grade}")
        if factors:
            pieces.append(factors)
        if stage:
            pieces.append(stage)

        line = f"{date_txt}: {', '.join(pieces)}" if pieces else f"{date_txt}:"
        extras: list[str] = []
        if careplan:
            extras.append(f"  Treatment - {careplan}")
        if death_cause:
            extras.append(f"  Death - {death_cause}")
        if extras:
            return f"{line}\n" + "\n".join(extras)
        return line

    def _compose_patient_summary(
        self, patient_id: str, pending_row: dict[str, Any]
    ) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    AutoincrementID, Event_Date, Diagnosis, Histo, Grade,
                    Factors, Stage, Careplan, Death_Cause
                FROM oncology_data
                WHERE PatientID = ?
                ORDER BY Event_Date ASC, AutoincrementID ASC
                """,
                (patient_id,),
            )
            rows = cursor.fetchall()
            cols = [d[0] for d in cursor.description]

        history = [dict(zip(cols, row, strict=False)) for row in rows]
        history.append(
            {
                "AutoincrementID": 0,
                "Event_Date": pending_row.get("Event_Date", ""),
                "Diagnosis": pending_row.get("Diagnosis", ""),
                "Histo": pending_row.get("Histo", ""),
                "Grade": pending_row.get("Grade", ""),
                "Factors": pending_row.get("Factors", ""),
                "Stage": pending_row.get("Stage", ""),
                "Careplan": pending_row.get("Careplan", ""),
                "Death_Cause": pending_row.get("Death_Cause", ""),
            }
        )

        history.sort(key=self._sort_key)
        blocks = [self._summary_block(item) for item in history]
        return "\n".join(blocks)
