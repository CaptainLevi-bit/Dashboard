import streamlit as st
import pandas as pd
import urllib.parse
import plotly.express as px
import plotly.graph_objects as go


# 1. Page Configuration
st.set_page_config(
    page_title="Master Project Tracking Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# 2. Executive Dashboard CSS (Menu is now unhidden)
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #0052cc;
    }
    div[data-testid="metric-container"] > label, 
    div[data-testid="metric-container"] > div {
        color: #1f1f1f !important;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# SINGLE TAB CONFIGURATION
# ==========================================
SHEET_ID = "1RczkaAj-y4RuQPFOC_lZAbWKK7nA4vmcQJmdhCQkb2E"
TARGET_TAB = "Master Project List"
# ==========================================


# 3. Auto-Detecting Data Loader (Bulletproof)
@st.cache_data(ttl=600)
def load_master_data(sheet_id, sheet_name):
    encoded_sheet_name = urllib.parse.quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    
    # Read the raw sheet WITHOUT skipping rows
    df_raw = pd.read_csv(url, header=None)
    
    # Automatically scan the first 10 rows to find the true header row
    header_idx = 0
    for i, row in df_raw.head(10).iterrows():
        row_text = ' '.join(row.astype(str).str.lower())
        if 'entity' in row_text or 'cost' in row_text:
            header_idx = i
            break
            
    # Set the columns to the detected header row and keep the data below it
    df = df_raw.iloc[header_idx + 1:].reset_index(drop=True)
    df.columns = df_raw.iloc[header_idx]
    
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
    
    # Clean the column names to be perfectly uniform
    df.columns = df.columns.astype(str).str.replace(r'[^a-zA-Z0-9 ]', ' ', regex=True).str.replace(r'\s+', ' ', regex=True).str.strip().str.lower()
    
    # Filter out total rows
    if len(df.columns) > 0 and len(df) > 0:
        df = df[~df[df.columns[0]].astype(str).str.contains("total", case=False, na=False)]
    
    # Convert financial text to numbers
    financial_keywords = ['cost', 'grant', 'contribution', 'loan', 'disbursed', 'amount']
    for col in df.columns:
        if any(keyword in col for keyword in financial_keywords):
            df[col] = df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df


st.title("🎯 Master Project Portfolio")
st.markdown("Live operational and financial evaluation metrics for all active enterprise entities.")
st.divider()


try:
    with st.spinner('Fetching live operational data...'):
        df = load_master_data(SHEET_ID, TARGET_TAB)
    
    # Search uses the guaranteed cleaned lowercase strings
    entity_col = next((c for c in df.columns if 'entity' in c or 'name' in c), None)
    cost_col = next((c for c in df.columns if 'total project cost' in c), None)
    disbursed_col = next((c for c in df.columns if 'disbursed' in c), None)
    value_chain_col = next((c for c in df.columns if 'value chain' in c), None)
    
    # 4. Top Level Operational KPIs
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric("Active Entities", f"{len(df):,}")
    
    if value_chain_col:
        c2.metric("Distinct Value Chains", f"{df[value_chain_col].nunique():,}")
    
    if cost_col and disbursed_col:
        total_portfolio = df[cost_col].sum()
        total_disbursed = df[disbursed_col].sum()
        disbursement_rate = (total_disbursed / total_portfolio * 100) if total_portfolio > 0 else 0
        
        c3.metric("Total Portfolio Value", f"₹ {total_portfolio:,.0f}")
        c4.metric("Total Funds Disbursed", f"₹ {total_disbursed:,.0f}", f"{disbursement_rate:.1f}% Execution Rate")


    st.write("") 


    # 5. Interactive Visualizations
    chart_col1, chart_col2 = st.columns([6, 4])
    
    with chart_col1:
        st.subheader("Financial Tranche Status by Entity")
        if entity_col and cost_col and disbursed_col:
            chart_df = df.groupby(entity_col)[[cost_col, disbursed_col]].sum().reset_index()
            chart_df = chart_df.sort_values(by=cost_col, ascending=True).tail(12) 
            
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                y=chart_df[entity_col].str.title(), x=chart_df[cost_col], 
                name='Approved Cost', orientation='h', marker_color='#0052cc'
            ))
            fig_bar.add_trace(go.Bar(
                y=chart_df[entity_col].str.title(), x=chart_df[disbursed_col], 
                name='Disbursed Amount', orientation='h', marker_color='#36b37e'
            ))
            
            fig_bar.update_layout(barmode='group', template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Awaiting structural financial columns to render execution progress.")


    with chart_col2:
        st.subheader("Value Chain Distribution")
        if value_chain_col and cost_col:
            pie_df = df.groupby(value_chain_col)[cost_col].sum().reset_index()
            
            fig_pie = px.pie(pie_df, values=cost_col, names=value_chain_col, hole=0.4, template='plotly_white', color_discrete_sequence=px.colors.qualitative.Prism)
            fig_pie.update_traces(textposition='inside', textinfo='percent')
            fig_pie.update_layout(margin=dict(l=0, r=0, t=30, b=0), showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Awaiting value chain categorization columns.")


    with st.expander("🔍 View Raw Monitoring Data & Column Names"):
        st.write("**Processed Column Headers:**", list(df.columns))
        st.dataframe(df, use_container_width=True)
    
except Exception as e:
    st.error("⚠️ Connection interrupted or data structure altered.")
    st.write(f"Diagnostic Output: {e}")
