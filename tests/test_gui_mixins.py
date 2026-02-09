import csv
import os
import tkinter as tk

import pytest

from kilimanjaro_oncology.classes.oncology_patient_data import (
    OncologyPatientData,
)
from kilimanjaro_oncology.gui.common_widgets import (
    CancerDetailsMixin,
    CarePlanMixin,
    NotesMixin,
    PatientInfoMixin,
)


@pytest.fixture
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


class _RecordCtrl:
    def __init__(self, data):
        self._data = data

    def fetch_patient_ids(self, _prefix):
        return ["P1", "P2"]

    def fetch_patient_data(self, _pid):
        return self._data


class _PatientInfoScreen(PatientInfoMixin, CancerDetailsMixin, tk.Frame):
    def __init__(self, parent, record_ctrl):
        super().__init__(parent)
        self.scrollable_frame = tk.Frame(self)
        self.record_ctrl = record_ctrl
        self.record = OncologyPatientData()
        self.date_label_text = "Date"
        self.create_patient_info()
        self.create_cancer_details()

    def update_event_date(self, *args):
        return None


class _CarePlanScreen(CarePlanMixin, tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.scrollable_frame = tk.Frame(self)
        self.record = OncologyPatientData()
        self.create_care_plan()


class _CancerDetailsScreen(CancerDetailsMixin, tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.scrollable_frame = tk.Frame(self)
        self.record = OncologyPatientData()
        self.create_cancer_details()


class _NotesScreen(NotesMixin, tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.scrollable_frame = tk.Frame(self)
        self.record = OncologyPatientData()
        self.create_notes()


def test_patient_info_on_key_and_select_populates_fields(tk_root, monkeypatch):
    import tkinter.ttk as ttk

    callbacks = {}
    orig_bind = ttk.Combobox.bind

    def capture_bind(self, sequence=None, func=None, add=None):
        if sequence in ("<KeyRelease>", "<<ComboboxSelected>>") and func:
            callbacks[(sequence, self)] = func
        return orig_bind(self, sequence, func, add)

    monkeypatch.setattr(ttk.Combobox, "bind", capture_bind)

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
    code = row[0].strip()
    display = " ".join(row).strip()

    data = {
        "Diagnosis": code,
        "Histo": "H1",
        "Grade": "2",
        "Factors": "F1",
    }
    screen = _PatientInfoScreen(tk_root, _RecordCtrl(data))

    class E:
        def __init__(self, widget):
            self.widget = widget

    screen.patient_id_var.set("P")
    callbacks[("<KeyRelease>", screen.patient_id_combo)](
        E(screen.patient_id_combo)
    )
    assert list(screen.patient_id_combo["values"]) == ["P1", "P2"]

    screen.patient_id_var.set("P1")
    callbacks[("<<ComboboxSelected>>", screen.patient_id_combo)](
        E(screen.patient_id_combo)
    )
    assert screen.record.patient_id == "P1"
    assert screen.record.diagnosis == code
    assert screen.diagnosis_combo.get() == display
    assert screen.record.histo == "H1"
    assert screen.record.grade == "2"
    assert screen.factors_entry.get() == "F1"


def test_patient_info_on_select_with_missing_data(tk_root, monkeypatch):
    import tkinter.ttk as ttk

    callbacks = {}
    orig_bind = ttk.Combobox.bind

    def capture_bind(self, sequence=None, func=None, add=None):
        if sequence in ("<KeyRelease>", "<<ComboboxSelected>>") and func:
            callbacks[(sequence, self)] = func
        return orig_bind(self, sequence, func, add)

    monkeypatch.setattr(ttk.Combobox, "bind", capture_bind)

    screen = _PatientInfoScreen(tk_root, _RecordCtrl({}))

    class E:
        def __init__(self, widget):
            self.widget = widget

    screen.patient_id_var.set("P1")
    callbacks[("<<ComboboxSelected>>", screen.patient_id_combo)](
        E(screen.patient_id_combo)
    )
    assert screen.record.diagnosis == ""
    assert screen.record.histo == ""


def test_care_plan_toggle_order(tk_root):
    screen = _CarePlanScreen(tk_root)
    b1 = screen.care_buttons[0]
    b2 = screen.care_buttons[1]

    screen.toggle_button(b1)
    screen.toggle_button(b2)
    assert (
        screen.record.careplan
        == f"{b1.cget('text')}, {b2.cget('text')}"
    )

    screen.toggle_button(b1)
    assert screen.record.careplan == b2.cget("text")


def test_cancer_details_update_stage(tk_root):
    screen = _CancerDetailsScreen(tk_root)
    screen.t_stage_combo.set("T2")
    screen.n_stage_combo.set("N1")
    screen.m_stage_combo.set("M0")
    screen.update_stage()
    assert screen.record.stage == "T2 N1 M0"

    screen.m_stage_combo.set("")
    screen.update_stage()
    assert screen.record.stage == "T2 N1"


def test_cancer_details_grade_typed_updates_record(tk_root):
    screen = _CancerDetailsScreen(tk_root)
    screen.grade_var.set("3")
    screen._on_grade_typed()
    assert screen.record.grade == 3

    screen.grade_var.set("X")
    screen._on_grade_typed()
    assert screen.record.grade == 3


def test_notes_mixin_updates_record(tk_root):
    screen = _NotesScreen(tk_root)
    screen.notes_text.insert("1.0", "Note A")
    screen.update_notes(None)
    assert screen.record.note == "Note A"
