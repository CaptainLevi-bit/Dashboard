import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="Professional Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for a cleaner, professional look
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .st-eb {
        font-family: 'Arial', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Data Loading with Caching (Improves performance drastically)
@st.cache_data
def load_data():
    # Load the specific Excel file
    df = pd.read_excel("FCF_GAP_Baseline_Dataset_Clean.xlsx")
    
    # Optional: Do any standard data cleaning here (e.g., date conversions)
    # df['Date'] = pd.to_datetime(df['Date']) 
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ File 'FCF_GAP_Baseline_Dataset_Clean.xlsx' not found. Please ensure it is in the same folder as app.py.")
    st.stop()

# 4. Sidebar filters
st.sidebar.header("🔍 Dashboard Filters")

# Example Filter 1 (Update 'CategoryColumn' with a real column name from your dataset)
# category_options = df['CategoryColumn'].unique().tolist()
# selected_categories = st.sidebar.multiselect("Select Category", category_options, default=category_options)

# Example Filter 2
# selected_status = st.sidebar.selectbox("Select Status", ["All"] + df['StatusColumn'].unique().tolist())

# Apply filters (Uncomment and modify based on your real columns)
# filtered_df = df[df['CategoryColumn'].isin(selected_categories)]
# if selected_status != "All":
#     filtered_df = filtered_df[filtered_df['StatusColumn'] == selected_status]

# Fallback: using raw df if filters aren't customized yet
filtered_df = df 

# 5. Dashboard Header
st.title("📊 FCF GAP Baseline Overview")
st.markdown("Interactive dashboard analyzing the clean baseline dataset. Use the sidebar to filter data.")
st.divider()

# 6. Top Level KPI Metrics
col1, col2, col3, col4 = st.columns(4)

# Update these calculations based on your actual data
total_records = len(filtered_df)
# example_sum = filtered_df['Revenue'].sum()
# example_avg = filtered_df['Score'].mean()

col1.metric("Total Records", f"{total_records:,}")
col2.metric("Key Metric 2", "Update Me", delta="5%")
col3.metric("Key Metric 3", "Update Me", delta="-2%")
col4.metric("Key Metric 4", "Update Me")

st.divider()

# 7. Interactive Visualizations
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Distribution Overview")
    st.info("💡 To activate this chart, replace 'X_Column' and 'Y_Column' with real names from your Excel file.")
    # Example Bar Chart
    # fig_bar = px.bar(
    #     filtered_df, 
    #     x="X_Column", 
    #     y="Y_Column", 
    #     color="CategoryColumn",
    #     title="Bar Chart Overview",
    #     template="plotly_white"
    # )
    # st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    st.subheader("Proportion Breakdown")
    # Example Pie Chart
    # fig_pie = px.pie(
    #     filtered_df, 
    #     names="CategoryColumn", 
    #     values="NumericColumn", 
    #     title="Pie Chart Breakdown",
    #     hole=0.4 # Makes it a donut chart
    # )
    # st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# 8. Detailed Data View
st.subheader("📄 Detailed Data View")
# Data editor allows you to sort, search, and view the raw data beautifully
st.dataframe(filtered_df, use_container_width=True, height=400)
