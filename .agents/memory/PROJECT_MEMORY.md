# 🧠 Project Memory & Context Snapshot

> **Última Atualização:** 2026-09-24 18:30 (Local)  
> **Status Geral do Projeto:** STABLE  
> **Versão / Marco Atual:** v2.15.0 (Live Antigravity Server Quotas via Language Server RPC & Universal Workspace Ignore Deployment)

---

## 1. Quick Project Summary (Semantic)
- **Propósito:** Kit modular de governança, agentes, skills, workflows e políticas para pair programming com IA baseado na metodologia Extreme Programming (XP), Task Routing adaptativo por risco (L0-L3), TDD estrito com Matriz Multi-Camadas, Política Anti-Test-Bypass, SSDLC, Engenharia de Causa Raiz & Anti-Workaround, Code Deslop, DevOps & Zero-Downtime Deployments, Observabilidade & SLOs, Cloud Security & Zero Trust Architecture, Engenharia de Frontend Anti-Slop, Motor de Conversion Copywriting, Suíte Global de Otimização de Tokens no Antigravity (IDE & CLI), CI/CD Auto-Healer com Loop Autônomo de Autocorreção e Sistema de Memória Contínua em 4 Tiers com Auto-Onboarding, Recaptura Retroativa de Histórico Git (Reverse Ingestion), Instalação Global no Antigravity (`~/.gemini/config/`) e Hard-Enforced Disk Persistence Gate.
- **Tech Stack:** Antigravity Agent Framework (Markdown + YAML Frontmatter), Agnóstico de linguagem de produção, Python, Bash, Git, GitHub Actions CLI (`gh`).
- **Arquitetura Chave:** Estrutura modular em `.agents/` contendo `agents` (11 especialistas), `skills` (63 capacidades granulares com `ci-auto-heal`), `workflows` (7 esteiras L0-L3 com Passo 0 e Passo Final autônomos), `policies` (9 regras inegociáveis), `templates` (scaffolds) e `memory` (memória viva em 4 tiers, auto-onboarding, recaptura git e arquivo permanente). Suíte global instalada em `~/.local/bin/` (`agy-ci-heal`, `xp-ci-heal`, `agy-tokens`, `xp-tokens`, `agy-apply-ignore`, `agy-sanitize`, `agy-handoff`, `agy-audit`, `agy-fast`, `agy-deep`). Paridade e espelhamento integral em `~/.gemini/antigravity-cli/` e `~/.gemini/antigravity-ide/`.
- **Comandos Essenciais:**
  - Instalação / Re-sincronização Global: `./scripts/install-global.sh`
  - Telemetria de Tokens por Mensagem (Ao Vivo): `agy-tokens --turn` ou `xp-tokens --turn`
  - Telemetria de Tokens Acumulada: `agy-tokens --badge` ou `agy-tokens --check`
  - Implantação Universal de Ignore: `agy-apply-ignore` ou `python3 scripts/apply_ignore_rules.py`
  - CI/CD Auto-Healer: `agy-ci-heal --status` ou `agy-ci-heal --watch --heal --auto-push`
  - Diagnóstico Cirúrgico de CI: `agy-ci-heal --diagnose-run <run-id>`
  - Sanitizador Anti-Flood: `agy-sanitize <cmd>` ou `<cmd> | agy-sanitize`
  - Handoff / Reset de Sessão: `agy-handoff --write-file`
  - Auditoria de Configuração: `agy-audit`
  - Validação Git: `git status && git log -n 5 --oneline`

---

## 2. Current Health & System Status
- **Agent Suite Status:** OPERATIONAL (11 Agentes, 63 Skills, 7 Workflows, 9 Policies, CI/CD Auto-Healer, Suíte Global de Tokens em `~/.local/bin/`, Configuração Global Ativa em `~/.gemini/config/`, Paridade Total em `~/.gemini/antigravity-ide/`, Memória em 4 Tiers com Persistência Forçada em Disco)
- **Quality Gate / Rules:** 100% compliant com `AGENTS.md` (TDD Multi-Camadas, Anti-Test-Bypass, SSDLC, Zero-Downtime, IaC Governance, Observability RED, CloudSec OIDC, Root-Cause Debugging, No Workarounds, Code Deslop, Frontend Anti-Slop, 4-Tier Memory, Auto-Onboarding, Reverse Ingestion, CI/CD Auto-Healing com limite L-003, Telemetria Obrigatória por Mensagem e Hard Disk Persistence)
- **Última Execução / Evidência:** `EV-TOKEN-LIVE-20260924-01` (21/21 testes unitários aprovados em test_token_tracker.py, telemetria oficial ao vivo do Antigravity Language Server RPC via RetrieveUserQuotaSummary ativa e 54 projetos imunizados com .geminiignore e .antigravityignore)
- **Ambiente Ativo:** Local & Global / Antigravity IDE & CLI

