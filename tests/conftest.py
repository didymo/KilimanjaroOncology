import importlib

import pytest


@pytest.fixture
def config_module(monkeypatch, tmp_path):
    """Provide a config module with paths redirected to a temp directory."""
    import kilimanjaro_oncology.utils.config as config

    app_dir = tmp_path / "africa_oncology_settings"
    settings_file = app_dir / "settings.json"
    database_file = app_dir / "database.sqlite"
    schema_file = tmp_path / "schema.sql"

    monkeypatch.setattr(config, "APP_DIR", app_dir, raising=True)
    monkeypatch.setattr(config, "SETTINGS_FILE", settings_file, raising=True)
    monkeypatch.setattr(config, "DATABASE_FILE", database_file, raising=True)
    monkeypatch.setattr(config, "SCHEMA_FILE", schema_file, raising=True)

    # Reload to ensure any module-level reads use the patched paths.
    importlib.reload(config)
    # Re-apply after reload (reload restores original constants).
    monkeypatch.setattr(config, "APP_DIR", app_dir, raising=True)
    monkeypatch.setattr(config, "SETTINGS_FILE", settings_file, raising=True)
    monkeypatch.setattr(config, "DATABASE_FILE", database_file, raising=True)
    monkeypatch.setattr(config, "SCHEMA_FILE", schema_file, raising=True)
    return config


@pytest.fixture
def schema_sql() -> str:
    return """
        CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE oncology_data(
            AutoincrementID INTEGER PRIMARY KEY,
            record_creation_datetime TEXT,
            PatientID TEXT,
            Event TEXT,
            Event_Date TEXT,
            Diagnosis TEXT,
            Histo TEXT,
            Grade TEXT,
            Factors TEXT,
            Stage TEXT,
            Careplan TEXT,
            Note TEXT,
            Death_Date TEXT,
            Death_Cause TEXT
        );
    """


@pytest.fixture
def db_with_schema(tmp_path, schema_sql):
    from kilimanjaro_oncology.database.database_service import DatabaseService

    db_file = tmp_path / "test.sqlite"
    ds = DatabaseService(str(db_file))
    with ds.get_connection() as conn:
        conn.executescript(schema_sql)
    return ds
