"""WSGI entrypoint for Vercel."""

import json
from http import HTTPStatus

import india_assistant


MAX_QUESTION_LENGTH = 2000


def json_response(start_response, payload: dict, status: HTTPStatus = HTTPStatus.OK):
    """Return a JSON response from the WSGI app."""
    body = json.dumps(payload, indent=2).encode("utf-8")
    start_response(
        f"{status.value} {status.phrase}",
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]


def read_json_body(environ) -> dict:
    """Read a JSON request body from WSGI environ."""
    content_length = int(environ.get("CONTENT_LENGTH") or "0")
    raw_body = environ["wsgi.input"].read(content_length)
    if not raw_body:
        return {}
    return json.loads(raw_body.decode("utf-8"))


def app(environ, start_response):
    """Route Vercel API requests."""
    path = environ.get("PATH_INFO", "")
    method = environ.get("REQUEST_METHOD", "GET").upper()

    if path.endswith("/config") and method == "GET":
        return json_response(start_response, india_assistant.get_runtime_config())

    if path.endswith("/ask") and method == "POST":
        try:
            payload = read_json_body(environ)
        except json.JSONDecodeError:
            return json_response(
                start_response,
                {"error": "Request body must be valid JSON."},
                HTTPStatus.BAD_REQUEST,
            )

        question = str(payload.get("question", "")).strip()
        if not question:
            return json_response(
                start_response,
                {"error": "Please enter a question."},
                HTTPStatus.BAD_REQUEST,
            )

        if len(question) > MAX_QUESTION_LENGTH:
            return json_response(
                start_response,
                {"error": f"Question must be {MAX_QUESTION_LENGTH} characters or fewer."},
                HTTPStatus.BAD_REQUEST,
            )

        answer = india_assistant.ask(question)
        if answer == india_assistant.FALLBACK_ERROR_MESSAGE:
            config = india_assistant.get_runtime_config()
            return json_response(
                start_response,
                {
                    "error": india_assistant.LAST_ERROR_MESSAGE,
                    "provider": config["provider"],
                    "model": config["model"],
                },
                HTTPStatus.BAD_GATEWAY,
            )

        return json_response(
            start_response,
            {"answer": answer, "refused": answer == india_assistant.REFUSAL_STRING},
        )

    return json_response(start_response, {"error": "Endpoint not found."}, HTTPStatus.NOT_FOUND)
