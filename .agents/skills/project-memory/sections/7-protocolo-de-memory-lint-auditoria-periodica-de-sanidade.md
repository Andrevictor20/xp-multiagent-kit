## 7. Protocolo de Memory Lint (Auditoria Periódica de Sanidade)

Antes de releases ou marcos importantes, o agente `archivist` deve rodar uma auditoria de sanidade na memória:
1. **Contradições:** Decisões antigas em conflito com a arquitetura atual?
2. **Stale Claims:** Links para arquivos deletados ou comandos obsoletos?
3. **Token Budget:** O arquivo ativo ultrapassou 300 linhas? (Se sim, mova entradas antigas para `archive/HISTORY.md`).
4. **Handoffs Antigos:** Handoffs pendentes que já foram executados devem ser marcados como `[DONE]`.
