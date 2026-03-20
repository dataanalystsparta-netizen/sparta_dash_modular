import streamlit as st
import pandas as pd
import datetime

# --- Import our custom modules ---
from config import CSS_STYLE, LIVE_AGENTS
from data_loader import fetch_data
from utils import map_quality, map_portal, calculate_standardized_revenue

# Placeholder imports for tabs (we will build these next)
# from tabs.tab_1_team import render_team_tab
# from tabs.tab_2_agent import render_agent_tab
# from tabs.tab_3_finance import render_finance_tab

# --- CONFIG & STYLING ---
st.set_page_config(page_title="Sparta Master Dashboard", layout="wide")
st.markdown(CSS_STYLE, unsafe_allow_html=True)

try:
    # 1. Fetch Data
    df1, df2, last_sync = fetch_data()

    # 2. Header UI
    col_title, col_time = st.columns([3, 1])
    with col_title:
        st.image("https://raw.githubusercontent.com/dataanalystsparta-netizen/logos/refs/heads/main/sparta-lite.30f2063887def24833df3d0d5ac6c503.png", width=280)
        st.title("Sparta Performance & Live Status Dashboard")
    col_time.markdown(f"<p class='last-updated'>Data Last Synced:<br><b>{last_sync}</b></p>", unsafe_allow_html=True)

    # 3. Global Filters
    col_a, col_b, col_c = st.columns([1, 1, 1.5])
    start_date = col_a.date_input("Start Date", datetime.date.today().replace(day=1))
    end_date = col_b.date_input("End Date", datetime.date.today())

    # 4. Global Data Processing (Filter based on dates)
    f1 = df1[(df1['Date_Parsed'].dt.date >= start_date) & (df1['Date_Parsed'].dt.date <= end_date)].copy()
    f2 = df2[(df2['Date_Parsed'].dt.date >= start_date) & (df2['Date_Parsed'].dt.date <= end_date)].copy()

    f1['Q_Status'] = f1['Quality Status'].apply(map_quality)
    f2['P_Status'] = f2['Status'].apply(map_portal)
    
    f1['Standardized_Rev'] = f1['Packageoffered'].apply(calculate_standardized_revenue) if 'Packageoffered' in f1.columns else 0.0
    f2['Standardized_Rev'] = f2['PlanTariff'].apply(calculate_standardized_revenue) if 'PlanTariff' in f2.columns else 0.0

    all_advisors = sorted(list(set(f1['Advisor'].unique()) | set(f2['Advisor'].unique())))
    formatted_live = [name.strip().title() for name in LIVE_AGENTS]

    # --- TABS ROUTING ---
    tab1, tab2, tab3 = st.tabs(["📊 Team Overview", "👤 Individual Performance", "💰 Financials"])

    with tab1:
        st.write("Team Tab placeholder")
        # render_team_tab(f1, f2, all_advisors, formatted_live, start_date, end_date)

    with tab2:
        st.write("Agent Tab placeholder")
        # render_agent_tab(f1, f2, all_advisors, formatted_live)

    with tab3:
        st.write("Finance Tab placeholder")
        # render_finance_tab(f2, formatted_live)

except Exception as e:
    st.error(f"Error: {e}")
