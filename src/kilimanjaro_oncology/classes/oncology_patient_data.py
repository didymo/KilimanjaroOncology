# oncology_patient_data.py
from dataclasses import asdict, dataclass, field
from datetime import datetime


@dataclass
class OncologyPatientData:
    # Primary key, used for persistence (Optional)
    autoincrement_id: int | None = None

    # Core data fields
    patient_id: str = ""
    event: str = ""
    diagnosis: str = ""
    histo: str = ""
    grade: str = ""
    factors: str = ""
    stage: str = ""
    careplan: str = ""
    summary: str = ""
    note: str = ""

    # Timestamps stored as datetime objects
    record_creation_datetime: datetime = field(default_factory=datetime.now)
    event_date: datetime = field(default_factory=datetime.now)

    # Optional fields for death events.
    death_date: datetime | None = None
    death_cause: str = ""

    def to_dict(self) -> dict:
        """
        Convert the OncologyRecord instance to a dictionary suitable for storage.
        Datetime fields are converted to ISO format strings.
        """
        result = asdict(self)
        result["record_creation_datetime"] = (
            self.record_creation_datetime.isoformat()
        )
        result["event_date"] = self.event_date.isoformat()
        # If death_date is provided, convert it as well.
        result["death_date"] = (
            self.death_date.isoformat() if self.death_date else ""
        )
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "OncologyPatientData":
        """
        Create an OncologyPatientData instance from a dictionary.
        Converts ISO formatted date strings back to datetime objects.
        """
        # Convert date strings to datetime objects; provide defaults if parsing fails.
        try:
            record_creation_datetime = datetime.fromisoformat(
                data.get("record_creation_datetime", datetime.now().isoformat())
            )
        except Exception:
            record_creation_datetime = datetime.now()
        try:
            event_date = datetime.fromisoformat(
                data.get("event_date", datetime.now().isoformat())
            )
        except Exception:
            event_date = datetime.now()

        death_date_str = data.get("death_date", "")
        try:
            death_date = (
                datetime.fromisoformat(death_date_str)
                if death_date_str
                else None
            )
        except Exception:
            death_date = None

        return cls(
            autoincrement_id=data.get("autoincrement_id"),
            patient_id=data.get("patient_id", ""),
            event=data.get("event", ""),
            diagnosis=data.get("diagnosis", ""),
            histo=data.get("histo", ""),
            grade=data.get("grade", ""),
            factors=data.get("factors", ""),
            stage=data.get("stage", ""),
            careplan=data.get("careplan", ""),
            summary=data.get("summary", ""),
            note=data.get("note", ""),
            record_creation_datetime=record_creation_datetime,
            event_date=event_date,
            death_date=death_date,
            death_cause=data.get("death_cause", ""),
        )
