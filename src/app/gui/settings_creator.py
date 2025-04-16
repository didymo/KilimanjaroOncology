from src.app.utils.config import ConfigManager


class SettingsController:
    def __init__(self, gui):
        self.gui = gui
        self.config_manager = ConfigManager()

    def save_settings(self, data):
        """Update and save settings."""
        self.config_manager.settings.update(data)
        self.config_manager.save_settings()
        self.gui.show_success_message("Settings saved successfully!")

    def load_settings(self):
        """Load current settings."""
        return self.config_manager.settings
