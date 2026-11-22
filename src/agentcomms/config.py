"""Loads the OpenAI key from the environment / a git-ignored .env file."""
import os

from dotenv import load_dotenv

load_dotenv()

PLACEHOLDER = "your-key-here"


def get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key or key == PLACEHOLDER:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key "
            "(see README)."
        )
    return key


def get_model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def get_anthropic_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key or key == PLACEHOLDER:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to .env (see .env.example and README)."
        )
    return key


def get_anthropic_model() -> str:
    return os.environ.get("ANTHROPIC_MODEL", "claude-opus-5-5")
