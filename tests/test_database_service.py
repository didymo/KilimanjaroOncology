import pytest
from pathlib import Path
from kilimanjaro_oncology.database.database_service import DatabaseService
from kilimanjaro_oncology.classes.oncology_patient_data import OncologyPatientData

@pytest.fixture
def db(tmp_path):
    # copy your schema.sql into tmp_path
    schema = Path(__file__).parent.parent / "src/kilimanjaro_oncology/database/schema.sql"
    db_file = tmp_path / "test.sqlite"
    ds = DatabaseService(str(db_file))
    # initialize schema
    with ds.get_connection() as conn:
        conn.executescript(schema.read_text())
    return ds

def test_save_and_get(db):
    record = OncologyPatientData(patient_id="P1", event="Diagnosis")
    rid = db.save_diagnosis_record(record.to_dict())
    assert isinstance(rid, int)
    fetched = db.get_diagnosis_record(rid)
    assert fetched["PatientID"] == "P1"

def test_get_patient_records_order(db):
    # insert two records with different event_dates
    import datetime
    r1 = {"patient_id":"P2","event":"D","event_date":datetime.datetime(2020,1,1).isoformat()}
    r2 = {"patient_id":"P2","event":"F","event_date":datetime.datetime(2021,1,1).isoformat()}
    id1 = db.save_diagnosis_record(r1)
    id2 = db.save_diagnosis_record(r2)
    recs = db.get_patient_records("P2")
    assert recs[0]["AutoincrementID"] == id2
    assert recs[1]["AutoincrementID"] == id1
