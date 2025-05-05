import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from kilimanjaro_oncology.classes.oncology_patient_data import OncologyPatientData
from kilimanjaro_oncology.gui.common_widgets import (
    AutoCompleteCombobox,
    create_common_header,
    PatientInfoMixin,
    CancerDetailsMixin,
    CarePlanMixin,
    NotesMixin,
)


class FollowUpScreen(
    PatientInfoMixin,
    CancerDetailsMixin,
    CarePlanMixin,
    NotesMixin,
    tk.Frame,
):
    def __init__(self, parent, controller, record_ctrl):
        super().__init__(parent)
        self.controller = controller

        # use passed‐in service (or default singleton)
        # self.db_service = db_service
        # use the new controller/service layer
        self.record_ctrl = record_ctrl

        self.record = OncologyPatientData(
            record_creation_datetime=datetime.datetime.now(),
            patient_id="",
            event="Follow Up",
            event_date=datetime.datetime.now(),
            diagnosis="",
            histo="",
            grade="",
            factors="",
            stage="",
            careplan="",
            note="",
            death_date=None,
            death_cause="",
        )

        # Scrollable area
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Build UI
        create_common_header(self.scrollable_frame, controller)
        self.date_label_text = "Date of Follow‑up"
        self.create_patient_info()
        self.create_cancer_details()
        self.create_care_plan()
        self.create_notes()
        self.create_footer()

    def update_event_date(self, *args):
        try:
            self.record.event_date = datetime.datetime.strptime(
                self.date_var.get(), "%Y-%m-%d"
            )
        except ValueError:
            pass

    def create_footer(self):
        footer = ttk.Frame(self.scrollable_frame)
        footer.pack(fill="x", padx=5, pady=5)
        ttk.Button(footer, text="COPY", command=self.copy_to_clipboard).pack(
            side="right"
        )

    def copy_to_clipboard(self):
        out = (
            f"Patient_ID: {self.record.patient_id}\n"
            f"Event: {self.record.event}\n"
            f"Event_Date: {self.record.event_date.strftime('%Y-%m-%d')}\n"
            f"Diagnosis: {self.record.diagnosis}\n"
            f"Histo: {self.record.histo}\n"
            f"Grade: {self.record.grade}\n"
            f"Factors: {self.record.factors}\n"
            f"Stage: {self.record.stage}\n"
            f"Careplan: {self.record.careplan}\n"
            f"Note: {self.record.note}"
        )
        self.clipboard_clear()
        self.clipboard_append(out)
        try:
            rid = self.record_ctrl.save_record(self.record.to_dict())
            messagebox.showinfo("Success", f"Record saved successfully (ID: {rid})")
        except Exception as e:
            messagebox.showerror("Error", str(e))
