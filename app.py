import streamlit as st
import pandas as pd


# 1. Page Configuration
st.set_page_config(
    page_title="Live Google Sheet Dashboard",
    page_icon="🔄",
    layout="wide"
)


# 2. Fix for Dark Mode text visibility
st.markdown("""
    <style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #2e7bcf;
    }
    .stMetric label, .stMetric [data-testid="stMetricValue"] {
        color: #1f1f1f !important; 
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 🛑 UPDATE THESE TWO VARIABLES 🛑
# ==========================================
# Paste your specific Google Sheet ID here
SHEET_ID = "https://docs.google.com/spreadsheets/d/1RczkaAj-y4RuQPFOC_lZAbWKK7nA4vmcQJmdhCQkb2E/edit?gid=834679604#gid=834679604"


# Type the exact names of the tabs at the bottom of your Google Sheet
TAB_NAMES = ["Dashboard", "Master Project List", "Critical Projects"] 
# ==========================================


# 3. Live Google Sheet Loader
# ttl=600 clears the cache and pulls fresh data every 10 minutes
@st.cache_data(ttl=600)
def load_google_sheet(sheet_id, sheet_name):
    # This URL forces Google Sheets to export the specific tab as a readable CSV format
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    # Read the live URL directly into pandas
    return pd.read_csv(url)


# 4. Sidebar Navigation
st.sidebar.header("📁 Navigation")
selected_tab = st.sidebar.selectbox("Select a Sheet to View", TAB_NAMES)


# 5. Dashboard Display
st.title(f"🔄 Live Analysis: {selected_tab}")
st.markdown("This dashboard pulls live data directly from Google Sheets.")
st.divider()


try:
    # Load the data for the selected tab
    df = load_google_sheet(SHEET_ID, selected_tab)
    
    # Top Level KPI Metrics
    c1, c2 = st.columns(2)
    c1.metric(f"Rows in {selected_tab}", f"{len(df):,}")
    c2.metric("Total Columns", f"{len(df.columns):,}")


    st.divider()


    # Data View
    st.subheader("Live Data Preview")
    st.dataframe(df, use_container_width=True)
    
except Exception as e:
    st.error("⚠️ Could not load data. Please ensure the Google Sheet is shared as 'Anyone with the link can view' and that your Sheet ID and Tab Names are typed exactly correctly.")
    st.write(f"Technical Error Details: {e}")
