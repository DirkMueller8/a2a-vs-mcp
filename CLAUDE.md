Agent-to-agent communication demo with two interchangeable variants. See README.md.
- REST: Flask A2A-like server + two OpenAI agents (`python -m agentcomms`)
- MCP: MCP server (stdio) + two Claude agents (`python -m agentcomms.run_demo_mcp`)

## Commands
- Setup: `python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt; pip install -e .`
- Test: `pytest` (LLMs are faked; no keys needed; the MCP test starts a real stdio server subprocess)
- Run REST demo: `python -m agentcomms --turns 6` (needs OPENAI_API_KEY in `.env`)
- Run MCP demo: `python -m agentcomms.run_demo_mcp --turns 6` (needs ANTHROPIC_API_KEY in `.env`)
- Show configured model without calling any API: add `--show-model` to either demo

## Layout
- `src/agentcomms/server.py` – Flask app factory `create_app()`, `serve_in_background()`
- `src/agentcomms/agents.py` – shared prompts, `build_message()`, OpenAI `next_message()`
- `src/agentcomms/agents_claude.py` – Claude `next_message()`, reuses prompts from `agents.py`
- `src/agentcomms/mcp_server.py` – MCP mailbox (`MCPServer`, tools `post_message`, `get_conversation`)
- `src/agentcomms/run_demo.py` / `run_demo_mcp.py` – the two CLI demos
- `src/agentcomms/config.py` – loads `.env`; key and model getters for both providers
- `docs/agentcomms.ipynb` – original exercise; reference only