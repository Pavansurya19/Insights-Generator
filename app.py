import streamlit as st
import pandas as pd
import google.generativeai as genai

from config import GEMINI_MODEL
from prompts import SYSTEM_PROMPT


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Business Insights Generator",
    layout="wide"
)

st.title("📊 AI Business Insights Generator")
st.caption("Powered by Google Gemini")


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("Upload Dataset")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    analysis_type = st.selectbox(
        "Analysis Type",
        ["General Business", "Sales", "Marketing", "Finance"]
    )

    api_key = st.text_input("Gemini API Key", type="password")
    generate = st.button("Generate Insights")


# ---------------- MAIN LOGIC ----------------
if generate:

    if uploaded_file is None:
        st.error("Please upload a CSV file.")
        st.stop()

    if not api_key:
        st.error("Please enter your Gemini API key.")
        st.stop()

    # -------- SAFE CSV LOADING --------
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
    except Exception:
        st.error("Unable to read CSV file. Please upload a valid CSV.")
        st.stop()

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    # -------- DATA SUMMARY --------
    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_summary": df.describe().to_string()
    }

    # -------- GEMINI SETUP --------
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)

    prompt = f"""
{SYSTEM_PROMPT}

Type of analysis: {analysis_type}

Dataset Summary:
{summary}

Format the response with clear headings and bullet points.
"""

    with st.spinner("Analyzing dataset..."):
        response = model.generate_content(prompt)

    st.success("Insights generated successfully")

    st.markdown(response.text)
