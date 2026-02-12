import contextlib
import tkinter as tk

import pytest

from kilimanjaro_oncology.gui.config_screen import ConfigScreen


@pytest.fixture
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


class _DummyCursor:
    def __init__(self, calls):
        self.calls = calls

    def execute(self, sql, params):
        self.calls.append((sql, params))


class _DummyConn:
    def __init__(self, calls):
        self.calls = calls

    def cursor(self):
        return _DummyCursor(self.calls)


class _DummyDB:
    def __init__(self, _path):
        self.calls = []

    @contextlib.contextmanager
    def get_connection(self):
        yield _DummyConn(self.calls)


class _DummyRecordCtrl:
    def __init__(self, _db):
        pass


class _DummyConfigManager:
    def __init__(self):
        self.settings = {
            "db_path": "",
            "hospital_name": "",
            "department_name": "",
            "font_size": 10,
        }
        self.saved = False
        self.initialized = False

    def save_settings(self):
        self.saved = True

    def initialize_database(self):
        self.initialized = True


class _Parent(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config_manager = _DummyConfigManager()
        self.font_applied = False
        self.db_service = None
        self.record_ctrl = None
        self.screen_shown = False

    def apply_font_size(self):
        self.font_applied = True

    def show_new_diagnosis_screen(self):
        self.screen_shown = True


def test_select_existing_db_sets_path(tk_root, monkeypatch, tmp_path):
    parent = _Parent()
    parent.withdraw()
    try:
        screen = ConfigScreen(parent)
        selected = tmp_path / "test.sqlite"
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.filedialog.askopenfilename",
            lambda **_k: str(selected),
        )
        screen.select_existing_db()
        assert screen.db_path_var.get() == str(selected)
    finally:
        parent.destroy()


def test_select_db_folder_sets_database_file(tk_root, monkeypatch, tmp_path):
    parent = _Parent()
    parent.withdraw()
    try:
        screen = ConfigScreen(parent)
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.filedialog.askdirectory",
            lambda **_k: str(tmp_path),
        )
        screen.select_db_folder()
        assert screen.db_path_var.get() == str(tmp_path / "database.sqlite")
    finally:
        parent.destroy()


def test_save_and_continue_updates_settings(monkeypatch, tmp_path):
    parent = _Parent()
    parent.withdraw()
    try:
        db_path = tmp_path / "db.sqlite"
        screen = ConfigScreen(parent)
        screen.db_path_var.set(str(db_path))
        screen.hospital_var.set("HOSP")
        screen.department_var.set("DEPT")
        screen.font_size_var.set("14")

        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.DatabaseService",
            _DummyDB,
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.RecordController",
            _DummyRecordCtrl,
        )

        screen.save_and_continue()

        assert parent.config_manager.saved is True
        assert parent.config_manager.initialized is True
        assert parent.font_applied is True
        assert parent.screen_shown is True
        assert parent.config_manager.settings["db_path"] == str(db_path)
        assert parent.config_manager.settings["hospital_name"] == "HOSP"
        assert parent.config_manager.settings["department_name"] == "DEPT"
        assert parent.config_manager.settings["font_size"] == 14

        assert isinstance(parent.db_service, _DummyDB)
        assert isinstance(parent.record_ctrl, _DummyRecordCtrl)
        assert ("hospital_name", "HOSP") in [
            params for _sql, params in parent.db_service.calls
        ]
        assert ("department_name", "DEPT") in [
            params for _sql, params in parent.db_service.calls
        ]
    finally:
        parent.destroy()


def test_save_and_continue_requires_db_path():
    parent = _Parent()
    parent.withdraw()
    try:
        screen = ConfigScreen(parent)
        screen.db_path_var.set("")
        screen.save_and_continue()
        assert parent.config_manager.saved is False
        assert parent.screen_shown is False
    finally:
        parent.destroy()


