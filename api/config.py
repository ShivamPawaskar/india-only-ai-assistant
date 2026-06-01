"""Vercel function for safe runtime configuration details."""

from http.server import BaseHTTPRequestHandler

import india_assistant
from vercel_api import send_json


class handler(BaseHTTPRequestHandler):
    """Return non-secret assistant configuration."""

    def do_GET(self) -> None:
        send_json(self, india_assistant.get_runtime_config())
