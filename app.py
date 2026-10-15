import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="FCF GAP Baseline Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for analytical metric cards
st.markdown("""
    <style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #2e7bcf;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 3. Data Loading and Cleaning
@st.cache_data
def load_data():
    df = pd.read_excel("FCF_GAP_Baseline_Dataset_Clean.xlsx")
    
    # Clean specific numeric columns
    num_cols = ['Total Land Cultivated (acres)', 'Area under Horticulture (acres)', 'Age (years)']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # Clean text columns for filtering
    df['District'] = df['District'].fillna('Unknown')
    df['Gender'] = df['Gender'].fillna('Unknown')
    if 'Social Category' in df.columns:
        df['Social Category'] = df['Social Category'].fillna('Unknown')
        
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ File 'FCF_GAP_Baseline_Dataset_Clean.xlsx' not found. Ensure it is in the same folder as app.py.")
    st.stop()

# 4. Sidebar filters
st.sidebar.header("📊 Analytical Filters")

# Dynamic Filters based on dataset
districts = st.sidebar.multiselect("Select District", sorted(df['District'].unique()), default=sorted(df['District'].unique()))
genders = st.sidebar.multiselect("Select Gender", sorted(df['Gender'].unique()), default=sorted(df['Gender'].unique()))

if 'Social Category' in df.columns:
    categories = st.sidebar.multiselect("Social Category", sorted(df['Social Category'].unique()), default=sorted(df['Social Category'].unique()))
else:
    categories = []

# Apply filters
if categories:
    filtered_df = df[
        (df['District'].isin(districts)) & 
        (df['Gender'].isin(genders)) &
        (df['Social Category'].isin(categories))
    ]
else:
    filtered_df = df[(df['District'].isin(districts)) & (df['Gender'].isin(genders))]

# 5. Dashboard Header
st.title("📈 FCF GAP Baseline Analytical Dashboard")
st.markdown("Deep-dive analysis into farmer demographics, agricultural capacities, and commercial readiness.")

# 6. Top Level KPI Metrics
c1, c2, c3, c4 = st.columns(4)

total_farmers = len(filtered_df)
total_land = filtered_df['Total Land Cultivated (acres)'].sum()
total_hort = filtered_df['Area under Horticulture (acres)'].sum()
avg_age = filtered_df['Age (years)'].mean() if 'Age (years)' in filtered_df.columns else 0

c1.metric("Farmers Analyzed", f"{total_farmers:,}")
c2.metric("Total Cultivated Area", f"{total_land:,.1f} Acres")
c3.metric("Total Horticulture Area", f"{total_hort:,.1f} Acres")
c4.metric("Avg Farmer Age", f"{avg_age:,.1f} Years")

st.divider()

# 7. Interactive Analytical Tabs
tab1, tab2, tab3 = st.tabs(["👥 Demographics & Land", "🌾 Crop & Production", "🤝 Market Readiness"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Social Category Breakdown")
        if 'Social Category' in filtered_df.columns:
            fig_social = px.pie(filtered_df, names='Social Category', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_social, use_container_width=True)
        
    with col2:
        st.subheader("Land Holding Distribution")
        fig_land = px.histogram(
            filtered_df, 
            x='Total Land Cultivated (acres)', 
            nbins=20, 
            color='Gender', 
            marginal='box', 
            template='plotly_white'
        )
        st.plotly_chart(fig_land, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Primary Crop Categories")
        if '[Added] Crop 1 - Category' in filtered_df.columns:
            crop_data = filtered_df['[Added] Crop 1 - Category'].value_counts().reset_index()
            crop_data.columns = ['Crop Category', 'Count']
            fig_crop = px.bar(
                crop_data, 
                x='Count', 
                y='Crop Category', 
                orientation='h', 
                color='Count', 
                color_continuous_scale='Viridis'
            )
            fig_crop.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_crop, use_container_width=True)
            
    with col2:
        st.subheader("Cultivated Land vs. Horticulture Area")
        fig_scatter = px.scatter(
            filtered_df, 
            x='Total Land Cultivated (acres)', 
            y='Area under Horticulture (acres)', 
            color='District', 
            hover_data=['Farmer Name'],
            template='plotly_white'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Willingness to Sell to FCF / FPO")
        if 'Willing to Sell to FCF / FPO' in filtered_df.columns:
            willing_data = filtered_df['Willing to Sell to FCF / FPO'].value_counts().reset_index()
            willing_data.columns = ['Response', 'Count']
            fig_willing = px.pie(
                willing_data, 
                names='Response', 
                values='Count',
                color_discrete_sequence=['#2ecc71', '#e74c3c', '#f1c40f']
            )
            st.plotly_chart(fig_willing, use_container_width=True)
            
    with col2:
        st.subheader("Top Support Needed from FCF")
        if 'Top Support Needed from FCF' in filtered_df.columns:
            support_data = filtered_df['Top Support Needed from FCF'].value_counts().reset_index().head(5)
            support_data.columns = ['Support Type', 'Count']
            fig_support = px.bar(
                support_data, 
                x='Support Type', 
                y='Count', 
                template='plotly_white',
                text_auto=True
            )
            st.plotly_chart(fig_support, use_container_width=True)

st.divider()

# 8. Aggregated Analytical Summary (Replacing Raw Data)
st.subheader("📊 District Aggregation Summary")
st.markdown("A high-level view of average land holdings and horticulture adoption grouped by District.")

# Create a pivot table summarizing the data
pivot_df = filtered_df.groupby('District').agg(
    Total_Farmers=('Farmer Name', 'count'),
    Avg_Cultivated_Land=('Total Land Cultivated (acres)', 'mean'),
    Avg_Horticulture_Land=('Area under Horticulture (acres)', 'mean')
).reset_index()

# Format the numbers for a cleaner table view
pivot_df['Avg_Cultivated_Land'] = pivot_df['Avg_Cultivated_Land'].round(2)
pivot_df['Avg_Horticulture_Land'] = pivot_df['Avg_Horticulture_Land'].round(2)

st.dataframe(pivot_df, use_container_width=True)
