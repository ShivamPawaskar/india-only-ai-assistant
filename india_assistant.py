"""
India-Only AI Assistant
-----------------------
Uses a strong system prompt to answer only India-related questions.
The model decides topic relevance. Python does not use keyword filtering.

Supported providers:
- opencode: OpenCode Zen OpenAI-compatible API
- openai: OpenAI Chat Completions-compatible API
- ollama: Local Ollama API
"""

import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REFUSAL_STRING = "I am sorry, I can only talk about India."
FALLBACK_ERROR_MESSAGE = "Sorry, something went wrong while contacting the assistant."
LAST_ERROR_MESSAGE = ""

PROJECT_DIR = Path(__file__).parent
ENV_FILE = PROJECT_DIR / ".env"

DEFAULTS = {
    "ASSISTANT_PROVIDER": "opencode",
    "OPENCODE_BASE_URL": "https://opencode.ai/zen/v1",
    "OPENCODE_MODEL": "big-pickle",
    "OPENAI_BASE_URL": "https://api.openai.com/v1",
    "OPENAI_MODEL": "gpt-3.5-turbo",
    "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
    "OLLAMA_MODEL": "llama3.2:3b",
}


SYSTEM_PROMPT = """You are an India-Only AI Assistant.

Your ONLY purpose is to answer questions that are related to India in any way.

The following topics are India-related and you should answer them:
- Indian history, including ancient, medieval, colonial, and modern history
- Indian geography, including rivers, mountains, states, union territories, cities, and regions
- Indian culture, art, music, dance, literature, traditions, heritage, and cinema
- Indian politics, constitution, parliament, elections, parties, laws, and public policy
- Indian economy, business, agriculture, industries, trade, RBI, finance, and markets
- Famous Indian people, including leaders, freedom fighters, scientists, artists, athletes, and actors
- Indian food, cuisine, spices, sweets, beverages, and regional dishes
- Religion in India, including Hinduism, Islam, Sikhism, Christianity, Buddhism, Jainism, and others
- Indian festivals, including Diwali, Holi, Eid, Christmas in India, Pongal, Onam, Durga Puja, and others
- Indian sports, including cricket, hockey, kabaddi, chess, Olympics, IPL, and Indian athletes
- Indian science and technology, including ISRO, DRDO, IITs, Indian scientists, and inventions
- Indian states, capitals, languages, demographics, government, military, courts, and administration
- Indian monuments, temples, tourist places, architecture, rivers, and natural landmarks
- India's relationship with other countries, and people of Indian origin

STRICT RULE:
If the question is NOT related to India in any way, respond with EXACTLY this sentence and nothing else:
"I am sorry, I can only talk about India."

Do NOT add any explanation when refusing.
Do NOT add extra words before or after the refusal sentence.
Do NOT answer non-India questions partially.

When the question is about India, give a clear, accurate, and helpful answer."""


class AssistantConfigError(RuntimeError):
    """Raised when the assistant provider is not configured correctly."""


