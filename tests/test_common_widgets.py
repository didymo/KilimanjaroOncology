import csv
import os
import tkinter as tk

import pytest

from kilimanjaro_oncology.gui.common_widgets import (
    AutoCompleteCombobox,
    DiagnosisCombobox,
)


@pytest.fixture
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_autocomplete_filters(tk_root):
    combo = AutoCompleteCombobox(tk_root, values=["Apple", "Banana", "Apricot"])
    combo.set_completion_list(["Apple", "Banana", "Apricot"])
    # simulate typing “ap”
    combo.insert(0, "ap")
    combo.event_generate("<KeyRelease>")
    # expect “Apple”, “Apricot”
    vals = combo["values"]
    assert "Apple" in vals and "Apricot" in vals and "Banana" not in vals


def test_autocomplete_filters_match_values(tk_root):
    combo = AutoCompleteCombobox(
        tk_root,
        values=["Alpha", "Beta"],
        match_values=["A1", "B2"],
    )
    combo.insert(0, "b2")
    combo.event_generate("<KeyRelease>")
    vals = combo["values"]
    assert vals == ("Beta",)


def test_diagnosis_combobox_selects_code(tk_root):
    picked = {}

    def on_select(code):
        picked["code"] = code

    combo = DiagnosisCombobox(tk_root, on_select_code=on_select)
    # Use first entry from CSV to avoid hardcoding a code value.
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
    expected_code = row[0].strip()
    expected_display = " ".join(row).strip()

    combo.set(expected_display)
    combo._handle_selection(None)
    assert picked["code"] == expected_code


def test_diagnosis_combobox_ignores_tab(tk_root):
    combo = DiagnosisCombobox(tk_root, on_select_code=lambda _c: None)

    class E:
        keysym = "Tab"

    combo._on_keyrelease(E())
    assert combo._open_after_id is None
