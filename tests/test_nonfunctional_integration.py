import os
import stat
import tkinter as tk

import pytest

from kilimanjaro_oncology.database.database_service import DatabaseService
from kilimanjaro_oncology.gui.config_screen import ConfigScreen


def _schema_path():
    return os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
        "kilimanjaro_oncology",
        "database",
        "schema.sql",
    )


def test_readonly_database_rejects_writes(config_module, tmp_path):
    config_module.SCHEMA_FILE.write_text(open(_schema_path()).read())
    db_path = tmp_path / "readonly.sqlite"
    cm = config_module.ConfigManager()
    cm.settings["db_path"] = str(db_path)
    cm.initialize_database()

    # Make file read-only to simulate inability to write.
    os.chmod(db_path, stat.S_IREAD)

    db = DatabaseService(str(db_path))
    with pytest.raises(Exception):
        db.save_diagnosis_record({"patient_id": "RO", "event": "D"})


def test_backup_restore_round_trip(config_module, tmp_path, monkeypatch):
    config_module.SCHEMA_FILE.write_text(open(_schema_path()).read())
    db_path = tmp_path / "active.sqlite"
    cm = config_module.ConfigManager()
    cm.settings["db_path"] = str(db_path)
    cm.initialize_database()

    db = DatabaseService(str(db_path))
    db.save_diagnosis_record({"patient_id": "B1", "event": "Diagnosis"})

    class _Parent(tk.Tk):
        def __init__(self, config_manager):
            super().__init__()
            self.config_manager = config_manager
            self.db_service = db
            self.record_ctrl = None

        def apply_font_size(self):
            return None

        def show_new_diagnosis_screen(self):
            return None

    parent = _Parent(cm)
    parent.withdraw()
    try:
        screen = ConfigScreen(parent)
        screen.db_path_var.set(str(db_path))

        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.filedialog.askdirectory",
            lambda **_k: str(backup_dir),
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.messagebox.showinfo",
            lambda *_a, **_k: None,
        )
        screen.backup_database()

        backups = list(backup_dir.glob("database_*.sqlite"))
        assert backups

        # Restore from backup into a fresh database path
        restore_path = tmp_path / "restored.sqlite"
        screen.db_path_var.set(str(restore_path))
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.filedialog.askopenfilename",
            lambda **_k: str(backups[0]),
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.messagebox.askyesno",
            lambda *_a, **_k: True,
        )
        screen.restore_database()

        restored = DatabaseService(str(restore_path))
        recs = restored.get_patient_records("B1")
        assert recs
    finally:
        parent.destroy()