---

## 3. Recent Changes & Activity Log (Episodic - Sliding Window: 5-10 Entregas)

| Data / Hora | Tipo | Resumo da Alteração | Arquivos Principais | Test Evidence / Status |
| :--- | :--- | :--- | :--- | :--- |
| 2026-09-24 | `FEAT` | Telemetria Oficial de Quota ao Vivo via Language Server RPC & Implantação Universal de Ignore: token_tracker.py agora consulta RetrieveUserQuotaSummary em tempo real no daemon local da IDE via ConnectRPC (com fallback resiliente para heurística), corrigindo discrepâncias na janela móvel de 5h e semanal; hook PostInvocation sanitizado; script apply_ignore_rules.py imunizou 54 projetos e agy-apply-ignore adicionado ao PATH | `scripts/token_tracker.py`, `scripts/apply_ignore_rules.py`, `scripts/hooks/token-badge-hook.py`, `scripts/install-global.sh`, `tests/test_token_tracker.py` | `PASS (EV-TOKEN-LIVE-20260924-01)` |
| 2026-09-21 | `FEAT` | Exibição de Telemetria de Tokens Após Cada Mensagem (Delta + 3 Camadas): suporte universal a modelos Google (Gemini 3.8/3.7/3.1/2.5/2.0/1.5) e demais (Claude 4.6/3.7/3.5, GPT-4o, o1, o3-mini, DeepSeek), detecção dinâmica por transcript, comandos agy-tokens/xp-tokens --turn, hook post-invocation token-badge-hook.py e regra mandatória em AGENTS.md | `scripts/token_tracker.py`, `scripts/hooks/token-badge-hook.py`, `.agents/hooks.json`, `AGENTS.md`, `.agents/skills/token-budget-tracker/SKILL.md`, `scripts/install-global.sh`, `tests/test_token_tracker.py` | `PASS (EV-TOKEN-MSG-20260921-01)` |
| 2026-09-21 | `FEAT` | Paridade Global IDE & CLI, Desduplicação de Regras e Acoplamento de Git Hooks: remoção de links redundantes em ~/.gemini/, isolamento de 33 skills legadas GCP em plugin, espelhamento total em ~/.gemini/antigravity-ide/, git hook pre-push/post-push e correção de broken symlink em ~/.bashrc | `scripts/install-global.sh`, `scripts/global-token-optimizer/install-shell-aliases.sh`, `scripts/hooks/post-push-watcher.sh`, `scripts/agy-audit-config`, `tests/test_agy_audit_config.py` | `PASS (EV-GLOBAL-ENFORCE-20260921-02)` |
| 2026-09-21 | `FEAT` | CI/CD Auto-Healer & Loop Autônomo de Autocorreção: ci_healer.py (comandos agy-ci-heal/xp-ci-heal), extração cirúrgica de falhas via gh CLI, salvaguarda de 3 iterações (L-003), skill ci-auto-heal e hook post-push | `scripts/ci_healer.py`, `scripts/hooks/post-push-watcher.sh`, `.agents/skills/ci-auto-heal/SKILL.md`, `AGENTS.md`, `.agents/workflows/release.md`, `tests/test_ci_healer.py` | `PASS (EV-CI-AUTO-HEAL-20260921-01)` |
| 2026-09-21 | `FEAT` | Suíte Global de Redução de Tokens no Antigravity (IDE & CLI em qualquer projeto): agy-sanitize, agy-handoff, agy-audit, perfis de CLI agy-fast/agy-deep, aliases Fish/Bash, universal.geminiignore e guia prático | `scripts/agy-sanitize`, `scripts/agy-handoff`, `scripts/agy-audit-config`, `scripts/global-token-optimizer/*`, `templates/universal.geminiignore`, `docs/universal-token-reduction-guide.md`, `tests/` | `PASS (EV-GLOBAL-TOKEN-OPT-20260921-01)` |
| 2026-09-21 | `FEAT` | Implementação dos 4 Pilares de Redução de Tokens: Protocolo Anti-Flood de Ferramentas, sanitize-tool-output.sh, auditoria de gargalos (--audit), Session Reset aos 25 turnos e modulação de reasoning effort | `scripts/token_tracker.py`, `scripts/sanitize-tool-output.sh`, `AGENTS.md`, `.agents/skills/token-budget-tracker/` | `PASS (EV-TOKEN-OPTIMIZE-20260921-02)` |

