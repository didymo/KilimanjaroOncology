# main_app.py
import sys
import tkinter as tk

from app.gui.config_screen import ConfigScreen  # Assuming you have a config screen
from app.gui.death_screen import DeathScreen
from app.gui.follow_up_screen import FollowUpScreen  # Make sure this import is correct
from app.gui.new_diagnosis_screen import NewDiagnosisScreen
from app.utils.config import ConfigManager
from app.utils.exceptions import ConfigurationError, DatabaseError
from app.utils.logger import setup_logger
from app.utils.setup import check_initialization

logger = setup_logger()


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Africa Oncology Data Collection")
        self.geometry("1200x800")
        self.config_manager = ConfigManager()

        # Placeholder for the current screen (each screen is a Frame)
        self.current_screen = None

        try:
            if check_initialization():
                # If initialized, show the New Diagnosis screen by default.
                self.show_new_diagnosis_screen()
            else:
                logger.info("Configuration or database missing. Showing config screen.")
                self.show_config_screen()
        except Exception as e:
            logger.warning(f"Initialization check failed: {e}")
            self.show_config_screen()

    def show_config_screen(self):
        """Display the configuration screen."""
        self.clear_screen()
        # Pass 'controller=self' so that the config screen can also navigate if needed.
        # self.current_screen = ConfigScreen(self, controller=self)
        self.current_screen = ConfigScreen(self)
        self.current_screen.pack(expand=True, fill="both")

    def show_new_diagnosis_screen(self):
        """Display the New Diagnosis screen."""
        self.clear_screen()
        # Pass 'controller=self' so the NewDiagnosisScreen can call navigation methods.
        self.current_screen = NewDiagnosisScreen(self, controller=self)
        self.current_screen.pack(expand=True, fill="both")

    def show_followup_screen(self):
        """Display the Follow-Up screen."""
        self.clear_screen()
        # Pass 'controller=self' so the FollowUpScreen can call navigation methods.
        self.current_screen = FollowUpScreen(self, controller=self)
        self.current_screen.pack(expand=True, fill="both")

    def show_death_screen(self):
        """Display the Death screen."""
        self.clear_screen()
        self.current_screen = DeathScreen(self, controller=self)
        self.current_screen.pack(expand=True, fill="both")

    def clear_screen(self):
        """Destroy the current screen to transition to another."""
        if self.current_screen:
            self.current_screen.destroy()

    def run(self):
        try:
            self.mainloop()
        except ConfigurationError:
            logger.error("Configuration failed. Relaunching configuration screen.")
            self.show_config_screen()
        except DatabaseError:
            logger.error("Database initialization failed.")
            sys.exit(3)
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            sys.exit(1)
