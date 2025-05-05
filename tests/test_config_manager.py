import json
import tempfile
from pathlib import Path
import pytest
from kilimanjaro_oncology.utils.config import ConfigManager, APP_DIR, SETTINGS_FILE

@pytest.fixture(autouse=True)
def isolate_app_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))  # redirect APP_DIR
    yield

def test_default_settings_file_created(tmp_path):
    cm = ConfigManager()
    assert SETTINGS_FILE.exists()
    data = json.loads(SETTINGS_FILE.read_text())
    assert "db_path" in data
