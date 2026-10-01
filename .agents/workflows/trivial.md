---
name: trivial
description: "Workflow mínimo para alterações triviais (typo, doc, css)."
---
# Trivial Workflow (L0)

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) [com Auto-Onboarding se não inicializado/divergente] → builder → validation estática → **Passo Final OBRIGATÓRIO (Hard-Enforcement Gate): Escrita Física em Disco no `.agents/memory/PROJECT_MEMORY.md` pelo `archivist`**

## Colapso de Agentes (E3)
Apenas `builder` → `archivist`. Sem `orchestrator` (o roteamento é inferido na primeira linha da resposta), sem `navigator`, `test-guardian`, `refactor-warden` ou `release-gatekeeper`. Cada agente adicional é um contexto novo relendo specs e memória.

## Orçamento
- **Máximo de 3 chamadas de ferramenta** (`TURN_BUDGET["L0"]` em `scripts/kit_constants.py`).
- Consultas conceituais, dúvidas e explicações: **zero ferramenta**, resposta direta.
- Chamadas independentes no mesmo turno (batching).
- Comandos via `agy-run "<cmd>"` para remover banner/ruído e registrar telemetria.

## Guidelines
- Não executar pipeline completo de TDD/Segurança.
- Foco em resolver a tarefa com o mínimo de passos e tokens.
- **Fast-Path L0 & Isenção de Testes de Código:** Proibido executar suítes de testes unitários ou de integração quando a alteração for estritamente em documentação (`.md`, `.txt`, `.rst`, docstrings, `.gitignore`) ou estilos cosméticos. Validação estática e git status bastam.
- **Persistência Concisa em Memória:** O `archivist` deve persistir apenas uma linha resumida no log episódico do `.agents/memory/PROJECT_MEMORY.md` via `replace_file_content`, sem ler nem reenviar o arquivo de memória inteiro.
- **Hard-Enforced Auto-Sync:** O `archivist` DEVE fisicamente persistir a alteração concisa no `.agents/memory/PROJECT_MEMORY.md` antes de encerrar o turno. Nenhuma tarefa é dada como concluída sem a gravação em disco.
