import json


def test_default_settings_file_created(config_module):
    config_module.ConfigManager()
    assert config_module.SETTINGS_FILE.exists()
    data = json.loads(config_module.SETTINGS_FILE.read_text())
    assert "db_path" in data
    assert "font_size" in data


def test_config_exists_missing_file(config_module):
    cm = config_module.ConfigManager()
    config_module.SETTINGS_FILE.unlink()
    assert cm.config_exists() is False


def test_config_exists_invalid_json(config_module):
    cm = config_module.ConfigManager()
    config_module.SETTINGS_FILE.write_text("{not valid json")
    assert cm.config_exists() is False


def test_config_exists_unreadable_file(config_module, monkeypatch):
    cm = config_module.ConfigManager()
    config_module.SETTINGS_FILE.write_text("{}")

    def boom(*_a, **_k):
        raise OSError("nope")

    monkeypatch.setattr("builtins.open", boom)
    assert cm.config_exists() is False


def test_config_exists_missing_db_path(config_module):
    cm = config_module.ConfigManager()
    config_module.SETTINGS_FILE.write_text(json.dumps({"font_size": 11}))
    assert cm.config_exists() is False


def test_config_exists_db_path_not_found(config_module):
    cm = config_module.ConfigManager()
    config_module.SETTINGS_FILE.write_text(
        json.dumps({"db_path": "/nope.sqlite"})
    )
    assert cm.config_exists() is False


def test_config_exists_db_path_found(config_module, tmp_path):
    cm = config_module.ConfigManager()
    db_file = tmp_path / "exists.sqlite"
    db_file.write_text("")
    config_module.SETTINGS_FILE.write_text(
        json.dumps({"db_path": str(db_file)})
    )
    assert cm.config_exists() is True


def test_load_settings_fallback_on_invalid_json(config_module):
    config_module.APP_DIR.mkdir(parents=True, exist_ok=True)
    config_module.SETTINGS_FILE.write_text("{broken")
    cm = config_module.ConfigManager()
    assert "db_path" in cm.settings


def test_save_settings_raises_on_io_error(config_module, monkeypatch):
    cm = config_module.ConfigManager()

    def boom(*_a, **_k):
        raise OSError("disk full")

    monkeypatch.setattr("builtins.open", boom)

    import pytest

    with pytest.raises(OSError):
        cm.save_settings()


def test_initialize_settings_missing_db_path(config_module):
    cm = config_module.ConfigManager()
    cm.settings = {}
    import pytest

    with pytest.raises(config_module.ConfigurationError):
        cm.initialize_settings()


def test_initialize_database_creates_and_verifies(config_module, schema_sql):
    config_module.SCHEMA_FILE.write_text(schema_sql)
    cm = config_module.ConfigManager()
    cm.settings["db_path"] = str(config_module.DATABASE_FILE)
    cm.initialize_database()
    assert config_module.DATABASE_FILE.exists()


def test_initialize_database_missing_schema(config_module):
    cm = config_module.ConfigManager()
    cm.settings["db_path"] = str(config_module.DATABASE_FILE)
    import pytest

    with pytest.raises(config_module.DatabaseError):
        cm.initialize_database()


def test_create_database_missing_schema_does_not_create_db(config_module, tmp_path):
    cm = config_module.ConfigManager()
    db_path = tmp_path / "no_schema.sqlite"
    import pytest

    with pytest.raises(config_module.DatabaseError):
        cm._create_database(db_path)
    assert not db_path.exists()


def test_initialize_database_missing_tables(config_module, tmp_path):
    schema = """
        CREATE TABLE oncology_data(
            AutoincrementID INTEGER PRIMARY KEY,
            PatientID TEXT
        );
        CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT);
    """
    config_module.SCHEMA_FILE.write_text(schema)

    # create a DB missing the settings table to force verification failure
    db_path = tmp_path / "bad.sqlite"
    import sqlite3

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(
            "CREATE TABLE oncology_data(AutoincrementID INTEGER PRIMARY KEY, PatientID TEXT);"
        )
        conn.commit()
    finally:
        conn.close()

    cm = config_module.ConfigManager()
    cm.settings["db_path"] = str(db_path)

    import pytest

    with pytest.raises(config_module.DatabaseError):
        cm.initialize_database()


def test_initialize_database_sqlite_error(config_module, schema_sql, monkeypatch):
    config_module.SCHEMA_FILE.write_text(schema_sql)

    def boom(*_a, **_k):
        raise config_module.sqlite3.Error("fail")

    monkeypatch.setattr(config_module.sqlite3, "connect", boom)

    cm = config_module.ConfigManager()
    cm.settings["db_path"] = str(config_module.DATABASE_FILE)

    import pytest

    with pytest.raises(config_module.DatabaseError):
        cm.initialize_database()


def test_initialize_database_os_error(config_module, schema_sql, monkeypatch):
    config_module.SCHEMA_FILE.write_text(schema_sql)

    def boom(*_a, **_k):
        raise PermissionError("readonly")

    monkeypatch.setattr(config_module.sqlite3, "connect", boom)

    cm = config_module.ConfigManager()
    cm.settings["db_path"] = str(config_module.DATABASE_FILE)

    import pytest

    with pytest.raises(config_module.DatabaseError):
        cm.initialize_database()


def test_verify_database_schema_parsing_tolerates_whitespace(config_module, tmp_path):
    schema = """
        -- comment
          CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE oncology_data(AutoincrementID INTEGER PRIMARY KEY);
    """
    config_module.SCHEMA_FILE.write_text(schema)

    import sqlite3

    db_path = tmp_path / "ok.sqlite"
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE oncology_data(AutoincrementID INTEGER PRIMARY KEY);
            """
        )
        conn.commit()
    finally:
        conn.close()

    cm = config_module.ConfigManager()
    cm._verify_database(db_path)


def test_initialize_database_corrupt_db_file(config_module, schema_sql, tmp_path):
    config_module.SCHEMA_FILE.write_text(schema_sql)
    db_path = tmp_path / "corrupt.sqlite"
    db_path.write_bytes(b"not-a-sqlite-db")

    cm = config_module.ConfigManager()
    cm.settings["db_path"] = str(db_path)

    import pytest

    with pytest.raises(config_module.DatabaseError):
        cm.initialize_database()


def test_check_initialization_handles_exception(config_module, monkeypatch):
    def boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(config_module, "ConfigManager", boom)
    assert config_module.check_initialization() is False
