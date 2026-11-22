Agent-to-agent communication demo (Flask A2A-like server + two OpenAI agents). See README.md.

## Commands
- Setup: `python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt; pip install -e .`
- Test: `pytest` (OpenAI is mocked; no key needed)
- Run demo: `python -m agentcomms --turns 6` (needs a real key in `.env`)

## Layout
- `src/agentcomms/server.py` – Flask app factory `create_app()`, `serve_in_background()`
- `src/agentcomms/agents.py` – prompts, `next_message()` picks the role from the last message's `receiver`
- `src/agentcomms/config.py` – loads `.env`, `get_api_key()`, `get_model()`
- `docs/agentcomms.ipynb` – original exercise; reference only

## Rules
- **Secrets:** never read, print, log, or commit `.env` or any API key. Never hardcode keys. Only `.env.example` (placeholder) is tracked. Don't `git add -f` ignored files.
- Required message fields: `performative, sender, receiver, ontology, conversation_id, content`.
- Keep the server bound to `127.0.0.1`; it has no auth.
- Tests must not call the real OpenAI API; use fakes like `FakeClient` in `tests/`.
- Default model is `gpt-4o-mini`, overridable via `OPENAI_MODEL`.