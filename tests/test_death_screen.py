import datetime
import tkinter as tk

import pytest

from kilimanjaro_oncology.gui.death_screen import DeathScreen


@pytest.fixture
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


class _Controller:
    def show_new_diagnosis_screen(self):
        return None

    def show_followup_screen(self):
        return None

    def show_death_screen(self):
        return None


class _RecordCtrl:
    def __init__(self, settings):
        self._settings = settings
        self.saved = []

    def fetch_settings(self, keys):
        return {k: self._settings.get(k, "") for k in keys}

    def fetch_patient_ids(self, _prefix):
        return []

    def fetch_patient_data(self, _pid):
        return {}

    def save_record(self, data):
        self.saved.append(data)
        return 3


def test_death_screen_death_date_parsing(tk_root):
    rc = _RecordCtrl({"hospital_name": "H", "department_name": "D"})
    screen = DeathScreen(tk_root, _Controller(), rc)
    screen.death_date_var.set("not-a-date")
    screen._update_death_date()
    assert screen.record.death_date is None


def test_death_screen_copy_to_clipboard(tk_root, monkeypatch):
    rc = _RecordCtrl({"hospital_name": "HOSP", "department_name": "DEPT"})
    screen = DeathScreen(tk_root, _Controller(), rc)
    screen.record.patient_id = "1234.C18"
    screen.record.diagnosis = "C18"
    screen.record.event_date = datetime.datetime(2025, 1, 3)
    screen.death_date_var.set("2025-01-04")
    screen.cause_of_death_var.set("Cause A")
    screen.record.death_cause = "Cause A"
    screen._update_death_date()

    clipboard = {}

    def fake_clear():
        clipboard.clear()

    def fake_append(text):
        clipboard["text"] = text

    screen.clipboard_clear = fake_clear
    screen.clipboard_append = fake_append

    shown = {}

    def fake_info(_title, message):
        shown["message"] = message

    monkeypatch.setattr(
        "kilimanjaro_oncology.gui.death_screen.messagebox.showinfo",
        fake_info,
    )

    screen.copy_to_clipboard()
    assert "HOSP.DEPT.1234.C18" in clipboard["text"]
    assert "Death_Date: 2025-01-04" in clipboard["text"]
    assert "Death_Cause: Cause A" in clipboard["text"]
    assert rc.saved
    assert "Record saved successfully" in shown["message"]
