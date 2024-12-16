import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPalette, QIcon, QColor
import time
import hashlib

from file_handling import FileHandler
from gmail import OTPHandler
from register import Register
from login import Login

# --- Constants ---
ban_time_seconds = 15
login_attempts = 4
reset_timer_seconds = 40
max_username_length = 20
max_otp_attempt = 3

# --- Color Palette ---
primary_color = "#004aad"
secondary_color = "#5de0e6"
text_primary_color = "#354a67"
text_secondary_color = "#004aad"
white_color = "white"
black_color = "black"
form_background_color = "#f0f8ff"

# --- Font Settings ---
title_font_size = "35px"
section_font_size = "28px"
button_font_size = "15px"
normal_font_size = "14px"
bold_font_weight = "bold"
main_font_family = "'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif"

# --- Reusable Styles ---
button_style = f"""
    QPushButton {{
        border-radius: 20px;
        font-size: {button_font_size};
        font-weight: {bold_font_weight};
        border: none;
        color: {white_color};
        background-color: {primary_color};
        padding: 8px 12px;
        min-width: 100px;
        min-height: 30px;
        margin-bottom: 5px;
        margin-top: 5px;
    }}
    QPushButton:hover {{
        background-color: {secondary_color};
    }}
"""

input_style = f"""
    QLineEdit {{
        padding-left: 10px;
        border: {primary_color} solid 1px;
        margin-bottom: 10px;
        height: 40px;
        border-radius: 20px;
        background-color: {white_color};
        font-size: 16px;
    }}
"""

forgot_password_style = f"""
    QLabel {{
         color: {text_secondary_color};
         font-size: {normal_font_size};
         text-decoration: underline;
         margin-top: 10px;
    }}
    QLabel:hover {{
        color:{text_secondary_color};
    }}
"""

