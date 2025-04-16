# main.py
import sys

from app.gui.main_app import MainApp
from app.utils.logger import setup_logger

logger = setup_logger()


def main():
    try:
        app = MainApp()
        app.run()
        sys.exit(0)  # Success
    except Exception as e:
        logger.exception(f"Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
