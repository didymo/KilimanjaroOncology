# config_screen.py
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from kilimanjaro_oncology.controllers.record_controller import RecordController
from kilimanjaro_oncology.database.database_service import DatabaseService


class ConfigScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config_manager = parent.config_manager

        ttk.Label(self, text="Configuration Screen", font=("Arial", 16)).pack(pady=10)

        # Database Path Entry
        self.db_path_var = tk.StringVar(
            value=self.config_manager.settings.get("db_path", "")
        )
        ttk.Label(self, text="Database Path:").pack(pady=5)
        self.db_path_entry = ttk.Entry(self, textvariable=self.db_path_var, width=50)
        self.db_path_entry.pack(pady=5)

        # Browse Button
        # ttk.Button(self, text="Browse", command=self.browse_db_path).pack(pady=5)
        # ——— DATABASE PICKERS ———
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        ttk.Button(
            btn_frame,
            text="Use Existing Database…",
            command=self.select_existing_db,
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Create New Database Here…",
            command=self.select_db_folder,
        ).pack(side="left", padx=5)

        # Save Button
        ttk.Button(self, text="Save and Continue", command=self.save_and_continue).pack(
            pady=10
        )

        ttk.Label(self, text="Hospital Name:").pack(pady=(20, 5))
        self.hospital_var = tk.StringVar(
            value=self.config_manager.settings.get("hospital_name", "")
        )
        self.hospital_entry = ttk.Entry(self, textvariable=self.hospital_var, width=50)
        self.hospital_entry.pack(pady=5)

        ttk.Label(self, text="Department Name:").pack(pady=(10, 5))
        self.department_var = tk.StringVar(
            value=self.config_manager.settings.get("department_name", "")
        )
        self.department_entry = ttk.Entry(
            self, textvariable=self.department_var, width=50
        )
        self.department_entry.pack(pady=5)

    def browse_db_path(self):
        """Open a file dialog to select the database file."""
        db_path = filedialog.askopenfilename(
            title="Select SQLite Database",
            filetypes=(("SQLite files", "*.sqlite"), ("All files", "*.*")),
        )
        if db_path:
            self.db_path_var.set(db_path)

    def select_existing_db(self):
        """Let the user pick an existing .sqlite or .db file."""
        p = filedialog.askopenfilename(
            title="Select an existing SQLite database",
            filetypes=[("SQLite", "*.sqlite;*.db"), ("All files", "*.*")],
        )
        if p:
            self.db_path_var.set(p)

    def select_db_folder(self):
        """Let the user pick a folder to create database.sqlite inside."""
        d = filedialog.askdirectory(title="Select folder for new database")
        if not d:
            return
        new_db = Path(d) / "database.sqlite"
        # if it exists, optionally confirm overwrite
        if new_db.exists() and not tk.messagebox.askyesno(
            "Overwrite?", f"{new_db} already exists. Overwrite?"
        ):
            return
        self.db_path_var.set(str(new_db))

    def save_and_continue(self):
        """
        Save configuration, initialize the database, and transition to the main
        screen.
        """
        db_path = self.db_path_var.get()
        if db_path:
            self.config_manager.settings["db_path"] = db_path
            self.config_manager.save_settings()
            # Initialize the database so that the file is created if it doesn't
            # exist.
            self.config_manager.initialize_database()

            # 3) now rewire the app’s single DatabaseService  RecordController
            self.parent.db_service = DatabaseService(db_path)
            self.parent.record_ctrl = RecordController(self.parent.db_service)

            # 4) store hospital/department into the just-created DB
            with self.parent.db_service.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT OR REPLACE INTO settings(key,value) VALUES (?,?)",
                    ("hospital_name", self.hospital_var.get().strip()),
                )
                cur.execute(
                    "INSERT OR REPLACE INTO settings(key,value) VALUES (?,?)",
                    ("department_name", self.department_var.get().strip()),
                )

            # 5) finally switch to your main screen
            self.parent.show_new_diagnosis_screen()
        else:
            ttk.Label(
                self, text="Database path cannot be empty!", foreground="red"
            ).pack(pady=5)
