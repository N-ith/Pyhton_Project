import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import re
import time

class FileHandler:
    def __init__(self):
        """Initialize connection to the fixed user database."""
        self._json_key_path = "./data/database_key.json"
        self._scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        self._credentials = ServiceAccountCredentials.from_json_keyfile_name(self._json_key_path, self._scope)
        self._client = gspread.authorize(self._credentials)
        self._sheet_name = 'Centralized_Authentication_System'

        # Connect to the specified spreadsheet and worksheet
        self._spreadsheet = self._client.open(self._sheet_name)
        self._worksheet = self._spreadsheet.get_worksheet(0)
        
        self._usernames_cache = None
        self._cache_time = None
        self._cache_duration = 60 # in seconds


    def get_user(self, username):
        try:
            user_cell = self._worksheet.find(username.strip())
            if user_cell:
                user_row = user_cell.row
                username = self._worksheet.cell(user_row, 1).value.strip()  # Username is in the 1st column
                password = self._worksheet.cell(user_row, 2).value.strip()  # Password is in the 2nd column
                ip_list = self._worksheet.cell(user_row, 3).value.strip()  # IPs are in the 3rd column
                email = self._worksheet.cell(user_row, 4).value.strip()  # Email is in the 4th column
                return {
                   "username": username,
                   "password": password,
                   "ips": ip_list.split(",") if ip_list else [],
                   "email" : email
                }

            else:
                return None
        except Exception as e:
            print(f"Error fetching user {username}: {e}")
            raise Exception(f"Error fetching user : {e}")
    def get_user_email(self, username):
        """Retrieve the email address associated with a given username."""
        try:
            user_cell = self._worksheet.find(username.strip())
            if user_cell:
                user_row = user_cell.row
                return self._worksheet.cell(user_row, 4).value.strip()  # Email is in the 4th column
            else:
                return None  # If username is not found, return None
        except Exception as e:
            print(f"Error fetching email for {username}: {e}")
            raise Exception(f"Error fetching user email: {e}")


    def get_user_ip_list(self, username):
        """Retrieve the list of allowed IP addresses for a given username."""
        try:
            user_data = self.get_user(username)
            if user_data:
                return user_data["ips"]
            else:
                return None
        except Exception as e:
             print(f"Error fetching IP addresses for {username}: {e}")
             raise Exception(f"Error getting IP list for user : {e}")

    def add_ip_address(self, username, new_ip):
        """Add a new IP address to the user's allowed IP list."""
        try:
           user_data = self.get_user(username)
           if user_data:
                ip_list = user_data["ips"]
                user_cell = self._worksheet.find(username.strip())
                if new_ip.strip() not in ip_list:
                    ip_list.append(new_ip.strip())
                    updated_ips = ",".join(ip_list)  # Convert list back to comma-separated string
                    self._worksheet.update_cell(user_cell.row, 3, updated_ips)  # Update the IP column
                    return True
                else:
                    print(f"IP address {new_ip} already exists in the list for {username}.")
                    return False
           else:
               return False
        except Exception as e:
            print(f"Error adding IP address for {username}: {e}")
            raise Exception(f"Error adding IP address : {e}")

    def get_all_usernames(self):
        """Retrieve a list of all usernames from the spreadsheet."""
        if self._usernames_cache and self._cache_time and time.time() - self._cache_time < self._cache_duration:
           return self._usernames_cache
        try:
            usernames = self._worksheet.col_values(1)  # Get all values from the 1st column (Username)
            self._usernames_cache =  [username.strip() for username in usernames if username.strip()]  # Clean and return
            self._cache_time = time.time()
            return self._usernames_cache
        except Exception as e:
             print(f"Error fetching usernames: {e}")
             raise Exception(f"Error fetching all user names: {e}")

    def add_user(self, username, password, ip_address, email):
         """Add a new user with the given details (username, password, IP address, email)."""
         try:
            self._worksheet.append_row([username.strip(), password.strip(), ip_address.strip(), email.strip()])
         except Exception as e:
             print(f"Error adding user: {e}")
             raise Exception(f"Error adding user : {e}")

    def update_password(self, username, new_password):
        """Reset the user's password."""
        try:
            user_cell = self._worksheet.find(username.strip())
            if user_cell:
                 self._worksheet.update_cell(user_cell.row, 2, new_password.strip())  # Update password
                 return True
            else:
                 return False

        except Exception as e:
             print(f"Error resetting password: {e}")
             raise Exception(f"Error resetting password : {e}")

    def get_ip_address(self):
        """Retrieve the user's IP address."""
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            response.raise_for_status()
            return response.json().get("ip", "Unknown")
        except Exception as e:
            print(f"Error fetching IP address: {e}")
            return None