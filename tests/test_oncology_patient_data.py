from datetime import datetime

from kilimanjaro_oncology.classes.oncology_patient_data import (
    OncologyPatientData,
)


def test_to_dict_and_from_dict_round_trip():
    now = datetime.now().replace(microsecond=0)
    record = OncologyPatientData(
        autoincrement_id=42,
        patient_id="H.D.0001",
        event="Diagnosis",
        event_date=now,
        record_creation_datetime=now,
        diagnosis="C34.1",
        histo="Adeno",
        grade="2",
        factors="ER+",
        stage="T2 N0 M0",
        careplan="Chemo",
        note="Sample",
        death_date=None,
        death_cause="",
    )
    d = record.to_dict()
    # ISO strings
    assert isinstance(d["event_date"], str)
    assert d["event_date"].startswith(now.isoformat()[:19])
    # round‑trip
    rec2 = OncologyPatientData.from_dict(d)
    assert rec2 == record


def test_from_dict_invalid_dates_fallback():
    bad = {
        "record_creation_datetime": "not-a-date",
        "event_date": "",
        "death_date": "also-bad",
    }
    rec = OncologyPatientData.from_dict(bad)
    # should default to 'now'ish
    assert isinstance(rec.record_creation_datetime, datetime)
    assert isinstance(rec.event_date, datetime)
    assert rec.death_date is None
