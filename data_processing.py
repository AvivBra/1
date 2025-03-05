# data_processing.py
import pandas as pd
from io import BytesIO
from googleapiclient.http import MediaIoBaseUpload
import streamlit as st

def process_data(ppc_file, data_file, drive_service, daily_folder_id, account, today_str):
    ppc_df = pd.read_excel(ppc_file, engine='openpyxl')
    df = pd.read_excel(data_file, sheet_name='Sponsored Products Campaigns', engine='openpyxl')

    df = df.fillna("")

    text_columns = ['Entity', 'Portfolio Name (Informational only)', 'State', 
                    'Campaign State (Informational only)', 'Campaign Name (Informational only)']
    df[text_columns] = df[text_columns].astype(str)

    for column in df.columns:
        if column not in text_columns:
            df[column] = pd.to_numeric(df[column], errors='coerce')

    df = df[
        (df['Entity'].isin(['Product Targeting', 'Keyword'])) &
        (df['Portfolio Name (Informational only)'].str.contains('Never', case=False, na=False)) &
        (df['State'].str.lower() == 'enabled') &
        (df['Campaign State (Informational only)'].str.lower() == 'enabled')
    ]

    column_1, column_2 = ppc_df.columns[:2]
    df['Bid'] = df['Portfolio Name (Informational only)'].map(ppc_df.set_index(column_1)[column_2])
    return df, ppc_df

def save_files_to_drive(df_before, df, ppc_df, ppc_file, drive_service, daily_folder_id, account, today_str):
    # יצירת קובץ Before
    before_file_name = f"{account}_{today_str}_before.xlsx"
    before_output = BytesIO()
    with pd.ExcelWriter(before_output, engine='openpyxl') as writer:
        df_before.to_excel(writer, sheet_name='Before Processing', index=False)  # שימוש ב-df_before במקום df
        ppc_df.to_excel(writer, sheet_name='PPC Data', index=False)
    before_output.seek(0)

    st.write(f"📤 מעלה את הקובץ {before_file_name} ל-Google Drive...")
    before_file_metadata = {'name': before_file_name, 'parents': [daily_folder_id]}
    before_media = MediaIoBaseUpload(before_output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    drive_service.files().create(body=before_file_metadata, media_body=before_media, fields='id').execute()
    st.write(f"✅ קובץ {before_file_name} נשמר בהצלחה ב-Drive.")

    # יצירת קובץ After
    after_file_name = f"{account}_{today_str}_after.xlsx"
    after_output = BytesIO()
    with pd.ExcelWriter(after_output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='After Processing', index=False)
    after_output.seek(0)

    st.write(f"📤 מעלה את הקובץ {after_file_name} ל-Google Drive...")
    after_file_metadata = {'name': after_file_name, 'parents': [daily_folder_id]}
    after_media = MediaIoBaseUpload(after_output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    drive_service.files().create(body=after_file_metadata, media_body=after_media, fields='id').execute()
    st.write(f"✅ קובץ {after_file_name} נשמר בהצלחה ב-Drive.")

    # העלאת קובץ PPC המקורי
    ppc_file_name = f"{account}_{today_str}_ppc.xlsx"
    ppc_output = BytesIO(ppc_file.read())
    st.write(f"📤 מעלה את הקובץ {ppc_file_name} ל-Google Drive...")
    ppc_file_metadata = {'name': ppc_file_name, 'parents': [daily_folder_id]}
    ppc_media = MediaIoBaseUpload(ppc_output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    drive_service.files().create(body=ppc_file_metadata, media_body=ppc_media, fields='id').execute()
    st.write(f"✅ קובץ {ppc_file_name} נשמר בהצלחה ב-Drive.")

    return before_output, after_file_name, after_output, ppc_file_name
