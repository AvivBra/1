import streamlit as st
import data_processing
import drive_service
import config
import pandas as pd
from datetime import datetime
from io import BytesIO

def run_interface():
    st.title("🔧 עיבוד נתונים עבור כל חשבונות ה-PPC")
    selected_accounts = st.multiselect("בחר חשבונות PPC לעיבוד:", config.ACCOUNTS)

    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}
    if 'retry_accounts' not in st.session_state:
        st.session_state.retry_accounts = {}

    for account in selected_accounts:
        st.header(f"📂 העלאת קבצים עבור חשבון {account}")
        ppc_file = st.file_uploader(f"📂 העלה קובץ PPC עבור {account}", type=["xlsx"], key=f"ppc_{account}")
        data_file = st.file_uploader(f"📂 העלה קובץ נתונים עבור {account}", type=["xlsx"], key=f"data_{account}")
        if ppc_file and data_file:
            st.session_state.uploaded_files[account] = {'ppc': ppc_file, 'data': data_file}
            st.write(f"📂 קובץ PPC נטען: {ppc_file.name}")
            st.write(f"📂 קובץ נתונים נטען: {data_file.name}")

    st.write("🧠 מצב האפליקציה - uploaded_files:", st.session_state.get('uploaded_files', {}))

    if st.button("🔄 עיבוד כל הקבצים שנבחרו"):
        if not st.session_state.uploaded_files:
            st.error("❌ יש להעלות קבצים לכל חשבון שנבחר.")
        else:
            with st.spinner("⏳ מעבד את כל הקבצים..."):
                today_str = datetime.today().strftime('%Y-%m-%d')
                drive_service_instance = drive_service.get_drive_service()
                daily_folder_id = drive_service.create_unique_daily_folder(drive_service_instance, config.FOLDER_ID, today_str)

                accounts_to_process = st.session_state.uploaded_files.copy()
                for account, files in accounts_to_process.items():
                    try:
                        ppc_df = pd.read_excel(files['ppc'], engine='openpyxl')
                        df = pd.read_excel(files['data'], sheet_name='Sponsored Products Campaigns', engine='openpyxl')

                        st.write("📋 פורטפוליוז מקובץ ה-PPC:", ppc_df.iloc[:, 0].unique())
                        st.write("📋 פורטפוליוז מקובץ הנתונים המסונן:", df['Portfolio Name (Informational only)'].unique())

                    except Exception as e:
                        st.error(f"🚫 שגיאה בעיבוד הקבצים של {account}: {e}")
                        if st.button(f"📂 העלה מחדש קבצים עבור {account}", key=f"retry_{account}"):
                            st.session_state.uploaded_files.pop(account, None)

                st.success("✅ כל הקבצים עובדו ונשמרו בהצלחה (או ממתינים לתיקון).")
