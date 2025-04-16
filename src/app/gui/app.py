# app.py
# import tkinter as tk
# from tkinter import ttk
#
#
# class Application(tk.Tk):
#     def __init__(self):
#         super().__init__()
#
#         self.title("My Tkinter App")
#         self.geometry("800x600")
#
#         # Configure main window
#         self.configure(padx=10, pady=10)
#
#         # Create main frame
#         self.main_frame = ttk.Frame(self)
#         self.main_frame.pack(expand=True, fill="both")
#
#         # Add your widgets here
#         self.label = ttk.Label(self.main_frame, text="Hello, World!")
#         self.label.pack(pady=20)
#
#     def run(self):
#         self.mainloop()


import tkinter as tk
from tkinter import ttk

from src.app.utils.config import ConfigManager


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()

        self.title("My Tkinter App")
        self.geometry("800x600")
        self.configure(padx=10, pady=10)

        # Decide whether to show configuration screen or main screen
        if not self.config_manager.settings.get("db_path"):
            self.show_config_screen()
        else:
            self.show_main_screen()

    def show_config_screen(self):
        """Display the configuration screen."""
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(self, text="Configuration Screen").pack(pady=10)
        db_path_entry = ttk.Entry(self)
        db_path_entry.pack(pady=5)
        db_path_entry.insert(0, self.config_manager.settings.get("db_path", ""))

        def save_config():
            db_path = db_path_entry.get()
            if db_path:
                self.config_manager.settings["db_path"] = db_path
                self.config_manager.save_settings()
                self.show_main_screen()
            else:
                self.show_error_message("Database path cannot be empty.")

        ttk.Button(self, text="Save", command=save_config).pack(pady=10)

    def show_main_screen(self):
        """Display the main application screen."""
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(self, text="Welcome to the Application!").pack(pady=10)
        ttk.Button(self, text="Exit", command=self.destroy).pack(pady=10)

    def show_success_message(self, message):
        """Show a success message."""
        ttk.Label(self, text=message, foreground="green").pack(pady=5)

    def show_error_message(self, message):
        """Show an error message."""
        ttk.Label(self, text=message, foreground="red").pack(pady=5)

    def run(self):
        self.mainloop()
