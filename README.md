# BEYDA Security - Centralized Authentication System

## Project Overview

This project is a PyQt5-based centralized authentication system designed to provide a secure and user-friendly interface for user registration, login, password reset, and IP address management. The system uses a Google Sheets database for persistent storage of user information, including usernames, hashed passwords, allowed IP addresses, and email addresses.

Key features include:

*   **Secure User Authentication:** Implements password hashing using SHA256 for secure password storage.
*   **IP Address Verification:** Restricts logins to recognized IP addresses and requires email confirmation for new IP logins.
*   **Email-Based OTP:** Employs One-Time Passcodes (OTPs) sent via email for signup and password reset processes.
*   **Account Management:** Provides functionality for creating new accounts, logging in with existing credentials, and resetting forgotten passwords.
*   **Brute-Force Protection:** Includes a rate-limiting and temporary ban feature to protect against brute-force login attempts.
*   **User-Friendly UI:** Utilizes a consistent and visually appealing user interface with PyQt5.
*   **Reusable Code:** Code is organized into separate modules, with reusable functions and styles.


## Dependencies or Installation Instructions

Before running the code, you need to install the required Python packages. You can install them using pip (Packet installer for Python):

1.  Python: This project requires Python 3.6 or higher. Ensure you have it installed.

2.  Install the following packages:

    
    pip install PyQt5
    pip install gspread
    pip install google-auth-oauthlib google-auth-httplib2
    pip install requests
    

    * PyQt5: Used for building the graphical user interface (index.py).
    * gspread: Used to interact with the Google Sheets API (test.py).
    * google-auth-oauthlib, google-auth-httplib2: Necessary for Google Sheets API authentication (test.py).
    * requests: Used to get the user's IP address (test.py).


3.  Standard Python Modules (Included with Python):


    * hashlib: Used for password hashing in login.py, register.py.
    * smtplib: Used for sending emails in email_test.py.
    * random: Used for generating random codes/numbers in email_test.py, index.py.
    * time: Used for time-related operations such as implementing ban times or timers in index.py.
    * sys: Used for sys-related functions, particularly sys.exit() in index.py.

## GitHub Link 

[GitHub Link](https://github.com/N-ith/Project_Proposal)

## Additional Notes

*   Ensure that you have proper internet connectivity, as this application uses a Google Sheet and external API for IP retrieval.
*   Be sure to keep the gmail password.txt and database key.json files secure, as they contain sensitive information.

## Steps to Run the Code

1.  **Clone the repository:** (If applicable, you will want to provide the link to your repo here if this is hosted on github, but the below instruction can work also if u are running it locally.)

    git clone [https://github.com/N-ith/Project_Proposal]
    cd [...]
    
 or Download the project file and open it with the relevant IDE.

2.  Install dependencies: See the "Dependencies or Installation Instructions" section for details on required packages.

3.  Configure Google Sheets API:
    *   Create a Google Cloud Platform project.
    *   Enable the Google Sheets API.
    *   Create a service account and download the JSON key file.
    *   Share your Google Sheet with the service account's email.
    *   Place your JSON key file in the same directory as the test.py file and name it database key.json.
    *   Create your Google Sheet and name it Centralized_Authentication_System.

4.  Set up Email Configuration (using App Password):

*   Generate an App Password:
    *   Go to your Google Account settings.
    *   Navigate to "Security".
    *   Under "How you sign in to Google", click "2-Step Verification" (it must be enabled).
    *   Click "App passwords".
    *   Select "Mail" and "Other (custom name)".
    *   Enter a name, for example, "BEYDA Security App", then click "Generate."
    *   Copy the generated app password.
*   Store App Password:
    *   Create a file named gmail password.txt in the same directory as your email_test.py file.
    *   Paste the app password (not your regular Gmail password) into this file.
    *   Important: Do not share your app password file.

5.  Run the main application:

    
    python index.py
    

    This will launch the authentication application GUI.



 you have any questions or feedback, feel free to reach out!🙏

