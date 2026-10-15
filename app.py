import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Farmer Procurement Dashboard",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Farmer Procurement Dashboard")
st.write(
    "Interactive analysis of farmer profiles, "
    "horticulture production and procurement potential."
)

st.info(
    "Upload a sample Excel or CSV file to explore the dashboard. "
    "Use anonymised or synthetic data for testing."
)

uploaded_file = st.file_uploader(
    "Upload farmer survey data",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("Dataset loaded successfully!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Records", len(df))

    with col2:
        st.metric("Total Columns", len(df.columns))

    with col3:
        st.metric(
            "Duplicate Rows",
            int(df.duplicated().sum())
        )

    st.subheader("Dataset Preview")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("Explore a Variable")

    selected_column = st.selectbox(
        "Select a column",
        df.columns
    )

    counts = (
        df[selected_column]
        .fillna("Missing")
        .astype(str)
        .value_counts()
        .head(15)
        .reset_index()
    )

    counts.columns = ["Category", "Count"]

    fig = px.bar(
        counts,
        x="Category",
        y="Count",
        title=f"Distribution of {selected_column}"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.write("Upload a file to view the dashboard.")
