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

    def fetch_patient_summary(self, _pid):
        return "2025-01-01: C18, T2 N1 M0\n  Surgery - Primary"

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


def test_followup_updated_therapy_buttons_and_summary_panel(tk_root):
    rc = _RecordCtrl({"hospital_name": "H", "department_name": "D"})
    screen = FollowUpScreen(tk_root, _Controller(), rc)

    labels = [
        child.cget("text")
        for child in screen.winfo_children()[0].winfo_children()
        if child.winfo_class() in {"TLabel", "Label"}
    ]
    assert "Care Planned First" not in labels

    expected_buttons = {
        "Observe",
        "Primary",
        "Neoadjuvant",
        "Adjuvant",
        "Palliative",
        "PalliativeCare",
    }
    actual_buttons = {
        b.cget("text")
        for b in getattr(screen, "care_buttons", [])
    }
    assert expected_buttons.issubset(actual_buttons)

    assert screen.summary_text.cget("state") == "disabled"


def test_followup_copy_excludes_summary_text(tk_root, monkeypatch):
    rc = _RecordCtrl({"hospital_name": "HOSP", "department_name": "DEPT"})
    screen = FollowUpScreen(tk_root, _Controller(), rc)
    screen.record.patient_id = "1234.C18"
    screen.record.diagnosis = "C18"
    screen.record.event_date = datetime.datetime(2025, 1, 2)
    screen.date_var.set("2025-01-02")

    clipboard = {}
    screen.clipboard_clear = lambda: None
    screen.clipboard_append = lambda text: clipboard.setdefault("text", text)
    monkeypatch.setattr(
        "kilimanjaro_oncology.gui.follow_up_screen.messagebox.showinfo",
        lambda *_a, **_k: None,
    )

    screen.copy_to_clipboard()
    assert "Summary" not in clipboard["text"]
