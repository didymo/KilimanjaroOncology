import tkinter as tk
import pytest
from kilimanjaro_oncology.gui.common_widgets import AutoCompleteCombobox

@pytest.fixture
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()

def test_autocomplete_filters(tk_root):
    combo = AutoCompleteCombobox(tk_root, values=["Apple","Banana","Apricot"])
    combo.set_completion_list(["Apple","Banana","Apricot"])
    # simulate typing “ap”
    combo.insert(0, "ap")
    combo.event_generate("<KeyRelease>")
    # expect “Apple”, “Apricot”
    vals = combo["values"]
    assert "Apple" in vals and "Apricot" in vals and "Banana" not in vals
