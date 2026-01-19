import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(
    page_title="AI Business Insights Generator",
    layout="wide"
)

st.title("📊 AI Business Insights Generator (Gemini)")
st.caption("Powered by Google Gemini")

with st.sidebar:
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    analysis_type = st.selectbox(
        "Analysis Type",
        ["General Business", "Sales", "Marketing", "Finance"]
    )
    api_key = st.text_input("Gemini API Key", type="password")
    generate = st.button("Generate Insights")

if generate:

    if uploaded_file is None:
        st.error("Please upload a CSV file.")
        st.stop()

    if not api_key:
        st.error("Please enter Gemini API key.")
        st.stop()

    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
    except Exception:
        st.error("Invalid CSV file.")
        st.stop()

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_summary": df.describe().to_string()
    }

    prompt = f"""
You are a senior business analyst.

Perform a {analysis_type} analysis and generate:

### Executive Summary
### Key Insights
### Trends
### Risks
### Recommendations

Dataset Summary:
{summary}

Write in professional business language.
"""

    with st.spinner("Analyzing dataset..."):
        response = model.generate_content(prompt)

    st.success("Insights generated")

    st.markdown(response.text)
