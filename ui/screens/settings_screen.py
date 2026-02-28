from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QListWidget, QStackedWidget,
                               QTextEdit, QComboBox, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QFormLayout, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import os
import shutil
import bcrypt
from database.connection import get_connection
from services.backup_service import backup_to_usb, backup_to_local, get_last_backup_date, check_backup_reminder

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add User")
        self.setFixedSize(300, 250)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        self.username = QLineEdit()
        self.fullname = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.role = QComboBox()
        self.role.addItems(["staff", "admin"])
        
        layout.addRow("Username *:", self.username)
        layout.addRow("Full Name *:", self.fullname)
        layout.addRow("Password *:", self.password)
        layout.addRow("Role:", self.role)
        
        btn_save = QPushButton("Save User")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)
        
    def save(self):
        un = self.username.text().strip()
        fn = self.fullname.text().strip()
        pwd = self.password.text().strip()
        r = self.role.currentText()
        
        if not un or not fn or not pwd:
            QMessageBox.warning(self, "Error", "All fields are required")
            return
            
        hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = get_connection()
        try:
            with conn:
                conn.execute("INSERT INTO users (username, full_name, password, role) VALUES (?, ?, ?, ?)",
                             (un, fn, hashed, r))
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add user (Username might exist). Error: {e}")

