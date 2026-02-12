# config_screen.py
import shutil
import sqlite3
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from kilimanjaro_oncology.controllers.record_controller import RecordController
from kilimanjaro_oncology.database.database_service import DatabaseService


class ConfigScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config_manager = parent.config_manager

        ttk.Label(self, text="Configuration Screen", font=("Arial", 16)).pack(
            pady=10
        )

        # Database Path Entry
        self.db_path_var = tk.StringVar(
            value=self.config_manager.settings.get("db_path", "")
        )
        ttk.Label(self, text="Database Path:").pack(pady=5)
        self.db_path_entry = ttk.Entry(
            self, textvariable=self.db_path_var, width=50
        )
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

        action_frame = ttk.Frame(self)
        action_frame.pack(pady=10)
        # Save Button
        ttk.Button(
            action_frame, text="Save and Continue", command=self.save_and_continue
        ).pack(side="left", padx=5)
        self.back_button = ttk.Button(
            action_frame, text="Back to Main", command=self.back_to_main
        )
        self.back_button.pack(side="left", padx=5)

        backup_frame = ttk.LabelFrame(self, text="Backup / Restore")
        backup_frame.pack(pady=(10, 5), padx=5, fill="x")
        ttk.Button(
            backup_frame, text="Backup Database…", command=self.backup_database
        ).pack(side="left", padx=5, pady=5)
        ttk.Button(
            backup_frame, text="Restore Database…", command=self.restore_database
        ).pack(side="left", padx=5, pady=5)

        ttk.Label(self, text="Hospital Name:").pack(pady=(20, 5))
        self.hospital_var = tk.StringVar(
            value=self.config_manager.settings.get("hospital_name", "")
        )
        self.hospital_entry = ttk.Entry(
            self, textvariable=self.hospital_var, width=50
        )
        self.hospital_entry.pack(pady=5)

        ttk.Label(self, text="Department Name:").pack(pady=(10, 5))
        self.department_var = tk.StringVar(
            value=self.config_manager.settings.get("department_name", "")
        )
        self.department_entry = ttk.Entry(
            self, textvariable=self.department_var, width=50
        )
        self.department_entry.pack(pady=5)
        # ——— NEW: Font Size setting ———
        ttk.Label(self, text="Font Size:").pack(pady=(10, 5))
        self.font_size_var = tk.StringVar(
            value=str(self.config_manager.settings.get("font_size", 10))
        )
        self.font_size_entry = ttk.Entry(
            self, textvariable=self.font_size_var, width=10
        )
        self.font_size_entry.pack(pady=5)

        self._initial_state: tuple[str, str, str, str] = (
            self._capture_form_state()
        )
        self.db_path_var.trace_add(
            "write", lambda *_a: self._update_back_button_state()
        )
        self._update_back_button_state()

    def _capture_form_state(self) -> tuple[str, str, str, str]:
        return (
            self.db_path_var.get().strip(),
            self.hospital_var.get().strip(),
            self.department_var.get().strip(),
            self.font_size_var.get().strip(),
        )

    def _is_dirty(self) -> bool:
        return bool(self._capture_form_state() != self._initial_state)

    def _update_back_button_state(self):
        has_db_path = bool(self.db_path_var.get().strip())
        self.back_button.state(["!disabled"] if has_db_path else ["disabled"])

    def _mark_clean(self):
        self._initial_state = self._capture_form_state()

    def back_to_main(self):
        if self.back_button.instate(["disabled"]):
            return

        if self._is_dirty():
            choice = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Save changes before returning to the main screen?",
            )
            if choice is None:
                return
            if choice:
                self.save_and_continue()
                return

        self.parent.show_new_diagnosis_screen()

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
            self.config_manager.settings["hospital_name"] = (
                self.hospital_var.get().strip()
            )
            self.config_manager.settings["department_name"] = (
                self.department_var.get().strip()
            )
            # ——— NEW: store font size ———
            try:
                fs = int(self.font_size_var.get())
            except ValueError:
                fs = 10
            self.config_manager.settings["font_size"] = fs
            self.config_manager.save_settings()
            # ← apply it immediately for the running app
            self.parent.apply_font_size()
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
            self._mark_clean()
            self._update_back_button_state()

            # 5) finally switch to your main screen
            self.parent.show_new_diagnosis_screen()
        else:
            ttk.Label(
                self, text="Database path cannot be empty!", foreground="red"
            ).pack(pady=5)

    def backup_database(self):
        db_path = self.db_path_var.get()
        if not db_path:
            messagebox.showerror(
                "Backup Error", "Database path is not set."
            )
            return
        if not Path(db_path).exists():
            messagebox.showerror(
                "Backup Error", f"Database not found: {db_path}"
            )
            return

        dest_dir = filedialog.askdirectory(
            title="Select folder for backup"
        )
        if not dest_dir:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_path = Path(dest_dir) / f"database_{timestamp}.sqlite"

        try:
            # Use sqlite backup API to capture WAL content safely.
            src = sqlite3.connect(db_path)
            try:
                dest = sqlite3.connect(dest_path)
                try:
                    src.backup(dest)
                finally:
                    dest.close()
            finally:
                src.close()
        except sqlite3.Error:
            # Fallback to file copy if backup API fails.
            try:
                shutil.copy2(db_path, dest_path)
            except OSError as e:
                messagebox.showerror("Backup Error", str(e))
                return
        except OSError as e:
            messagebox.showerror("Backup Error", str(e))
            return

        messagebox.showinfo(
            "Backup Complete", f"Backup saved to:\n{dest_path}"
        )

    def restore_database(self):
        db_path = self.db_path_var.get()
        if not db_path:
            messagebox.showerror(
                "Restore Error", "Database path is not set."
            )
            return

        source = filedialog.askopenfilename(
            title="Select a backup database",
            filetypes=[("SQLite", "*.sqlite;*.db"), ("All files", "*.*")],
        )
        if not source:
            return

        if not messagebox.askyesno(
            "Restore Database",
            f"This will overwrite:\n{db_path}\nContinue?",
        ):
            return

        try:
            if getattr(self.parent, "db_service", None):
                self.parent.db_service.close_connections()
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, db_path)
            self.config_manager.settings["db_path"] = db_path
            self.config_manager.save_settings()
            self.config_manager.initialize_database()
            self.parent.db_service = DatabaseService(db_path)
            self.parent.record_ctrl = RecordController(self.parent.db_service)
        except OSError as e:
            messagebox.showerror("Restore Error", str(e))
            return

        messagebox.showinfo(
            "Restore Complete", "Database restored successfully."
        )
