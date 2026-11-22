"""Flask server implementing a minimal A2A-like message exchange."""
from __future__ import annotations

import threading

from flask import Flask, jsonify, request

REQUIRED_FIELDS = ("performative", "sender", "receiver", "ontology", "conversation_id", "content")


def create_app() -> Flask:
    app = Flask(__name__)
    messages: list[dict] = []
    lock = threading.Lock()

    @app.post("/a2a")
    def post_message():
        msg = request.get_json(silent=True)
        if not isinstance(msg, dict) or not all(f in msg for f in REQUIRED_FIELDS):
            return jsonify({"error": "Missing required A2A fields"}), 400
        with lock:
            messages.append(msg)
        return jsonify({"status": "A2A message received"}), 201

    @app.get("/a2a/<conversation_id>")
    def get_conversation(conversation_id: str):
        with lock:
            conv = [m for m in messages if m["conversation_id"] == conversation_id]
        return jsonify(conv)

    return app


def serve_in_background(app: Flask, host: str = "127.0.0.1", port: int = 5000):
    """Start the app on a background thread; returns the werkzeug server (call .shutdown())."""
    from werkzeug.serving import make_server

    server = make_server(host, port, app)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
