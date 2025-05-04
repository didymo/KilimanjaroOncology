import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from kilimanjaro_oncology.classes.oncology_patient_data import OncologyPatientData
from kilimanjaro_oncology.gui.common_widgets import (
    AutoCompleteCombobox,
    create_common_header,
    CancerDetailsMixin,
    CarePlanMixin,
    NotesMixin,
)


class NewDiagnosisScreen(
    CancerDetailsMixin,
    CarePlanMixin,
    NotesMixin,
    tk.Frame,
):
    def __init__(self, parent, controller, db_service):
        super().__init__(parent)
        self.controller = controller

        # use passed‐in service (or default singleton)
        self.db_service = db_service

        with self.db_service.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT key,value FROM settings WHERE key IN ('hospital_name','department_name')")
            settings = dict(cur.fetchall())
        self._hospital = settings.get("hospital_name", "")
        self._department = settings.get("department_name", "")

        # Initialize the data model
        self.record = OncologyPatientData(
            record_creation_datetime=datetime.datetime.now(),
            patient_id="",
            event="Diagnosis",
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

        # Scrollable frame setup
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
        self.create_patient_info()      # overridden below
        self.create_cancer_details()
        self.create_care_plan()
        self.create_notes()
        self.create_footer()

    def create_patient_info(self):
        """Free-text entry for Patient ID, date, and diagnosis auto-combo."""
        info = ttk.LabelFrame(self.scrollable_frame, padding=5)
        info.pack(fill="x", padx=5, pady=2)

        # Patient ID Entry
        ttk.Label(info, text="Patient ID").grid(row=0, column=0, sticky="w")
        self.patient_id_var = tk.StringVar()
        entry = ttk.Entry(info, textvariable=self.patient_id_var, width=40)
        entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.patient_id_var.trace_add("write", self.update_patient_id)

        # Date of Diagnosis
        ttk.Label(info, text="Date of Diagnosis").grid(row=1, column=0, sticky="w")
        self.date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(info, textvariable=self.date_var, width=40)
        date_entry.grid(row=1, column=1, sticky="ew", padx=5)
        self.date_var.trace_add("write", self.update_event_date)

        # Diagnosis Combobox w/ autocomplete
        ttk.Label(info, text="Diagnosis").grid(row=2, column=0, sticky="w")
        # Load codes/display from CSV
        csv_path = (
            __import__("os")
            .path.join(
                __import__("os").path.dirname(__file__),
                "..",
                "csv_files",
                "Diagnosis.ICD10.csv",
            )
        )
        self.diagnosis_codes, self.diagnosis_display = [], []
        with open(csv_path, newline="", encoding="latin-1") as f:
            for row in __import__("csv").reader(f):
                if row:
                    self.diagnosis_codes.append(row[0].strip())
                    self.diagnosis_display.append(" ".join(row).strip())

        self.diagnosis_var = tk.StringVar()
        combo = AutoCompleteCombobox(
            info,
            values=self.diagnosis_display,
            textvariable=self.diagnosis_var,
            width=40,
        )
        combo.grid(row=2, column=1, sticky="ew", padx=5)
        combo.bind("<<ComboboxSelected>>", self.update_diagnosis)

        info.grid_columnconfigure(1, weight=1)

    # def update_patient_id(self, *args):
    #     self.record.patient_id = self.patient_id_var.get()

    def update_patient_id(self, *args):
        # raw user‐entered ID (e.g. "0001")
        raw = self.patient_id_var.get().lstrip(".")

        # build the full ID: "Hospital.Dept.raw"
        if self._hospital and self._department:
            full = f"{self._hospital}.{self._department}.{raw}"
        else:
            full = raw

        # store only in the record—not in the entry widget
        self.record.patient_id = full


    def update_event_date(self, *args):
        try:
            self.record.event_date = datetime.datetime.strptime(
                self.date_var.get(), "%Y-%m-%d"
            )
        except ValueError:
            pass

    def update_diagnosis(self, event):
        val = self.diagnosis_var.get()
        if val in self.diagnosis_display:
            idx = self.diagnosis_display.index(val)
            self.record.diagnosis = self.diagnosis_codes[idx]

    def create_footer(self):
        footer = ttk.Frame(self.scrollable_frame)
        footer.pack(fill="x", padx=5, pady=5)
        ttk.Button(footer, text="COPY", command=self.copy_to_clipboard).pack(side="right")

    def copy_to_clipboard(self):
        output = (
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
        self.clipboard_append(output)
        try:
            rid = self.db_service.save_diagnosis_record(self.record.to_dict())
            messagebox.showinfo("Success", f"Record saved successfully (ID: {rid})")
        except Exception as e:
            messagebox.showerror("Error", str(e))
