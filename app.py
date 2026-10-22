import streamlit as st
import pandas as pd
import urllib.parse
import plotly.express as px


# 1. Page Configuration
st.set_page_config(
    page_title="Projects Update Dashboard",
    page_icon="📊",
    layout="wide"
)


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
# DASHBOARD CONFIGURATION
# ==========================================
SHEET_ID = "1RczkaAj-y4RuQPFOC_lZAbWKK7nA4vmcQJmdhCQkb2E"


# Map each tab to the number of rows to SKIP before hitting the actual column headers.
# If headers are on Row 4, skip 3. If headers are on Row 1, skip 0.
TAB_CONFIG = {
    "Master Project List": 3, 
    "Financial Summary": 0,   # Update this to the correct number for this tab
    "Critical Projects": 0,   # Update this
    "Anupam": 3, 
    "Bigan": 3, 
    "Mufti": 3, 
    "Sashesh": 3, 
    "Kavita": 3, 
    "Pramod": 3
}
# ==========================================


# 2. Live Google Sheet Loader (Now accepts dynamic skiprows)
@st.cache_data(ttl=600)
def load_google_sheet(sheet_id, sheet_name, rows_to_skip):
    encoded_sheet_name = urllib.parse.quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    
    # Read the data using the specific skiprows value for this tab
    df = pd.read_csv(url, skiprows=rows_to_skip)
    
    # Clean up empty columns and rows
    df = df.dropna(how='all', axis=1)
    df = df.dropna(how='all', axis=0)
    
    return df


# 3. Sidebar Navigation
st.sidebar.header("📁 Navigation")
# Extract just the tab names from our dictionary for the dropdown menu
available_tabs = list(TAB_CONFIG.keys())
selected_tab = st.sidebar.selectbox("Select a Sheet to View", available_tabs)


st.title(f"📊 Live Analysis: {selected_tab}")
st.divider()


try:
    with st.spinner('Pulling live data from Google Sheets...'):
        # Look up the correct skiprows value for the selected tab
        skip_count = TAB_CONFIG[selected_tab]
        df = load_google_sheet(SHEET_ID, selected_tab, skip_count)
    
    # 4. Top Level KPI Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Total Records in {selected_tab}", f"{len(df):,}")
    
    if 'Total Project Cost' in df.columns:
        df['Clean Cost'] = df['Total Project Cost'].astype(str).str.replace(r'[₹, ]', '', regex=True)
        df['Clean Cost'] = pd.to_numeric(df['Clean Cost'], errors='coerce').fillna(0)
        total_cost = df['Clean Cost'].sum()
        c2.metric("Total Project Cost", f"₹ {total_cost:,.0f}")
        
    if 'State' in df.columns:
        c3.metric("States Covered", f"{df['State'].nunique()}")


    st.divider()
    
    # 5. Visualizations
    if 'State' in df.columns and not df.empty:
        st.subheader(f"Projects by State")
        state_counts = df['State'].value_counts().reset_index()
        state_counts.columns = ['State', 'Count']
        fig = px.bar(state_counts, x='State', y='Count', template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)


    # 6. Data View
    st.subheader("Live Data Preview")
    st.dataframe(df, use_container_width=True)
    
except Exception as e:
    st.error("⚠️ Could not load data. Check the TAB_CONFIG numbers or sharing settings.")
    st.write(f"Technical Error Details: {e}")
