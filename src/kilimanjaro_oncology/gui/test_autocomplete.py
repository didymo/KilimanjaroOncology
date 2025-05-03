# src/app/gui/test_autocomplete.py
import tkinter as tk

from kilimanjaro_oncology.gui.common_widgets import AutoCompleteCombobox

# from gui.custom_widgets import AutoCompleteCombobox


def main():
    root = tk.Tk()
    root.title("AutoCompleteCombobox Test")

    # Define some test values.
    fruits = [
        "Apple",
        "Apricot",
        "Banana",
        "Blackberry",
        "Blueberry",
        "Cherry",
        "Date",
        "Grape",
    ]

    # Create an instance of the AutoCompleteCombobox.
    ac_combo = AutoCompleteCombobox(root, values=fruits)
    ac_combo.pack(padx=10, pady=10)

    # Optionally, you can test updating the completion list later.
    # ac_combo.set_completion_list(fruits)

    root.mainloop()


if __name__ == "__main__":
    main()
