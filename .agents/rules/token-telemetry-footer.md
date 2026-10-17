# Mandatory Compact Token Telemetry Footer — Universal Rule (IDE & CLI)

Every final assistant response across any project MUST end with the compact 4-line telemetry block (with two trailing spaces `  \n` per line for Markdown line breaks), while keeping all user-facing prose in **Portuguese**:

```text
Contexto: [{bar_ctx}] {pct_ctx}% ({tot_ctx} / {win_str})  
Limites:  5h [{bar_5h}] {pct_5h_used}% usado (↻ {renova_5h}) • Semana [{bar_7d}] **{pct_7d_rem}% livre** (↻ {renova_7d})  
Consumo:  {turn_tot} tok (In: {turn_in} | Tool: {turn_tools} | Out: {turn_out})  
Modelo:   {display_model} ({effort_level}) • Janela: {win_str} • Saída: {max_out_str}
```

### Rules:
1. **Compact & Clean:** Show ONLY `Contexto`, `Limites` (5h & Semana), `Consumo`, and `Modelo`. Do not include `Reenvio:` or `RTK:` lines in the chat footer.
2. **Exact Copy from Hook / CLI:** Copy the live block injected by `dynamic-effort-router` or output by `agy-tokens --turn` (`xp-tokens --turn`).
3. **Terminal Colors:** When running `xp-tokens` / `agy-tokens` directly in a terminal TTY (or with `--color`), ANSI colors are rendered automatically.
