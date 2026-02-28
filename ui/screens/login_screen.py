from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from forms.login_form import LoginForm

class LoginScreen(QWidget):
    login_success = Signal(object) # Emits User object

    def __init__(self):
        super().__init__()
        self.form = LoginForm()
        self.setup_ui()

    def setup_ui(self):
        # We let the global stylesheet (main.qss) control the background #F8FAFC
        # But for login, the prompt requested a dark navy background #0F172A
        self.setStyleSheet("background-color: #0F172A;")
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # White Card
        card = QFrame()
        card.setFixedSize(400, 450)
        card.setObjectName("card") # Uses QFrame#card from main.qss
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        # Title / Subtitle Layout
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        
        title_label = QLabel("SHARMA GENERAL STORE")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #0F172A; font-size: 17px; font-weight: bold; background: transparent;")
        
        subtitle = QLabel("Smart Billing System")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #64748B; font-size: 12px; background: transparent;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle)

        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumHeight(40)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)

        # Labels for inputs
        lbl_user = QLabel("USERNAME")
        lbl_user.setStyleSheet("color: #64748B; font-size: 10px; font-weight: bold; background: transparent;")
        
        lbl_pass = QLabel("PASSWORD")
        lbl_pass.setStyleSheet("color: #64748B; font-size: 10px; font-weight: bold; background: transparent;")

        # Error Label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #EF4444; font-size: 12px; background: transparent;")
        self.error_label.hide()

        # Login Button
        login_btn = QPushButton("LOGIN")
        login_btn.setObjectName("btn_primary")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.password_input.setFocus)

        help_text = QLabel("Trouble logging in? Contact Admin")
        help_text.setAlignment(Qt.AlignCenter)
        help_text.setStyleSheet("color: #94A3B8; font-size: 11px; background: transparent;")

        # Add to card layout
        card_layout.addLayout(title_layout)
        card_layout.addSpacing(10)
        card_layout.addWidget(lbl_user)
        card_layout.addWidget(self.username_input)
        card_layout.addSpacing(5)
        card_layout.addWidget(lbl_pass)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.error_label)
        card_layout.addStretch()
        card_layout.addWidget(login_btn)
        card_layout.addSpacing(10)
        card_layout.addWidget(help_text)

        main_layout.addWidget(card)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_error("Please enter both username and password.")
            return

        try:
            user = self.form.validate(username, password)
            self.error_label.hide()
            self.login_success.emit(user)
        except ValueError as e:
            self.show_error(str(e))

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
