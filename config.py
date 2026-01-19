
MODEL_NAME = "gpt-4o-mini"

INSIGHTS_SCHEMA = {
    "type": "object",
    "properties": {
        "executiveSummary": {"type": "string"},
        "keyInsights": {
            "type": "array",
            "items": {"type": "string"}
        },
        "trends": {
            "type": "array",
            "items": {"type": "string"}
        },
        "risks": {
            "type": "array",
            "items": {"type": "string"}
        },
        "recommendations": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}
