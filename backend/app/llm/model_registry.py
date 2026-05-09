AVAILABLE_MODELS = {
    "claude": {
        "provider": "claude",
        "label": "Claude",
        "default_model": "claude-haiku-4-5"
    },

    "openai": {
        "provider": "openai",
        "label": "GPT",
        "default_model": "gpt-4o-mini"
    },

    "groq": {
        "provider": "groq",
        "label": "Groq",
        "default_model": "llama-3.1-8b-instant"
    }
}


DEFAULT_PROVIDER = "claude"


def get_available_model_names():
    return list(
        AVAILABLE_MODELS.keys()
    )


def get_model_label(
    provider: str
):
    return AVAILABLE_MODELS.get(
        provider,
        AVAILABLE_MODELS[
            DEFAULT_PROVIDER
        ]
    )["label"]


def validate_provider(
    provider: str
):
    if provider not in AVAILABLE_MODELS:
        return DEFAULT_PROVIDER

    return provider