# new_diagnosis_screen.py
import csv
import datetime
import os
import tkinter as tk
from tkinter import messagebox, ttk

# from app.classes.oncology_data import OncologyData
from app.classes.oncology_patient_data import OncologyPatientData
from app.database.database_service import DatabaseService
from app.gui.common_widgets import AutoCompleteCombobox, create_common_header


class NewDiagnosisScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Initialize an OncologyData instance with default values.
        # This record instance is updated live as fields are filled.
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
            death_date=None,  # Optional; leave blank for a diagnosis event.
            death_cause="",
        )

        # self.record = OncologyData(
        #     record_creation_datetime=datetime.datetime.now(),
        #     patient_id="",
        #     event="Diagnosis",
        #     event_date=datetime.datetime.now(),  # Updated from user input later.
        #     diagnosis="",
        #     histo="",
        #     grade="",
        #     factors="",
        #     stage="",
        #     careplan="",
        #     note="",
        # )

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
        self.create_care_plan()
        self.create_notes()
        self.create_footer()

    def create_patient_info(self):
        info_frame = ttk.LabelFrame(self.scrollable_frame, padding=5)
        info_frame.pack(fill="x", padx=5, pady=2)

        # Patient ID field using StringVar binding.
        ttk.Label(info_frame, text="Patient ID").grid(row=0, column=0, sticky="w")
        self.patient_id_var = tk.StringVar()
        self.patient_id_entry = ttk.Entry(
            info_frame, textvariable=self.patient_id_var, width=40
        )
        self.patient_id_entry.grid(row=0, column=1, sticky="ew", padx=5)
        # Update the dataclass whenever the Patient ID field changes.
        self.patient_id_var.trace_add("write", self.update_patient_id)

        # Date of Diagnosis field.
        ttk.Label(info_frame, text="Date of Diagnosis").grid(
            row=1, column=0, sticky="w"
        )
        self.date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.date_entry = ttk.Entry(info_frame, textvariable=self.date_var, width=40)
        self.date_entry.grid(row=1, column=1, sticky="ew", padx=5)
        self.date_var.trace_add("write", self.update_event_date)

        # Diagnosis field using a combobox with auto-complete.
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
        # self.diagnosis_combo = ttk.Combobox(
        #     info_frame, values=self.diagnosis_display, textvariable=self.diagnosis_var
        # )
        self.diagnosis_combo = AutoCompleteCombobox(
            info_frame,
            values=self.diagnosis_display,
            textvariable=self.diagnosis_var,
            width=40,
        )
        self.diagnosis_combo.grid(row=2, column=1, sticky="ew", padx=5)
        self.diagnosis_combo.grid(row=2, column=1, sticky="ew", padx=5)
        self.diagnosis_combo.bind("<<ComboboxSelected>>", self.update_diagnosis)

        info_frame.grid_columnconfigure(1, weight=1)

    # Update functions to keep the dataclass in sync with the GUI.
    def update_patient_id(self, *args):
        self.record.patient_id = self.patient_id_var.get()

    def update_event_date(self, *args):
        try:
            self.record.event_date = datetime.datetime.strptime(
                self.date_var.get(), "%Y-%m-%d"
            )
        except ValueError:
            pass  # Optionally add error handling for invalid dates.

    def update_diagnosis(self, event):
        selected_value = self.diagnosis_var.get()
        try:
            index = self.diagnosis_display.index(selected_value)
            self.record.diagnosis = self.diagnosis_codes[index]
            # Optionally update patient ID to include the diagnosis code.
            self.record.patient_id = (
                f"{self.patient_id_var.get()}.{self.record.diagnosis}"
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
        self.histo_combo.bind("<<ComboboxSelected>>", self.update_histo)

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
        self.grade_combo.bind("<<ComboboxSelected>>", self.update_grade)

        # Factors field.
        ttk.Label(details_frame, text="Factors").grid(row=2, column=0, sticky="w")
        self.factors_var = tk.StringVar(
            value=(
                "ER|PR|HER2|LN/|BRCA1|BRCA2|GS+|PSA|EPE|cores/|p16|"
                "EBV|ENE|PNI|PDL1%|EGFR|ALK|ROS1|BRAF|KRAS|R-mm"
            )
        )

        self.factors_entry = ttk.Entry(details_frame, textvariable=self.factors_var)
        self.factors_entry.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5)
        self.factors_var.trace_add("write", self.update_factors)

        # Stage section: combine T, N, and M values.
        stage_frame = ttk.Frame(details_frame)
        stage_frame.grid(row=3, column=1, columnspan=3, sticky="w")
        ttk.Label(stage_frame, text="Stage").pack(side="left")
        self.t_stage_var = tk.StringVar()
        ttk.Entry(stage_frame, width=8, textvariable=self.t_stage_var).pack(
            side="left", padx=5
        )
        self.t_stage_var.trace_add("write", self.update_stage)
        ttk.Label(stage_frame, text="T").pack(side="left", padx=5)
        self.t_stage_combo = ttk.Combobox(
            stage_frame, values=["T0", "T1", "T2", "T3", "T4", "Tx"], width=4
        )
        self.t_stage_combo.pack(side="left", padx=5)
        self.t_stage_combo.bind("<<ComboboxSelected>>", self.update_stage)
        ttk.Label(stage_frame, text="N").pack(side="left", padx=5)
        self.n_stage_combo = ttk.Combobox(
            stage_frame, values=["N0", "N1", "N2", "N3", "Nx"], width=4
        )
        self.n_stage_combo.pack(side="left", padx=5)
        self.n_stage_combo.bind("<<ComboboxSelected>>", self.update_stage)
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
        self.m_stage_combo.bind("<<ComboboxSelected>>", self.update_stage)

        details_frame.grid_columnconfigure(1, weight=1)

    # Update functions for cancer details.
    def update_histo(self, event):
        self.record.histo = self.histo_var.get()

    def update_grade(self, event):
        self.record.grade = self.grade_var.get()

    def update_factors(self, *args):
        self.record.factors = self.factors_var.get()

    def update_stage(self, *args):
        # Combine the values from the T, N, and M fields into one string.
        stage = " ".join(
            [
                self.t_stage_combo.get(),
                self.n_stage_combo.get(),
                self.m_stage_combo.get(),
            ]
        ).strip()
        self.record.stage = stage

    def create_care_plan(self):
        care_frame = ttk.LabelFrame(self.scrollable_frame, padding=5)
        care_frame.pack(fill="x", padx=5, pady=2, anchor="e")
        ttk.Label(
            care_frame, text="Care Planned First", font=("Arial", 10, "bold")
        ).pack(anchor="center", pady=(0, 5))

        treatments = [
            ["Observe"],
            ["Surgery", "Radiation"],
            ["Chemo", "Brachy"],
            ["Immuno", "Hormones"],
            ["Small mol."],
        ]
        grid_frame = ttk.Frame(care_frame)
        grid_frame.pack(anchor="w")
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        self.care_plan_buttons = []
        for row_index, row in enumerate(treatments):
            for col in range(2):
                if col < len(row):
                    treatment = row[col]
                    btn = tk.Button(grid_frame, text=treatment)
                    btn.selected = False
                    btn.default_bg = btn.cget("bg")
                    btn.config(command=lambda b=btn: self.toggle_button(b))
                    btn.grid(row=row_index, column=col, padx=5, pady=2, sticky="ew")
                    self.care_plan_buttons.append(btn)
                else:
                    ttk.Label(grid_frame, text="").grid(
                        row=row_index, column=col, padx=5, pady=2
                    )

    def toggle_button(self, button):
        if button.selected:
            button.selected = False
            button.config(bg=button.default_bg)
        else:
            button.selected = True
            button.config(bg="green")
        # Update the careplan attribute based on the selected buttons.
        selected_treatments = ", ".join(
            btn.cget("text") for btn in self.care_plan_buttons if btn.selected
        )
        self.record.careplan = selected_treatments

    def create_notes(self):
        notes_frame = ttk.LabelFrame(self.scrollable_frame, padding=5)
        notes_frame.pack(fill="both", expand=True, padx=5, pady=2)

        ttk.Label(notes_frame, text="Notes").pack(anchor="w")
        self.notes_text = tk.Text(notes_frame, height=4)
        self.notes_text.pack(fill="both", expand=True, pady=5)
        # Update the note field when the text widget loses focus.
        self.notes_text.bind("<FocusOut>", self.update_notes)

    def update_notes(self, event):
        self.record.note = self.notes_text.get("1.0", "end").strip()

    def create_footer(self):
        footer_frame = ttk.Frame(self.scrollable_frame)
        footer_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(footer_frame, text="COPY", command=self.copy_to_clipboard).pack(
            side="right"
        )

    def copy_to_clipboard(self):
        # Format the output string using the current state of self.record.
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
