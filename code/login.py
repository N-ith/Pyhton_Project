import hashlib

class Login:
    def __init__(self, file_handler):
        self._file_handler = file_handler
      
    def login(self, username, password, ip_address):
        try:
            user_data = self._file_handler.get_user(username)
            if not user_data:
                return "Username is not in the database! Please sign up first!"
            
            stored_password = user_data["password"]
            hashed_input_password = hashlib.sha256(password.strip().encode()).hexdigest()
            if hashed_input_password != stored_password:
                return "Incorrect password."

            allowed_ips = user_data["ips"]
            if ip_address.strip() not in allowed_ips:
                return "new ip"

            return True
            
        except Exception as e:
            print(f"Error during login: {e}")
            return f"An error occurred during login. {e}"