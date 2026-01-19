import streamlit as st
import pandas as pd
import requests
import json

from analytics import detect_kpis, auto_charts
from prompts import insights_prompt, question_prompt
from config import GEMINI_ENDPOINT


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Business Insights Assistant",
    layout="wide"
)

st.markdown("""
<style>
body { background-color: #0f0f0f; }

.chat-box {
    background-color: #1f1f1f;
    padding: 1.2rem;
    border-radius: 16px;
    margin-top: 1rem;
}

.kpi-box {
    background-color: #1a1a1a;
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    border: 1px solid #2a2a2a;
}
</style>
""", unsafe_allow_html=True)

st.title("✨ AI Business Insights Assistant")
st.caption("Gemini-style analytics with auto KPIs, charts, and Q&A")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    api_key = st.text_input("Gemini API Key", type="password")


# ---------------- MAIN ----------------
if uploaded_file and api_key:

    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
    except Exception:
        st.error("Invalid CSV file.")
        st.stop()

    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "statistics": df.describe().to_string()
    }

    # -------- KPIs --------
    st.subheader("📌 Key Performance Indicators")

    kpis = detect_kpis(df)

    if kpis:
        cols = st.columns(len(kpis))
        for i, (k, v) in enumerate(kpis.items()):
            cols[i].markdown(
                f"<div class='kpi-box'><h3>{k}</h3><p>{round(v, 2)}</p></div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No KPI columns detected automatically.")

    # -------- CHARTS --------
    st.subheader("📊 Automatic Charts")

    charts = auto_charts(df)
    for fig in charts:
        st.pyplot(fig)

    # -------- CHAT --------
    st.subheader("💬 Ask Questions in English")

    question = st.text_input("Ask anything about your data")

    if question:
        prompt = question_prompt(summary, question)

        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        response = requests.post(
            f"{GEMINI_ENDPOINT}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=payload
        )

        if response.status_code != 200:
            st.error("Gemini API error. Please check your API key or quota.")
            st.stop()

        result = response.json()
        answer = result["candidates"][0]["content"]["parts"][0]["text"]

        st.markdown(f"<div class='chat-box'>{answer}</div>", unsafe_allow_html=True)
