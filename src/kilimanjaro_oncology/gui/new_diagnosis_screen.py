import datetime
import re
import tkinter as tk
from contextlib import suppress
from tkinter import messagebox, ttk

from kilimanjaro_oncology.classes.oncology_patient_data import (
    OncologyPatientData,
)
from kilimanjaro_oncology.gui.common_widgets import (
    CancerDetailsMixin,
    CarePlanMixin,
    DiagnosisCombobox,
    NotesMixin,
    create_common_header,
)


class NewDiagnosisScreen(
    CancerDetailsMixin,
    CarePlanMixin,
    NotesMixin,
    tk.Frame,
):
    FACTOR_BUTTON_MAP: dict[str, str] = {
        "ER+": "ER+",
        "PR+": "PR+",
        "HER2+": "HER2+",
        "ER-": "ER-",
        "PR-": "PR-",
        "HER2-": "HER2-",
        "BRCA1": "BRCA1+",
        "BRCA2": "BRCA2+",
        "ALK": "ALK+",
        "ROS": "ROS+",
        "p16+": "p16+",
        "p16-": "p16-",
        "ENE": "ENE+",
        "EGFR": "EGFR+",
        "BRAF": "BRAF+",
    }

    def __init__(self, parent, controller, record_ctrl):
        super().__init__(parent)
        self.controller = controller
        self.record_ctrl = record_ctrl

        settings = self.record_ctrl.fetch_settings(
            ["hospital_name", "department_name"]
        )
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
        self.create_patient_info()  # overridden below
        self.create_cancer_details()
        # self.create_care_plan()
        self.create_notes()
        self.create_footer()

    def create_patient_info(self):
        """Free-text entry for Patient ID, date, and diagnosis auto-combo."""
        info = ttk.LabelFrame(self.scrollable_frame, padding=5)
        info.pack(fill="x", padx=5, pady=2)

        # Patient ID Entry
        ttk.Label(info, text="Patient ID").grid(row=0, column=0, sticky="w")
        self.patient_id_var = tk.StringVar()
        # entry = ttk.Entry(info, textvariable=self.patient_id_var, width=40)
        # entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.patient_id_entry = ttk.Entry(
            info, textvariable=self.patient_id_var, width=40
        )
        self.patient_id_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.patient_id_var.trace_add("write", self.update_patient_id)

        # Date of Diagnosis
        ttk.Label(info, text="Date of Diagnosis").grid(
            row=1, column=0, sticky="w"
        )
        self.date_var = tk.StringVar(
            value=datetime.date.today().strftime("%Y-%m-%d")
        )
        date_entry = ttk.Entry(info, textvariable=self.date_var, width=40)
        date_entry.grid(row=1, column=1, sticky="ew", padx=5)
        self.date_var.trace_add("write", self.update_event_date)

        # Diagnosis Combobox w/ autocomplete
        # ttk.Label(info, text="Diagnosis").grid(row=2, column=0, sticky="w")
        # # Load codes/display from CSV
        # csv_path = __import__("os").path.join(
        #     __import__("os").path.dirname(__file__),
        #     "..",
        #     "csv_files",
        #     "Diagnosis.ICD10.csv",
        # )
        # self.diagnosis_codes, self.diagnosis_display = [], []
        # with open(csv_path, newline="", encoding="latin-1") as f:
        #     for row in __import__("csv").reader(f):
        #         if row:
        #             self.diagnosis_codes.append(row[0].strip())
        #             self.diagnosis_display.append(" ".join(row).strip())
        #
        # self.diagnosis_var = tk.StringVar()
        # combo = AutoCompleteCombobox(
        #     info,
        #     values=self.diagnosis_display,
        #     textvariable=self.diagnosis_var,
        #     width=40,
        # )
        # combo.grid(row=2, column=1, sticky="ew", padx=5)
        # combo.bind("<<ComboboxSelected>>", self.update_diagnosis)
        """
        Updated here
        """
        # Diagnosis Combobox w/ autocomplete
        ttk.Label(info, text="Diagnosis").grid(row=2, column=0, sticky="w")
        self.diagnosis_var = tk.StringVar()
        self.diagnosis_combo = DiagnosisCombobox(
            info,
            on_select_code=self._on_new_dx_chosen,
            textvariable=self.diagnosis_var,
            width=40,
        )
        self.diagnosis_combo.grid(row=2, column=1, sticky="ew", padx=5)

        info.grid_columnconfigure(1, weight=1)

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

    def create_cancer_details(self):
        details = ttk.LabelFrame(self.scrollable_frame, padding=5)
        details.pack(fill="x", padx=5, pady=2)

        # Histo
        ttk.Label(details, text="Histo").grid(row=0, column=0, sticky="w")
        self.histo_var = tk.StringVar()
        self.histo_combo = ttk.Entry(
            details, textvariable=self.histo_var, width=40
        )
        self.histo_combo.grid(row=0, column=1, sticky="ew", padx=5)
        self.histo_var.trace_add(
            "write", lambda *_a: setattr(self.record, "histo", self.histo_var.get())
        )

        # Grade
        ttk.Label(details, text="Grade").grid(row=1, column=0, sticky="w")
        self.grade_var = tk.StringVar()
        self.grade_combo = ttk.Combobox(
            details, values=[1, 2, 3, 4, 9], textvariable=self.grade_var
        )
        self.grade_combo.grid(row=1, column=1, sticky="ew", padx=5)
        self.grade_combo.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._on_grade_typed(),
        )
        self.grade_var.trace_add("write", lambda *_a: self._on_grade_typed())

        # Structured factor buttons
        marker_frame = ttk.LabelFrame(details, text="Markers", padding=5)
        marker_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        self._selected_markers: set[str] = set()
        self._marker_buttons: dict[str, tk.Button] = {}
        for idx, marker in enumerate(self.FACTOR_BUTTON_MAP):
            btn = tk.Button(
                marker_frame,
                text=marker,
                command=lambda m=marker: self.toggle_factor_button(m),
            )
            btn.grid(row=idx // 5, column=idx % 5, padx=3, pady=2, sticky="ew")
            self._marker_buttons[marker] = btn

        # Numeric/structured fields
        reg_digits = self.register(self._validate_digits)
        reg_decimal = self.register(self._validate_decimal)

        numeric = ttk.Frame(details)
        numeric.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)

        ttk.Label(numeric, text="GS").grid(row=0, column=0, sticky="w")
        self.gs_left_var = tk.StringVar()
        self.gs_right_var = tk.StringVar()
        ttk.Entry(
            numeric,
            width=4,
            textvariable=self.gs_left_var,
            validate="key",
            validatecommand=(reg_digits, "%P"),
        ).grid(row=0, column=1, padx=2)
        ttk.Label(numeric, text="+").grid(row=0, column=2)
        ttk.Entry(
            numeric,
            width=4,
            textvariable=self.gs_right_var,
            validate="key",
            validatecommand=(reg_digits, "%P"),
        ).grid(row=0, column=3, padx=2)

        ttk.Label(numeric, text="PSA").grid(row=0, column=4, sticky="w", padx=(10, 0))
        self.psa_var = tk.StringVar()
        ttk.Entry(
            numeric,
            width=8,
            textvariable=self.psa_var,
            validate="key",
            validatecommand=(reg_decimal, "%P"),
        ).grid(row=0, column=5, padx=2)

        ttk.Label(numeric, text="PDL1%").grid(
            row=0, column=6, sticky="w", padx=(10, 0)
        )
        self.pdl1_var = tk.StringVar()
        ttk.Entry(
            numeric,
            width=6,
            textvariable=self.pdl1_var,
            validate="key",
            validatecommand=(reg_digits, "%P"),
        ).grid(row=0, column=7, padx=2)

        ttk.Label(numeric, text="Cores").grid(
            row=1, column=0, sticky="w", pady=(6, 0)
        )
        self.cores_num_var = tk.StringVar()
        self.cores_den_var = tk.StringVar()
        ttk.Entry(
            numeric,
            width=4,
            textvariable=self.cores_num_var,
            validate="key",
            validatecommand=(reg_digits, "%P"),
        ).grid(row=1, column=1, padx=2, pady=(6, 0))
        ttk.Label(numeric, text="/").grid(row=1, column=2, pady=(6, 0))
        ttk.Entry(
            numeric,
            width=4,
            textvariable=self.cores_den_var,
            validate="key",
            validatecommand=(reg_digits, "%P"),
        ).grid(row=1, column=3, padx=2, pady=(6, 0))

        ttk.Label(numeric, text="Nodes").grid(
            row=1, column=4, sticky="w", padx=(10, 0), pady=(6, 0)
        )
        self.nodes_num_var = tk.StringVar()
        self.nodes_den_var = tk.StringVar()
        ttk.Entry(
            numeric,
            width=4,
            textvariable=self.nodes_num_var,
            validate="key",
            validatecommand=(reg_digits, "%P"),
        ).grid(row=1, column=5, padx=2, pady=(6, 0))
        ttk.Label(numeric, text="/").grid(row=1, column=6, pady=(6, 0))
        ttk.Entry(
            numeric,
            width=4,
            textvariable=self.nodes_den_var,
            validate="key",
            validatecommand=(reg_digits, "%P"),
        ).grid(row=1, column=7, padx=2, pady=(6, 0))

        # Single-select resection
        resection = ttk.LabelFrame(details, text="Resection", padding=5)
        resection.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)
        self.resection_var = tk.StringVar()
        self.resection_mm_var = tk.StringVar()
        for idx, val in enumerate(["Rx", "R0", "R1", "R2"]):
            ttk.Radiobutton(
                resection,
                text=val,
                value=val,
                variable=self.resection_var,
                command=self.update_factors,
            ).grid(row=0, column=idx, padx=4, pady=2, sticky="w")
        ttk.Label(resection, text="mm").grid(row=0, column=4, padx=(10, 2))
        ttk.Entry(
            resection,
            width=6,
            textvariable=self.resection_mm_var,
            validate="key",
            validatecommand=(reg_digits, "%P"),
        ).grid(row=0, column=5, padx=2)

        # Stage T/N/M
        frm = ttk.Frame(details)
        frm.grid(row=5, column=1, columnspan=2, sticky="w")
        ttk.Label(frm, text="Stage").pack(side="left")
        self.t_stage_combo = ttk.Combobox(
            frm, values=["T0", "T1", "T2", "T3", "T4", "Tx"], width=4
        )
        self.t_stage_combo.pack(side="left", padx=5)
        self.t_stage_combo.bind(
            "<<ComboboxSelected>>", lambda _e: self.update_stage()
        )
        self.n_stage_combo = ttk.Combobox(
            frm, values=["N0", "N1", "N2", "N3", "Nx"], width=4
        )
        self.n_stage_combo.pack(side="left", padx=5)
        self.n_stage_combo.bind(
            "<<ComboboxSelected>>", lambda _e: self.update_stage()
        )
        m_vals = ["M0", "M1", "M1-liver", "M1-lung", "M1-bone", "M1-cerebellum"]
        self.m_stage_combo = ttk.Combobox(
            frm, values=m_vals, width=max(len(s) for s in m_vals)
        )
        self.m_stage_combo.pack(side="left", padx=5)
        self.m_stage_combo.bind(
            "<<ComboboxSelected>>", lambda _e: self.update_stage()
        )

        # Keep factors updated from text inputs.
        for var in (
            self.gs_left_var,
            self.gs_right_var,
            self.psa_var,
            self.pdl1_var,
            self.cores_num_var,
            self.cores_den_var,
            self.nodes_num_var,
            self.nodes_den_var,
            self.resection_mm_var,
            self.resection_var,
        ):
            var.trace_add("write", lambda *_a: self.update_factors())

        details.grid_columnconfigure(1, weight=1)

    @staticmethod
    def _validate_digits(value: str) -> bool:
        return value == "" or value.isdigit()

    @staticmethod
    def _validate_decimal(value: str) -> bool:
        return value == "" or bool(re.fullmatch(r"\d+(\.\d+)?", value))

    def _on_grade_typed(self):
        val = self.grade_var.get()
        try:
            num = int(val)
        except ValueError:
            return
        if num in [1, 2, 3, 4, 9]:
            self.record.grade = num

    def toggle_factor_button(self, label: str):
        btn = self._marker_buttons[label]
        if label in self._selected_markers:
            self._selected_markers.remove(label)
            btn.config(bg=btn.cget("activebackground"))
        else:
            self._selected_markers.add(label)
            btn.config(bg="green")
        self.update_factors()

    def update_stage(self, *_args):
        parts = [
            self.t_stage_combo.get(),
            self.n_stage_combo.get(),
            self.m_stage_combo.get(),
        ]
        self.record.stage = " ".join(p for p in parts if p)

    def update_factors(self):
        tokens = [
            self.FACTOR_BUTTON_MAP[k]
            for k in self.FACTOR_BUTTON_MAP
            if k in self._selected_markers
        ]

        if self.gs_left_var.get() and self.gs_right_var.get():
            tokens.append(f"GS{self.gs_left_var.get()}+{self.gs_right_var.get()}")
        if self.psa_var.get():
            tokens.append(f"PSA{self.psa_var.get()}")
        if self.pdl1_var.get():
            tokens.append(f"PDL1%{self.pdl1_var.get()}")
        if self.cores_num_var.get() and self.cores_den_var.get():
            tokens.append(f"{self.cores_num_var.get()}/{self.cores_den_var.get()}")
        if self.nodes_num_var.get() and self.nodes_den_var.get():
            tokens.append(f"{self.nodes_num_var.get()}/{self.nodes_den_var.get()}")
        if self.resection_var.get() and self.resection_mm_var.get():
            tokens.append(f"{self.resection_var.get()}-{self.resection_mm_var.get()}mm")

        self.record.factors = ", ".join(tokens)

    def update_event_date(self, *args):
        with suppress(ValueError):
            self.record.event_date = datetime.datetime.strptime(
                self.date_var.get(), "%Y-%m-%d"
            )

    # def update_diagnosis(self, event):
    #     val = self.diagnosis_var.get()
    #     if val in self.diagnosis_display:
    #         idx = self.diagnosis_display.index(val)
    #         self.record.diagnosis = self.diagnosis_codes[idx]
    #         # append the diagnosis code to whatever ID already built
    #         self.record.patient_id =
    #           f"{self.record.patient_id}.{self.record.diagnosis}"
    def _on_new_dx_chosen(self, code: str):
        """
        Called when the user selects a diagnosis from the dropdown.
        Stores the raw ICD code and appends it to patient_id.
        """
        self.record.diagnosis = code
        # rebuild from raw entry to avoid double-appending
        raw = self.patient_id_var.get().lstrip(".")
        if self._hospital and self._department:
            base = f"{self._hospital}.{self._department}.{raw}"
        else:
            base = raw
        self.record.patient_id = f"{base}.{code}"

    def create_footer(self):
        footer = ttk.Frame(self.scrollable_frame)
        footer.pack(fill="x", padx=5, pady=5)
        ttk.Button(footer, text="COPY", command=self.copy_to_clipboard).pack(
            side="right"
        )

    def copy_to_clipboard(self):
        if not self.patient_id_var.get().strip():
            messagebox.showerror("Error", "Patient ID is required.")
            return
        if not self.record.diagnosis:
            messagebox.showerror("Error", "Diagnosis is required.")
            return
        try:
            datetime.datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date of diagnosis.")
            return

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

        # Andrew only wants the Patient ID and Diagnosis Key used in
        # the database
        # Prepare a dict for DB with only raw_id + diagnosis
        data = self.record.to_dict()
        # split the full ID on '.', keep last two segments e.g. ["0009009","C20"]
        # strip off the known "Hospital.Department." prefix,
        # leaving exactly "<rawID>.<diagnosisCode...>"
        prefix = f"{self._hospital}.{self._department}."
        full = self.record.patient_id
        data["patient_id"] = (
            full[len(prefix) :] if full.startswith(prefix) else full
        )
        try:
            # rid = self.record_ctrl.save_record(self.record.to_dict())
            rid = self.record_ctrl.save_record(data)
            messagebox.showinfo(
                "Success", f"Record saved successfully (ID: {rid})"
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))
