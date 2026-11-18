# Adapter: OpenDesign (`od` CLI / `open-design` MCP)

Use this adapter when the `design` pack (`open-design` MCP or `od`) is enabled in the workspace.

| Skill verb | In OpenDesign |
|---|---|
| Start / Read context | `list_projects` / `get_active_context` / `get_project` to locate active brief and design files |
| Brief & confirmation | `collect_brief` / `confirm_brief` or `DESIGN.md` at project root (`DESIGN.md` remains the canonical brief) |
| Read existing artifacts | `list_files`, `search_files`, `get_file`, `get_artifact` |
| Create / update design | `create_artifact` / `write_file` (or build rendered HTML boards via `html.md`) |
| Look at it | Render HTML fallback (`html.md`) at desktop (`1280px`) and mobile (`390px`) widths with Playwright or headless browser before `craft-critique` |
