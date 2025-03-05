# drive_service.py
import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import utils  # שינוי מ-from .utils ל-import utils
import config  # שינוי מ-from .config ל-import config

def get_drive_service():
    creds = None
    
    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)
    
    if not creds or not creds.valid:
        st.warning("📢 יש לאשר הרשאות גישה ל-Google Drive:")
        flow = InstalledAppFlow.from_client_secrets_file(config.CREDENTIALS_FILE, config.SCOPES)
        free_port = utils.find_free_port()
        creds = flow.run_local_server(port=free_port)
        
        with open(config.TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        st.success("🎯 ההרשאות התקבלו בהצלחה! המשך בתהליך העיבוד.")
    
    if creds:
        return build('drive', 'v3', credentials=creds)
    else:
        st.stop()

def create_unique_daily_folder(service, parent_folder_id, base_folder_name):
    query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    response = service.files().list(q=query, fields="files(id, name)").execute()
    existing_folders = [f['name'] for f in response.get('files', [])]
    
    folder_name = base_folder_name
    counter = 1
    while folder_name in existing_folders:
        folder_name = f"{base_folder_name}_{counter}"
        counter += 1
    
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')
