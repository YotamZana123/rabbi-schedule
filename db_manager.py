import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import json

# מזהה הגיליון שהמשתמש יצר
SPREADSHEET_ID = "1Whu2RMVQgQzIEhx_WvFJ0bjue5O48ePxnMPdSK24130"

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

@st.cache_resource
def get_gspread_client():
    # קודם בודקים אם אנחנו רצים ב-Streamlit Cloud (מתוך st.secrets)
    if "gcp_service_account" in st.secrets:
        # במידה והמשתמש המיר את ה-JSON ל-TOML
        creds_dict = dict(st.secrets["gcp_service_account"])
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(credentials)
        
    if "gcp_json" in st.secrets:
        # במידה והמשתמש פשוט הדביק את ה-JSON כסטרינג
        creds_dict = json.loads(st.secrets["gcp_json"])
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(credentials)
    
    # אם אנחנו במחשב המקומי (כמו אצל יותם), קוראים מהקובץ
    if os.path.exists("credentials.json"):
        credentials = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        return gspread.authorize(credentials)
        
    raise Exception("No Google credentials found! Please add credentials.json or configure st.secrets")

def get_worksheet():
    client = get_gspread_client()
    sheet = client.open_by_key(SPREADSHEET_ID)
    return sheet.sheet1

@st.cache_data(ttl=10)
def get_all_assignments():
    try:
        worksheet = get_worksheet()
        return worksheet.get_all_records()
    except Exception as e:
        print(f"Error reading from Google Sheets: {e}")
        return []

def get_assignment(year, month, day):
    records = get_all_assignments()
    for row in records:
        if str(row.get('year')) == str(year) and str(row.get('month')) == str(month) and str(row.get('day')) == str(day):
            return {
                "friday_night": row.get('friday_night', ''),
                "shabbat_morning": row.get('shabbat_morning', ''),
                "seuda_shlishit": row.get('seuda_shlishit', '')
            }
    return None

def save_assignment(year, month, day, event_name, friday_night, shabbat_morning, seuda_shlishit):
    try:
        worksheet = get_worksheet()
        # משיכת נתונים ישירות מהגיליון כדי לא לדרוס בטעות משהו חדש
        records = worksheet.get_all_records()
        
        row_index = None
        for idx, row in enumerate(records):
            if str(row.get('year')) == str(year) and str(row.get('month')) == str(month) and str(row.get('day')) == str(day):
                row_index = idx + 2 # idx starts at 0, headers are row 1
                break
                
        update_values = [year, month, day, event_name, friday_night, shabbat_morning, seuda_shlishit]
        
        if row_index is not None:
            # עדכון שורה קיימת
            worksheet.update(range_name=f'A{row_index}', values=[update_values])
        else:
            # הוספת שורה חדשה
            worksheet.append_row(update_values)
            
        # ניקוי המטמון כדי שהעמוד יקרא נתונים חדשים
        get_all_assignments.clear()
        
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")
        st.error("שגיאה בשמירה למסד הנתונים בענן.")
