"""MCP variant of the demo: agents use an MCP server (stdio) as their mailbox, Claude writes the text."""
from __future__ import annotations

import argparse
import asyncio
import sys

import anthropic
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from .agents import build_message
from .agents_claude import next_message
from .config import get_anthropic_key, get_anthropic_model

START_TEXT = "AI is transforming healthcare by enabling early detection of diseases and providing personalized treatment options."


class Mailbox:
    """Thin wrapper over the MCP tools; mirrors the REST POST/GET calls of the Flask version."""

    def __init__(self, session: ClientSession):
        self.session = session

    async def post(self, msg: dict) -> dict:
        res = await self.session.call_tool("post_message", msg)
        if res.is_error:
            raise RuntimeError(f"post_message failed: {res.content}")
        return res.structured_content

    async def get(self, conversation_id: str) -> list[dict]:
        res = await self.session.call_tool("get_conversation", {"conversation_id": conversation_id})
        if res.is_error:
            raise RuntimeError(f"get_conversation failed: {res.content}")
        return res.structured_content["messages"]


async def run(client, model: str, turns: int, delay: float, conversation_id: str, start_text: str = START_TEXT) -> list[dict]:
    params = StdioServerParameters(command=sys.executable, args=["-m", "agentcomms.mcp_server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            box = Mailbox(session)

            start = build_message("agent_1", "agent_2", conversation_id,
                                  {"text": start_text, "format": "plaintext"}, "request")
            print("Initial message sent:", await box.post(start))

            for i in range(turns):
                await asyncio.sleep(delay)
                thread = await box.get(conversation_id)
                # The Anthropic SDK client is synchronous; keep the event loop free for MCP I/O.
                msg = await asyncio.to_thread(next_message, client, model, conversation_id, thread)
                await box.post(msg)
                print(f"\nTurn {i + 1}: {msg['sender']} -> {msg['receiver']} ({msg['performative']})")
                print(msg["content"])
            return await box.get(conversation_id)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--turns", type=int, default=6)
    p.add_argument("--delay", type=float, default=1.0, help="seconds between turns")
    p.add_argument("--conversation-id", default="conv_100")
    p.add_argument("--show-model", action="store_true", help="print the configured model and exit")
    args = p.parse_args()

    model = get_anthropic_model()
    print(f"Provider: Anthropic (MCP) | Model: {model}")
    if args.show_model:
        return
    client = anthropic.Anthropic(api_key=get_anthropic_key())
    asyncio.run(run(client, model, args.turns, args.delay, args.conversation_id))


if __name__ == "__main__":
    main()
