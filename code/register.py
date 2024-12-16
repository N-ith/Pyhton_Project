import hashlib

class Register:
    def __init__(self, file_handler):
        self._file_handler = file_handler

    def _check_username(self, username):
        """Check if the username is valid and does not contain spaces, and has the right character."""
        if not username:
            return "Username cannot be empty."
        if len(username) < 4:
            return "Username must be at least 4 characters long."
        if ' ' in username:
            return "Username cannot contain spaces."
       
        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"
        for char in username:
            if char not in allowed_chars:
                return "Username cannot contain special characters."

        existing_usernames = self._file_handler.get_all_usernames()
        if username in existing_usernames:
            return f"Username {username} is already taken."
        return None

    def _check_email(self, email):
        """Check the email format and verify it."""
        if not email:
            return "Email cannot be empty."

        if "@" not in email or "." not in email:
            return "Invalid email format."

        parts = email.split("@")
        if len(parts) != 2 or not parts[1]:
            return "Invalid email format."
            
        domain_parts = parts[1].split(".")
        if len(domain_parts) < 2 or not all(domain_parts):
            return "Invalid email format."

        all_user_emails = [self._file_handler.get_user_email(username) for username in self._file_handler.get_all_usernames()]
        if all_user_emails.count(email) >= 5:
            return f"{email} has already reached the maximum registration limit."

        return True

    def _check_password(self, password):
        """Validate password strength."""
        if not password:
            return "Password cannot be empty."
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        if not any(c.isupper() for c in password):
            return "Password must contain at least one uppercase letter."
        if not any(c.islower() for c in password):
            return "Password must contain at least one lowercase letter."
        if not any(c.isdigit() for c in password):
            return "Password must contain at least one digit."
        if not any(c in "!@#$%^&*()" for c in password):
            return "Password must contain at least one special character (!@#$%^&*())."

        return None

    def register(self, username, password, ip_address, email):
        username_error = self._check_username(username)
        if username_error:
            return username_error

        email_error = self._check_email(email)
        if email_error != True:
            return email_error
        
        password_error = self._check_password(password)
        if password_error:
            return password_error

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
             self._file_handler.add_user(username, hashed_password, ip_address, email)
             # Invalidate the username cache after adding a new user
             self._file_handler._usernames_cache = None
             self._file_handler._cache_time = None
        except Exception as e:
            return f"Failed to register user: {e}"

        return True