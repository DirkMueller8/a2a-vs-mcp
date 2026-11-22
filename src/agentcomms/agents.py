"""The two agents: a summariser (agent_2) and a task initiator (agent_1)."""
from __future__ import annotations

SUMMARISER_PROMPT = "You are a summarisation agent. Provide a short, helpful summary."
INITIATOR_PROMPT = (
    "You are a task-initiating agent. Based on the last summary, write a new text "
    "that should be summarised."
)


def generate_response(client, model: str, role: str, input_text: str) -> str:
    """Ask the LLM to act as `role` ('agent_2' summarises, 'agent_1' writes a new task)."""
    if role == "agent_2":
        system, user = SUMMARISER_PROMPT, f"Summarise this: {input_text}"
    else:
        system = INITIATOR_PROMPT
        user = f"Based on this summary: {input_text}, write a new passage that agent_2 should summarise next."
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return resp.choices[0].message.content.strip()


def build_message(sender: str, receiver: str, conversation_id: str, content: dict, performative: str) -> dict:
    return {
        "performative": performative,
        "sender": sender,
        "receiver": receiver,
        "ontology": "document_summary",
        "conversation_id": conversation_id,
        "content": content,
    }


def next_message(client, model: str, conversation_id: str, thread: list[dict]) -> dict:
    """Produce the reply to the last message in `thread`, based on who it was addressed to."""
    last = thread[-1]
    role = last["receiver"]
    if role == "agent_2":
        content = {"summary": generate_response(client, model, role, last["content"]["text"]), "format": "plaintext"}
        performative = "inform"
    else:
        content = {"text": generate_response(client, model, role, last["content"]["summary"]), "format": "plaintext"}
        performative = "request"
    return build_message(role, last["sender"], conversation_id, content, performative)
