import datetime
import tkinter as tk

import pytest

from kilimanjaro_oncology.gui.follow_up_screen import FollowUpScreen


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
        return 2


def test_followup_copy_to_clipboard_includes_prefix(tk_root, monkeypatch):
    rc = _RecordCtrl({"hospital_name": "HOSP", "department_name": "DEPT"})
    screen = FollowUpScreen(tk_root, _Controller(), rc)
    screen.record.patient_id = "1234.C18"
    screen.record.diagnosis = "C18"
    screen.record.event_date = datetime.datetime(2025, 1, 2)
    screen.date_var.set("2025-01-02")

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
        "kilimanjaro_oncology.gui.follow_up_screen.messagebox.showinfo",
        fake_info,
    )

    screen.copy_to_clipboard()
    assert "HOSP.DEPT.1234.C18" in clipboard["text"]
    assert rc.saved
    assert "Record saved successfully" in shown["message"]


def test_followup_update_event_date_invalid(tk_root):
    rc = _RecordCtrl({"hospital_name": "H", "department_name": "D"})
    screen = FollowUpScreen(tk_root, _Controller(), rc)
    before = screen.record.event_date
    screen.date_var.set("bad-date")
    screen.update_event_date()
    assert screen.record.event_date == before
