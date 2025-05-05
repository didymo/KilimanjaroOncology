# common_widgets.py
from tkinter import ttk
import tkinter as tk
import csv
import os
import datetime


class AutoCompleteCombobox(ttk.Combobox):
    """
    A ttk.Combobox with basic auto-complete functionality.
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._completion_list = list(kwargs.get("values", []))
        self.bind("<KeyRelease>", self._on_keyrelease)
        # wrap insert() so tests that do combo.insert(...) get an immediate filter
        _orig_insert = self.insert
        def _insert_and_filter(index, string):
            _orig_insert(index, string)
            class E:  # dummy event container
                widget = self
            self._on_keyrelease(E)
        self.insert = _insert_and_filter

    def set_completion_list(self, completion_list):
        self._completion_list = completion_list
        self["values"] = self._completion_list

    def _on_keyrelease(self, event):
        typed = self.get()
        if not typed:
            self["values"] = self._completion_list
        else:
            self["values"] = [i for i in self._completion_list if typed.lower() in i.lower()]
        self.event_generate("<Down>")


def create_common_header(parent, controller):
    header = ttk.Frame(parent)
    header.pack(fill="x", padx=5, pady=5)
    ttk.Button(header, text="New Dx", style="Active.TButton",
               command=controller.show_new_diagnosis_screen).pack(side="left", padx=2)
    ttk.Button(header, text="FollowUp",
               command=controller.show_followup_screen).pack(side="left", padx=2)
    ttk.Button(header, text="Death",
               command=controller.show_death_screen).pack(side="left", padx=2)
    return header


class PatientInfoMixin:
    """
    Mixin providing create_patient_info().
    """
    def create_patient_info(self):
        info = ttk.LabelFrame(self.scrollable_frame, padding=5)
        info.pack(fill="x", padx=5, pady=2)

        # Patient ID
        ttk.Label(info, text="Patient ID").grid(row=0, column=0, sticky="w")
        self.patient_id_var = tk.StringVar()
        self.patient_id_combo = ttk.Combobox(info, textvariable=self.patient_id_var)
        self.patient_id_combo.grid(row=0, column=1, sticky="ew", padx=5)

        def on_key(e):
            prefix = e.widget.get()
            vals = self.record_ctrl.fetch_patient_ids(prefix)
            e.widget["values"] = vals
            if vals:
                e.widget.event_generate("<Down>")

        def on_select(e):
            pid = self.patient_id_var.get()
            # from kilimanjaro_oncology.database.database_service import DatabaseService
            # db = DatabaseService()
            # recs = db.get_patient_records(pid)
            # if not recs:
            #     return
            # data = recs[0]
            # pull full patient record via controller
            data = self.record_ctrl.fetch_patient_data(pid)
            if not data:
                return

            # Diagnosis
            code = data.get("Diagnosis", "")
            if code in self.diagnosis_codes:
                idx = self.diagnosis_codes.index(code)
                self.diagnosis_combo.set(self.diagnosis_display[idx])
            else:
                self.diagnosis_combo.set("")
            self.record.diagnosis = code
            # Histo, Grade, Factors
            self.histo_combo.set(data.get("Histo", ""))
            self.record.histo = data.get("Histo", "")
            self.grade_combo.set(data.get("Grade", ""))
            self.record.grade = data.get("Grade", "")
            self.factors_entry.delete(0, tk.END)
            self.factors_entry.insert(0, data.get("Factors", ""))
            self.record.factors = data.get("Factors", "")
            # update id
            self.record.patient_id = f"{pid}.{code}"

        self.patient_id_combo.bind("<KeyRelease>", on_key)
        self.patient_id_combo.bind("<<ComboboxSelected>>", on_select)

        # Date
        # ttk.Label(info, text="Date of Diagnosis").grid(row=1, column=0, sticky="w")
        # self.date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        # self.date_entry = ttk.Entry(info, textvariable=self.date_var, width=40)
        # self.date_entry.grid(row=1, column=1, sticky="ew", padx=5)
        # self.date_var.trace_add("write", self.update_event_date)
        # Date (optional)
        if getattr(self, "date_label_text", None):
            ttk.Label(info, text=self.date_label_text).grid(row=1, column=0, sticky="w")
            self.date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
            self.date_entry = ttk.Entry(info, textvariable=self.date_var, width=40)
            self.date_entry.grid(row=1, column=1, sticky="ew", padx=5)
            self.date_var.trace_add("write", self.update_event_date)


        # Diagnosis
        ttk.Label(info, text="Diagnosis").grid(row=2, column=0, sticky="w")
        path = os.path.join(os.path.dirname(__file__), "..", "csv_files", "Diagnosis.ICD10.csv")
        self.diagnosis_codes, self.diagnosis_display = [], []
        with open(path, newline="", encoding="latin-1") as f:
            for row in csv.reader(f):
                if row:
                    self.diagnosis_codes.append(row[0].strip())
                    self.diagnosis_display.append(" ".join(row).strip())
        self.diagnosis_var = tk.StringVar()
        self.diagnosis_combo = AutoCompleteCombobox(
            info,
            values=self.diagnosis_display,
            textvariable=self.diagnosis_var,
            width=40,
        )
        self.diagnosis_combo.grid(row=2, column=1, sticky="ew", padx=5)

        info.grid_columnconfigure(1, weight=1)
        return info


class CancerDetailsMixin:
    """
    Mixin providing create_cancer_details() and update_stage().
    """
    def create_cancer_details(self):
        details = ttk.LabelFrame(self.scrollable_frame, padding=5)
        details.pack(fill="x", padx=5, pady=2)

        # Histo
        ttk.Label(details, text="Histo").grid(row=0, column=0, sticky="w")
        path = os.path.join(os.path.dirname(__file__), "..", "csv_files", "Histopathology.CSV")
        self.histo_options = []
        with open(path, newline="", encoding="latin-1") as f:
            for row in csv.reader(f):
                if row:
                    self.histo_options.append(" ".join(row).strip())
        self.histo_var = tk.StringVar()
        self.histo_combo = ttk.Combobox(details, values=self.histo_options, textvariable=self.histo_var)
        self.histo_combo.grid(row=0, column=1, sticky="ew", padx=5)
        self.histo_combo.bind("<<ComboboxSelected>>", lambda e: setattr(self.record, "histo", self.histo_var.get()))
        self.histo_combo.bind(
            "<KeyRelease>",
            lambda e: (
                self.histo_combo.configure(
                    values=[o for o in self.histo_options if e.widget.get().lower() in o.lower()]
                ),
                self.histo_combo.event_generate("<Down>")
            ),
        )

        # Grade
        ttk.Label(details, text="Grade").grid(row=1, column=0, sticky="w")
        self.grade_var = tk.StringVar()
        self.grade_combo = ttk.Combobox(details, values=[1,2,3,4,9], textvariable=self.grade_var)
        self.grade_combo.grid(row=1, column=1, sticky="ew", padx=5)
        self.grade_combo.bind("<<ComboboxSelected>>", lambda e: setattr(self.record, "grade", self.grade_var.get()))

        # Factors
        ttk.Label(details, text="Factors").grid(row=2, column=0, sticky="w")
        default = "ER|PR|HER2|LN/|BRCA1|BRCA2|GS+|PSA|EPE|cores/|p16|EBV|ENE|PNI|PDL1%|EGFR|ALK|ROS1|BRAF|KRAS|R-mm"
        self.factors_var = tk.StringVar(value=default)
        self.factors_entry = ttk.Entry(details, textvariable=self.factors_var)
        self.factors_entry.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5)
        self.factors_var.trace_add("write", lambda *a: setattr(self.record, "factors", self.factors_var.get()))

        # Stage T/N/M
        frm = ttk.Frame(details)
        frm.grid(row=3, column=1, columnspan=3, sticky="w")
        ttk.Label(frm, text="Stage").pack(side="left")
        self.t_stage_combo = ttk.Combobox(frm, values=["T0","T1","T2","T3","T4","Tx"], width=4)
        self.t_stage_combo.pack(side="left", padx=5)
        self.t_stage_combo.bind("<<ComboboxSelected>>", lambda e: self.update_stage())

        self.n_stage_combo = ttk.Combobox(frm, values=["N0","N1","N2","N3","Nx"], width=4)
        self.n_stage_combo.pack(side="left", padx=5)
        self.n_stage_combo.bind("<<ComboboxSelected>>", lambda e: self.update_stage())

        m_vals = [
            "M0","M1","M1-adrenal","M1-bladder","M1-bone","M1-cerebellum",
            "M1-cerebrum","M1-eye","M1-fat","M1-headandneck","M1-heart",
            "M1-kidneys","M1-liver","M1-lung","M1-lymphnode","M1-muscle",
            "M1-nasalcavity","M1-oesophagus","M1-ovary","M1-pancreas",
            "M1-parathyroid","M1-peritoneum","M1-pleural","M1-retroperitoneum",
            "M1-salivaryglang","M1-sinuses","M1-skin","M1-spinalcanal",
            "M1-spinalcord","M1-spleen","M1-stomach","M1-subcutaneous",
            "M1-thyroid","M1-vagina"
        ]
        self.m_stage_combo = ttk.Combobox(frm, values=m_vals, width=max(len(s) for s in m_vals))
        self.m_stage_combo.pack(side="left", padx=5)
        self.m_stage_combo.bind("<<ComboboxSelected>>", lambda e: self.update_stage())

        details.grid_columnconfigure(1, weight=1)

    def update_stage(self, *args):
        parts = [self.t_stage_combo.get(), self.n_stage_combo.get(), self.m_stage_combo.get()]
        self.record.stage = " ".join(p for p in parts if p)


class CarePlanMixin:
    """
    Mixin providing create_care_plan() and toggle_button().
    """
    def create_care_plan(self):
        care = ttk.LabelFrame(self.scrollable_frame, padding=5)
        care.pack(fill="x", padx=5, pady=2, anchor="e")
        ttk.Label(care, text="Care Planned First", font=("Arial",10,"bold")).pack(anchor="center", pady=(0,5))
        grid = ttk.Frame(care)
        grid.pack(anchor="w")
        grid.columnconfigure((0,1), weight=1)

        # ← initialize empty list to track click order
        self._care_order = []

        self.care_buttons = []
        rows = [
            ["Observe"],
            ["Surgery","Radiation"],
            ["Chemo","Brachy"],
            ["Immuno","Hormones"],
            ["Small mol."]
        ]
        for r, opts in enumerate(rows):
            for c in range(2):
                if c < len(opts):
                    b = tk.Button(grid, text=opts[c])
                    b.selected = False
                    b.default_bg = b.cget("bg")
                    b.config(command=lambda btn=b: self.toggle_button(btn))
                    b.grid(row=r, column=c, padx=5, pady=2, sticky="ew")
                    self.care_buttons.append(b)
                else:
                    ttk.Label(grid, text="").grid(row=r, column=c, padx=5, pady=2)

    # def toggle_button(self, btn):
    #     btn.selected = not btn.selected
    #     btn.config(bg="green" if btn.selected else btn.default_bg)
    #     self.record.careplan = ", ".join(b.cget("text") for b in self.care_buttons if b.selected)
    def toggle_button(self, btn):
        text = btn.cget("text")
        if btn.selected:
            btn.selected = False
            btn.config(bg=btn.default_bg)
            if text in self._care_order:
                self._care_order.remove(text)
        else:
            btn.selected = True
            btn.config(bg="green")
            if text not in self._care_order:
                self._care_order.append(text)

        self.record.careplan = ", ".join(self._care_order)


class NotesMixin:
    """
    Mixin providing create_notes() and update_notes().
    """
    def create_notes(self):
        nf = ttk.LabelFrame(self.scrollable_frame, padding=5)
        nf.pack(fill="both", expand=True, padx=5, pady=2)
        ttk.Label(nf, text="Notes").pack(anchor="w")
        self.notes_text = tk.Text(nf, height=4)
        self.notes_text.pack(fill="both", expand=True, pady=5)
        self.notes_text.bind("<FocusOut>", self.update_notes)

    def update_notes(self, event):
        self.record.note = self.notes_text.get("1.0", "end").strip()
