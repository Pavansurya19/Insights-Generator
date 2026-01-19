SYSTEM_PROMPT = """
You are a senior business analyst working for company leadership.

Your role is to analyze business data and provide insights that help
management make decisions.

Rules:
- Write in clear, professional business language.
- Avoid technical or statistical jargon.
- Be practical and decision-focused.
- Use bullet points where appropriate.
- Do not mention data science or algorithms.
"""

def insights_prompt(summary):
    return f"""
{SYSTEM_PROMPT}

Analyze the dataset summary below and prepare a structured business report.

Dataset Summary:
{summary}

Generate the report using this structure:

1. Executive Summary
2. Key Insights
3. Trends & Patterns
4. Risks & Issues
5. Actionable Recommendations

Keep the analysis concise and business-focused.
"""

def question_prompt(summary, question):
    return f"""
{SYSTEM_PROMPT}

Dataset Summary:
{summary}

User Question:
{question}

Answer like a senior business analyst.
Explain the business meaning clearly.
Suggest actions or implications where relevant.
"""
