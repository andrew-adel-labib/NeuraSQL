from backend.app.exceptions import SecurityViolation

FORBIDDEN = ["drop", "delete", "password", "ignore"]

def classify_intent(text: str):
    for word in FORBIDDEN:
        if word in text.lower():
            raise SecurityViolation("Forbidden keyword", context={"keyword": word})