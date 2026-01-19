import streamlit as st
import pandas as pd
import requests
import json
import time

from analytics import detect_kpis, auto_charts
from prompts import insights_prompt, question_prompt
from config import GEMINI_ENDPOINT


# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Business Insights Assistant", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
body { background-color: #0f0f0f; }

.center {
    height: 70vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.chat-user {
    background: #2b2b2b;
    padding: 12px;
    border-radius: 15px;
    margin: 10px 0;
    text-align: right;
}

.chat-ai {
    background: #1f1f1f;
    padding: 12px;
    border-radius: 15px;
    margin: 10px 0;
    text-align: left;
}

.kpi-box {
    background: #1a1a1a;
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    border: 1px solid #333;
}
</style>
""", unsafe_allow_html=True)

# ---------------- CENTER LANDING ----------------
st.markdown("""
<div class="center">
    <h1>✨ AI Business Insights Assistant</h1>
</div>
""", unsafe_allow_html=True)

question = st.text_input("", placeholder="Ask anything about your data...")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    uploaded_file = st.file_uploader("Upload your data file")
    api_key = st.text_input("Gemini API Key", type="password")

# ---------------- WARNING ----------------
if question and uploaded_file is None:
    st.warning("⚠️ Please upload a file before asking questions.")
    st.stop()

# ---------------- FILE UNDERSTANDING ----------------
df = None

if uploaded_file:
    with st.spinner("Understanding your file..."):
        time.sleep(1.2)

    file_name = uploaded_file.name.lower()

    try:
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif file_name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        elif file_name.endswith(".txt"):
            df = pd.read_csv(uploaded_file, delimiter="|")
        else:
            st.error("Unsupported file format.")
            st.stop()
    except Exception:
        st.error("Unable to read file.")
        st.stop()

    st.success("✅ File uploaded successfully")

# ---------------- MAIN LOGIC ----------------
if df is not None and api_key:

    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "missing": df.isnull().sum().to_dict(),
        "stats": df.describe().to_string()
    }

    # -------- KPIs --------
    st.subheader("📌 Key KPIs")
    kpis = detect_kpis(df)

    if kpis:
        cols = st.columns(len(kpis))
        for i, (k, v) in enumerate(kpis.items()):
            cols[i].markdown(
                f"<div class='kpi-box'><h3>{k}</h3><p>{round(v,2)}</p></div>",
                unsafe_allow_html=True
            )

    # -------- CHARTS --------
    st.subheader("📊 Auto Charts")
    for fig in auto_charts(df):
        st.pyplot(fig)

    # -------- INSIGHTS --------
    st.subheader("📄 Business Insights")

    payload = {
        "contents": [{"parts": [{"text": insights_prompt(summary)}]}]
    }

    r = requests.post(
        f"{GEMINI_ENDPOINT}?key={api_key}",
        headers={"Content-Type": "application/json"},
        json=payload
    )

    if r.status_code == 200:
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        st.markdown(text)

    # -------- CHAT --------
    if question:
        st.markdown(f"<div class='chat-user'>{question}</div>", unsafe_allow_html=True)

        q_payload = {
            "contents": [{"parts": [{"text": question_prompt(summary, question)}]}]
        }

        qr = requests.post(
            f"{GEMINI_ENDPOINT}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=q_payload
        )

        if qr.status_code == 200:
            ans = qr.json()["candidates"][0]["content"]["parts"][0]["text"]
            st.markdown(f"<div class='chat-ai'>{ans}</div>", unsafe_allow_html=True)
