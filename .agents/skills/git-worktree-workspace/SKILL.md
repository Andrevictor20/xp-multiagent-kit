---
name: git-worktree-workspace
description: Isolamento físico de subagentes e tarefas paralelas em Git Worktrees limpos, eliminando contaminação do repositório principal.
---

# Git Worktree Workspace Skill

Esta skill governa o uso de **Git Worktrees** para isolar completamente a execução de subagentes e explorações arquiteturais arriscadas, impedindo a contaminação da working tree principal do desenvolvedor.

---

## 1. Por que usar Git Worktrees com Agentes?
- **Isolamento Total:** Subagentes trabalham em branches e diretórios separados (`.agents/worktrees/<task-name>`), podendo compilar, quebrar testes e rodar ferramentas sem interferir no código em edição.
- **Rollback Instantâneo de Falhas:** Se o subagente não conseguir fazer os testes passarem ou produzir código insatisfatório, o worktree é destruído instantaneamente com `git worktree remove --force`, sem deixar resíduos de commits quebrados.
- **Merge Atômico e Controlado:** Apenas soluções verificadas com 100% de testes aprovados pelo `release-gatekeeper` são integradas à branch de trabalho principal.

---

## 2. Comandos e Utilitários (`agy-worktree`)

O kit fornece o utilitário nativo `agy-worktree` (e `xp-worktree`):

```bash
# 1. Criar um worktree isolado para uma tarefa
agy-worktree --create auth-oauth-refactor --base main

# 2. Listar worktrees ativos
agy-worktree --list

# 3. Remover um worktree e deletar a branch associada após conclusão ou descarte
agy-worktree --remove auth-oauth-refactor

# 4. Limpar todos os worktrees órfãos sob .agents/worktrees/
agy-worktree --clean-all
```

---

## 3. Protocolo de Delegação a Subagentes
1. O **`orchestrator`** cria o worktree isolado antes de disparar o subagente.
2. O subagente executa todo o ciclo TDD (RED -> GREEN -> REFACTOR) exclusivamente dentro do caminho do worktree.
3. Concluída a verificação pelo **`test-guardian`**, o **`builder`** ou **`orchestrator`** faz o cherry-pick/squash merge para a branch principal.
4. O **`archivist`** aciona `agy-worktree --remove <task>` para manter o workspace limpo.
