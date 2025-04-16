# config.py
import json
import sqlite3
from pathlib import Path

from app.utils.exceptions import ConfigurationError, DatabaseError

# Define the application directory in the user's home directory
APP_DIR = Path.home() / "africa_oncology_settings"
SETTINGS_FILE = APP_DIR / "settings.json"
DATABASE_FILE = APP_DIR / "database.sqlite"
SCHEMA_FILE = Path(__file__).parent.parent / "database" / "schema.sql"


class ConfigManager:
    def __init__(self):
        # Ensure the application directory exists
        self.create_app_directory()
        # Initialize settings
        self.settings = self.load_settings()

    def create_app_directory(self):
        """Ensure the application directory exists."""
        APP_DIR.mkdir(exist_ok=True)

    def config_exists(self):
        """
        Check if both settings and database files exist and are valid.
        Returns True only if both exist and settings file contains valid JSON.
        """
        if not (SETTINGS_FILE.exists() and DATABASE_FILE.exists()):
            return False

        try:
            # Verify settings file contains valid JSON
            with open(SETTINGS_FILE, "r") as file:
                settings = json.load(file)
                # Verify required settings exist
                if not settings.get("db_path"):
                    return False
                return True
        except (json.JSONDecodeError, IOError):
            return False

    def load_settings(self):
        """Load the settings from the settings file."""
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r") as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError):
                # If file is invalid or corrupt, fall back to default settings
                return self.create_default_settings()
        else:
            return self.create_default_settings()

    def save_settings(self):
        """Save the current settings to the settings file."""
        with open(SETTINGS_FILE, "w") as file:
            json.dump(self.settings, file, indent=4)

    def create_default_settings(self):
        """Create and return default settings."""
        default_settings = {"db_path": str(DATABASE_FILE)}
        self.settings = default_settings  # Ensure self.settings is initialized
        self.save_settings()  # Save default settings to file
        return default_settings

    def initialize_settings(self):
        """Ensure the settings file and directory exist."""
        if not self.settings.get("db_path"):
            raise ConfigurationError("Database path is missing in configuration.")

    def initialize_database(self):
        """Ensure the database file exists and is initialized."""
        try:
            if not DATABASE_FILE.exists():
                # Ensure parent directory exists
                DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
                self._create_database()
            # Verify database is accessible and has correct schema
            self._verify_database()
        except sqlite3.Error as e:
            raise DatabaseError(f"Database initialization failed: {e}")

    def _create_database(self):
        """Create the database using schema.sql."""
        conn = None
        try:
            # Read the schema file
            if not SCHEMA_FILE.exists():
                raise DatabaseError(f"Schema file not found: {SCHEMA_FILE}")

            with open(SCHEMA_FILE, "r") as f:
                schema_script = f.read()

            # Create and initialize the database
            conn = sqlite3.connect(str(DATABASE_FILE))
            cursor = conn.cursor()
            cursor.executescript(schema_script)
            conn.commit()

        except (sqlite3.Error, IOError) as e:
            if DATABASE_FILE.exists():
                DATABASE_FILE.unlink()  # Delete failed database file
            raise DatabaseError(f"Failed to create database: {e}")
        finally:
            if conn:
                conn.close()

    def _verify_database(self):
        """Verify database is accessible and has the correct schema."""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()

            # Get all tables from schema.sql
            with open(SCHEMA_FILE, "r") as f:
                schema_content = f.read().lower()
                table_names = []
                # Iterate over each line in the schema file
                for line in schema_content.split("\n"):
                    line = line.strip()
                    # Only process lines that start with "create table"
                    if line.startswith("create table"):
                        # Extract the portion after "table"
                        name_part = line.split("table", 1)[1].split("(")[0].strip()
                        # NEW: If the extracted name starts with "if not exists",
                        # remove that prefix
                        if name_part.startswith("if not exists"):
                            name_part = name_part[len("if not exists") :].strip()
                        # Append the cleaned table name
                        table_names.append(name_part)

            # Check if required tables exist
            cursor.execute(
                """
                SELECT name FROM sqlite_master WHERE type='table'
            """
            )
            existing_tables = {row[0].lower() for row in cursor.fetchall()}
            required_tables = set(table_names)

            if not required_tables.issubset(existing_tables):
                missing_tables = required_tables - existing_tables
                raise DatabaseError(
                    f"Database missing required tables: {missing_tables}"
                )

        except sqlite3.Error as e:
            raise DatabaseError(f"Database verification failed: {e}")
        except IOError as e:
            raise DatabaseError(f"Failed to read schema file: {e}")
        finally:
            if conn:
                conn.close()


# Module-level function since it's a utility that creates its own ConfigManager
def check_initialization():
    """
    Check if both configuration and database are properly initialized.
    Returns True if both exist and are valid, False otherwise.
    """
    try:
        config_manager = ConfigManager()
        return config_manager.config_exists()
    except Exception:
        return False
