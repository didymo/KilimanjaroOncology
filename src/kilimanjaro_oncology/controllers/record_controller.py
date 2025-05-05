# kilimanjaro_oncology/controllers/record_controller.py

from typing     import List, Dict, Any

from kilimanjaro_oncology.database.database_service import DatabaseService


# from .database_service import DatabaseService

class RecordController:
    def __init__(self, db: DatabaseService):
        self._db = db

    def fetch_settings(self, keys: List[str]) -> Dict[str, str]:
        """Return a dict of key→value for each setting in `keys`."""
        placeholders = ",".join("?" for _ in keys)
        sql = f"SELECT key, value FROM settings WHERE key IN ({placeholders})"
        with self._db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, keys)
            return dict(cur.fetchall())

    def fetch_patient_ids(self, prefix: str) -> List[str]:
        """Return all distinct PatientID values that start with `prefix`."""
        with self._db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT DISTINCT PatientID FROM oncology_data WHERE PatientID LIKE ?",
                (f"{prefix}%",),
            )
            return [row[0] for row in cur.fetchall()]

    def fetch_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """
        Return the most recent record for this patient_id,
        as a dict of column→value.
        """
        with self._db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM oncology_data
                 WHERE PatientID = ?
                 ORDER BY Event_Date DESC
                 LIMIT 1
                """,
                (patient_id,),
            )
            row = cur.fetchone()
            if not row:
                return {}
            cols = [d[0] for d in cur.description]
            return dict(zip(cols, row))

    def save_record(self, record: Dict[str, Any]) -> int:
        """
        Persist a new record via the existing DatabaseService API.
        Assumes `record` is already a dict with the correct keys.
        """
        # you could add validation here if you like
        return self._db.save_diagnosis_record(record)
