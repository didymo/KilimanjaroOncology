import csv
import os
import tkinter as tk

import pytest

from kilimanjaro_oncology.gui.config_screen import ConfigScreen
from kilimanjaro_oncology.gui.death_screen import DeathScreen
from kilimanjaro_oncology.gui.follow_up_screen import FollowUpScreen
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


class _Parent(tk.Tk):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.db_service = None
        self.record_ctrl = None
        self._font_applied = False

    def apply_font_size(self):
        self._font_applied = True

    def show_new_diagnosis_screen(self):
        return None


def _first_icd_code():
    path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
        "kilimanjaro_oncology",
        "csv_files",
        "Diagnosis.ICD10.csv",
    )
    with open(path, newline="", encoding="latin-1") as f:
        row = next(csv.reader(f))
    return row[0].strip(), " ".join(row).strip()


def test_full_flow_config_new_dx_followup_death(
    tk_root, config_module, tmp_path, monkeypatch
):
    schema_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
        "kilimanjaro_oncology",
        "database",
        "schema.sql",
    )
    config_module.SCHEMA_FILE.write_text(open(schema_path).read())

    parent = _Parent(config_module.ConfigManager())
    parent.withdraw()
    try:
        # Config flow
        screen = ConfigScreen(parent)
        db_path = tmp_path / "integration.sqlite"
        screen.db_path_var.set(str(db_path))
        screen.hospital_var.set("HOSP")
        screen.department_var.set("DEPT")
        screen.font_size_var.set("12")
        screen.save_and_continue()

        assert db_path.exists()
        assert parent.db_service is not None
        assert parent.record_ctrl is not None
        assert parent._font_applied is True

        # New diagnosis flow
        code, _display = _first_icd_code()
        new_dx = NewDiagnosisScreen(parent, _Controller(), parent.record_ctrl)
        new_dx.patient_id_var.set("0001")
        new_dx.update_patient_id()
        new_dx._on_new_dx_chosen(code)
        new_dx.date_var.set("2025-01-01")
        new_dx.update_event_date()
        new_dx.record.histo = "H1"
        new_dx.record.grade = "2"
        new_dx.record.factors = "F1"

        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.new_diagnosis_screen.messagebox.showinfo",
            lambda *_a, **_k: None,
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.new_diagnosis_screen.messagebox.showerror",
            lambda *_a, **_k: None,
        )
        new_dx.clipboard_clear = lambda: None
        new_dx.clipboard_append = lambda _t: None
        new_dx.copy_to_clipboard()

        raw_patient_id = f"0001.{code}"

        # Follow-up flow
        follow = FollowUpScreen(parent, _Controller(), parent.record_ctrl)
        follow.record.patient_id = raw_patient_id
        follow.record.diagnosis = code
        follow.record.histo = "H1"
        follow.record.grade = "2"
        follow.record.factors = "F1"
        follow.date_var.set("2025-02-01")
        follow.update_event_date()
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.follow_up_screen.messagebox.showinfo",
            lambda *_a, **_k: None,
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.follow_up_screen.messagebox.showerror",
            lambda *_a, **_k: None,
        )
        follow.clipboard_clear = lambda: None
        follow.clipboard_append = lambda _t: None
        follow.copy_to_clipboard()

        # Death flow
        death = DeathScreen(parent, _Controller(), parent.record_ctrl)
        death.record.patient_id = raw_patient_id
        death.record.diagnosis = code
        death.death_date_var.set("2025-03-01")
        death.cause_of_death_var.set("Cause A")
        death.record.death_cause = "Cause A"
        death._update_death_date()
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.death_screen.messagebox.showinfo",
            lambda *_a, **_k: None,
        )
        monkeypatch.setattr(
            "kilimanjaro_oncology.gui.death_screen.messagebox.showerror",
            lambda *_a, **_k: None,
        )
        death.clipboard_clear = lambda: None
        death.clipboard_append = lambda _t: None
        death.copy_to_clipboard()

        # Verify persisted records
        recs = parent.db_service.get_patient_records(raw_patient_id)
        events = [r["Event"] for r in recs]
        assert "Diagnosis" in events
        assert "Management" in events
        assert "Death" in events
        assert any(r.get("Death_Date") for r in recs)
        assert any(r.get("Death_Cause") for r in recs)
    finally:
        parent.destroy()
