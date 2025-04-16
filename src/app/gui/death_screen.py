# death_screen.py
import csv
import datetime
import os
import tkinter as tk
from tkinter import messagebox, ttk

# from app.classes.oncology_data import OncologyData
from app.classes.oncology_patient_data import OncologyPatientData
from app.database.database_service import DatabaseService
from app.gui.common_widgets import AutoCompleteCombobox, create_common_header


class DeathScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Initialize a new OncologyData instance with defaults for a Death event.
        self.record = OncologyPatientData(
            record_creation_datetime=datetime.datetime.now(),
            patient_id="",
            event="Death",
            event_date=datetime.datetime.now(),  # Date of Diagnosis (baseline)
            diagnosis="",
            histo="",
            grade="",
            factors="",
            stage="",
            careplan="",
            note="",
            death_date=None,  # Explicitly setting death_date as None for Death events
            death_cause="",  # And death_cause as empty string
        )

        # Create canvas and scrollbar for a scrollable frame.
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

        # Use the common header component
        create_common_header(self.scrollable_frame, controller)
        # Build the rest of the GUI sections.
        self.create_patient_info()
        self.create_cancer_details()
        self.death_date_cause()
        self.create_notes()
        self.create_footer()

    def create_patient_info(self):
        """Create patient identification section.
        When a Patient ID is selected, populate Diagnosis, Histo, Grade, and Factors.
        """
        info_frame = ttk.LabelFrame(self.scrollable_frame, padding=5)
        info_frame.pack(fill="x", padx=5, pady=2)

        # Patient ID with live search.
        ttk.Label(info_frame, text="Patient ID").grid(row=0, column=0, sticky="w")
        self.patient_id_var = tk.StringVar()
        self.patient_id_combo = ttk.Combobox(
            info_frame, textvariable=self.patient_id_var
        )
        self.patient_id_combo.grid(row=0, column=1, sticky="ew", padx=5)

        def on_patient_id_keyrelease(event):
            typed = event.widget.get()
            from app.database.database_service import DatabaseService

            db_service = DatabaseService()
            with db_service.get_connection() as conn:
                cursor = conn.cursor()
                query = (
                    "SELECT DISTINCT PatientID FROM oncology_data "
                    "WHERE PatientID LIKE ?"
                )
                cursor.execute(query, (typed + "%",))

                results = [row[0] for row in cursor.fetchall()]
            event.widget["values"] = results if results else []
            if results:
                event.widget.event_generate("<Down>")

        self.patient_id_combo.bind("<KeyRelease>", on_patient_id_keyrelease)

        def on_patient_id_selected(event):
            selected_patient_id = self.patient_id_var.get()
            from app.database.database_service import DatabaseService

            db_service = DatabaseService()
            records = db_service.get_patient_records(selected_patient_id)
            if not records:
                return
            # Use the first record for simplicity.
            record_data = records[0]
            diagnosis_code = record_data.get("Diagnosis", "")
            if diagnosis_code in self.diagnosis_codes:
                index = self.diagnosis_codes.index(diagnosis_code)
                diagnosis_display_value = self.diagnosis_display[index]
            else:
                diagnosis_display_value = ""
            self.diagnosis_combo.set(diagnosis_display_value)
            self.record.diagnosis = diagnosis_code

            # Populate Histo, Grade, and Factors.
            self.histo_combo.set(record_data.get("Histo", ""))
            self.record.histo = record_data.get("Histo", "")
            self.grade_combo.set(record_data.get("Grade", ""))
            self.record.grade = record_data.get("Grade", "")
            self.factors_entry.delete(0, tk.END)
            self.factors_entry.insert(0, record_data.get("Factors", ""))
            self.record.factors = record_data.get("Factors", "")
            # Update patient_id with diagnosis code.
            self.record.patient_id = f"{selected_patient_id}.{diagnosis_code}"

        self.patient_id_combo.bind("<<ComboboxSelected>>", on_patient_id_selected)

        # Date of Diagnosis field.
        ttk.Label(info_frame, text="Date of Diagnosis").grid(
            row=1, column=0, sticky="w"
        )
        self.date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.date_entry = ttk.Entry(info_frame, textvariable=self.date_var)
        self.date_entry.grid(row=1, column=1, sticky="ew", padx=5)
        self.date_var.trace_add("write", lambda *args: self._update_date_field())

        # Diagnosis combobox from CSV.
        ttk.Label(info_frame, text="Diagnosis").grid(row=2, column=0, sticky="w")
        csv_path = os.path.join(
            os.path.dirname(__file__), "..", "csv_files", "Diagnosis.ICD10.csv"
        )
        self.diagnosis_codes = []
        self.diagnosis_display = []
        with open(csv_path, newline="", encoding="latin-1") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:
                    self.diagnosis_codes.append(row[0].strip())
                    self.diagnosis_display.append(" ".join(row).strip())
        self.diagnosis_var = tk.StringVar()
        self.diagnosis_combo = AutoCompleteCombobox(
            info_frame, values=self.diagnosis_display, textvariable=self.diagnosis_var
        )
        self.diagnosis_combo.grid(row=2, column=1, sticky="ew", padx=5)

        info_frame.grid_columnconfigure(1, weight=1)

    def _update_date_field(self):
        try:
            self.record.event_date = datetime.datetime.strptime(
                self.date_var.get(), "%Y-%m-%d"
            )
        except ValueError:
            pass

    def create_cancer_details(self):
        details_frame = ttk.LabelFrame(self.scrollable_frame, padding=5)
        details_frame.pack(fill="x", padx=5, pady=2)

        # Histo field.
        ttk.Label(details_frame, text="Histo").grid(row=0, column=0, sticky="w")
        csv_path = os.path.join(
            os.path.dirname(__file__), "..", "csv_files", "Histopathology.CSV"
        )
        self.histo_options = []
        with open(csv_path, newline="", encoding="latin-1") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:
                    self.histo_options.append(" ".join(row).strip())
        self.histo_var = tk.StringVar()
        self.histo_combo = ttk.Combobox(
            details_frame, values=self.histo_options, textvariable=self.histo_var
        )
        self.histo_combo.grid(row=0, column=1, sticky="ew", padx=5)
        self.histo_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: setattr(self.record, "histo", self.histo_var.get()),
        )

        def on_histo_keyrelease(event):
            typed = self.histo_combo.get()
            if typed == "":
                self.histo_combo["values"] = self.histo_options
            else:
                filtered = [
                    option
                    for option in self.histo_options
                    if typed.lower() in option.lower()
                ]
                self.histo_combo["values"] = filtered
            self.histo_combo.event_generate("<Down>")

        self.histo_combo.bind("<KeyRelease>", on_histo_keyrelease)

        # Grade field.
        ttk.Label(details_frame, text="Grade").grid(row=1, column=0, sticky="w")
        self.grade_var = tk.StringVar()
        self.grade_combo = ttk.Combobox(
            details_frame, values=[1, 2, 3, 4, 9], textvariable=self.grade_var
        )
        self.grade_combo.grid(row=1, column=1, sticky="ew", padx=5)
        self.grade_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: setattr(self.record, "grade", self.grade_var.get()),
        )

        # Factors field.
        ttk.Label(details_frame, text="Factors").grid(row=2, column=0, sticky="w")
        self.factors_var = tk.StringVar(
            value=(
                "ER|PR|HER2|LN/|BRCA1|BRCA2|GS+|PSA|EPE|cores/|"
                "p16|EBV|ENE|PNI|PDL1%|EGFR|ALK|ROS1|BRAF|KRAS|R-mm"
            )
        )
        self.factors_entry = ttk.Entry(details_frame, textvariable=self.factors_var)
        self.factors_entry.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5)
        self.factors_var.trace_add(
            "write",
            lambda *args: setattr(self.record, "factors", self.factors_var.get()),
        )

        # Stage fields (T, N, and M).
        stage_frame = ttk.Frame(details_frame)
        stage_frame.grid(row=3, column=1, columnspan=3, sticky="w")
        ttk.Label(stage_frame, text="Stage").pack(side="left")
        ttk.Entry(stage_frame, width=8).pack(side="left", padx=5)
        ttk.Label(stage_frame, text="T").pack(side="left", padx=5)
        self.t_stage_combo = ttk.Combobox(
            stage_frame, values=["T0", "T1", "T2", "T3", "T4", "Tx"], width=4
        )
        self.t_stage_combo.pack(side="left", padx=5)
        self.t_stage_combo.bind("<<ComboboxSelected>>", lambda e: self.update_stage())
        ttk.Label(stage_frame, text="N").pack(side="left", padx=5)
        self.n_stage_combo = ttk.Combobox(
            stage_frame, values=["N0", "N1", "N2", "N3", "Nx"], width=4
        )
        self.n_stage_combo.pack(side="left", padx=5)
        self.n_stage_combo.bind("<<ComboboxSelected>>", lambda e: self.update_stage())
        ttk.Label(stage_frame, text="M").pack(side="left", padx=5)
        m_values = [
            "M0",
            "M1",
            "M1-adrenal",
            "M1-bladder",
            "M1-bone",
            "M1-cerebellum",
            "M1-cerebrum",
            "M1-eye",
            "M1-fat",
            "M1-headandneck",
            "M1-heart",
            "M1-kidneys",
            "M1-liver",
            "M1-lung",
            "M1-lymphnode",
            "M1-muscle",
            "M1-nasalcavity",
            "M1-oesophagus",
            "M1-ovary",
            "M1-pancreas",
            "M1-parathyroid",
            "M1-peritoneum",
            "M1-pleural",
            "M1-retroperitoneum",
            "M1-salivaryglang",
            "M1-sinuses",
            "M1-skin",
            "M1-spinalcanal",
            "M1-spinalcord",
            "M1-spleen",
            "M1-stomach",
            "M1-subcutaneous",
            "M1-thyroid",
            "M1-vagina",
        ]
        m_width = max(len(s) for s in m_values)
        self.m_stage_var = tk.StringVar()
        self.m_stage_combo = ttk.Combobox(
            stage_frame, values=m_values, width=m_width, textvariable=self.m_stage_var
        )
        self.m_stage_combo.pack(side="left", padx=5)
        self.m_stage_combo.bind("<<ComboboxSelected>>", lambda e: self.update_stage())

        details_frame.grid_columnconfigure(1, weight=1)

    def update_stage(self, *args):
        stage = " ".join(
            [
                self.t_stage_combo.get(),
                self.n_stage_combo.get(),
                self.m_stage_combo.get(),
            ]
        ).strip()
        self.record.stage = stage

    def death_date_cause(self):
        """Create inputs specific for Death: Date of Death and Cause of Death."""
        death_frame = ttk.LabelFrame(self.scrollable_frame, padding=5)
        death_frame.pack(fill="x", padx=5, pady=2, anchor="w")

        # Date of Death.
        ttk.Label(death_frame, text="Date of Death").grid(
            row=0, column=0, sticky="w", padx=5, pady=2
        )
        self.death_date_var = tk.StringVar(
            value=datetime.date.today().strftime("%Y-%m-%d")
        )
        self.death_date_entry = ttk.Entry(death_frame, textvariable=self.death_date_var)
        self.death_date_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.death_date_var.trace_add("write", lambda *args: self._update_death_date())

        # Cause of Death.
        ttk.Label(death_frame, text="Cause of Death").grid(
            row=1, column=0, sticky="w", padx=5, pady=2
        )
        self.cause_of_death_var = tk.StringVar()
        self.cause_of_death_entry = ttk.Entry(
            death_frame, textvariable=self.cause_of_death_var
        )
        self.cause_of_death_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.cause_of_death_var.trace_add(
            "write",
            lambda *args: setattr(
                self.record, "death_cause", self.cause_of_death_var.get()
            ),
        )

        death_frame.columnconfigure(0, weight=0)
        death_frame.columnconfigure(1, weight=1)

    def _update_death_date(self):
        try:
            self.record.death_date = datetime.datetime.strptime(
                self.death_date_var.get(), "%Y-%m-%d"
            )
        except ValueError:
            self.record.death_date = None

    def create_notes(self):
        notes_frame = ttk.LabelFrame(self.scrollable_frame, padding=5)
        notes_frame.pack(fill="both", expand=True, padx=5, pady=2)
        ttk.Label(notes_frame, text="Notes").pack(anchor="w")
        self.notes_text = tk.Text(notes_frame, height=4)
        self.notes_text.pack(fill="both", expand=True, pady=5)
        self.notes_text.bind(
            "<FocusOut>",
            lambda e: setattr(
                self.record, "note", self.notes_text.get("1.0", "end").strip()
            ),
        )

    def create_footer(self):
        footer_frame = ttk.Frame(self.scrollable_frame)
        footer_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(footer_frame, text="COPY", command=self.copy_to_clipboard).pack(
            side="right"
        )

    def copy_to_clipboard(self):
        output = (
            f"PatientID: {self.record.patient_id}\n"
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
        self.clipboard_append(output)

        # Save the record directly by passing the dataclass instance.
        try:
            db_service = DatabaseService()  # Singleton instance.
            # Explicitly convert the record to a dict for persistence.
            record_data = self.record.to_dict()
            record_id = db_service.save_diagnosis_record(record_data)
            messagebox.showinfo(
                "Success", f"Record saved successfully (ID: {record_id})"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save record: {str(e)}")
