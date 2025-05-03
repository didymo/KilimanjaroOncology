# setup.py
from kilimanjaro_oncology.utils.config import DATABASE_FILE, ConfigManager


def check_initialization():
    """
    Check if both configuration and database are present.
    Returns True if both exist, False otherwise.
    """
    config_manager = ConfigManager()

    # Check if config directory and settings exist
    config_exists = config_manager.config_exists()

    # Check if database exists
    db_exists = DATABASE_FILE.exists()

    return config_exists and db_exists


def initialize_app():
    """Initialize the application only if needed."""
    if not check_initialization():
        # Only initialize if either config or database is missing
        initialize_settings()
        initialize_database()


def initialize_settings():
    """Ensure the settings file and directory exist."""
    config_manager = ConfigManager()
    if not config_manager.settings.get("db_path"):
        raise ValueError("Database path is missing in configuration.")


def initialize_database():
    """Ensure the database file exists and is initialized."""
    if not DATABASE_FILE.exists():
        raise FileNotFoundError(f"Database file not found: {DATABASE_FILE}")