class AuthApp(QWidget):
    def __init__(self):
        super().__init__()

        self._file_handler = FileHandler()
        self._otp_handler = OTPHandler()
        self._register_handler = Register(self._file_handler)
        self._login_handler = Login(self._file_handler)

        self._signup_email = None
        self._signup_username = None
        self._otp_sent = False
        self._attempts = login_attempts
        self._ip_confirmation_pending = {}
        self._ban_time = None
        self._current_otp = None
        self._reset_timer_active = False
        self._remaining_time = reset_timer_seconds
        self._timer = None
        self._otp_requested_signup = False
        self._otp_requested_reset = False
        self._ip_verification_attempts = 3
        self._otp_verification_attempts = max_otp_attempt
        
        # Input storage
        self._username_text = ""
        self._password_text = ""
        self._reenter_password_text = ""
        self._email_text = ""
        self._otp_text = ""
        
        #Timer Widget storage
        self._timer_label = None
        self._send_otp_button = None

        self.initUI()
    
    # --- Setup UI ---
    def initUI(self):
        self.setWindowTitle('BEYDA Security')
        self.setGeometry(100, 100, 500, 750)  # Adjusted width and height
        self.setMinimumSize(450, 600)
        self.setbackground()
        self._main_layout = QVBoxLayout()
        self.loadlogo()
        self._title_label = QLabel("Login to Your Account", self)
        self._title_label.setAlignment(Qt.AlignCenter)
        self._title_label.setStyleSheet(f"font-size: {title_font_size}; font-weight: {bold_font_weight}; color: {text_primary_color}; margin-top: 20px; margin-bottom: 15px;")
        self._main_layout.addWidget(self._title_label)
        self._dynamic_content_layout = QVBoxLayout()
        self._main_layout.addLayout(self._dynamic_content_layout)
        self.setLayout(self._main_layout)
        self._username_input = None
        self._password_input = None
        self._reenter_password_input = None
        self._email_input = None
        self._otp_input = None
        self.setWindowIcon(QIcon("background.png"))
        self.show_login_view()

    def setbackground(self):
        try:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(240, 248, 255))
            self.setPalette(palette)
            self.setAutoFillBackground(False)
        except Exception as e:
            print(f"Error setting background: {e}")
            palette = self.palette()
            palette.setColor(QPalette.Window, Qt.white)
            self.setPalette(palette)
            self.setAutoFillBackground(False)

    def loadlogo(self):
         try:
            logo_path = './picture/logo.png'
            pixmap_logo = QPixmap(logo_path)
            scaled_pixmap_logo = pixmap_logo.scaled(200, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._logo_label = QLabel(self)
            self._logo_label.setPixmap(scaled_pixmap_logo)
            self._logo_label.setAlignment(Qt.AlignCenter)
            self._logo_label.setStyleSheet("padding-bottom: 15px;")
            self._main_layout.insertWidget(0, self._logo_label)
            self._main_layout.setSpacing(1)

            background_path = './picture/background.png'
            pixmap_background = QPixmap(background_path)
            background_width = 400
            background_height = 250
            scaled_pixmap_background = pixmap_background.scaled(background_width, background_height,
                                                                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._background_label = QLabel(self)
            self._background_label.setPixmap(scaled_pixmap_background)
            self._background_label.setAlignment(Qt.AlignCenter)
            self._main_layout.insertWidget(self._main_layout.count(), self._background_label)
            self._background_label.lower()

         except Exception as e:
            print(f"Error Loading Logo : {e}")

    # --- View Functions ---
    def show_login_view(self):
        self.clear_dynamic_content()
        self._title_label.setText("Login to Your Account")
        self._title_label.setStyleSheet(f"font-size: {section_font_size}; font-weight: {bold_font_weight}; color: {text_secondary_color}; margin-bottom: 10px; margin-top:10px;")
        
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_container.setStyleSheet(f"background-color: {form_background_color}; border-radius: 20px; padding-left: 40px; padding-right: 40px; margin-bottom: 5px; width: 350px; height:180px")

        self._username_input = QLineEdit(self)
        self._username_input.setPlaceholderText("Enter username")
        form_layout.addWidget(self._username_input)
        self._username_input.setStyleSheet(input_style)

        self._password_input = QLineEdit(self)
        self._password_input.setPlaceholderText("Enter Password")
        self._password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self._password_input)
        self._password_input.setStyleSheet(input_style)

        self._dynamic_content_layout.addWidget(form_container, alignment=Qt.AlignCenter)

        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_container.setStyleSheet("margin-top:5px;")

        self._login_button = QPushButton('Login', self)
        self._login_button.clicked.connect(self.verify_user)
        button_layout.addWidget(self._login_button)
        self._login_button.setStyleSheet(button_style)

        self._forgot_password_label = QLabel('<a href="#">Forgot password?</a>', self)
        self._forgot_password_label.setAlignment(Qt.AlignCenter)
        self._forgot_password_label.setStyleSheet(forgot_password_style)
        self._forgot_password_label.linkActivated.connect(self.show_reset_password_view_1)
        button_layout.addWidget(self._forgot_password_label)
        
        self._create_account_button = QPushButton('Create New Account', self)
        self._create_account_button.clicked.connect(self.show_signup_view_1)
        button_layout.addWidget(self._create_account_button)
        self._create_account_button.setStyleSheet(button_style)

        self._dynamic_content_layout.addWidget(button_container, alignment=Qt.AlignCenter)

    def reset_attempts(self):
        self._attempts = login_attempts
        self._ban_time = None

    def verify_user(self):
        username = self._username_input.text().strip()
        password = self._password_input.text().strip()
        ip_address = self._file_handler.get_ip_address()

        if not username or not password:
            self.show_message('Error', 'Please enter both username and password.')
            return
        
        if self._ban_time and time.time() < self._ban_time:
            remaining_time = int(self._ban_time - time.time())
            self.show_message('Error', f"You are banned! Please try again after {remaining_time} seconds.")
            return
        elif self._ban_time and time.time() >= self._ban_time:
           self._attempts = login_attempts
           self._ban_time = None
        
        if self._attempts == 0:
            self.show_message('Error', "Too many incorrect attempts! You are banned for 15 seconds.")
            self._ban_time = time.time() + ban_time_seconds
            return

        try:
           result = self._login_handler.login(username, password, ip_address)
           if result == True:
               self.show_homepage(username)
               self._attempts = login_attempts
           elif result == "Incorrect password.":
                self._attempts -= 1
                if self._attempts == 0:
                    self.show_message('Error', "Too many incorrect attempts! You are banned for 15 seconds.")
                else:
                    self.show_message('Error', f"Incorrect password. You have {self._attempts} attempt(s) left.")
           elif result == "new ip":
                   user_email = self._file_handler.get_user_email(username)
                   if user_email:
                       confirmation_code = self._otp_handler.generate_confirmation_code()
                       self._ip_confirmation_pending[username] = confirmation_code
                       if self._otp_handler.send_ip_confirmation_email(user_email, username, ip_address, confirmation_code):
                           self.show_message('Confirm New IP', 'A confirmation email has been sent to your email to confirm new IP')
                           self.show_ip_confirmation_view(username)
                           return
                       else:
                           self.show_message("Error", "Failed to send IP Confirmation email")
                           return
                   else:
                       self.show_message("Error", "Could not get user email")
                       return
           else:
                self.show_message('Error', result)

        except Exception as e:
            self.show_message('Error', f'An error occurred during login: {e}')
    
    def show_confirmation_dialog(self, username):
       pass

    def show_ip_confirmation_view(self, username):
        self.clear_dynamic_content()
        self._title_label.setText("Confirm New IP Address")
        self._title_label.setStyleSheet(f"font-size: {section_font_size}; font-weight: {bold_font_weight}; color: {text_secondary_color}; margin-bottom: 10px; margin-top:10px;")

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_container.setStyleSheet(f"background-color: {form_background_color}; border-radius: 20px; padding-left: 40px; padding-right: 40px; margin-bottom: 5px; width: 350px; height: 180px")

        code_input = QLineEdit(self)
        code_input.setPlaceholderText("Enter confirmation code")
        form_layout.addWidget(code_input)
        code_input.setStyleSheet(input_style)

        self._dynamic_content_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_container.setStyleSheet("margin-top:5px;")

        confirm_button = QPushButton("Confirm", self)
        confirm_button.setStyleSheet(button_style)
        confirm_button.clicked.connect(lambda: self.confirm_ip_address_action(username, code_input.text().strip()))
        button_layout.addWidget(confirm_button)

        self._go_back_button = QPushButton('Back to Login', self)
        self._go_back_button.clicked.connect(self.show_login_view)
        button_layout.addWidget(self._go_back_button)
        self._go_back_button.setStyleSheet(button_style)
        
        self._dynamic_content_layout.addWidget(button_container, alignment=Qt.AlignCenter)
    
    def confirm_ip_address_action(self, username, confirmation_code):
        """Confirms the new IP address based on the confirmation code"""
        if self.confirm_ip_address(username, confirmation_code):
            self._ip_verification_attempts = max_otp_attempt
            self.show_homepage(username)
        else:
             self._ip_verification_attempts -= 1
             if self._ip_verification_attempts <= 0 :
                  self.show_message("Error", "Too many attempts. Redirecting to Login page.")
                  self._ip_verification_attempts = max_otp_attempt
                  self.show_login_view()
                  return
             else:
                 self.show_message("Error", f"Invalid or expired confirmation code. You have {self._ip_verification_attempts} attempt(s) left")
    
    def confirm_ip_address(self, username, confirmation_code):
        if username in self._ip_confirmation_pending and self._otp_handler.verify_confirmation_code(self._ip_confirmation_pending[username],confirmation_code):
            ip_address = self._file_handler.get_ip_address()
            self._file_handler.add_ip_address(username, ip_address)
            del self._ip_confirmation_pending[username]
            self.show_message("Success", "IP has been added.")
            return True
        else:
            return False

    def show_signup_view_1(self):
        self.clear_dynamic_content()
        self._title_label.setText("Create New Account")
        self._title_label.setStyleSheet(f"font-size: {section_font_size}; font-weight: {bold_font_weight}; color: {text_secondary_color}; margin-bottom: 10px; margin-top:10px;")
          
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_container.setStyleSheet(f"background-color: {form_background_color}; border-radius: 20px; padding-left: 40px; padding-right: 40px; margin-bottom: 5px; width: 350px; height: 180px")

        self._username_input = QLineEdit(self)
        self._username_input.setPlaceholderText("Enter username")
        form_layout.addWidget(self._username_input)
        self._username_input.setStyleSheet(input_style)

        self._email_input = QLineEdit(self)
        self._email_input.setPlaceholderText("Enter Gmail")
        form_layout.addWidget(self._email_input)
        self._email_input.setStyleSheet(input_style)

        self._dynamic_content_layout.addWidget(form_container, alignment=Qt.AlignCenter)

        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_container.setStyleSheet("margin-top:5px;")

        self._next_button = QPushButton('Next', self)
        self._next_button.clicked.connect(self.next_to_signup2)
        button_layout.addWidget(self._next_button)
        self._next_button.setStyleSheet(button_style)

        self._back_to_login_button = QPushButton('Back to Login', self)
        self._back_to_login_button.clicked.connect(self.show_login_view)
        button_layout.addWidget(self._back_to_login_button)
        self._back_to_login_button.setStyleSheet(button_style)
        
        self._dynamic_content_layout.addWidget(button_container, alignment=Qt.AlignCenter)

    def next_to_signup2(self):
        if self._username_input and self._email_input:
             self._username_text = self._username_input.text().strip()
             self._email_text = self._email_input.text().strip()
        else:
            self.show_message("Error", "Could not get input values")
            return


        username_error = self._register_handler._check_username(self._username_text)
        if username_error:
            self.show_message("Error", username_error)
            return
        if len(self._username_text) > max_username_length:
                self.show_message("Error", f"Username must be less than {max_username_length} characters.")
                return

        email_error = self._register_handler._check_email(self._email_text)
        if email_error != True:
            self.show_message("Error", email_error)
            return

        self._signup_username = self._username_text
        self._signup_email = self._email_text
        self.show_signup_view_2()

    def show_signup_view_2(self):
        self.clear_dynamic_content()
        self._title_label.setText("Create New Account")
        self._title_label.setStyleSheet(f"font-size: {section_font_size}; font-weight: {bold_font_weight}; color: {text_secondary_color}; margin-bottom: 10px; margin-top:10px;")
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_container.setStyleSheet(f"background-color: {form_background_color}; border-radius: 20px; padding-left: 40px; padding-right: 40px; margin-bottom: 5px; width: 350px; height: 180px")

        self._otp_input = QLineEdit(self)
        self._otp_input.setPlaceholderText("Enter Verification Code")
        form_layout.addWidget(self._otp_input)
        self._otp_input.setStyleSheet(input_style)
        
        timer_label = QLabel(f"<a href='#'>Haven't gotten verification code?</a> {self._remaining_time}s", self)
        timer_label.setAlignment(Qt.AlignLeft)
        timer_label.setStyleSheet(forgot_password_style)
        timer_label.linkActivated.connect(lambda: self.resend_otp_for_signup_handler(timer_label, send_otp_button))
        form_layout.addWidget(timer_label)

        self._dynamic_content_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_container.setStyleSheet("margin-top:5px;")
        
        send_otp_button = QPushButton('Get New Verification Code', self)
        send_otp_button.clicked.connect(lambda: self.send_otp_for_signup(timer_label, send_otp_button))
        button_layout.addWidget(send_otp_button)
        send_otp_button.setStyleSheet(button_style)

        self._next_button = QPushButton('Next', self)
        self._next_button.clicked.connect(self.next_to_signup3_handler)
        button_layout.addWidget(self._next_button)
        self._next_button.setStyleSheet(button_style)

        self._back_to_login_button = QPushButton('Back to Login', self)
        self._back_to_login_button.clicked.connect(self.show_login_view)
        button_layout.addWidget(self._back_to_login_button)
        self._back_to_login_button.setStyleSheet(button_style)        
      
        self._dynamic_content_layout.addWidget(button_container, alignment=Qt.AlignCenter)

    def next_to_signup3_handler(self):
        if self._otp_input:
             self._otp_text = self._otp_input.text().strip()
        else:
             self.show_message("Error", "Could not get OTP input")
             return
         
        if not self._otp_sent:
            self.show_message('Error', 'Please send a verification code first.')
            return

        if not self._otp_text:
            self.show_message('Error', 'Please enter the verification code.')
            return
         
        if self._otp_verification_attempts <= 0 :
             self.show_message("Error", "Too many attempts. Redirecting to Login page.")
             self._otp_verification_attempts = max_otp_attempt
             self.show_login_view()
             return
        elif self._otp_text != self._current_otp:
              self._otp_verification_attempts -=1
              self.show_message('Error', f'Invalid OTP. Please try again. {self._otp_verification_attempts} attempt(s) left')
              return

        self.show_signup_view_3()

    def show_signup_view_3(self):
        self.clear_dynamic_content()
        self._title_label.setText("Create New Account")
        self._title_label.setStyleSheet(f"font-size: {section_font_size}; font-weight: {bold_font_weight}; color: {text_secondary_color}; margin-bottom: 10px; margin-top:10px;")
        
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_container.setStyleSheet(f"background-color: {form_background_color}; border-radius: 20px; padding-left: 40px; padding-right: 40px; margin-bottom: 5px; width: 350px; height: 180px")

        # Password input
        self._password_input = QLineEdit(self)
        self._password_input.setPlaceholderText("Enter password")
        self._password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self._password_input)
        self._password_input.setStyleSheet(input_style)

        # Re-enter password input
        self._reenter_password_input = QLineEdit(self)
        self._reenter_password_input.setPlaceholderText("Re-enter password")
        self._reenter_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self._reenter_password_input)
        self._reenter_password_input.setStyleSheet(input_style)

        self._dynamic_content_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_container.setStyleSheet("margin-top:5px;")

        # Sign-up button
        self._signup_button = QPushButton('Finish', self)
        self._signup_button.clicked.connect(self.sign_up)
        button_layout.addWidget(self._signup_button)
        self._signup_button.setStyleSheet(button_style)

        # Back to first step button
        self._back_to_login_button = QPushButton('Back to Login', self)
        self._back_to_login_button.clicked.connect(self.show_login_view)
        button_layout.addWidget(self._back_to_login_button)
        self._back_to_login_button.setStyleSheet(button_style)

        self._dynamic_content_layout.addWidget(button_container, alignment=Qt.AlignCenter)
    
    def send_otp_for_signup(self, timer_label, send_otp_button):
         email = self._signup_email
         self._send_otp(email, "signup", timer_label = timer_label, send_otp_button = send_otp_button)
         self._otp_requested_signup = True
    
    def resend_otp_for_signup_handler(self, timer_label, send_otp_button):
        if self._otp_requested_signup:
            self.resend_otp_for_signup(timer_label, send_otp_button)
        else:
            self.show_message("Error", "Click get verification code first.")

    def resend_otp_for_signup(self, timer_label, send_otp_button):
        email = self._signup_email
        self._send_otp(email, "resend", "signup", timer_label = timer_label, send_otp_button = send_otp_button)

    def _send_otp(self, email, action, view=None, timer_label=None, send_otp_button=None):
        if not email:
            self.show_message('Error', 'Please enter a valid email address.')
            return

        if "@gmail.com" not in email:
            self.show_message('Error', 'Please use a valid Gmail address.')
            return

        if self._otp_sent and action == "signup":
            self.show_message('Error', 'Verification code has already been sent. Please check your inbox and enter the OTP to proceed.')
            return
        
        if action == "resend":
            self._otp_sent = False

        otp_sent, generated_otp = self._otp_handler.send_verification_email(email)
        if otp_sent:
            self._otp_sent = True
            self._current_otp = generated_otp
            self.show_message('Verification Code Sent', 'A verification code has been sent to your gmail. Please check your inbox.')
            if view == "signup":
                 self.start_timer("signup", timer_label, send_otp_button)
            else:
               self.start_timer(timer_label=timer_label, send_otp_button=send_otp_button)
        else:
            self.show_message('Error', 'Failed to send verification code. Please check your email address and try again.')

    def sign_up(self):
        username = self._signup_username
        password = self._password_input.text().strip()
        reentered_password = self._reenter_password_input.text().strip()
        entered_otp = self._otp_text # Changed from self._otp_input.text().strip()

        if password != reentered_password:
            self.show_message('Error', 'Passwords do not match. Please try again.')
            return
        
        password_error = self._register_handler._check_password(password)
        if password_error:
             self.show_message("Error", password_error)
             return

        if not self._otp_sent:
            self.show_message('Error', 'Please send a verification code first.')
            return

        if not entered_otp:
            self.show_message('Error', 'Please enter the verification code.')
            return

        if entered_otp != self._current_otp:
            self.show_message('Error', 'Invalid verification code. Please try again.')
            return

        ip_address = self._file_handler.get_ip_address()
        try:
            register_result = self._register_handler.register(username, password, ip_address, self._signup_email)
            if register_result != True:
                self.show_message("Error", register_result)
                return
        except Exception as e:
            self.show_message("Error", f"Registration Error : {e}")
            return
        self.show_homepage(username)

    def show_reset_password_view_1(self):
        """Switch to forgot password view - Step 1."""
        self.clear_dynamic_content()
        self._title_label.setText("Reset Password")
        self._title_label.setStyleSheet(f"font-size: {section_font_size}; font-weight: {bold_font_weight}; color: {text_secondary_color}; margin-top: 10px; margin-bottom: 10px;")

        # Form Container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_container.setStyleSheet(f"background-color: {form_background_color}; border-radius: 20px; padding-left: 40px; padding-right: 40px; margin-bottom: 5px; width: 350px;")

        self._username_input = QLineEdit(self)
        self._username_input.setPlaceholderText("Enter username")
        form_layout.addWidget(self._username_input)
        self._username_input.setStyleSheet(input_style)
        
        self._otp_input = QLineEdit(self)
        self._otp_input.setPlaceholderText("Enter verification code")
        form_layout.addWidget(self._otp_input)
        self._otp_input.setStyleSheet(input_style)

        self._dynamic_content_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        
        button_container = QWidget() 
        button_layout = QVBoxLayout(button_container)  

        timer_label = QLabel(f"<a href='#'>Haven't gotten verification code?</a> {self._remaining_time}s", self)
        timer_label.setAlignment(Qt.AlignLeft)
        timer_label.setStyleSheet(forgot_password_style)
        timer_label.linkActivated.connect(self.resend_otp_handler)
        button_layout.addWidget(timer_label)
        
        send_otp_button = QPushButton('Get Verification Code', self)
        send_otp_button.clicked.connect(self.send_otp)
        button_layout.addWidget(send_otp_button)
        send_otp_button.setStyleSheet(button_style)

        self._next_button = QPushButton('Next', self)
        self._next_button.clicked.connect(self.show_reset_password_view_2_handler)
        button_layout.addWidget(self._next_button)
        self._next_button.setStyleSheet(button_style)

        self._go_back_button = QPushButton('Back to Login', self)
        self._go_back_button.clicked.connect(self.show_login_view)
        button_layout.addWidget(self._go_back_button)
        self._go_back_button.setStyleSheet(button_style)
        
        self._dynamic_content_layout.addWidget(button_container, alignment=Qt.AlignCenter)

    def show_reset_password_view_2_handler(self):
        if self._username_input and self._otp_input:
            self._username_text = self._username_input.text().strip()
            self._otp_text = self._otp_input.text().strip()
        else:
            self.show_message("Error", "Could not get input values")
            return
        if not self._otp_sent:
            self.show_message('Error', 'Please request OTP first.')
            return

        if not self._otp_text:
            self.show_message('Error', 'Please enter the OTP.')
            return
        
        if self._otp_verification_attempts <= 0 :
            self.show_message("Error", "Too many attempts. Redirecting to Login page.")
            self._otp_verification_attempts = max_otp_attempt
            self.show_login_view()
            return

        elif self._otp_text != self._current_otp:
            self._otp_verification_attempts -=1
            self.show_message('Error', f'Invalid OTP. Please try again. {self._otp_verification_attempts} attempt(s) left')
            return
        self.show_reset_password_view_2()
    def show_reset_password_view_2(self):
        self.clear_dynamic_content()
        self._title_label.setText("Reset Password")
        self._title_label.setStyleSheet(f"font-size: {section_font_size}; font-weight: {bold_font_weight}; color: {text_secondary_color}; margin-bottom: 10px; margin-top:10px;")
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_container.setStyleSheet(f"background-color: {form_background_color}; border-radius: 20px; padding-left: 40px; padding-right: 40px; margin-bottom: 5px; width: 350px; height: 180px")

        self._password_input = QLineEdit(self)
        self._password_input.setPlaceholderText("New Password")
        self._password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self._password_input)
        self._password_input.setStyleSheet(input_style)

        self._reenter_password_input = QLineEdit(self)
        self._reenter_password_input.setPlaceholderText("Re-enter New Password")
        self._reenter_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self._reenter_password_input)
        self._reenter_password_input.setStyleSheet(input_style)

        self._dynamic_content_layout.addWidget(form_container, alignment=Qt.AlignCenter)

        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_container.setStyleSheet("margin-top:5px;")

        self._reset_password_button = QPushButton('Finish', self)
        self._reset_password_button.clicked.connect(self.reset_password)
        button_layout.addWidget(self._reset_password_button)
        self._reset_password_button.setStyleSheet(button_style)

        self._go_back_button = QPushButton('Back to Login', self)
        self._go_back_button.clicked.connect(self.show_login_view)
        button_layout.addWidget(self._go_back_button)
        self._go_back_button.setStyleSheet(button_style)
        
        self._dynamic_content_layout.addWidget(button_container, alignment=Qt.AlignCenter)

    def show_homepage(self, username):
        """Show the homepage after successful login, registration, or password reset."""
        self.clear_dynamic_content()
        self._title_label.setText(f"Hello, {username}!") # modified to say hello
        self._title_label.setStyleSheet(f"font-size: {title_font_size}; font-weight: {bold_font_weight}; color: {text_primary_color}; margin-top: 10px; margin-bottom: 10px;")

        homepage_label = QLabel(f"You have successfully secured your account!", self)
        homepage_label.setAlignment(Qt.AlignCenter)
        homepage_label.setStyleSheet(f"font-size: 16px; color: {text_secondary_color}; margin-top: 20px; margin-bottom: 10px")
        self._dynamic_content_layout.addWidget(homepage_label)
        
        slogan_label = QLabel("SLOGAN: BETTER SECURITY with BEYDA SECURITY", self)
        slogan_label.setAlignment(Qt.AlignCenter)
        slogan_label.setStyleSheet(f"font-size: 14px; color: {text_secondary_color}; margin-top: 10px; margin-bottom: 10px")
        self._dynamic_content_layout.addWidget(slogan_label)

        visit_us_label = QLabel('<a href="https://github.com/N-ith/Project_Proposal">Visit us on:  github.com/N-ith/Project_Proposal</a>', self)
        visit_us_label.setAlignment(Qt.AlignCenter)
        visit_us_label.setStyleSheet(f"font-size: {normal_font_size}; color: {text_secondary_color}; margin-top: 10px; margin-bottom: 10px; text-decoration: underline;")
        visit_us_label.setOpenExternalLinks(True)
        self._dynamic_content_layout.addWidget(visit_us_label)
        
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_container.setStyleSheet("margin-top:5px;")

        self._finish_button = QPushButton('Finish', self)
        self._finish_button.clicked.connect(self.show_login_view)
        button_layout.addWidget(self._finish_button)
        self._finish_button.setStyleSheet(button_style + """
            QPushButton {
                margin-top: 20px;
            }
        """)
        self._dynamic_content_layout.addWidget(button_container, alignment=Qt.AlignCenter)

    def start_timer(self, view = None, timer_label = None, send_otp_button = None):
            """Starts the countdown timer."""
            self._remaining_time = reset_timer_seconds  # Reset the remaining time
            if view == "signup":
                timer_label.setText(f"<a href='#'>Haven't gotten verification code? Please wait for {self._remaining_time}s</a>")
            else:
                timer_label.setText(f"<a href='#'>Haven't gotten verification code? Please wait for {self._remaining_time}s</a>")
            
            if send_otp_button:
               send_otp_button.setEnabled(False)
            if timer_label:
               timer_label.setEnabled(False)
            
            self._reset_timer_active = True # Timer is active
            self._timer = QTimer()
            self._timer.timeout.connect(lambda: self.update_timer(timer_label, send_otp_button))
            self._timer.start(1000)  # Update every second

    def update_timer(self, timer_label, send_otp_button):
        """Updates the countdown timer and the button."""
        if self._remaining_time > 0:
            self._remaining_time -= 1
            if timer_label:  # Check if the label exists
               try:
                    if "signup" in str(timer_label.text()):
                        timer_label.setText(f"<a href='#'>Haven't gotten verification code? Please wait for {self._remaining_time}s</a>")
                    else:
                        timer_label.setText(f"<a href='#'>Haven't gotten verification code? Please wait for {self._remaining_time}s</a>")
               except RuntimeError:
                   self.stop_timer(timer_label, send_otp_button)
        else:
            self.stop_timer(timer_label, send_otp_button)

    def stop_timer(self, timer_label, send_otp_button):
            """Stops the timer."""
            if self._timer:
                self._timer.stop()
                self._timer = None
            self._reset_timer_active = False
            if send_otp_button:
                send_otp_button.setText("Get Verification Code")
                send_otp_button.setEnabled(True)
            if timer_label:
               timer_label.setEnabled(True)
            #enable send button
            if timer_label:
                 if "signup" in str(timer_label.text()):
                    timer_label.setText("<a href='#'>Haven't gotten verification code?</a> Resend verification code now")
                 else:
                   timer_label.setText("<a href='#'>Haven't gotten verification code?</a> Resend verification code now") # Resend Now
            
    def resend_otp(self, timer_label, send_otp_button):
        """Resend OTP for reset email verification, resetting otp_sent."""
        username = self._username_input.text().strip()
        if username:
           email = self._file_handler.get_user_email(username)
           if email:
                 self._send_otp(email, "resend", timer_label=timer_label, send_otp_button=send_otp_button)
           else:
                self.show_message("Error", "Could not get user email")
        else:
            self.show_message("Error", "Please provide a username")
    
    def resend_otp_handler(self):
        """Handles the resend OTP request when the user clicks the 'resend' link."""
        if self._otp_requested_reset:
           # Attempt to find the timer_label and send_otp_button in the current view
            timer_label = None
            send_otp_button = None

            # Iterate through the layout to find widgets by type
            for i in range(self._dynamic_content_layout.count()):
                item = self._dynamic_content_layout.itemAt(i)
                if item and item.widget():
                  widget = item.widget()
                  if isinstance(widget, QWidget):
                      for j in range(widget.layout().count()):
                          item2 = widget.layout().itemAt(j)
                          if item2 and item2.widget():
                              widget2 = item2.widget()
                              if isinstance(widget2, QLabel) and "<a href='#'>" in widget2.text():
                                timer_label = widget2
                              if isinstance(widget2, QPushButton) and widget2.text() == "Get Verification Code":
                                send_otp_button = widget2

            if timer_label and send_otp_button:
               self.resend_otp(timer_label, send_otp_button)
            else:
               self.show_message("Error", "Could not find verification elements")
        else:
            self.show_message("Error", "Click verification code first.")

    def send_otp(self):
        """Send OTP to the user's email."""
        if self._reset_timer_active:
            self.show_message('Error',
                             'Please wait before sending another verification code.')
            return

        username = self._username_input.text().strip()
        if username:
           email = self._file_handler.get_user_email(username)
           if email:
               otp_sent, generated_otp = self._otp_handler.send_verification_email(email)
               if otp_sent:
                   self._otp_sent = True
                   self._current_otp = generated_otp
                   self.show_message('OTP Sent', f'Verification code has been sent to your email. Please check your inbox.')
                   timer_label = self._dynamic_content_layout.itemAt(1).widget().layout().itemAt(0).widget()
                   send_otp_button = self._dynamic_content_layout.itemAt(1).widget().layout().itemAt(1).widget()
                   self.start_timer(timer_label=timer_label, send_otp_button=send_otp_button)
                   self._otp_requested_reset = True
               else:
                    self.show_message('Error', 'Failed to send verification code. Please try again later.')

           else:
                self.show_message('Error', 'No user found with that username.')
        else:
            self.show_message('Error', 'Please provide username.')

    def reset_password(self):
        """Reset the user's password."""
        new_password = self._password_input.text().strip()
        reentered_password = self._reenter_password_input.text().strip()

        if new_password != reentered_password:
            self.show_message('Error', 'Passwords do not match. Please try again.')
            return
        
        password_error = self._register_handler._check_password(new_password)
        if password_error:
            self.show_message("Error", password_error)
            return

        username = self._username_text

        if not new_password:
            self.show_message('Error', 'Please enter a new password.')
            return
        try:
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            self._file_handler.update_password(username, hashed_new_password)
            self.show_message('Success', 'Password has been reset successfully.')
            self.show_homepage(username)
        except Exception as e:
            self.show_message('Error', f"Reset password error : {e}")
    
    def clear_dynamic_content(self):
       """Clears the dynamic content layout."""
       self.stop_timer(self._timer_label, self._send_otp_button) # stop the timer
       while self._dynamic_content_layout.count():
          item = self._dynamic_content_layout.takeAt(0)
          widget = item.widget()
          if widget:
              widget.deleteLater()
       self._otp_input = None
       self._username_input = None
       self._password_input = None
       self._reenter_password_input = None
       self._email_input = None
       self._timer_label = None
       self._send_otp_button = None
    
    
    def confirm_ip_address(self, username, confirmation_code):
        """Confirms the new IP address based on the confirmation code"""
        if username in self._ip_confirmation_pending and self._otp_handler.verify_confirmation_code(self._ip_confirmation_pending[username],confirmation_code):
            ip_address = self._file_handler.get_ip_address()
            self._file_handler.add_ip_address(username, ip_address)
            del self._ip_confirmation_pending[username]
            self.show_message("Success", "IP has been added.")
            return True
        else:
             return False

    def show_message(self, title, message):
        """Show a message box."""
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    auth_app = AuthApp()
    auth_app.show()
    sys.exit(app.exec_())