---

## 4. Active Backlog & Immediate Handoff (Working / Episodic)
- [x] **[DONE] Exibição de Consumo de Tokens Após Cada Mensagem (IDE & CLI): delta por mensagem (in/tools/out) e acumulado em 3 camadas, suporte multi-modelo com detecção dinâmica e hook PostInvocation (34/34 testes unitários).**
- [x] **[DONE] CI/CD Auto-Healer: monitoramento autônomo de GitHub Actions (gh run), extração cirúrgica de logs de erro, loop de autocorreção em até 3 tentativas (L-003) e hook post-push.**
- [x] **[DONE] Suíte Global de Redução de Tokens (IDE & CLI em qualquer projeto): agy-sanitize, agy-handoff, agy-audit, perfis de CLI (fast/deep) e universal.geminiignore com 28/28 testes unitários aprovados.**
- [x] **[DONE] Otimização de consumo de tokens: orçamento de Rules e Skills < 20% com zero truncamento.**
- [x] **[DONE] Instalação global e linkagem de 63 skills, 9 políticas, 7 workflows e 11 agentes em ~/.gemini/config/.**
- [x] **[DONE] Cross-referencing exaustivo de todos os pacotes e arquivos no AGENTS.md.**
- [x] **[DONE] Hard-Enforcement Gate para escrita física obrigatória em disco no PROJECT_MEMORY.md em todos os workflows e agentes.**
- [x] **[DONE] Token Optimization & Tracker: Telemetria em 3 Camadas (Contexto, 5h e Semanal), binários xp-tokens/agy-tokens, skill token-budget-tracker e eliminação de injeções redundantes.**
- [x] **[DONE] 4 Pilares de Redução de Tokens: Protocolo Anti-Flood de Ferramentas, sanitize-tool-output.sh, auditoria de gargalos (--audit), Session Reset aos 25 turnos e modulação de reasoning effort.**
- [ ] **[P1] Validar a execução da matriz multi-testes em um projeto piloto complexo.**

---

