
import streamlit as st
import pandas as pd
import json
from openai import OpenAI

from config import MODEL_NAME, INSIGHTS_SCHEMA
from prompts import SYSTEM_INSTRUCTION


st.set_page_config(
    page_title="AI Business Insights Generator",
    layout="wide"
)

st.title("📊 AI Business Insights Generator")
st.caption("Upload a dataset and get management-level insights instantly.")

with st.sidebar:
    st.header("Upload & Analyze")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    analysis_type = st.selectbox(
        "Analysis Type",
        ["General Business", "Sales", "Marketing", "Finance"]
    )
    api_key = st.text_input("OpenAI API Key", type="password")
    generate = st.button("Generate Insights")

if generate:

    if not uploaded_file:
        st.error("Please upload a CSV file.")
        st.stop()

    if not api_key:
        st.error("Please enter your OpenAI API key.")
        st.stop()

    df = pd.read_csv(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_summary": df.describe().to_string()
    }

    client = OpenAI(api_key=api_key)

    user_prompt = f"""
Perform a {analysis_type} analysis on the dataset summary below.

Dataset Summary:
{json.dumps(summary, indent=2)}

Return output strictly as JSON following this schema:
{json.dumps(INSIGHTS_SCHEMA)}
"""

    with st.spinner("Analyzing dataset..."):
        try:
            response = client.responses.create(
                model=MODEL_NAME,
                input=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )

            insights = json.loads(response.output_text)

            st.success("Insights Generated Successfully")

            st.subheader("Executive Summary")
            st.write(insights["executiveSummary"])

            st.subheader("Key Insights")
            for i in insights["keyInsights"]:
                st.markdown(f"- {i}")

            st.subheader("Trends")
            for t in insights["trends"]:
                st.markdown(f"- {t}")

            st.subheader("Risks")
            for r in insights["risks"]:
                st.markdown(f"- {r}")

            st.subheader("Recommendations")
            for rec in insights["recommendations"]:
                st.markdown(f"- {rec}")

        except Exception as e:
            st.error(f"Error: {e}")
