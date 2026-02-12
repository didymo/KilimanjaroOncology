# kilimanjaro_oncology/controllers/record_controller.py
from __future__ import annotations

import re
from typing import Any

from kilimanjaro_oncology.database.database_service import DatabaseService


class RecordController:
    # Hard limits are a “medical/PII friendly” safety measure:
    # - avoids pathological queries
    # - prevents accidental huge IN(...) lists from UI bugs
    MAX_IN_KEYS = 500

    # Optional: restrict setting keys to a safe identifier-ish format.
    # This is not required for SQL safety (params already handle values),
    # but it reduces risk of accidental misuse and makes audits easier.
    _KEY_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")

    def __init__(self, db: DatabaseService):
        self._db = db

    def fetch_settings(self, keys: list[str]) -> dict[str, str]:
        """
        Return a dict of key→value for each setting in `keys`.

        SECURITY:
        - Values are bound via parameters (never interpolated into SQL).
        - The only dynamic part of the SQL string is the number of "?" placeholders,
          derived from len(keys) only (not from user-provided SQL fragments).
        - Ruff S608 / Bandit B608 flag this pattern heuristically; we suppress
          with justification.
        """
        if not keys:
            return {}

        if len(keys) > self.MAX_IN_KEYS:
            raise ValueError(
                f"Too many keys for settings lookup ({len(keys)} > {self.MAX_IN_KEYS})"
            )

        # Fail closed if keys contain unexpected characters.
        # (If you later want to allow broader key names, loosen _KEY_RE.)
        for k in keys:
            if not self._KEY_RE.match(k):
                raise ValueError(f"Invalid settings key: {k!r}")

        placeholders = ",".join(["?"] * len(keys))

        # ruff: noqa: S608
        # bandit: B608 is heuristic here; values are parameterized, and only the
        # placeholder count is dynamic (derived from len(keys)).
        sql = f"SELECT key, value FROM settings WHERE key IN ({placeholders})"  # nosec B608

        with self._db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, keys)
            return dict(cur.fetchall())

    def fetch_patient_ids(self, prefix: str) -> list[str]:
        """Return all distinct PatientID values that start with `prefix`."""
        with self._db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT DISTINCT PatientID FROM oncology_data WHERE PatientID LIKE ?",
                (f"{prefix}%",),
            )
            return [row[0] for row in cur.fetchall()]

    def fetch_patient_data(self, patient_id: str) -> dict[str, Any]:
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
            return dict(zip(cols, row, strict=False))

    def save_record(self, record: dict[str, Any]) -> int:
        """Persist a new record via the existing DatabaseService API."""
        return int(self._db.save_diagnosis_record(record))

    def fetch_patient_summary(self, patient_id: str) -> str:
        """Return the most recent cumulative summary for patient_id."""
        return str(self._db.get_patient_summary(patient_id))
