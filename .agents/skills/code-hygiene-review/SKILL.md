---
name: code-hygiene-review
description: Strict code quality guardian enforcing atomic commits, code deslop, YAGNI diff simplification, no-workarounds, and no god files.
---

# Code Hygiene Review (`code-hygiene-review`)

Consolida as disciplinas de **Higiene de Código**, **Commits Atômicos**, **No-Workarounds**, **Diff Simplification** e **No-God-Files**.

## 1. Commits Atômicos & Git Ops
- Cada commit deve conter uma unidade única, indivisível e testada de trabalho.
- Mensagens padronizadas segundo Conventional Commits: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`.
- A suíte de testes deve passar (100% verde) em cada commit individual.

## 2. No Workarounds & Causa Raiz
- **Proibição Absoluta de Contornos:** Nunca suprimir tipagem (`as any`, `@ts-ignore`, `# type: ignore`) ou testes para passar gates.
- **Sem Sleeps Arbitrários:** Substituir `time.sleep()` ou pausas temporais por polling condicional determinístico ou awaits de estado.
- Resolver sempre a causa raiz ao invés de mascarar sintomas.

## 3. Deslop & Simplificação de Diff (YAGNI)
- Remoção ativa de código morto, variáveis não utilizadas, comentários gerados por IA e prosa redundante.
- Minimalismo de diff: alterar somente os arquivos estritamente necessários para satisfazer o contrato da tarefa.
- Sem abstrações para requisitos hipotéticos.

## 4. No God Files (< 500 Linhas)
- Nenhum arquivo de código de produção, script ou suíte de testes deve ultrapassar 500 linhas.
- Ao aproximar-se do teto, refatorar extraindo submódulos de responsabilidade única.
- Sem duplicação de lógica entre módulos.
