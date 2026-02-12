import datetime
import tkinter as tk
from contextlib import suppress
from tkinter import messagebox, ttk

from kilimanjaro_oncology.classes.oncology_patient_data import (
    OncologyPatientData,
)
from kilimanjaro_oncology.gui.common_widgets import (
    CancerDetailsMixin,
    CarePlanMixin,
    NotesMixin,
    PatientInfoMixin,
    create_common_header,
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

        # pull hospital/department so we can prepend later
        settings = self.record_ctrl.fetch_settings(
            ["hospital_name", "department_name"]
        )
        self._hospital = settings.get("hospital_name", "")
        self._department = settings.get("department_name", "")
        self._prefix = f"{self._hospital}.{self._department}."

        self.record = OncologyPatientData(
            record_creation_datetime=datetime.datetime.now(),
            patient_id="",
            event="Management",
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
        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )
        # self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        # keep a handle on the window, so we can resize it on-the-fly
        self._scrollwin = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        # whenever the canvas itself resizes, force the inner frame to match its width
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self._scrollwin, width=e.width),
        )
        # self.canvas.configure(yscrollcommand=scrollbar.set)
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
        with suppress(ValueError):
            self.record.event_date = datetime.datetime.strptime(
                self.date_var.get(), "%Y-%m-%d"
            )

    def create_footer(self):
        footer = ttk.Frame(self.scrollable_frame)
        footer.pack(fill="x", padx=5, pady=5)
        ttk.Button(footer, text="COPY", command=self.copy_to_clipboard).pack(
            side="right"
        )

    def copy_to_clipboard(self):
        if not self.record.patient_id.strip():
            messagebox.showerror("Error", "Patient ID is required.")
            return
        if not self.record.diagnosis:
            messagebox.showerror("Error", "Diagnosis is required.")
            return
        try:
            datetime.datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid follow-up date.")
            return

        # build a full‐prefix display ID
        full_id = f"{self._prefix}{self.record.patient_id}"
        out = (
            f"Patient_ID: {full_id}\n"
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
            messagebox.showinfo(
                "Success", f"Record saved successfully (ID: {rid})"
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))
