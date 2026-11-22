from types import SimpleNamespace

from agentcomms.agents import next_message
from agentcomms.server import create_app

MSG = {
    "performative": "request", "sender": "agent_1", "receiver": "agent_2",
    "ontology": "document_summary", "conversation_id": "c1",
    "content": {"text": "hello", "format": "plaintext"},
}


class FakeClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kw):
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=" reply "))])


def test_post_and_get():
    c = create_app().test_client()
    assert c.post("/a2a", json=MSG).status_code == 201
    assert c.get("/a2a/c1").get_json() == [MSG]
    assert c.get("/a2a/other").get_json() == []


def test_missing_fields_rejected():
    c = create_app().test_client()
    assert c.post("/a2a", json={"sender": "x"}).status_code == 400
    assert c.post("/a2a", data="not json").status_code == 400


def test_agent_roundtrip():
    reply = next_message(FakeClient(), "m", "c1", [MSG])
    assert (reply["sender"], reply["receiver"], reply["performative"]) == ("agent_2", "agent_1", "inform")
    assert reply["content"]["summary"] == "reply"
    back = next_message(FakeClient(), "m", "c1", [MSG, reply])
    assert (back["sender"], back["receiver"], back["performative"]) == ("agent_1", "agent_2", "request")
    assert back["content"]["text"] == "reply"
