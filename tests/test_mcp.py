"""End-to-end test of the MCP variant: real stdio MCP server subprocess, fake Claude client."""
import asyncio
from types import SimpleNamespace

from agentcomms.run_demo_mcp import run


class FakeAnthropic:
    def __init__(self):
        self.calls = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kw):
        self.calls.append(kw)
        block = SimpleNamespace(type="text", text=f" reply{len(self.calls)} ")
        return SimpleNamespace(stop_reason="end_turn", content=[block])


def test_mcp_conversation_roundtrip():
    client = FakeAnthropic()
    thread = asyncio.run(run(client, "fake-model", turns=3, delay=0, conversation_id="t1"))
    assert [(m["sender"], m["receiver"], m["performative"]) for m in thread] == [
        ("agent_1", "agent_2", "request"),
        ("agent_2", "agent_1", "inform"),
        ("agent_1", "agent_2", "request"),
        ("agent_2", "agent_1", "inform"),
    ]
    assert thread[1]["content"]["summary"] == "reply1"
    assert thread[2]["content"]["text"] == "reply2"
    assert len(client.calls) == 3
