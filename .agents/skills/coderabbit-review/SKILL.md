---
name: coderabbit-review
version: 1.0.0
description: External AI diff review and security audit using CodeRabbit CLI with graceful fallback.
author: André Victor
license: MIT
tags: [code-review, coderabbit, static-analysis, diff-audit, security]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode, antigravity]
entrypoint: SKILL.md
---

# CodeRabbit Review (External Diff & Security Audit)

Audita diffs locais e segurança de código via CodeRabbit CLI como verificação externa opcional. Opera de forma 100% não-bloqueante: se a CLI não estiver instalada ou autenticada, aplica fallback automático para o EGM Pass 2 interno e ferramentas locais.

## 1. Princípio Fundamental: Não-Bloqueante & Zero Hard-Dependency

- **Nunca bloqueie o pipeline por ausência do CodeRabbit:** O XP Kit é autossuficiente e funciona offline com `code-review-graph`, linters locais e o modelo EGM de 3 passos (`xp-goldfish`).
- **Uso Opcional/Aditivo:** O CodeRabbit atua como uma segunda opinião externa especializada em diffs, bugs de regressão e segurança de código.
- Se a CLI estiver indisponível ou desautenticada, emita `[CODERABBIT_SKIPPED]` e prossiga normalmente sem falhar o gate.

## 2. Protocolo de Verificação de Ambiente

Antes de executar qualquer comando de revisão:

1. **Checar Presença do Binário:**
   ```bash
   command -v coderabbit >/dev/null 2>&1
   ```
2. **Checar Autenticação:**
   ```bash
   coderabbit auth status 2>/dev/null || coderabbit --version >/dev/null 2>&1
   ```
3. **Decisão:**
   - **Disponível e Autenticado:** Prosseguir para o Passo 3.
   - **Indisponível / Não Autenticado:** Registrar log e prosseguir com a governança nativa:
     ```text
     ℹ️ [CODERABBIT_SKIPPED]: CodeRabbit CLI não instalado ou não autenticado.
     Prosseguindo com linters locais, AST graph (code-review-graph) e EGM Pass 2 nativo.
     ```

## 3. Comandos de Execução Local (`--agent`)

Sempre utilize a flag `--agent` para saída em formato NDJSON estruturado para agentes de IA:

### 3.A Revisar Modificações Não-Commitadas (Inner Loop)
```bash
coderabbit review --agent --uncommitted
```

### 3.B Revisar Alterações contra Branch Base (Pre-PR / Conformance)
```bash
coderabbit review --agent --base main
```

### 3.C Revisar Diretório Específico
```bash
coderabbit review --agent --dir <caminho_do_modulo>
```

## 4. Tratamento de Severidades e Remediação

Ao processar a saída NDJSON:
- `critical` e `major`: Devem ser analisados obrigatoriamente. Se representarem falhas reais (vulnerabilidades, race conditions, leaks, quebras de contrato), devem ser corrigidos antes da aprovação do `refactor-warden` ou `release-gatekeeper`.
- `minor`, `trivial`, `info`: Avaliados contra as diretrizes do kit (`No God Files < 500 linhas`, `No Workarounds`, remoção de slop).
- **Sem falsos positivos:** Se um apontamento do CodeRabbit conflitar com uma regra explícita do XP Kit ou especificação aprovada, prevalece a especificação do kit.

## 5. Integração com Subagentes do Kit

- **`refactor-warden` (EGM Pass 2):** Dispara `coderabbit review --agent --uncommitted` após o código atingir status GREEN para detectar complexidade estática, duplicações e code smells adicionais.
- **`release-gatekeeper` (Conformance Gate):** Valida se não há pendências críticas em aberto apontadas pelo CodeRabbit antes da emissão do selo `PASS`.
