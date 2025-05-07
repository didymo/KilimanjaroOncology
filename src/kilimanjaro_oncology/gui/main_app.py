# main_app.py
import sys
import tkinter as tk

from kilimanjaro_oncology.controllers.record_controller import RecordController
from kilimanjaro_oncology.database.database_service import DatabaseService
from kilimanjaro_oncology.gui.config_screen import (
    ConfigScreen,  # Assuming you have; a config screen
)
from kilimanjaro_oncology.gui.death_screen import DeathScreen
from kilimanjaro_oncology.gui.follow_up_screen import (
    FollowUpScreen,  # Make sure this; import is correct
)
from kilimanjaro_oncology.gui.new_diagnosis_screen import NewDiagnosisScreen
from kilimanjaro_oncology.utils.config import ConfigManager
from kilimanjaro_oncology.utils.exceptions import ConfigurationError, DatabaseError
from kilimanjaro_oncology.utils.logger import setup_logger

logger = setup_logger()


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kilimanjaro Christian Medical Centre Oncology Data Collection")
        self.geometry("1200x800")
        self.config_manager = ConfigManager()

        # create exactly one DatabaseService to pass into all screens
        self.db_service = DatabaseService(self.config_manager.settings["db_path"])
        self.record_ctrl = RecordController(self.db_service)

        # Placeholder for the current screen (each screen is a Frame)
        self.current_screen = None

        try:
            if self.config_manager.config_exists():
                # ensure that database really *is* initialized
                self.config_manager.initialize_database()
                # first screen is the “real” one
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

        self.current_screen = ConfigScreen(self)
        self.current_screen.pack(expand=True, fill="both")

    def show_new_diagnosis_screen(self):
        """Display the New Diagnosis screen."""
        self.clear_screen()
        # Pass 'controller=self' so the NewDiagnosisScreen can call navigation methods.
        self.current_screen = NewDiagnosisScreen(
            self,
            controller=self,
            record_ctrl=self.record_ctrl,
        )
        self.current_screen.pack(expand=True, fill="both")

    def show_followup_screen(self):
        """Display the Follow-Up screen."""
        self.clear_screen()
        # Pass 'controller=self' so the FollowUpScreen can call navigation methods.
        self.current_screen = FollowUpScreen(
            self,
            controller=self,
            record_ctrl=self.record_ctrl,
        )
        self.current_screen.pack(expand=True, fill="both")

    def show_death_screen(self):
        """Display the Death screen."""
        self.clear_screen()
        self.current_screen = DeathScreen(
            self,
            controller=self,
            record_ctrl=self.record_ctrl,
        )
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