def test_backup_database_copies_file(monkeypatch, tmp_path):
    parent = _Parent()
    parent.withdraw()
    try:
        screen = ConfigScreen(parent)
        db_path = tmp_path / "db.sqlite"
        db_path.write_text("data")
        screen.db_path_var.set(str(db_path))

        dest_dir = tmp_path / "backup"
        dest_dir.mkdir()

        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.filedialog.askdirectory",
            lambda **_k: str(dest_dir),
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.sqlite3.connect",
            lambda *_a, **_k: (_ for _ in ()).throw(
                __import__("sqlite3").Error("nope")
            ),
        )

        copied = {}

        def fake_copy(src, dst):
            copied["src"] = src
            copied["dst"] = dst
            return dst

        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.shutil.copy2",
            fake_copy,
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.messagebox.showinfo",
            lambda *_a, **_k: None,
        )

        screen.backup_database()
        assert copied["src"] == str(db_path)
        assert str(copied["dst"]).startswith(str(dest_dir))
    finally:
        parent.destroy()


def test_restore_database_overwrites_file(monkeypatch, tmp_path):
    parent = _Parent()
    parent.withdraw()
    try:
        screen = ConfigScreen(parent)
        db_path = tmp_path / "db.sqlite"
        db_path.write_text("old")
        backup_path = tmp_path / "backup.sqlite"
        backup_path.write_text("new")
        screen.db_path_var.set(str(db_path))

        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.filedialog.askopenfilename",
            lambda **_k: str(backup_path),
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.messagebox.askyesno",
            lambda *_a, **_k: True,
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.messagebox.showinfo",
            lambda *_a, **_k: None,
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.DatabaseService",
            _DummyDB,
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.RecordController",
            _DummyRecordCtrl,
        )

        def fake_copy(src, dst):
            assert src == str(backup_path)
            assert dst == str(db_path)
            return dst

        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.shutil.copy2",
            fake_copy,
        )

        screen.restore_database()
    finally:
        parent.destroy()


def test_back_to_main_disabled_without_db_path():
    parent = _Parent()
    parent.withdraw()
    try:
        screen = ConfigScreen(parent)
        screen.db_path_var.set("")
        screen._update_back_button_state()
        assert screen.back_button.instate(["disabled"])
    finally:
        parent.destroy()


def test_back_to_main_enabled_with_db_path_and_navigates(tmp_path):
    parent = _Parent()
    parent.withdraw()
    try:
        screen = ConfigScreen(parent)
        screen.db_path_var.set(str(tmp_path / "db.sqlite"))
        screen._update_back_button_state()
        assert not screen.back_button.instate(["disabled"])
        screen.back_to_main()
        assert parent.screen_shown is True
    finally:
        parent.destroy()


def test_back_to_main_cancel_keeps_user_on_config(monkeypatch, tmp_path):
    parent = _Parent()
    parent.withdraw()
    try:
        screen = ConfigScreen(parent)
        screen.db_path_var.set(str(tmp_path / "db.sqlite"))
        screen.hospital_var.set("Changed")
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.messagebox.askyesnocancel",
            lambda *_a, **_k: None,
        )
        screen.back_to_main()
        assert parent.screen_shown is False
        assert parent.config_manager.saved is False
    finally:
        parent.destroy()


def test_back_to_main_discard_changes_navigates_without_save(
    monkeypatch, tmp_path
):
    parent = _Parent()
    parent.withdraw()
    try:
        screen = ConfigScreen(parent)
        screen.db_path_var.set(str(tmp_path / "db.sqlite"))
        screen.hospital_var.set("Changed")
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.messagebox.askyesnocancel",
            lambda *_a, **_k: False,
        )
        screen.back_to_main()
        assert parent.screen_shown is True
        assert parent.config_manager.saved is False
    finally:
        parent.destroy()


def test_back_to_main_save_changes_then_navigates(monkeypatch, tmp_path):
    parent = _Parent()
    parent.withdraw()
    try:
        screen = ConfigScreen(parent)
        db_path = tmp_path / "db.sqlite"
        screen.db_path_var.set(str(db_path))
        screen.hospital_var.set("HOSP")
        screen.department_var.set("DEPT")
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.DatabaseService",
            _DummyDB,
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.RecordController",
            _DummyRecordCtrl,
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.config_screen.messagebox.askyesnocancel",
            lambda *_a, **_k: True,
        )
        screen.back_to_main()
        assert parent.config_manager.saved is True
        assert parent.screen_shown is True
    finally:
        parent.destroy()