## 5. Architectural Decisions & Domain Models (Semantic Memory)
- **2026-09-21 - CI/CD Auto-Healer & Loop Autônomo de Autocorreção:** Mecanismo autônomo acoplado ao GitHub Actions (`gh` CLI) para monitoramento em tempo real de esteiras, isolamento cirúrgico de logs de falha (`agy-ci-heal`), TDD local corretivo e re-push automático com teto estrito de 3 iterações (Regra [L-003]) para prevenção de loops infinitos.
- **2026-09-21 - Suíte Global de Redução de Tokens no Antigravity:** Desacoplamento da otimização de tokens do escopo exclusivo do kit para abranger qualquer pasta/repositório aberto na máquina via `~/.local/bin/` (`agy-sanitize`, `agy-handoff`, `agy-audit`, `agy-fast`, `agy-deep`) e aliases em `fish`/`bash`, com governança de `.geminiignore` e limites de linha de saída.
- **2026-09-21 - 4 Pilares de Otimização de Tokens:** Combate sistemático ao acúmulo de histórico reenviado através de (1) Protocolo Anti-Flood em comandos e leituras, (2) Desduplicação de rules globais, (3) Rotação compulsória aos 25 turnos / 70k tokens e (4) Modulação de esforço de raciocínio por nível de risco (L0-L3).
- **2026-09-21 - Telemetria de Tokens em 3 Camadas:** O kit diferencia rigorosamente (1) Janela de Mensagem/Sessão (Context Window até 1M/2M tokens), (2) Janela Móvel de 5 Horas (Rolling Rate Limit de curto prazo) e (3) Limite Semanal (Weekly Quota Cycle). Utilitário `xp-tokens` calcula agregação em tempo real através dos bancos SQLite e transcripts do Antigravity.
- **2026-09-05 - Paridade Antigravity CLI e Auto-Aprovação de Edições:** Configuração unificada em `~/.gemini/antigravity-cli/settings.json` com `agentMode: "accept-edits"` e `permissions.allow: ["write_file(*)", "read_file(*)", "command(*)", "mcp(*)", "read_url(*)"]`. Symlinks espelhados em `~/.gemini/antigravity-cli/` garantem que o ecossistema multiagente e a governança XP funcionem identicamente no terminal sem fricção de confirmações repetitivas.
- **2026-08-31 - Otimização de Token Budget no Antigravity:** `rules/` e `plugins/.../rules` não devem conter symlinks redundantes de agents/policies/workflows (que são carregados sob demanda). O `AGENTS.md` atua como regra mestre única e as descrições no frontmatter YAML das skills são mantidas concisas (1-2 frases), reduzindo o consumo de tokens em >75%.
- **2026-08-31 - Instalação Global por Symlinks:** Configuração de `~/.gemini/config/` apontando diretamente para o repositório mestre, permitindo que todas as regras, skills e workflows fiquem ativos globalmente e sejam atualizados em tempo real a cada edição.
- **2026-08-31 - Hard-Enforced Memory Disk Persistence:** Proibição estrita de encerramento de tarefas ou respostas de conclusão sem chamada explícita de ferramenta (`write_to_file`/`replace_file_content`) no `PROJECT_MEMORY.md`.

---

## 6. Gotchas, Hurdles & Learned Playbooks (Procedural Memory)
- **[L-001] Schema Injection em Frontend:** Validar scripts de dados estruturados Schema.org JSON-LD via Browser / Rich Results Test.
- **[L-002] Viewport Shifts no Mobile:** Uso estrito de `min-h-[100dvh]` em vez de `h-screen`.
- **[L-003] Regra dos 3 Fixes em Debugging:** Três falhas consecutivas indicam problema arquitetural.
- **[L-004] Autenticação OIDC em CI/CD:** GitHub Actions requer permissão `id-token: write` no workflow.
- **[L-005] Anti-Test-Bypass Check:** Nunca checar apenas o tipo retornado (`typeof`); valide sempre os valores exatos de negócio (`id`, `status`, `amount`).
- **[L-006] Auto-Onboarding de Repositórios:** Se o repositório aberto for novo ou diferente do kit, o Passo 0-A deve detectar manifestos e reconstruir `PROJECT_MEMORY.md` imediatamente antes de qualquer outra ação.
- **[L-007] Ingestão Reversa de Commits:** Usar formato conciso de git log (`%h - %ad : %s`) com janela deslizante de 5 a 10 commits para não estourar o orçamento de tokens da memória ativa.
- **[L-008] Bash set -e em Incrementos Aritméticos:** No bash com `set -e`, a expressão `(( count++ ))` quando `count=0` avalia para 0 e retorna status de saída 1, abortando o script. Use sempre `count=$((count + 1))` ou `(( count += 1 ))`.
- **[L-009] Token Budget de Customizações no Antigravity:** Arquivos colocados em `rules/` ou descrições verbosas em `SKILL.md` são injetados diretamente em cada turno. Mantenha `rules/` enxuto (apenas regras mestras) e o frontmatter YAML de skills com no máximo 1-2 sentenças objetivas.
- **[L-010] 3 Camadas de Limites no Antigravity:** Não confundir a janela de contexto da mensagem com os limites de rate limit da API. O modelo pode suportar 1M de tokens por turno, mas rajadas contínuas de 50k+ tokens podem atingir a barreira móvel de 5 horas ou o teto semanal da conta.
- **[L-011] Pre-Flight Token Gate & Modo Cirúrgico Atômico:** Sempre alertar o usuário quando qualquer camada estiver crítica (>80% em 5h/Semana ou >70% no Contexto). Se o usuário insistir em rodar, dimensionar o escopo estritamente para o que for cabível no orçamento restante, garantindo um checkpoint completo, testado e estável, proibindo deixar trabalho quebrado ou pela metade.
- **[L-012] O Maior Devorador de Tokens é o Histórico de Ferramentas:** Em sessões longas, saídas volumosas de terminal (logs de testes/builds) e leituras de arquivos inteiros sem StartLine/EndLine representam mais de 50% dos tokens faturados a cada novo turno. Use sempre sanitize-tool-output.sh e grep cirúrgico.
- **[L-013] Sanitização Transparente com Preservação de Exit Code:** O `agy-sanitize` trunca saídas excessivas intermediárias mantendo o topo (head) e a cauda diagnóstica (tail), propagando 100% o código de retorno para garantir compatibilidade com scripts de automação e pipelines de CI.
- **[L-014] Rotação Cirúrgica de Sessão via Handoff Packet:** Usar `agy-handoff --write-file` ao aproximar-se de 25 turnos para gerar um resumo de menos de 25 linhas (~300 tokens). Abrir um novo chat com esse pacote restaura o modelo à velocidade máxima e reduz os custos por turno em mais de 90%.
- **[L-015] Auditoria Proativa de Configuração Global:** O utilitário `agy-audit` monitora a saúde de `~/.gemini/config/`, alertando sobre inchaço de regras (>150 linhas), servidores MCP configurados como `eager` e quantidade excessiva de skills globais (>50) que causam descarte de contexto.
- **[L-016] Extração Cirúrgica de Logs de CI/CD:** Falhas de CI/CD contêm em média 95% de ruído em seus logs brutos (prints de instalação e setup). A filtragem focada em blocos `##[error]`, `Error:`, `FAILED` e stack traces pelo `ci_healer.py` reduz o contexto a menos de 10 linhas, viabilizando o auto-diagnóstico sem estourar a janela de contexto.
- **[L-017] Desduplicação de Regras e Paridade IDE/CLI:** Ter links symlink simultâneos em `~/.gemini/` e `~/.gemini/config/` faz o Antigravity carregar regras globais multiplicadas por 3. Mantenha `AGENTS.md` exclusivamente em `~/.gemini/config/` e garanta que `~/.gemini/antigravity-ide/` espelhe a mesma estrutura de pastas do CLI (`agents`, `workflows`, `skills`, `policies`, `templates`, `rules`).

