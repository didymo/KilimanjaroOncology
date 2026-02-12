import sqlite3

from kilimanjaro_oncology.classes.oncology_patient_data import (
    OncologyPatientData,
)


def test_save_and_get(db_with_schema):
    record = OncologyPatientData(patient_id="P1", event="Diagnosis")
    rid = db_with_schema.save_diagnosis_record(record.to_dict())
    assert isinstance(rid, int)
    fetched = db_with_schema.get_diagnosis_record(rid)
    assert fetched["PatientID"] == "P1"


def test_get_patient_records_order(db_with_schema):
    # insert two records with different event_dates
    import datetime

    r1 = {
        "patient_id": "P2",
        "event": "D",
        "event_date": datetime.datetime(2020, 1, 1).isoformat(),
    }
    r2 = {
        "patient_id": "P2",
        "event": "F",
        "event_date": datetime.datetime(2021, 1, 1).isoformat(),
    }
    id1 = db_with_schema.save_diagnosis_record(r1)
    id2 = db_with_schema.save_diagnosis_record(r2)
    recs = db_with_schema.get_patient_records("P2")
    assert recs[0]["AutoincrementID"] == id2
    assert recs[1]["AutoincrementID"] == id1


def test_save_rejects_invalid_input(db_with_schema):
    import pytest

    with pytest.raises(TypeError):
        db_with_schema.save_diagnosis_record("nope")


def test_save_rejects_no_valid_columns(db_with_schema):
    rid = db_with_schema.save_diagnosis_record({"unknown": "x"})
    assert isinstance(rid, int)
    rec = db_with_schema.get_diagnosis_record(rid)
    assert rec["AutoincrementID"] == rid


def test_get_diagnosis_record_missing_returns_empty(db_with_schema):
    assert db_with_schema.get_diagnosis_record(99999) == {}


def test_save_accepts_dataclass(db_with_schema):
    record = OncologyPatientData(patient_id="PDC", event="Diagnosis")
    rid = db_with_schema.save_diagnosis_record(record)
    got = db_with_schema.get_diagnosis_record(rid)
    assert got["PatientID"] == "PDC"


def test_save_fills_missing_fields_with_empty_strings(db_with_schema):
    rid = db_with_schema.save_diagnosis_record(
        {"patient_id": "PEM", "event": "D"}
    )
    got = db_with_schema.get_diagnosis_record(rid)
    assert got["Diagnosis"] == ""
    assert got["Histo"] == ""
    assert got["Grade"] == ""


def test_update_diagnosis_record_validation(db_with_schema):
    import pytest

    rid = db_with_schema.save_diagnosis_record(
        {"patient_id": "P3", "event": "D"}
    )
    with pytest.raises(ValueError):
        db_with_schema.update_diagnosis_record(rid, {"BadColumn": "x"})
    assert db_with_schema.update_diagnosis_record(rid, {}) is False
    assert (
        db_with_schema.update_diagnosis_record(rid, {"Note": "ok"})
        is True
    )
    got = db_with_schema.get_diagnosis_record(rid)
    assert got["Note"] == "ok"


def test_update_diagnosis_record_type_error(db_with_schema):
    import pytest

    with pytest.raises(TypeError):
        db_with_schema.update_diagnosis_record(1, "bad")


def test_update_diagnosis_record_ignores_autoincrement_id(db_with_schema):
    rid = db_with_schema.save_diagnosis_record(
        {"patient_id": "P4", "event": "D"}
    )
    ok = db_with_schema.update_diagnosis_record(
        rid, {"AutoincrementID": 999, "Note": "keep"}
    )
    assert ok is True
    rec = db_with_schema.get_diagnosis_record(rid)
    assert rec["AutoincrementID"] == rid
    assert rec["Note"] == "keep"


def test_save_with_no_allowed_columns_raises(db_with_schema, monkeypatch):
    import pytest

    monkeypatch.setattr(db_with_schema, "ALLOWED_COLUMNS", set())
    with pytest.raises(ValueError):
        db_with_schema.save_diagnosis_record({"patient_id": "P5"})


def test_get_connection_rolls_back_on_exception(db_with_schema):
    import pytest

    with pytest.raises(RuntimeError), db_with_schema.get_connection() as conn:
        conn.execute(
            "INSERT INTO oncology_data(PatientID,Event) VALUES (?,?)",
            ("P9", "D"),
        )
        raise RuntimeError("boom")

    recs = db_with_schema.get_patient_records("P9")
    assert recs == []


def test_save_raises_when_lastrowid_missing(monkeypatch):
    import contextlib

    from kilimanjaro_oncology.database.database_service import DatabaseService

    class _NoLock:
        def __enter__(self):
            return None

        def __exit__(self, _exc_type, _exc, _tb):
            return False

    class _Cursor:
        lastrowid = None

        def execute(self, _sql, _values):
            return None

    class _Conn:
        def cursor(self):
            return _Cursor()

        def commit(self):
            return None

        def rollback(self):
            return None

    @contextlib.contextmanager
    def fake_get_connection(self):
        yield _Conn()

    ds = DatabaseService("ignored.sqlite")
    monkeypatch.setattr(ds, "get_connection", fake_get_connection.__get__(ds))
    monkeypatch.setattr(ds, "_write_lock", _NoLock())

    import pytest

    with pytest.raises(RuntimeError):
        ds.save_diagnosis_record({"patient_id": "PZ"})


def test_save_rolls_back_on_sqlite_error(monkeypatch):
    import contextlib

    from kilimanjaro_oncology.database.database_service import DatabaseService

    class _NoLock:
        def __enter__(self):
            return None

        def __exit__(self, _exc_type, _exc, _tb):
            return False

    class _Cursor:
        def execute(self, _sql, _values):
            raise sqlite3.Error("boom")

    class _Conn:
        def __init__(self):
            self.rolled_back = False

        def cursor(self):
            return _Cursor()

        def commit(self):
            return None

        def rollback(self):
            self.rolled_back = True

    @contextlib.contextmanager
    def fake_get_connection(self):
        conn = _Conn()
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise

    ds = DatabaseService("ignored.sqlite")
    monkeypatch.setattr(ds, "get_connection", fake_get_connection.__get__(ds))
    monkeypatch.setattr(ds, "_write_lock", _NoLock())

    import pytest

    with pytest.raises(sqlite3.Error):
        ds.save_diagnosis_record({"patient_id": "PX"})


def test_close_connections_removes_thread_local(db_with_schema):
    with db_with_schema.get_connection():
        assert hasattr(db_with_schema._local, "connection")
    db_with_schema.close_connections()
    assert not hasattr(db_with_schema._local, "connection")


def test_thread_local_connections_are_distinct(db_with_schema):
    import threading

    results = []

    def worker():
        with db_with_schema.get_connection() as conn:
            results.append(conn)

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert len(results) == 2
    assert results[0] is not results[1]


def test_connection_pragmas_set(db_with_schema):
    with db_with_schema.get_connection() as conn:
        fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        sync = conn.execute("PRAGMA synchronous;").fetchone()[0]
        timeout = conn.execute("PRAGMA busy_timeout;").fetchone()[0]
    assert fk == 1
    assert str(mode).lower() == "wal"
    assert sync in (1, 2)
    assert timeout == 5000
