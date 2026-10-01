## 3. O Ciclo de Vida Autônomo da Memória (Zero-Prompt Lifecycle)

> **⚠️ REGRA DE OURO:** O agente NUNCA deve esperar que o usuário peça "leia a memória", "use o PROJECT_MEMORY.md" ou "atualize a memória". O ciclo abaixo é executado **automaticamente em toda e qualquer tarefa**.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      CICLO DE VIDA DA MEMÓRIA                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. INÍCIO (Passo 0 / 0-A)                                              │
│    Fast Context Bootstrap: Lê PROJECT_MEMORY.md                        │
│    (Se não adaptado -> Executa Auto-Onboarding & Git Recapture)        │
├────────────────────────────────────────────────────────────────────────┤
│ 2. EXECUÇÃO (TDD / Builder / Refactor)                                 │
│    Consulta Procedural Memory (Gotchas [L-NNN]) para evitar erros      │
│    Registra novos aprendizados não-óbvios                              │
├────────────────────────────────────────────────────────────────────────┤
│ 3. ENCERRAMENTO (Passo Final)                                          │
│    Archivist Auto-Sync: Atualiza PROJECT_MEMORY.md com a entrega,      │
│    evidência de testes reais, backlog e poda se > 300 linhas           │
└────────────────────────────────────────────────────────────────────────┘
```

### Fase 1: Fast Context Bootstrap no Início (Passo 0)
- Todo prompt ou tarefa inicia consultando `.agents/memory/PROJECT_MEMORY.md` e `.agents/memory/REPO_MAP.md`.
- Carrega instantaneamente a arquitetura, comandos de teste, últimas alterações, armadilhas conhecidas e mapa de símbolos AST, eliminando dezenas de tool calls exploratórias (`list_dir`, `grep_search`, `find`) e milhares de tokens.

### Fase 2: Aplicação Procedural Durante a Execução
- Durante o desenvolvimento, o agente verifica as armadilhas listadas em **Gotchas & Learned Playbooks** para garantir que soluções incompatíveis não sejam repetidas.
- Se um novo obstáculo ou peculiaridade de biblioteca for resolvido, formaliza a lição no padrão `[L-NNN]` (`lesson-learned`).

### Fase 3: Auto-Sync Obrigatório de Encerramento (Passo Final)
- Antes de entregar a resposta final ou walkthrough ao usuário, o agente simula o `archivist` e atualiza `.agents/memory/PROJECT_MEMORY.md`:
  - **Timestamp e Status:** Atualiza `Última Atualização` e `Status Geral`.
  - **Recent Changes:** Adiciona a nova linha na tabela com data, tipo (`FEAT`, `FIX`, `REFACTOR`, `CHORE`), resumo conciso, arquivos tocados e evidência de testes (`PASS (exit_code: 0)`).
  - **Active Backlog:** Marca `[x] [DONE]` nas tarefas concluídas e adiciona novos itens se identificados.
  - **ADRs & Gotchas:** Adiciona novas decisões de arquitetura ou gotchas se aplicável.
  - **Pruning (Sliding Window):** Se o log exceder 10 entradas ou o arquivo ultrapassar 300 linhas, move entradas antigas para `archive/HISTORY.md`.

---
