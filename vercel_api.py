"""Small helpers shared by Vercel Python functions."""

import json
from http import HTTPStatus


def read_json_body(request_handler) -> dict:
    """Read JSON from a Vercel function request body."""
    content_length = int(request_handler.headers.get("Content-Length", "0"))
    raw_body = request_handler.rfile.read(content_length)
    if not raw_body:
        return {}
    return json.loads(raw_body.decode("utf-8"))


def send_json(request_handler, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
    """Send a JSON response from a Vercel Python function."""
    response = json.dumps(payload, indent=2).encode("utf-8")
    request_handler.send_response(status)
    request_handler.send_header("Content-Type", "application/json; charset=utf-8")
    request_handler.send_header("Content-Length", str(len(response)))
    request_handler.end_headers()
    request_handler.wfile.write(response)