class SettingsScreen(QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self.setup_ui()
        self.load_settings()
        self.load_users()
        self.update_backup_info()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Left Nav
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(200)
        nav_items = ["Shop Information", "GST & Tax", "Printer", "Users & Access", "Backup & Restore"]
        self.nav_list.addItems(nav_items)
        self.nav_list.setCurrentRow(0)
        
        # Right Content
        self.stacked_widget = QStackedWidget()
        
        self.setup_shop_info_page()
        self.setup_gst_page()
        self.setup_printer_page()
        self.setup_users_page()
        self.setup_backup_page()
        
        self.nav_list.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)
        
        main_layout.addWidget(self.nav_list)
        main_layout.addWidget(self.stacked_widget)
        
    def setup_shop_info_page(self):
        page = QWidget()
        layout = QFormLayout(page)
        
        self.shop_name = QLineEdit()
        self.address = QTextEdit()
        self.address.setFixedHeight(60)
        self.phone = QLineEdit()
        self.email = QLineEdit()
        
        self.gst_no = QLineEdit()
        font = QFont("Courier", 10)
        self.gst_no.setFont(font)
        self.gst_no.setMaxLength(15)
        
        self.fssai_no = QLineEdit()
        self.upi_id = QLineEdit()
        self.upi_id.setPlaceholderText("Used for QR code on receipts")
        
        self.footer_msg = QLineEdit()
        
        # Logo upload
        logo_layout = QHBoxLayout()
        self.btn_logo = QPushButton("Upload Logo")
        self.btn_logo.clicked.connect(self.upload_logo)
        self.lbl_logo_preview = QLabel("No Logo")
        self.lbl_logo_preview.setFixedSize(100, 100)
        self.lbl_logo_preview.setScaledContents(True)
        self.lbl_logo_preview.setStyleSheet("border: 1px solid #ccc;")
        if os.path.exists("assets/logo.png"):
            self.lbl_logo_preview.setPixmap(QPixmap("assets/logo.png"))
        logo_layout.addWidget(self.btn_logo)
        logo_layout.addWidget(self.lbl_logo_preview)
        logo_layout.addStretch()
        
        layout.addRow("Shop Name *:", self.shop_name)
        layout.addRow("Address:", self.address)
        layout.addRow("Phone:", self.phone)
        layout.addRow("Email:", self.email)
        layout.addRow("GST Number:", self.gst_no)
        layout.addRow("FSSAI Number:", self.fssai_no)
        layout.addRow("UPI ID:", self.upi_id)
        layout.addRow("Receipt Footer:", self.footer_msg)
        layout.addRow("Logo:", logo_layout)
        
        btn_save = QPushButton("Save Shop Info")
        btn_save.setStyleSheet("background-color: #3B82F6; color: white; padding: 10px; font-weight: bold;")
        btn_save.clicked.connect(self.save_shop_info)
        layout.addRow("", btn_save)
        
        self.stacked_widget.addWidget(page)
        
    def setup_gst_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("<h2>GST & Tax Settings</h2>\nConfigure tax slabs in standard settings here (coming soon)."))
        layout.addStretch()
        self.stacked_widget.addWidget(page)
        
    def setup_printer_page(self):
        page = QWidget()
        layout = QFormLayout(page)
        
        self.paper_width = QComboBox()
        self.paper_width.addItems(["58mm", "80mm"])
        
        port_layout = QHBoxLayout()
        self.printer_port = QLineEdit()
        btn_detect = QPushButton("Auto-detect")
        btn_detect.hide() # Implementation empty for now
        port_layout.addWidget(self.printer_port)
        port_layout.addWidget(btn_detect)
        
        layout.addRow("Paper Width:", self.paper_width)
        layout.addRow("Printer Port:", port_layout)
        
        btn_save = QPushButton("Save Printer Settings")
        btn_save.clicked.connect(self.save_printer_settings)
        btn_test = QPushButton("Test Print")
        btn_test.clicked.connect(self.test_print)
        
        btns = QHBoxLayout()
        btns.addWidget(btn_save)
        btns.addWidget(btn_test)
        layout.addRow("", btns)
        
        self.stacked_widget.addWidget(page)
        
    def setup_users_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("<b>User Management</b> (Admin Only)"))
        toolbar.addStretch()
        btn_add = QPushButton("+ Add User")
        btn_add.clicked.connect(self.add_user)
        toolbar.addWidget(btn_add)
        layout.addLayout(toolbar)
        
        self.users_table = QTableWidget(0, 5)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Full Name", "Role", "Actions"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.users_table)
        
        self.stacked_widget.addWidget(page)
        
    def setup_backup_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        self.lbl_backup_warning = QLabel("Warning: Backup is overdue!")
        self.lbl_backup_warning.setStyleSheet("color: white; background-color: #EF4444; padding: 10px; border-radius: 4px; font-weight: bold;")
        self.lbl_backup_warning.hide()
        layout.addWidget(self.lbl_backup_warning)
        
        self.lbl_last_backup = QLabel("Last Backup: Never")
        self.lbl_last_backup.setStyleSheet("font-size: 16px; margin: 10px 0;")
        layout.addWidget(self.lbl_last_backup)
        
        btn_usb = QPushButton("Backup to USB")
        btn_usb.setStyleSheet("padding: 10px; font-weight: bold;")
        btn_usb.clicked.connect(self.do_backup_usb)
        
        btn_local = QPushButton("Backup to Local Folder")
        btn_local.setStyleSheet("padding: 10px; font-weight: bold;")
        btn_local.clicked.connect(self.do_backup_local)
        
        btn_drive = QPushButton("Backup to Google Drive")
        btn_drive.setStyleSheet("padding: 10px; font-weight: bold; color: #666;")
        btn_drive.clicked.connect(self.do_backup_drive)
        
        layout.addWidget(btn_usb)
        layout.addWidget(btn_local)
        layout.addWidget(btn_drive)
        layout.addStretch()
        
        self.stacked_widget.addWidget(page)
        
    def load_settings(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        s = {row['key']: row['value'] for row in cursor.fetchall()}
        
        self.shop_name.setText(s.get('shop_name', ''))
        self.address.setText(s.get('address', ''))
        self.phone.setText(s.get('phone', ''))
        self.email.setText(s.get('email', ''))
        self.gst_no.setText(s.get('gst_number', ''))
        self.fssai_no.setText(s.get('fssai_number', ''))
        self.upi_id.setText(s.get('upi_id', ''))
        self.footer_msg.setText(s.get('receipt_footer', ''))
        
        pw = s.get('paper_width', '58mm')
        idx = self.paper_width.findText(pw)
        if idx >= 0: self.paper_width.setCurrentIndex(idx)
        self.printer_port.setText(s.get('printer_port', ''))

    def load_users(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role, is_active FROM users")
        users = cursor.fetchall()
        
        self.users_table.setRowCount(len(users))
        for i, u in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(str(u['id'])))
            self.users_table.setItem(i, 1, QTableWidgetItem(u['username']))
            self.users_table.setItem(i, 2, QTableWidgetItem(u['full_name']))
            self.users_table.setItem(i, 3, QTableWidgetItem(u['role']))
            
            btn_deact = QPushButton("Deactivate" if u['is_active'] else "Activate")
            btn_deact.clicked.connect(lambda checked=False, uid=u['id'], act=u['is_active']: self.toggle_user(uid, act))
            if self.current_user and self.current_user.id == u['id']:
                btn_deact.setEnabled(False) # Can't toggle self
                
            self.users_table.setCellWidget(i, 4, btn_deact)
            
    def update_backup_info(self):
        last = get_last_backup_date()
        if last:
            self.lbl_last_backup.setText(f"Last Backup: {last}")
        else:
            self.lbl_last_backup.setText("Last Backup: Never")
            
        if check_backup_reminder():
            self.lbl_backup_warning.show()
        else:
            self.lbl_backup_warning.hide()

    def upload_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Logo Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            if not os.path.exists("assets"): os.makedirs("assets")
            dest = "assets/logo.png"
            shutil.copy(file_path, dest)
            self.lbl_logo_preview.setPixmap(QPixmap(dest))
            QMessageBox.information(self, "Success", "Logo updated successfully")

    def save_shop_info(self):
        s = {
            'shop_name': self.shop_name.text().strip(),
            'address': self.address.toPlainText().strip(),
            'phone': self.phone.text().strip(),
            'email': self.email.text().strip(),
            'gst_number': self.gst_no.text().strip(),
            'fssai_number': self.fssai_no.text().strip(),
            'upi_id': self.upi_id.text().strip(),
            'receipt_footer': self.footer_msg.text().strip()
        }
        if not s['shop_name']:
            QMessageBox.warning(self, "Validation", "Shop Name is required")
            return
            
        conn = get_connection()
        with conn:
            c = conn.cursor()
            for k, v in s.items():
                c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))
        QMessageBox.information(self, "Saved", "Shop information saved successfully")
        
    def save_printer_settings(self):
        conn = get_connection()
        with conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('paper_width', self.paper_width.currentText()))
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('printer_port', self.printer_port.text().strip()))
        QMessageBox.information(self, "Saved", "Printer settings saved successfully")
        
    def test_print(self):
        # We assume printer_service has a test print
        try:
            from services.printer_service import print_test_receipt
            print_test_receipt()
            QMessageBox.information(self, "Success", "Test print sent.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to print: {e}")

    def add_user(self):
        if self.current_user and self.current_user.role != 'admin':
            QMessageBox.warning(self, "Error", "Only admin can add users")
            return
        dlg = AddUserDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self.load_users()

    def toggle_user(self, user_id, current_active):
        if self.current_user and self.current_user.role != 'admin':
            QMessageBox.warning(self, "Error", "Only admin can manage users")
            return
        new_status = 0 if current_active else 1
        conn = get_connection()
        with conn:
            conn.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id))
        self.load_users()

    def do_backup_usb(self):
        try:
            p = backup_to_usb()
            QMessageBox.information(self, "Success", f"Backup complete: {p}")
            self.update_backup_info()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
    def do_backup_local(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Backup Folder")
        if folder:
            try:
                p = backup_to_local(folder)
                QMessageBox.information(self, "Success", f"Backup complete: {p}")
                self.update_backup_info()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def do_backup_drive(self):
        from services.backup_service import backup_to_google_drive
        try:
            msg = backup_to_google_drive()
            QMessageBox.information(self, "Info", msg)
            self.update_backup_info()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

