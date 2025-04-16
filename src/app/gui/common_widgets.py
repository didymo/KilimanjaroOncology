# src/app/gui/common_widgets.py
from tkinter import ttk


class AutoCompleteCombobox(ttk.Combobox):
    """
    A ttk.Combobox with basic auto-complete functionality.
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        # Store the initial list of values for later filtering.
        self._completion_list = list(kwargs.get("values", []))
        self.bind("<KeyRelease>", self._on_keyrelease)

    def set_completion_list(self, completion_list):
        """
        Set a new list of values for auto-completion.
        """
        self._completion_list = completion_list
        self["values"] = self._completion_list

    def _on_keyrelease(self, event):
        """
        Update the drop-down list based on the current text.
        """
        typed = self.get()
        if not typed:
            self["values"] = self._completion_list
        else:
            filtered = [
                item for item in self._completion_list if typed.lower() in item.lower()
            ]
            self["values"] = filtered
        # Automatically show the drop-down list after filtering.
        self.event_generate("<Down>")


def create_common_header(parent, controller):
    """
    Create a common header frame with navigation buttons.

    Args:
        parent: The parent widget where the header will be placed.
        controller: The controller object that provides navigation methods.

    Returns:
        A ttk.Frame containing the header buttons.
    """
    header_frame = ttk.Frame(parent)
    header_frame.pack(fill="x", padx=5, pady=5)

    new_dx_btn = ttk.Button(
        header_frame,
        text="New Dx",
        style="Active.TButton",
        command=controller.show_new_diagnosis_screen,
    )
    followup_btn = ttk.Button(
        header_frame,
        text="FollowUp",
        command=controller.show_followup_screen,
    )
    death_btn = ttk.Button(
        header_frame,
        text="Death",
        command=controller.show_death_screen,
    )

    new_dx_btn.pack(side="left", padx=2)
    followup_btn.pack(side="left", padx=2)
    death_btn.pack(side="left", padx=2)

    return header_frame
