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

.fade-in {
    animation: fadeIn 0.6s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

.chat-user {
    background: #2b2b2b;
    padding: 14px;
    border-radius: 18px;
    margin-top: 20px;
    text-align: right;
    font-size: 1.05rem;
}

.chat-ai {
    background: #1f1f1f;
    padding: 16px;
    border-radius: 18px;
    margin-top: 12px;
    font-size: 1.05rem;
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
<div style="text-align:center; margin-top:90px;">
    <h1 style="font-size:3.2rem; font-weight:800;">
        AI Business Insights Assistant
    </h1>
</div>
""", unsafe_allow_html=True)


# ---------------- GEMINI STYLE INPUT ----------------
col1, col2 = st.columns([6, 1])

with col1:
    question = st.text_input(
        "",
        placeholder="Ask anything about your data...",
        key="question_input",
        label_visibility="collapsed"
    )

with col2:
    submit = st.button("➤")


# ---------------- SIDEBAR ----------------
with st.sidebar:
    uploaded_file = st.file_uploader("Upload your data file")
    api_key = st.text_input("Gemini API Key", type="password")


# ---------------- WARNINGS ----------------
if submit and uploaded_file is None:
    st.warning("⚠️ Please upload a file before asking a question.")
    st.stop()


# ---------------- FILE UNDERSTANDING ----------------
df = None

if uploaded_file:
    with st.spinner("Understanding your file..."):
        time.sleep(1)

    name = uploaded_file.name.lower()

    try:
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        elif name.endswith(".txt"):
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

    # ---------- KPIs ----------
    st.subheader("📌 Key Performance Indicators")

    kpis = detect_kpis(df)
    if kpis:
        cols = st.columns(len(kpis))
        for i, (k, v) in enumerate(kpis.items()):
            cols[i].markdown(
                f"<div class='kpi-box'><h3>{k}</h3><p>{round(v,2)}</p></div>",
                unsafe_allow_html=True
            )

    # ---------- CHARTS ----------
    st.subheader("📊 Auto Charts")
    for fig in auto_charts(df):
        st.pyplot(fig)

    # ---------- INSIGHTS ----------
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
        insights_text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        st.markdown(f"<div class='fade-in'>{insights_text}</div>", unsafe_allow_html=True)

    # ---------- CHAT ----------
    if submit and question:

        st.markdown(
            f"<div class='chat-user fade-in'>{question}</div>",
            unsafe_allow_html=True
        )

        q_payload = {
            "contents": [{"parts": [{"text": question_prompt(summary, question)}]}]
        }

        qr = requests.post(
            f"{GEMINI_ENDPOINT}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=q_payload
        )

        if qr.status_code == 200:
            answer = qr.json()["candidates"][0]["content"]["parts"][0]["text"]

            placeholder = st.empty()
            typed_text = ""

            # typing animation
            for word in answer.split(" "):
                typed_text += word + " "
                placeholder.markdown(
                    f"<div class='chat-ai'>{typed_text}</div>",
                    unsafe_allow_html=True
                )
                time.sleep(0.03)
