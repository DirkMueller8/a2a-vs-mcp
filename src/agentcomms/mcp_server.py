"""MCP server exposing the same mailbox as the Flask A2A server, as two tools.

REST /a2a (POST)            ->  tool post_message
REST /a2a/<conversation_id> ->  tool get_conversation

Runs over stdio: the client launches it as a subprocess, so no port is opened.
"""
from __future__ import annotations

import threading
from typing import Any

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("agentcomms")

_messages: list[dict[str, Any]] = []
_lock = threading.Lock()


@mcp.tool()
def post_message(
    performative: str,
    sender: str,
    receiver: str,
    ontology: str,
    conversation_id: str,
    content: dict[str, Any],
) -> dict[str, str]:
    """Post an A2A-style message to a conversation."""
    msg = {
        "performative": performative,
        "sender": sender,
        "receiver": receiver,
        "ontology": ontology,
        "conversation_id": conversation_id,
        "content": content,
    }
    with _lock:
        _messages.append(msg)
    return {"status": "A2A message received"}


@mcp.tool()
def get_conversation(conversation_id: str) -> dict[str, list[dict[str, Any]]]:
    """Return all messages of a conversation, oldest first."""
    with _lock:
        conv = [m for m in _messages if m["conversation_id"] == conversation_id]
    return {"messages": conv}


if __name__ == "__main__":
    mcp.run(transport="stdio")
