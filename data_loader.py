import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

@st.cache_data(ttl=300)
def fetch_data():
    # 1. Pull secrets from Streamlit Cloud
    info = dict(st.secrets["gcp_service_account"])
    
    # 2. FIXED: Critical fix for 'InvalidPadding' or PEM load errors
    # This replaces literal '\n' characters with actual newlines that Google's library expects
    if "private_key" in info:
        info["private_key"] = info["private_key"].replace("\\n", "\n")

    # 3. Authorize via Service Account
    creds = Credentials.from_service_account_info(
        info, 
        scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
    )
    client = gspread.authorize(creds)
    
    # 4. Open the Spreadsheet by your specific ID
    ss = client.open_by_key('1R1nXJHnmsHQhisEDronG-DMo5tWeI3Ysh8TyQmKQ2fQ')
    
    # --- Process Worksheet: Sparta (df1) ---
    sheet1 = ss.worksheet('Sparta')
    df1 = pd.DataFrame(sheet1.get_all_records())
    
    # Data Cleaning for df1
    df1['Date_Parsed'] = pd.to_datetime(df1['Standardized_Date'], errors='coerce')
    # Standardize Advisor names for clean merging/filtering
    df1['Advisor'] = df1['Advisor'].astype(str).str.strip().str.title()
    
    # --- Process Worksheet: Sparta2 (df2) ---
    sheet2 = ss.worksheet('Sparta2')
    df2 = pd.DataFrame(sheet2.get_all_records())
    
    # Data Cleaning for df2
    # Using format='mixed' and dayfirst=True to handle UK date formats common in your telecom data
    df2['Date_Parsed'] = pd.to_datetime(df2['Sale Date'], dayfirst=True, errors='coerce')
    # Map 'Agent' column to 'Advisor' for consistency across the dashboard
    df2['Advisor'] = df2['Agent'].astype(str).str.strip().str.title()

    # --- Fetch Last Sync from Meta ---
    try:
        meta_sheet = ss.worksheet('Meta')
        meta_data = meta_sheet.get_all_values()
        # Assumes sync time is in the first row, second column (B1)
        last_sync = meta_data[0][1] if meta_data else "No sync data"
    except Exception:
        last_sync = "Sync data unavailable"
    
    return df1, df2, last_sync
