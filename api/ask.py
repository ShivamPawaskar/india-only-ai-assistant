"""Vercel function for assistant questions."""

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

import india_assistant
from vercel_api import read_json_body, send_json


MAX_QUESTION_LENGTH = 2000


class handler(BaseHTTPRequestHandler):
    """Handle assistant requests on Vercel."""

    def do_POST(self) -> None:
        try:
            payload = read_json_body(self)
        except json.JSONDecodeError:
            send_json(self, {"error": "Request body must be valid JSON."}, HTTPStatus.BAD_REQUEST)
            return

        question = str(payload.get("question", "")).strip()
        if not question:
            send_json(self, {"error": "Please enter a question."}, HTTPStatus.BAD_REQUEST)
            return

        if len(question) > MAX_QUESTION_LENGTH:
            send_json(
                self,
                {"error": f"Question must be {MAX_QUESTION_LENGTH} characters or fewer."},
                HTTPStatus.BAD_REQUEST,
            )
            return

        answer = india_assistant.ask(question)
        if answer == india_assistant.FALLBACK_ERROR_MESSAGE:
            config = india_assistant.get_runtime_config()
            send_json(
                self,
                {
                    "error": india_assistant.LAST_ERROR_MESSAGE,
                    "provider": config["provider"],
                    "model": config["model"],
                },
                HTTPStatus.BAD_GATEWAY,
            )
            return

        send_json(self, {"answer": answer, "refused": answer == india_assistant.REFUSAL_STRING})
