import streamlit as st
import pandas as pd
import requests
import json

from config import GEMINI_ENDPOINT


st.set_page_config(
    page_title="AI Business Insights Generator",
    layout="wide"
)

st.title("📊 AI Business Insights Generator (Gemini REST)")


with st.sidebar:
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    analysis_type = st.selectbox(
        "Analysis Type",
        ["General Business", "Sales", "Marketing", "Finance"]
    )
    api_key = st.text_input("Gemini API Key", type="password")
    generate = st.button("Generate Insights")


if generate:

    if uploaded_file is None:
        st.error("Upload CSV file.")
        st.stop()

    if not api_key:
        st.error("Enter Gemini API key.")
        st.stop()

    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
    except Exception:
        st.error("Invalid CSV.")
        st.stop()

    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_summary": df.describe().to_string()
    }

    prompt = f"""
You are a senior business analyst.

Perform {analysis_type} analysis and generate:

- Executive Summary
- Key Insights
- Trends
- Risks
- Recommendations

Dataset Summary:
{json.dumps(summary, indent=2)}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    with st.spinner("Analyzing..."):
        response = requests.post(
            f"{GEMINI_ENDPOINT}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=payload
        )

    if response.status_code != 200:
        st.error("Gemini API error. Please check your key or quota.")
        st.stop()

    result = response.json()
    text = result["candidates"][0]["content"]["parts"][0]["text"]

    st.success("Insights Generated")
    st.markdown(text)
