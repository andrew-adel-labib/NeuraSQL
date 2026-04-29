from backend.app.llm.groq_client import chat


def generate_response(question, predictions):

    prompt = f"""
User question:
{question}

Predicted values for next months:
{predictions}

Explain clearly in business language.
"""

    answer = chat(
        prompt=prompt,
        system_prompt="You are a financial forecasting analyst."
    )

    return {
        "forecast": predictions,
        "answer": answer
    }