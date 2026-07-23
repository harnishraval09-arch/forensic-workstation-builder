import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForensicWorkstationBuilder(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Forensic Workstation Builder")
        self.setStyle('Fusion')
        logger.info("Application initialized")

def main():
    try:
        app = ForensicWorkstationBuilder(sys.argv)
        from .ui.main_window import MainWindow
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())