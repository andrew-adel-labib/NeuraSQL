from backend.app.llm.groq_client import chat


def explain(question, rows, cols):

    prompt = f"""
User Question:
{question}

Columns:
{cols}

Rows (first 10):
{rows[:10]}

Explain the result in simple business language.
"""

    response = chat([
        {
            "role": "system",
            "content": "You are a business data analyst."
        },
        {
            "role": "user",
            "content": prompt
        }
    ])

    return response


def explain_forecast(question, forecast_df):

    prompt = f"""
User Question:
{question}

Forecast Results:
{forecast_df.to_string(index=False)}

Explain the forecast in simple business language.
Highlight trend direction and risks.
"""

    response = chat([
        {
            "role": "system",
            "content": "You are a business forecasting analyst."
        },
        {
            "role": "user",
            "content": prompt
        }
    ])

    return response