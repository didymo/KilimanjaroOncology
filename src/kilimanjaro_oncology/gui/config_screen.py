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
            self.parent.show_new_diagnosis_screen()  # Transition to the main screen
        else:
            ttk.Label(
                self, text="Database path cannot be empty!", foreground="red"
            ).pack(pady=5)
