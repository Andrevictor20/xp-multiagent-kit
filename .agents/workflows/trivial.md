---
name: trivial
description: "Workflow mínimo para alterações triviais (typo, doc, css)."
---
# Trivial Workflow (L0)

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) [com Auto-Onboarding se não inicializado/divergente] → orchestrator → builder → validation → **Passo Final OBRIGATÓRIO (Hard-Enforcement Gate): Escrita Física em Disco no `.agents/memory/PROJECT_MEMORY.md` pelo `archivist`**

## Guidelines
- Não executar pipeline completo de TDD/Segurança.
- Foco em resolver a tarefa com o mínimo de passos e tokens.
- **Fast-Path L0 & Isenção de Testes de Código:** Proibido executar suítes de testes unitários ou de integração quando a alteração for estritamente em documentação (`.md`, `.txt`, `.rst`, docstrings, `.gitignore`) ou estilos cosméticos. Validação estática e git status bastam.
- **Persistência Concisa em Memória:** O `archivist` deve persistir apenas uma linha resumida no log episódico do `.agents/memory/PROJECT_MEMORY.md` via `replace_file_content`, sem ler nem reenviar o arquivo de memória inteiro.
- **Hard-Enforced Auto-Sync:** O `archivist` DEVE fisicamente persistir a alteração concisa no `.agents/memory/PROJECT_MEMORY.md` antes de encerrar o turno. Nenhuma tarefa é dada como concluída sem a gravação em disco.
