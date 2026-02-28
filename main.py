import sys
import os
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def load_stylesheet(app):
    qss_path = os.path.join(os.path.dirname(__file__), "ui", "styles", "main.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Stylesheet not found at {qss_path}")

def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Smart POS")
    
    load_stylesheet(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
