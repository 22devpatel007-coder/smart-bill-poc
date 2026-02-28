import os
import sys
from database.connection import get_connection
from database.schema import create_tables
from database.seed import seed_database
from database.migrations.add_day_close import run_migration
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QMessageBox
from PySide6.QtCore import Qt

class SetupWizard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart POS - First Run Setup")
        self.setFixedSize(400, 400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.shop_name = QLineEdit()
        self.shop_name.setText("My Shop")
        self.address = QLineEdit()
        self.gst_no = QLineEdit()
        self.phone = QLineEdit()
        self.printer_port = QLineEdit()
        self.printer_port.setPlaceholderText("Leave blank for auto-detect")
        
        layout.addRow("Shop Name:", self.shop_name)
        layout.addRow("Address:", self.address)
        layout.addRow("GST Number:", self.gst_no)
        layout.addRow("Phone:", self.phone)
        layout.addRow("Printer Port:", self.printer_port)
        
        btn_save = QPushButton("Save & Complete Setup")
        btn_save.clicked.connect(self.save_settings)
        layout.addRow(btn_save)
        
    def save_settings(self):
        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                settings = {
                    'shop_name': self.shop_name.text().strip(),
                    'address': self.address.text().strip(),
                    'gst_number': self.gst_no.text().strip(),
                    'phone': self.phone.text().strip(),
                    'printer_port': self.printer_port.text().strip(),
                }
                for k, v in settings.items():
                    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))
            QMessageBox.information(self, "Success", "Setup complete! You can now run SmartPOS.")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    print("Running First Run Setup...")
    conn = get_connection()
    create_tables(conn)
    seed_database()
    run_migration()
    
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    wizard.show()
    sys.exit(app.exec())
