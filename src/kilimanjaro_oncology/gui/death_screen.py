import csv
import datetime
import os
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


class DeathScreen(
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
        # use the controller/service layer
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
            event="Death",
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
        self.date_label_text = None  # no date row on the death screen
        self.create_patient_info()
        self.create_cancer_details()
        self.death_date_cause()
        # self.create_care_plan()
        self.create_notes()
        self.create_footer()

    def update_event_date(self, *args):
        with suppress(ValueError):
            self.record.event_date = datetime.datetime.strptime(
                self.date_var.get(), "%Y-%m-%d"
            )

    def death_date_cause(self):
        frm = ttk.LabelFrame(self.scrollable_frame, padding=5)
        frm.pack(fill="x", padx=5, pady=2, anchor="w")

        ttk.Label(frm, text="Date of Death").grid(
            row=0, column=0, sticky="w", padx=5, pady=2
        )
        self.death_date_var = tk.StringVar(
            value=datetime.date.today().strftime("%Y-%m-%d")
        )
        self.death_date_entry = ttk.Entry(frm, textvariable=self.death_date_var)
        self.death_date_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.death_date_var.trace_add(
            "write", lambda *a: self._update_death_date()
        )

        # ttk.Label(frm, text="Cause of Death").grid(
        #     row=1, column=0, sticky="w", padx=5, pady=2
        # )
        # self.cause_of_death_var = tk.StringVar()
        # self.cause_of_death_entry =
        #           ttk.Entry(frm, textvariable=self.cause_of_death_var)
        # self.cause_of_death_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        # self.cause_of_death_var.trace_add(
        #     "write",
        #     lambda *a: setattr(
        #         self.record, "death_cause", self.cause_of_death_var.get()
        #     ),
        # )
        # --- load all causes from the CSV ---
        path = os.path.join(
            os.path.dirname(__file__), "..", "csv_files", "Cause_of_Death.CSV"
        )
        causes = []
        with open(path, newline="", encoding="latin-1") as f:
            for row in csv.reader(f):
                if row and row[0].strip():
                    causes.append(row[0].strip())

        ttk.Label(frm, text="Cause of Death").grid(
            row=1, column=0, sticky="w", padx=5, pady=2
        )
        self.cause_of_death_var = tk.StringVar()
        self.cause_of_death_combo = ttk.Combobox(
            frm,
            values=causes,
            textvariable=self.cause_of_death_var,
            state="readonly",  # optional: force selection from list
            width=30,
        )
        self.cause_of_death_combo.grid(
            row=1, column=1, sticky="ew", padx=5, pady=2
        )
        self.cause_of_death_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: setattr(
                self.record, "death_cause", self.cause_of_death_var.get()
            ),
        )

        frm.columnconfigure(0, weight=0)
        frm.columnconfigure(1, weight=1)

    def _update_death_date(self):
        try:
            self.record.death_date = datetime.datetime.strptime(
                self.death_date_var.get(), "%Y-%m-%d"
            )
        except ValueError:
            self.record.death_date = None

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
        if not self.death_date_var.get().strip():
            messagebox.showerror("Error", "Date of death is required.")
            return
        if not self.cause_of_death_var.get().strip():
            messagebox.showerror("Error", "Cause of death is required.")
            return

        # build a full‐prefix display ID
        full_id = f"{self._prefix}{self.record.patient_id}"
        out = (
            f"PatientID: {full_id}\n"
            f"Event: {self.record.event}\n"
            f"Event_Date: {self.record.event_date.strftime('%Y-%m-%d')}\n"
            f"Diagnosis: {self.record.diagnosis}\n"
            f"Histo: {self.record.histo}\n"
            f"Grade: {self.record.grade}\n"
            f"Factors: {self.record.factors}\n"
            f"Stage: {self.record.stage}\n"
            f"Death_Date: {self.death_date_var.get()}\n"
            f"Death_Cause: {self.cause_of_death_var.get()}\n"
            f"Note: {self.record.note}"
        )
        self.clipboard_clear()
        self.clipboard_append(out)
        try:
            # db = DatabaseService()
            rid = self.record_ctrl.save_record(self.record.to_dict())
            messagebox.showinfo(
                "Success", f"Record saved successfully (ID: {rid})"
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))
