# config.py
import os

BASE_DIR = "/Applications/My Apps/Python Streamlit PPC all Accounts 5.3.25"
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
ACCOUNTS = ["US Main", "US Second", "UK", "ED", "ES", "IT", "FR"]
FOLDER_ID = "1YXMDkhVBxe0iU9sc_TSCiZDVr-FkexUt"
