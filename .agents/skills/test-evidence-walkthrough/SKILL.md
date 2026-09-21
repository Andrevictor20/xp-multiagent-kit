---
name: test-evidence-walkthrough
description: "Validação de evidência de testes nativos de acordo com risco (L0-L4)."
---

# Test Evidence Walkthrough

Evidências vazias como "os testes passaram" não são aceitas. O nível de evidência exigido depende do tipo da tarefa.

## Evidence Levels
- **L0 — Trivial**: (typo, documentação). Nenhuma evidência de teste exigida.
- **L1 — Small**: (CSS simples, alterações declarativas). Comando e resultado do comando.
- **L2 — Feature**: (nova funcionalidade). Execução do teste + output bruto (ex: colado no walkthrough).
- **L3 — Release**: (mudança em ambiente). CI artifact / log do pipeline de aprovação de CI.
- **L4 — Mudança Crítica**: Evidência originada de staging/produção, garantindo que foi validada além do ambiente de dev.

A tarefa não avança de fase (RED ou GREEN) se o nível de evidência exigido não for apresentado.
