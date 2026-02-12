import os
from pathlib import Path

from kilimanjaro_oncology.controllers.record_controller import RecordController
from kilimanjaro_oncology.database.database_service import DatabaseService


def test_multi_patient_record_order_and_fetch(config_module, tmp_path):
    schema_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
        "kilimanjaro_oncology",
        "database",
        "schema.sql",
    )
    config_module.SCHEMA_FILE.write_text(Path(schema_path).read_text())

    db_path = tmp_path / "system.sqlite"
    cm = config_module.ConfigManager()
    cm.settings["db_path"] = str(db_path)
    cm.initialize_database()

    db = DatabaseService(str(db_path))
    ctrl = RecordController(db)

    id1 = db.save_diagnosis_record(
        {"patient_id": "P1", "event": "Diagnosis", "event_date": "2025-01-01"}
    )
    id2 = db.save_diagnosis_record(
        {"patient_id": "P1", "event": "Management", "event_date": "2025-02-01"}
    )
    id3 = db.save_diagnosis_record(
        {"patient_id": "P2", "event": "Diagnosis", "event_date": "2025-01-15"}
    )

    recs_p1 = db.get_patient_records("P1")
    assert recs_p1[0]["AutoincrementID"] == id2
    assert recs_p1[1]["AutoincrementID"] == id1

    ids = sorted(ctrl.fetch_patient_ids("P"))
    assert ids == ["P1", "P2"]

    last_p2 = ctrl.fetch_patient_data("P2")
    assert last_p2["AutoincrementID"] == id3
