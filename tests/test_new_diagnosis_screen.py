import datetime
import tkinter as tk

import pytest

from kilimanjaro_oncology.gui.new_diagnosis_screen import NewDiagnosisScreen


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

    def save_record(self, data):
        self.saved.append(data)
        return 1


def test_patient_id_and_diagnosis_append(tk_root):
    rc = _RecordCtrl({"hospital_name": "HOSP", "department_name": "DEPT"})
    screen = NewDiagnosisScreen(tk_root, _Controller(), rc)
    screen.patient_id_var.set("0001")
    screen.update_patient_id()
    assert screen.record.patient_id == "HOSP.DEPT.0001"
    screen._on_new_dx_chosen("C50")
    assert screen.record.patient_id == "HOSP.DEPT.0001.C50"


def test_update_event_date_invalid_no_crash(tk_root):
    rc = _RecordCtrl({"hospital_name": "H", "department_name": "D"})
    screen = NewDiagnosisScreen(tk_root, _Controller(), rc)
    before = screen.record.event_date
    screen.date_var.set("not-a-date")
    screen.update_event_date()
    assert screen.record.event_date == before


def test_copy_to_clipboard_strips_prefix_and_saves(tk_root, monkeypatch):
    rc = _RecordCtrl({"hospital_name": "HOSP", "department_name": "DEPT"})
    screen = NewDiagnosisScreen(tk_root, _Controller(), rc)
    screen.patient_id_var.set("1234")
    screen._on_new_dx_chosen("C34")
    screen.record.event_date = datetime.datetime(2025, 1, 1)
    screen.date_var.set("2025-01-01")

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
        "kilimanjaro_oncology.gui.new_diagnosis_screen.messagebox.showinfo",
        fake_info,
    )

    screen.copy_to_clipboard()
    assert rc.saved
    assert rc.saved[0]["patient_id"] == "1234.C34"
    assert "Record saved successfully" in shown["message"]
