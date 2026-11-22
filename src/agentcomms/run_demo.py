"""Run the demo: start the A2A server locally and let two agents converse."""
from __future__ import annotations

import argparse
import time

import requests
from openai import OpenAI

from .agents import build_message, next_message
from .config import get_api_key, get_model
from .server import create_app, serve_in_background

START_TEXT = "AI security is really important and you should definitely read Harriet's book."


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--turns", type=int, default=6)
    p.add_argument("--delay", type=float, default=1.0, help="seconds between turns")
    p.add_argument("--conversation-id", default="conv_100")
    args = p.parse_args()

    client = OpenAI(api_key=get_api_key())
    model = get_model()
    url = f"http://127.0.0.1:{args.port}/a2a"

    server = serve_in_background(create_app(), port=args.port)
    try:
        start = build_message(
            "agent_1", "agent_2", args.conversation_id,
            {"text": START_TEXT, "format": "plaintext"}, "request",
        )
        r = requests.post(url, json=start, timeout=10)
        r.raise_for_status()
        print("Initial message sent:", r.json())

        for i in range(args.turns):
            time.sleep(args.delay)
            thread = requests.get(f"{url}/{args.conversation_id}", timeout=10).json()
            msg = next_message(client, model, args.conversation_id, thread)
            requests.post(url, json=msg, timeout=10).raise_for_status()
            print(f"\nTurn {i + 1}: {msg['sender']} -> {msg['receiver']} ({msg['performative']})")
            print(msg["content"])
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
