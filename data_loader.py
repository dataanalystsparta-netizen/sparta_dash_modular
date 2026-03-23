import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

@st.cache_data(ttl=300)
def fetch_data():
    # 1. Pull secrets from Streamlit Cloud
    # Convert to dict to allow modification of the key string
    info = dict(st.secrets["gcp_service_account"])
    
    # 2. ROBUST PRIVATE KEY CLEANUP
    # This handles triple-quotes, literal \n strings, and stray spaces
    if "private_key" in info:
        # Step A: Remove any accidental wrapping quotes if pasted with them
        cleaned_key = info["private_key"].strip()
        if (cleaned_key.startswith('"') and cleaned_key.endswith('"')) or \
           (cleaned_key.startswith("'") and cleaned_key.endswith("'")):
            cleaned_key = cleaned_key[1:-1]
        
        # Step B: Replace literal '\n' text with actual newline characters
        # This is the most common cause of 'Invalid private key'
        cleaned_key = cleaned_key.replace("\\n", "\n")
        
        # Step C: Re-strip to ensure no leading/trailing whitespace remains
        info["private_key"] = cleaned_key.strip()

    # 3. Authorize via Service Account
    try:
        creds = Credentials.from_service_account_info(
            info, 
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        client = gspread.authorize(creds)
    except Exception as e:
        st.error(f"Authentication Error: {e}")
        st.stop()
    
    # 4. Open the Spreadsheet by your specific ID
    try:
        ss = client.open_by_key('1R1nXJHnmsHQhisEDronG-DMo5tWeI3Ysh8TyQmKQ2fQ')
    except Exception as e:
        st.error(f"Sheet Access Error: Ensure sheet is shared with {info.get('client_email')}")
        st.stop()
    
    # --- Process Worksheet: Sparta (df1) ---
    sheet1 = ss.worksheet('Sparta')
    df1 = pd.DataFrame(sheet1.get_all_records())
    
    # Data Cleaning for df1
    df1['Date_Parsed'] = pd.to_datetime(df1['Standardized_Date'], errors='coerce')
    df1['Advisor'] = df1['Advisor'].astype(str).str.strip().str.title()
    
    # --- Process Worksheet: Sparta2 (df2) ---
    sheet2 = ss.worksheet('Sparta2')
    df2 = pd.DataFrame(sheet2.get_all_records())
    
    # Data Cleaning for df2
    df2['Date_Parsed'] = pd.to_datetime(df2['Sale Date'], dayfirst=True, errors='coerce')
    df2['Advisor'] = df2['Agent'].astype(str).str.strip().str.title()

    # --- Fetch Last Sync from Meta ---
    try:
        meta_sheet = ss.worksheet('Meta')
        meta_data = meta_sheet.get_all_values()
        # Assumes sync time is in cell B1
        last_sync = meta_data[0][1] if meta_data else "No sync data"
    except Exception:
        last_sync = "Sync data unavailable"
    
    return df1, df2, last_sync
