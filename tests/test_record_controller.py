import pytest
from kilimanjaro_oncology.controllers.record_controller import RecordController
from kilimanjaro_oncology.database.database_service import DatabaseService

@pytest.fixture
def ctrl(tmp_path):
    # set up DBService with schema + test data
    db_file = tmp_path / "rc.sqlite"
    ds = DatabaseService(str(db_file))
    # init schema & settings table
    with ds.get_connection() as c:
        c.executescript("""
            CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE oncology_data(
                AutoincrementID INTEGER PRIMARY KEY,
                PatientID TEXT, Event TEXT, Event_Date TEXT
            );
        """)
        c.execute("INSERT INTO settings VALUES(?,?)", ("k","v"))
        c.execute("INSERT INTO oncology_data(PatientID,Event,Event_Date) VALUES(?,?,?)",
                  ("P1","D","2025-01-01"))
    return RecordController(ds)

def test_fetch_settings(ctrl):
    d = ctrl.fetch_settings(["k"])
    assert d == {"k":"v"}

def test_fetch_patient_ids(ctrl):
    ids = ctrl.fetch_patient_ids("P")
    assert ids == ["P1"]

def test_fetch_patient_data(ctrl):
    d = ctrl.fetch_patient_data("P1")
    assert d["PatientID"] == "P1"
    assert d["Event"] == "D"
