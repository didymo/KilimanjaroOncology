import pytest

from kilimanjaro_oncology.controllers.record_controller import RecordController


@pytest.fixture
def ctrl(db_with_schema):
    with db_with_schema.get_connection() as c:
        c.execute("INSERT INTO settings VALUES(?,?)", ("k", "v"))
        c.execute(
            "INSERT INTO oncology_data(PatientID,Event,Event_Date) VALUES(?,?,?)",
            ("P1", "D", "2025-01-01"),
        )
    return RecordController(db_with_schema)


def test_fetch_settings(ctrl):
    d = ctrl.fetch_settings(["k"])
    assert d == {"k": "v"}


def test_fetch_patient_ids(ctrl):
    ids = ctrl.fetch_patient_ids("P")
    assert ids == ["P1"]


def test_fetch_patient_data(ctrl):
    d = ctrl.fetch_patient_data("P1")
    assert d["PatientID"] == "P1"
    assert d["Event"] == "D"


def test_fetch_settings_empty(ctrl):
    assert ctrl.fetch_settings([]) == {}


def test_fetch_settings_too_many(ctrl):
    with pytest.raises(ValueError):
        ctrl.fetch_settings(["k"] * (ctrl.MAX_IN_KEYS + 1))


def test_fetch_settings_invalid_key(ctrl):
    with pytest.raises(ValueError):
        ctrl.fetch_settings(["bad key"])


def test_fetch_patient_data_missing(ctrl):
    assert ctrl.fetch_patient_data("NOPE") == {}


def test_fetch_settings_key_length_boundaries(ctrl, db_with_schema):
    key_128 = "k" * 128
    with db_with_schema.get_connection() as c:
        c.execute("INSERT INTO settings VALUES(?,?)", (key_128, "v128"))
    out = ctrl.fetch_settings([key_128])
    assert out == {key_128: "v128"}

    key_129 = "k" * 129
    with pytest.raises(ValueError):
        ctrl.fetch_settings([key_129])


def test_fetch_settings_duplicate_keys(ctrl):
    out = ctrl.fetch_settings(["k", "k"])
    assert out == {"k": "v"}


def test_fetch_patient_ids_wildcard_prefix(ctrl):
    ids = ctrl.fetch_patient_ids("%")
    assert "P1" in ids
