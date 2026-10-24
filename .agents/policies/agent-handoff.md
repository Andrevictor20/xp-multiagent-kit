# Structured Agent Handoff Policy

When delegating between specialized agents, pass a structured contract (via `agy-handoff` or structured JSON block) containing: `task_id`, `risk_level`, `surfaces`, `spec_path`, `tests.status` (`RED`/`GREEN`), `tests.command`, and `files_touched`. Free-form ambiguous delegation is forbidden. In multi-agent missions, always report total agent count and agent roster in the initial plan and final delivery.