def load_env_file(path: Path = ENV_FILE) -> None:
    """Load simple KEY=value pairs from .env without requiring extra packages."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key:
            os.environ[key] = value


def setting(name: str) -> str:
    """Return a setting from the environment or the project defaults."""
    return os.environ.get(name, DEFAULTS.get(name, "")).strip()


def looks_like_real_key(value: str) -> bool:
    """Return whether an API key value looks configured rather than placeholder-like."""
    key = value.strip()
    return bool(key) and key not in {
        "your-api-key-here",
        "paste-your-api-key-here",
        "your-opencode-api-key",
    }


def get_provider() -> str:
    """Return the selected provider name."""
    load_env_file()
    return setting("ASSISTANT_PROVIDER").lower()


def get_runtime_config() -> dict[str, Any]:
    """Return safe runtime configuration details for diagnostics."""
    load_env_file()
    provider = get_provider()

    if provider == "opencode":
        return {
            "provider": provider,
            "base_url": setting("OPENCODE_BASE_URL"),
            "model": setting("OPENCODE_MODEL"),
            "has_key": looks_like_real_key(os.environ.get("OPENCODE_API_KEY", "")),
        }

    if provider == "openai":
        return {
            "provider": provider,
            "base_url": setting("OPENAI_BASE_URL"),
            "model": setting("OPENAI_MODEL"),
            "has_key": looks_like_real_key(os.environ.get("OPENAI_API_KEY", "")),
        }

    if provider == "ollama":
        return {
            "provider": provider,
            "base_url": setting("OLLAMA_BASE_URL"),
            "model": setting("OLLAMA_MODEL"),
            "has_key": True,
        }

    return {
        "provider": provider,
        "base_url": "",
        "model": "",
        "has_key": False,
    }


def require_key(name: str) -> str:
    """Read a required API key from the environment."""
    key = os.environ.get(name, "").strip()
    if not looks_like_real_key(key):
        raise AssistantConfigError(f"{name} is not set. Add it to .env and restart the server.")
    return key


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
    """Send a JSON POST request and return the JSON response."""
    request_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "India-Only-AI-Assistant/1.0",
    }
    if headers:
        request_headers.update(headers)

    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=request_headers,
        method="POST",
    )

    try:
        with urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code}: {body}") from error
    except URLError as error:
        raise RuntimeError(f"Could not connect to {url}: {error.reason}") from error


def openai_compatible_chat(base_url: str, api_key: str, model: str, question: str) -> str:
    """Call an OpenAI-compatible /chat/completions endpoint."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    data = post_json(url, payload, headers)

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError(f"Unexpected chat response: {data}") from error


def ollama_chat(question: str) -> str:
    """Call the local Ollama chat endpoint."""
    base_url = setting("OLLAMA_BASE_URL")
    model = setting("OLLAMA_MODEL")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "stream": False,
        "options": {"temperature": 0.2},
    }
    data = post_json(f"{base_url.rstrip('/')}/api/chat", payload)

    try:
        return data["message"]["content"].strip()
    except (KeyError, TypeError) as error:
        raise RuntimeError(f"Unexpected Ollama response: {data}") from error


def ask(question: str) -> str:
    """Ask the configured India-only assistant provider a question."""
    global LAST_ERROR_MESSAGE
    load_env_file()
    LAST_ERROR_MESSAGE = ""

    try:
        provider = get_provider()

        if provider == "opencode":
            return openai_compatible_chat(
                setting("OPENCODE_BASE_URL"),
                require_key("OPENCODE_API_KEY"),
                setting("OPENCODE_MODEL"),
                question,
            )

        if provider == "openai":
            return openai_compatible_chat(
                setting("OPENAI_BASE_URL"),
                require_key("OPENAI_API_KEY"),
                setting("OPENAI_MODEL"),
                question,
            )

        if provider == "ollama":
            return ollama_chat(question)

        raise AssistantConfigError("ASSISTANT_PROVIDER must be opencode, openai, or ollama.")
    except Exception as error:
        LAST_ERROR_MESSAGE = str(error)
        print(f"Assistant error: {LAST_ERROR_MESSAGE}")
        return FALLBACK_ERROR_MESSAGE


def print_qa_block(question: str, answer: str) -> None:
    """Print one formatted question-and-answer block."""
    separator = "\u2500" * 45
    print(separator)
    print(f"Q: {question}")
    print(f"A: {answer}")
    print(separator)


def main() -> None:
    """Run a command-line demo with mixed India and non-India questions."""
    questions = [
        "What is the capital of India?",
        "Who was Akbar?",
        "Tell me about the history of London.",
        "What are the major festivals of India?",
        "Who is the President of the United States?",
        "Explain the significance of the Ganges river.",
        "What is the Eiffel Tower?",
        "Which states share a border with Maharashtra?",
    ]

    answered_count = 0
    refused_count = 0
    config = get_runtime_config()

    print(f"Provider: {config['provider']}")
    print(f"Model: {config['model']}")

    for question in questions:
        answer = ask(question)
        print_qa_block(question, answer)

        if answer == REFUSAL_STRING:
            refused_count += 1
        else:
            answered_count += 1

    print(f"Summary: {answered_count} answered, {refused_count} refused.")


if __name__ == "__main__":
    main()
