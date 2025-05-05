# config_screen.py
import tkinter as tk
from tkinter import filedialog, ttk


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
        ttk.Button(self, text="Browse", command=self.browse_db_path).pack(pady=5)

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
            from kilimanjaro_oncology.database.database_service import DatabaseService

            db = DatabaseService(self.config_manager.settings["db_path"])
            with db.get_connection() as conn:
                cur = conn.cursor()
                # insert hospital_name
                cur.execute(
                    "INSERT OR REPLACE INTO settings(key,value) VALUES (?,?)",
                    ("hospital_name", self.hospital_var.get().strip()),
                )
                # insert department_name
                cur.execute(
                    "INSERT OR REPLACE INTO settings(key,value) VALUES (?,?)",
                    ("department_name", self.department_var.get().strip()),
                )
            self.parent.show_new_diagnosis_screen()  # Transition to the main screen
        else:
            ttk.Label(
                self, text="Database path cannot be empty!", foreground="red"
            ).pack(pady=5)
