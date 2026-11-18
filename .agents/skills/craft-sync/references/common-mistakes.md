# `design-sync.json` & Common mistakes (`craft-sync`)

## `design-sync.json`

```json
{
  "source": "packages/ui/tokens.css",
  "tool": "paper: file 'Fieldnote', page 'Guide'",
  "naming": "CSS custom property names as written in the source",
  "synced": "2026-11-15",
  "tokens": { "--color-accent": "#2e6b57", "--radius-md": "10px" },
  "components": { "Button": "drawn", "Badge": "drawn", "Input": "in code only" }
}
```

- `tokens` holds the values **both sides agreed on** at the last sync, and only those.
- A component import changes only its own `components` entry.

## Common mistakes

| Thought | Reality |
|---|---|
| "The code has the system, so setup only needs the brief" | Offer the import, or the tool never gets a guide and screens drift from the code. |
| "I'll build foundations and an index, components later" | Show the inventory and ask which components to draw now. |
| "I'll rename `--sand-200` to a role name while importing" | Keep the code's name; propose a role as an open question. |
| "The tool already has `--color-accent`, I'll update it" | That's a conflict for the inventory stop, not a silent overwrite. |
| "Guide and code differ, so the guide is out of date" | Check `design-sync.json`: it may be the person's unexported change. |
| "The diff is tiny, I'll just apply it" | Propose, stop, then apply and run the project's checks. |

## Rules

| Rule | Why |
|---|---|
| Same names in code and tool, by one written naming rule | One name per decision; no mapping to drift |
| `design-sync.json` records only agreed values | Without the last agreed value, "who changed it?" is a guess |
| Inventory and pick before drawing; conflicts listed there | Big packages and existing tool tokens need the person's say |
| Values from code, never from screenshots | Screenshots round colours and sizes |
| Missing states drawn as "proposed" | The guide must not claim the code does what it doesn't |
| Export proposes, then stops; edits the source, not generated output | Code ships to users; a generated file is overwritten by the next build |
| Both changed → ask | Overwriting either side loses someone's decision |
| Code is the source of truth until the person says otherwise | Matches "code beats a stale brief" |
