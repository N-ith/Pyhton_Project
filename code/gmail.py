import smtplib
import random

class OTPHandler:
    def __init__(self):
        self._verification_code = None
        self._email_sender = 'keosovannmonyneath@gmail.com'  # Replace with your email
        self._email_password = self._read_password_from_file("./data/gmail password.txt")

    def _read_password_from_file(self, password_file):
      """Read the password from the file and return it."""
      try:
          with open(password_file, "r") as file:
            return file.read().strip()
      except FileNotFoundError:
          print(f"Error: Password file '{password_file}' not found.")
          return None  # Return None if file is not found
      except Exception as e:
          print(f"Error reading password file: {e}")
          return None  # Return False if there was another error

    def _generate_otp(self):
        """Generate a 7-digit OTP."""
        verification_code = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        print(f"Generated OTP: {verification_code}")  # Debugging line
        return verification_code
    
    def send_ip_confirmation_email(self, receiver_email, username, ip_address, confirmation_code):
        """Send an email to the user to confirm a new IP address."""
        
        
        subject = "New Login Attempt from Unrecognized IP"

        body = f"""
        Hello {username},

        A login attempt from a new IP address has been detected for your account:

        IP Address: {ip_address}

        If you recognize this activity, please confirm the IP address:
        Confirmation Code: {confirmation_code}

        If this wasn't you, please ignore this email.

        Regards,
        Your Authentication System
        """
        content = f"Subject: {subject}\n\n{body}"
         # Set up the SMTP server
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)  # For Gmail
            server.starttls()  # Start TLS encryption
            server.login(self._email_sender, self._email_password)
            server.sendmail(self._email_sender, receiver_email, content)
            print("Confirmation email sent successfully!")
            return True  # Return True if email was sent successfully
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False  # Return False if there was an error
        finally:
             if server:
                 server.quit()


    
    def generate_confirmation_code(self):
        """Generate a random confirmation code."""
        return str(random.randint(100000, 999999))
    
    def verify_confirmation_code(self, expected_code, input_code):
          """Verify if the confirmation code entered matches the generated one."""
          return str(expected_code) == str(input_code)

    def send_verification_email(self, receiver_email):
        """Send the OTP to the user's email and return a success flag and generated otp."""
        verification_code = self._generate_otp()

        # Email content
        subject = "Security Alert!!!"
        message = f"Your verification code is: {verification_code}"
        content = f"Subject: {subject}\n\n{message}"

        # Set up the SMTP server
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)  # For Gmail
            server.starttls()  # Start TLS encryption
            server.login(self._email_sender, self._email_password)
            server.sendmail(self._email_sender, receiver_email, content)
            print("Verification email sent successfully!")
            return True, verification_code  # Return True and the OTP
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False, None  # Return False and None if there was an error
        finally:
            if server:
                 server.quit()


    def verify_otp(self, entered_otp):
        """Verify the entered OTP against the generated one."""
        if self._verification_code == entered_otp:
            return True
        return False