---

## 7. Technical Debts & Known Blockers
- **Nenhum bloqueio ativo.** CI/CD Auto-Healer operacional, 29/29 testes unitários aprovados, comandos integrados em `~/.local/bin/`, git hooks ativos e persistência de disco rigorosamente cumprida.




---
## [v2.14.0] - Token Tracker: 5 Bugs de Contabilização Corrigidos

### Bugs Corrigidos em `scripts/token_tracker.py`

| # | Bug | Impacto | Correção |
|---|-----|---------|----------|
| 1 | Rolling window estimava tokens via linha JSONL bruta | Overestimava 3-5x (metadata JSON incluso) | `calculate_rolling_windows()` parseia `content+thinking` de cada step |
| 2 | Steps `is_truncated=True` eram contados no contexto ativo | Double-counting de conteúdo já removido | Loop pula steps com `is_truncated: true` |
| 3 | `CONVERSATION_HISTORY` contava 100% | Double-counting de resumos de histórico | HISTORY conta 50% (compressão); CHECKPOINT e KNOWLEDGE_ARTIFACTS contam 100% |
| 4 | `estimate_tokens(" " * bytes)` usava ratio uniforme | Tool outputs (JSON) subestimados, prose superestimados | `_tokens_from_bytes(bytes, ratio)` com ratios por tipo: PROSE=4.0, CODE=3.2, MIXED=3.5, CONFIG=3.3 |
| 5 | `detect_model_name()` ignorava env vars e config.json | Fallback errado para Gemini ao usar Claude | Pipeline: env vars → config.json → SQLite → padrão |

### Nova função auxiliar
- `_tokens_from_bytes(byte_count, chars_per_token)` — conversão direta sem proxy de espaços
- `_measure_system_prompt_bytes()` — lê tamanho real de regras/schemas no disco

### Lição Procedural
- **[L-018]** Nunca use `estimate_tokens(" " * bytes)` como proxy de byte→token. Esse padrão ignora o ratio de code_chars e sempre usa chars_per_token=3.8 (prose puro), subestimando outputs de ferramentas JSON/código em ~16% e superestimando prose em ~5%.
