"""Claude-backed versions of the two agents (same prompts/roles as agents.py)."""
from __future__ import annotations

from .agents import INITIATOR_PROMPT, SUMMARISER_PROMPT, build_message


def generate_response(client, model: str, role: str, input_text: str) -> str:
    """Ask Claude to act as `role` ('agent_2' summarises, 'agent_1' writes a new task)."""
    if role == "agent_2":
        system, user = SUMMARISER_PROMPT, f"Summarise this: {input_text}"
    else:
        system = INITIATOR_PROMPT
        user = f"Based on this summary: {input_text}, write a new passage that agent_2 should summarise next."
    # Opus 5.5 can refuse via safety classifiers; the server-side fallback re-runs the request
    # on another model within the same call (beta, Claude API only).
    response = client.beta.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={"effort": "low"},  # short, simple text tasks
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Model refused the request: {response.stop_details}")
    return "".join(b.text for b in response.content if b.type == "text").strip()


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
