import streamlit as st
import pandas as pd
import requests
import json
import time

from analytics import detect_kpis, auto_charts
from prompts import insights_prompt, question_prompt
from config import GEMINI_ENDPOINT


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Business Insights Assistant",
    layout="wide"
)

# ---------------- STYLING ----------------
st.markdown("""
<style>
body {
    background-color: #0f0f0f;
}

/* Center title */
.title-container {
    text-align: center;
    margin-top: 90px;
}

/* Prompt UI */
.prompt-container {
    display: flex;
    justify-content: center;
    margin-top: 25px;
}

.prompt-box {
    width: 60%;
    background: #1f1f1f;
    border-radius: 40px;
    padding: 16px 22px;
    display: flex;
    align-items: center;
    border: 1px solid #333;
}

.prompt-box input {
    background: transparent;
    border: none;
    outline: none;
    color: white;
    width: 100%;
    font-size: 1.1rem;
}

.send-btn {
    background: #2a2a2a;
    border-radius: 50%;
    border: none;
    width: 42px;
    height: 42px;
    margin-left: 12px;
    cursor: pointer;
    color: white;
    font-size: 18px;
}

.chat-user {
    background: #2b2b2b;
    padding: 12px;
    border-radius: 16px;
    margin-top: 15px;
    text-align: right;
}

.chat-ai {
    background: #1f1f1f;
    padding: 12px;
    border-radius: 16px;
    margin-top: 10px;
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


# ---------------- TITLE ----------------
st.markdown("""
<div class="title-container">
    <h1>✨ AI Business Insights Assistant</h1>
</div>
""", unsafe_allow_html=True)


# ---------------- PROMPT BAR ----------------
question = st.text_input(
    "",
    placeholder="Ask anything about your data...",
    key="question_input",
    label_visibility="collapsed"
)

submit = st.button("➤", help="Submit question")


# ---------------- SIDEBAR ----------------
with st.sidebar:
    uploaded_file = st.file_uploader("Upload your data file")
    api_key = st.text_input("Gemini API Key", type="password")


# ---------------- WARNINGS ----------------
if submit and uploaded_file is None:
    st.warning("⚠️ Please upload a file before submitting your question.")
    st.stop()


# ---------------- FILE UNDERSTANDING ----------------
df = None

if uploaded_file:
    with st.spinner("Understanding your file..."):
        time.sleep(1)

    filename = uploaded_file.name.lower()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif filename.endswith(".json"):
            df = pd.read_json(uploaded_file)
        elif filename.endswith(".txt"):
            df = pd.read_csv(uploaded_file, delimiter="|")
        else:
            st.error("Unsupported file format.")
            st.stop()
    except Exception:
        st.error("Unable to read the uploaded file.")
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
    st.subheader("📌 Key Performance Indicators")

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

    insights_payload = {
        "contents": [{"parts": [{"text": insights_prompt(summary)}]}]
    }

    insights_response = requests.post(
        f"{GEMINI_ENDPOINT}?key={api_key}",
        headers={"Content-Type": "application/json"},
        json=insights_payload
    )

    if insights_response.status_code == 200:
        text = insights_response.json()["candidates"][0]["content"]["parts"][0]["text"]
        st.markdown(text)

    # -------- QUESTION CHAT --------
    if submit and question:

        st.markdown(f"<div class='chat-user'>{question}</div>", unsafe_allow_html=True)

        q_payload = {
            "contents": [{"parts": [{"text": question_prompt(summary, question)}]}]
        }

        q_response = requests.post(
            f"{GEMINI_ENDPOINT}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=q_payload
        )

        if q_response.status_code == 200:
            answer = q_response.json()["candidates"][0]["content"]["parts"][0]["text"]
            st.markdown(f"<div class='chat-ai'>{answer}</div>", unsafe_allow_html=True)
