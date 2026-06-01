"""Local website server for the India-Only AI Assistant."""

import json
import os
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import india_assistant


HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "8000"))
WEB_DIR = Path(__file__).parent / "web"
MAX_QUESTION_LENGTH = 2000


class WebHandler(SimpleHTTPRequestHandler):
    """Serve static files and JSON API endpoints."""

    def do_GET(self) -> None:
        """Serve the UI or configuration endpoint."""
        if self.path == "/api/config":
            self._send_json(india_assistant.get_runtime_config())
            return

        if self.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def do_POST(self) -> None:
        """Handle assistant requests."""
        if self.path != "/api/ask":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        try:
            payload = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json({"error": "Request body must be valid JSON."}, HTTPStatus.BAD_REQUEST)
            return

        question = str(payload.get("question", "")).strip()
        if not question:
            self._send_json({"error": "Please enter a question."}, HTTPStatus.BAD_REQUEST)
            return

        if len(question) > MAX_QUESTION_LENGTH:
            self._send_json(
                {"error": f"Question must be {MAX_QUESTION_LENGTH} characters or fewer."},
                HTTPStatus.BAD_REQUEST,
            )
            return

        answer = india_assistant.ask(question)
        if answer == india_assistant.FALLBACK_ERROR_MESSAGE:
            config = india_assistant.get_runtime_config()
            self._send_json(
                {
                    "error": india_assistant.LAST_ERROR_MESSAGE,
                    "provider": config["provider"],
                    "model": config["model"],
                },
                HTTPStatus.BAD_GATEWAY,
            )
            return

        self._send_json({"answer": answer, "refused": answer == india_assistant.REFUSAL_STRING})

    def _read_json_body(self) -> dict:
        """Read JSON from the request body."""
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        if not raw_body:
            return {}
        return json.loads(raw_body.decode("utf-8"))

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        """Send a JSON response."""
        response = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


def main() -> None:
    """Start the local website server."""
    india_assistant.load_env_file()
    config = india_assistant.get_runtime_config()
    handler = partial(WebHandler, directory=str(WEB_DIR))
    server = ThreadingHTTPServer((HOST, PORT), handler)

    print(f"India-Only AI Assistant running at http://{HOST}:{PORT}")
    print(f"Provider: {config['provider']}")
    print(f"Model: {config['model']}")
    print(f"API key configured: {'yes' if config['has_key'] else 'no'}")
    print("Press Ctrl+C to stop.")

    server.serve_forever()


if __name__ == "__main__":
    main()
