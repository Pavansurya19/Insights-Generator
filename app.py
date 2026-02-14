import streamlit as st
import pandas as pd
import time

from google import genai
from analytics import auto_charts
from prompts import insights_prompt, question_prompt


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="InsightIQ — AI Business Insights",
    layout="wide"
)


# ---------------- STYLING ----------------
st.markdown("""
<style>
body { background-color: #0f0f0f; }

.kpi-box {
    background: #1a1a1a;
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    border: 1px solid #333;
}

.chat-user {
    background: #2b2b2b;
    padding: 14px;
    border-radius: 18px;
    margin-top: 20px;
    text-align: right;
}

.chat-ai {
    background: #1f1f1f;
    padding: 16px;
    border-radius: 18px;
    margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- TITLE ----------------
st.markdown("""
<h1 style="text-align:center; margin-top:40px;">
InsightIQ — Business Intelligence Assistant
</h1>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
with st.sidebar:
    uploaded_file = st.file_uploader("📂 Upload your data file")
    api_key = st.text_input("🔑 Gemini API Key", type="password")


# ---------------- FILE LOADING ----------------
df = None

if uploaded_file:
    with st.spinner("Reading file..."):
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

        st.success("✅ File uploaded successfully")

    except Exception as e:
        st.error("❌ Unable to read the file")
        st.code(str(e))
        st.stop()


# ---------------- STOP IF API KEY MISSING ----------------
if df is not None and not api_key:
    st.warning("⚠️ Please enter your Gemini API key in the sidebar.")
    st.stop()


# ---------------- CREATE GEMINI CLIENT ----------------
client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error("❌ Failed to initialize Gemini client")
        st.code(str(e))
        st.stop()


# ===================== AUTO SUMMARY =====================
if df is not None and client:

    # ---------- SAFE DATA SUMMARY ----------
    summary = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_statistics": df.describe().round(2).to_string()
    }

    # ---------- DATASET OVERVIEW ----------
    st.subheader("📊 Dataset Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", summary["rows"])
    c2.metric("Columns", summary["columns"])
    c3.metric("Missing Cells", int(df.isnull().sum().sum()))

    st.divider()

    # ---------- AUTO CHARTS ----------
    st.subheader("📈 Auto Visualizations")

    charts = auto_charts(df)

    if charts:
        for chart in charts:
            if hasattr(chart, "to_dict"):
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.pyplot(chart, clear_figure=True)
    else:
        st.info("No suitable charts could be generated.")

    st.divider()

    # ---------- AI DATASET INSIGHTS ----------
    st.subheader("🧠 Automated Business Insights")

    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=insights_prompt(summary)
        )

        st.markdown(response.text)

    except Exception as e:
        st.error("❌ Gemini Error while generating insights")
        st.code(str(e))

    st.divider()


# ===================== USER QUESTIONS =====================
if df is not None and client:

    st.subheader("💬 Ask Questions About Your Data")

    question = st.text_input(
        "Ask a question about the dataset",
        placeholder="e.g. Which category has the highest revenue?",
        label_visibility="collapsed"
    )

    ask = st.button("Ask")

    if ask and question.strip():

        st.markdown(
            f"<div class='chat-user'>{question}</div>",
            unsafe_allow_html=True
        )

        try:
            answer = client.models.generate_content(
                model="models/gemini-flash-latest",
                contents=question_prompt(summary, question)
            )

            st.markdown(
                f"<div class='chat-ai'>{answer.text}</div>",
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error("❌ Gemini Error while answering question")
            st.code(str(e))
