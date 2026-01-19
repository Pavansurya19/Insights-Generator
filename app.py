import streamlit as st
import pandas as pd
import json
from openai import OpenAI

from config import MODEL_NAME, INSIGHTS_SCHEMA
from prompts import SYSTEM_INSTRUCTION


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Business Insights Generator",
    layout="wide"
)

st.title("📊 AI Business Insights Generator")
st.caption("Upload a dataset and receive management-level insights instantly.")


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("Setup")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    analysis_type = st.selectbox(
        "Analysis Type",
        ["General Business", "Sales", "Marketing", "Finance"]
    )

    api_key = st.text_input("OpenAI API Key", type="password")
    generate = st.button("Generate Insights")


# ---------------- MAIN LOGIC ----------------
if generate:

    if uploaded_file is None:
        st.error("Please upload a CSV file.")
        st.stop()

    if not api_key:
        st.error("Please enter your OpenAI API key.")
        st.stop()

    # ---------- SAFE CSV LOADING ----------
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError:
        st.error("Uploaded file is empty.")
        st.stop()
    except Exception:
        st.error("Unable to read CSV file.")
        st.stop()

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    summary = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_summary": df.describe().to_string()
    }

    client = OpenAI(api_key=api_key)

    user_prompt = f"""
Perform a {analysis_type} analysis on the dataset summary below.

Dataset Summary:
{json.dumps(summary, indent=2)}

Return ONLY valid JSON in this schema:
{json.dumps(INSIGHTS_SCHEMA)}
"""

    with st.spinner("Analyzing dataset..."):

        try:
            response = client.responses.create(
                model=MODEL_NAME,
                input=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": user_prompt}
                ]
            )

            raw_text = response.output_text

            try:
                insights = json.loads(raw_text)
            except json.JSONDecodeError:
                st.error("AI returned invalid JSON. Please try again.")
                st.stop()

            st.success("Insights generated successfully")

            st.subheader("Executive Summary")
            st.write(insights.get("executiveSummary", "N/A"))

            st.subheader("Key Insights")
            for i in insights.get("keyInsights", []):
                st.markdown(f"- {i}")

            st.subheader("Trends")
            for t in insights.get("trends", []):
                st.markdown(f"- {t}")

            st.subheader("Risks")
            for r in insights.get("risks", []):
                st.markdown(f"- {r}")

            st.subheader("Recommendations")
            for rec in insights.get("recommendations", []):
                st.markdown(f"- {rec}")

        except Exception as e:
            st.error(f"Error generating insights: {e}")
