# 🧠 Project Memory & Context Snapshot

> **Última Atualização:** 2026-09-26 17:08 (Local)  
> **Status Geral do Projeto:** STABLE  
> **Versão / Marco Atual:** v2.33.0 (Autonomous Session Checkpointing, Background Daemon & Terminal Dashboard)

---

## 1. Quick Project Summary (Semantic)
- **Propósito:** Kit modular de governança, agentes, skills, workflows e políticas para pair programming com IA baseado na metodologia Extreme Programming (XP), Task Routing adaptativo por risco (L0-L3), TDD estrito com Matriz Multi-Camadas, Política Anti-Test-Bypass, SSDLC, Engenharia de Causa Raiz & Anti-Workaround, Code Deslop, DevOps & Zero-Downtime Deployments, Observabilidade & SLOs, Cloud Security & Zero Trust Architecture, Engenharia de Frontend Anti-Slop, Motor de Conversion Copywriting, Suíte Global de Otimização de Tokens no Antigravity (IDE & CLI), CI/CD Auto-Healer com Loop Autônomo de Autocorreção e Sistema de Memória Contínua em 4 Tiers com Auto-Onboarding, Recaptura Retroativa de Histórico Git (Reverse Ingestion), Instalação Global no Antigravity (`~/.gemini/config/`) e Hard-Enforced Disk Persistence Gate.
- **Tech Stack:** Antigravity Agent Framework (Markdown + YAML Frontmatter), Agnóstico de linguagem de produção, Python, Bash, Git, GitHub Actions CLI (`gh`).
- **Arquitetura Chave:** Estrutura modular em `.agents/` contendo `agents` (11 especialistas), `skills` (71 capacidades granulares com `ci-auto-heal`, `spec-driven-development`, `git-worktree-workspace`), `workflows` (10 esteiras com Passo 0 e Passo Final autônomos, incluindo SDD, Migration e Benchmark), `policies` (9 regras inegociáveis), `templates` (scaffolds) e `memory` (memória viva em 4 tiers, auto-onboarding, recaptura git e arquivo permanente). Suíte global instalada em `~/.local/bin/` (`agy-worktree`, `agy-ci-heal`, `xp-ci-heal`, `agy-tokens`, `xp-tokens`, `agy-apply-ignore`, `agy-sanitize`, `agy-handoff`, `agy-audit`, `agy-fast`, `agy-deep`, `agy-git-ops`, `agy-memory-archive`, `agy-health`). Paridade e espelhamento integral em `~/.gemini/antigravity-cli/` e `~/.gemini/antigravity-ide/`.
- **Comandos Essenciais:**
  - Instalação / Re-sincronização Global: `./scripts/install-global.sh`
  - Diagnóstico Global de Saúde: `agy-health`
  - Rotação Automática de Memória: `agy-memory-archive`
  - Operações Git & CI Compactas: `agy-git-ops status` / `diff` / `commit` / `push`
  - Telemetria de Tokens por Mensagem (Ao Vivo): `agy-tokens --turn` ou `xp-tokens --turn`
  - Telemetria de Tokens Acumulada: `agy-tokens --badge` ou `agy-tokens --check`
  - Implantação Universal de Ignore: `agy-apply-ignore` ou `python3 scripts/apply_ignore_rules.py`
  - CI/CD Auto-Healer: `agy-ci-heal --status` ou `agy-ci-heal --watch --heal --auto-push`
  - Diagnóstico Cirúrgico de CI: `agy-ci-heal --diagnose-run <run-id>`
  - Sanitizador Anti-Flood: `agy-sanitize <cmd>` ou `<cmd> | agy-sanitize`
  - Handoff / Reset de Sessão: `agy-handoff --write-file`
  - Retomada Instantânea de Sessão: `agy-resume` ou `agy-resume --prompt`
  - Busca FTS5 Rápida em Memória: `agy-memory-search "termo"` ou `agy-memory-search --index`
  - Daemon de Background & Watcher: `agy-daemon start` / `stop` / `status` / `run-once`
  - Dashboard Visual de Terminal (TUI): `agy-dashboard` ou `agy-dashboard --watch`
  - Auditoria de Configuração: `agy-audit`
  - Validação Git: `git status && git log -n 5 --oneline`

---

## 2. Current Health & System Status
- **Agent Suite Status:** OPERATIONAL (11 Agentes, 71 Skills, 10 Workflows, 9 Policies, CI/CD Auto-Healer, Suíte Global de Tokens, Git Ops, Memory Archiver e Health Scanner em `~/.local/bin/`, Configuração Global Ativa em `~/.gemini/config/`, Paridade Total em `~/.gemini/antigravity-ide/`, Memória em 4 Tiers com Persistência Forçada em Disco)
- **Quality Gate / Rules:** 100% compliant com `AGENTS.md` (TDD Multi-Camadas, Anti-Test-Bypass, SSDLC, Zero-Downtime, IaC Governance, Observability RED, CloudSec OIDC, Root-Cause Debugging, No Workarounds, Code Deslop, Frontend Anti-Slop, 4-Tier Memory, Auto-Onboarding, Reverse Ingestion, CI/CD Auto-Healing com limite L-003, Telemetria Obrigatória por Mensagem e Hard Disk Persistence)
- **Última Execução / Evidência:** `EV-DAEMON-DASHBOARD-RESUME-20260926-01` (Implementação do daemon desacoplado agy-daemon, dashboard visual TUI agy-dashboard, auto-snapshotting no agy-resume, 16/16 ferramentas no PATH e 170/170 testes unitários aprovados)
- **Ambiente Ativo:** Local & Global / Antigravity IDE & CLI

---

## 3. Recent Changes & Activity Log (Episodic - Sliding Window: 5-10 Entregas)

| 2026-09-26 | `FEAT` | Daemon em Background (agy-daemon), Dashboard Visual TUI (agy-dashboard) & Checkpoint Autônomo (agy-resume): (1) Implementação de `scripts/agy_daemon.py` e CLI `agy-daemon` como daemon leve em background (PID, log rotation, ciclo de 60s) executando monitoramento autônomo de CI/CD, auto-rotação de memória (>35KB) e garbage collection de worktrees, (2) Implementação de `scripts/agy_dashboard.py` e CLI `agy-dashboard` com interface TUI elegante em Python puro renderizando saúde do sistema, gauges ao vivo de cotas do Language Server RPC, telemetria de memória e sessões com suporte a `--watch`, (3) Expansão de `scripts/session_resumer.py` com `auto_snapshot` reativo e detecção de sessões interrompidas no Passo 0, (4) Atualização do instalador global e scanner de integridade para 16/16 ferramentas ativas no PATH, (5) 170/170 testes unitários aprovados | `scripts/agy_daemon.py`, `scripts/agy_dashboard.py`, `scripts/agy-daemon`, `scripts/agy-dashboard`, `scripts/session_resumer.py`, `scripts/agy_health.py`, `scripts/install-global.sh`, `tests/test_agy_daemon.py`, `tests/test_agy_dashboard.py`, `tests/test_session_resumer.py`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-DAEMON-DASHBOARD-RESUME-20260926-01)` |

| 2026-09-26 | `FEAT` | Motor de Busca Rápida FTS5 (agy-memory-search), Checkpoints Duráveis (agy-resume) & Transição no Projeto Saturn: (1) Implementação do motor `scripts/memory_search.py` e CLI `agy-memory-search` utilizando SQLite FTS5 para recuperação instantânea (<3ms, ~80 tokens) de lições aprendidas [L-NNN] e histórico episódico, (2) Implementação do motor de checkpoint durável `scripts/session_resumer.py` e CLI `agy-resume` com integração no `agy-handoff`, persistindo `.session_state.json` para retomada instantânea sem reexplicação de contexto, (3) Generalização do `scripts/memory_archiver.py` para suportar tanto tabelas quanto subseções markdown `### `, (4) Transição no projeto real `Saturn`: rotação com poda de 30.3 KB (~7.7k tokens poupados por leitura) em `PROJECT_MEMORY.md`, geração de `REPO_MAP.md` e indexação FTS5 com 133 itens indexados, (5) Atualização do `agy-health` para 14/14 ferramentas e 163/163 testes unitários aprovados | `scripts/memory_search.py`, `scripts/session_resumer.py`, `scripts/agy-memory-search`, `scripts/agy-resume`, `scripts/memory_archiver.py`, `scripts/install-global.sh`, `scripts/agy_health.py`, `tests/test_memory_search.py`, `tests/test_session_resumer.py`, `tests/test_memory_archiver.py`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-FTS5-RESUME-SATURN-ROLLOUT-20260926-01)` |

| 2026-09-26 | `FEAT` | Implementação de P2 (Filtro Anti-HTML & Cobertura Total de Testes) e P3 (Cache Incremental de AST no Repo Map): (1) Implementação de `compress_html` / `--html` no `scripts/context_compactor.py` reduzindo páginas HTML em até 85% e eliminando ruído CSS/SVG/JS, (2) Criação de testes unitários para scripts legados (`tests/test_apply_ignore_rules.py` 3/3 PASS, `tests/test_tool_size_guard.py` 3/3 PASS, `tests/test_agy_git_ops.py` 5/5 PASS), (3) Implementação de cache incremental persistente em `scripts/repo_map.py` com detecção de mtime/size em `.agents/memory/.repo_map_cache.json` evitando re-parsing de AST para arquivos inalterados, (4) Inclusão do arquivo de cache no `.gitignore`, (5) 155/155 testes unitários aprovados em toda a base de código do projeto | `scripts/context_compactor.py`, `scripts/repo_map.py`, `.gitignore`, `tests/test_context_compactor.py`, `tests/test_repo_map.py`, `tests/test_apply_ignore_rules.py`, `tests/test_tool_size_guard.py`, `tests/test_agy_git_ops.py`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-P2-P3-COMPACTION-AST-CACHE-20260926-01)` |

| 2026-09-26 | `FEAT` | Rotação Automática de Memória (Sliding Window) & Scanner de Saúde Global agy-health (P1): (1) Implementação do motor `scripts/memory_archiver.py` e CLI `agy-memory-archive` reduzindo `PROJECT_MEMORY.md` de 47.6 KB para 27.2 KB (~5.2k tokens poupados por leitura) mantendo 8 entregas ativas e movendo 32 entradas antigas para `archive/HISTORY.md`, (2) Integração de auto-arquivamento no `scripts/agy-handoff`, (3) Implementação do scanner de diagnóstico `scripts/agy_health.py` e CLI `agy-health` (<120ms) auditando RPC do Language Server, cotas ao vivo (>80% warn), integridade de plugins com auto-reparo e links no PATH, (4) Adição de symlinks em `install-global.sh` e resolução de links simbólicos via `readlink -f`, (5) 11 novos testes unitários adicionados com 100% de aprovação (142/142 testes totais) | `scripts/memory_archiver.py`, `scripts/agy-memory-archive`, `scripts/agy_health.py`, `scripts/agy-health`, `scripts/agy-handoff`, `scripts/install-global.sh`, `tests/test_memory_archiver.py`, `tests/test_agy_health.py`, `.agents/memory/PROJECT_MEMORY.md`, `.agents/memory/archive/HISTORY.md` | `PASS (EV-P1-MEMORY-ARCHIVER-HEALTH-20260926-01)` |

| 2026-09-26 | `FEAT` | Motor de Operações Git & CI/CD Ultra-Econômicas (< 1k tokens) & Auto-Healing de Plugins: (1) Implementação do utilitário `scripts/agy-git-ops` com status compacto (`git status -s`), diffs resumidos (`git diff --stat`), log oneline e push silencioso, (2) Extensão do `scripts/context_compactor.py` com modos `--ci` (eliminação de ruído de steps bem-sucedidos do GitHub Actions e isolamento de stacktrace) e `--git` (colapso de untracked files), (3) Blindagem no `scripts/hooks/smart_tool_optimizer.py` interceptando `gh run/workflow/release` e comandos git não restritos, com preservação de comandos compactos (`gh run list -L 5`, `git show --stat`), (4) Auto-Healing transparente dos diretórios de plugins internos em `scripts/hooks/dynamic_effort_hook.py`, `smart_tool_optimizer.py` e `install-global.sh`, eliminando falhas de chdir em hooks PreToolUse, (5) Atualização formal em `AGENTS.md`, `atomic-commit-discipline` e `ci-auto-heal`, (6) 131/131 testes unitários aprovados no projeto | `scripts/agy-git-ops`, `scripts/context_compactor.py`, `scripts/hooks/smart_tool_optimizer.py`, `scripts/hooks/dynamic_effort_hook.py`, `scripts/install-global.sh`, `tests/`, `AGENTS.md`, `.agents/skills/*` | `PASS (EV-GIT-CI-TOKEN-OPTIMIZATION-20260926-01)` |

| 2026-09-26 | `FEAT` | Otimização Inteligente de Consumo de Ferramentas & Eliminação do Custo Quadrático O(N^2): (1) Deduplicação estrita de injeções ephemerais em `scripts/hooks/dynamic_effort_hook.py` indexando o lock por conversa e hash do prompt do usuário, eliminando a re-injeção redundante de mensagens ephemerais a cada sub-etapa de ferramenta no mesmo turno (economia de 15k a 40k tokens por sessão), (2) Calibração de `MAX_VIEW_LINES = 60` e detecção de leitura contígua sequencial em `scripts/hooks/smart_tool_optimizer.py` com alerta contra fatiamento cego, (3) Discriminação precisa de tokens em `scripts/token_tracker.py` separando `ephemeral_tokens` de `tool_tokens` reais para evitar contaminação da métrica de ferramentas por injeções de hooks, (4) Atualização formal das regras no `AGENTS.md` e `docs/universal-token-reduction-guide.md` priorizando Symbol-First Navigation, (5) 74/74 testes unitários aprovados em `tests/test_dynamic_effort_hook.py`, `tests/test_smart_tool_optimizer.py` e `tests/test_token_tracker.py` | `scripts/hooks/dynamic_effort_hook.py`, `scripts/hooks/smart_tool_optimizer.py`, `scripts/token_tracker.py`, `AGENTS.md`, `docs/universal-token-reduction-guide.md`, `tests/` | `PASS (EV-SMART-TOOL-OPTIMIZER-20260926-01)` |

| 2026-09-26 | `FEAT` | Smart Quota Failover Bidirecional CLI (Google ⇄ Claude/GPT): (1) Implementação de `evaluate_provider_quota_health()` e `resolve_model_with_failover()` em `scripts/agy_effort_router.py`, (2) Consulta em tempo real via Language Server RPC alternando automaticamente para `claude-sonnet-4-6` se a cota do Google esgotar (<= 2%) e para `gemini-3.8-flash-<effort>` se a cota 3P esgotar, (3) Suporte a override manual via `--model <modelo>` bypassando failover, (4) Injeção automática da flag `--model` no comando nativo do CLI e sincronização com `settings.json`, (5) 21/21 testes unitários aprovados em `tests/test_agy_effort_router.py`, (6) Instalação global via `install-global.sh` | `scripts/agy_effort_router.py`, `tests/test_agy_effort_router.py`, `scripts/install-global.sh`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-SMART-QUOTA-FAILOVER-20260926-01)` |

| 2026-09-26 | `TEST` | Teste E2E em Repositório Real (`scratch/test-app`) & Prova de Isolamento Total de Memória: (1) Criação de repositório git autônomo com `pyproject.toml`, (2) Execução de `agy-init-memory` criando `.agents/memory/PROJECT_MEMORY.md` e `archive/HISTORY.md` dedicados para o projeto, (3) Comprovação de isolamento absoluto: a memória do `xp-multiagent-kit` permaneceu 100% intocada, (4) Execução de `agy-repo-map` gerando `REPO_MAP.md` isolado, (5) Ciclo TDD estrito com teste cirúrgico direcionado (Targeted Testing: RED em `test_calculator.py` -> GREEN em `src/calculator.py` com 3/3 testes aprovados sem rodar suíte geral), (6) Geração de `SESSION_HANDOFF.md` via `agy-handoff`, (7) Symlink global de `agy-init-memory` em `~/.local/bin/` | `scripts/agy-init-memory`, `scratch/test-app/`, `scripts/install-global.sh`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-REAL-REPO-E2E-ISOLATION-20260926-01)` |

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
- **[L-019] Protocolo de Elevação de Esforço Sob Demanda (Gate Medium -> High):** O usuário mantém a IDE fixada em `Medium` como baseline para conversas e planejamento. Quando a tarefa atingir risco L2 (Feature complexa) ou L3 (Arquitetura crítica/Segurança), o agente conclui o plano de implementação, emite um alerta explícito solicitando a alteração para `High` e PAUSA obrigatoriamente a execução. A implementação só é iniciada após o usuário confirmar a alteração do nível de esforço.
- **[L-020] Governança Quádrupla de Ferramentas e Eliminação de Loops:** Para deter o consumo desproporcional de tokens por chamadas repetitivas e exploração desordenada, o kit aplica 4 defesas simultâneas: (1) Loop Detection no hook `smart_tool_optimizer.py` (hash sha256 de tool+args bloqueando a 3ª repetição idêntica consecutiva com `deny`); (2) Repo Map Atômico em `.agents/memory/REPO_MAP.md` via `agy-repo-map` gerando resumo AST < 80 linhas que zera chamadas cegas de `list_dir` e `grep_search`; (3) Auto-Compaction e descarte de saídas efêmeras de ferramentas aos 15 turnos / 40k tokens; e (4) Zero-Tool Gate para consultas conceituais L0.


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
- **[L-020]** O acúmulo de outputs de ferramentas em conversas longas gera inflação exponencial de tokens faturados a cada novo turno. Mitiga-se na fonte com 4 defesas: (1) teto estrito de 40 linhas em `view_file`, (2) sanitização mandatória via `agy-sanitize`/pipes em `run_command`, (3) auditoria de payload em hook `PostToolUse` (`tool-size-guard.py`) e (4) antecipação do session reset para 15 turnos / 40k tokens.
- **[L-021]** Modulação de Reasoning Effort Inteligente no CLI (`agy-smart` / `agy-effort`): Mudar o effort manualmente a cada comando cria atrito e desperdício de tokens. O roteador inteligente inspeciona o prompt (L0 trivial -> low, L1 -> medium, L2/L3 -> high), inspeciona o contexto git (branches `docs/` ou `feat/`, arquivos `migration` ou `*.md`) e cruza com a telemetria ao vivo: se a cota móvel de 5h ou semanal estiver crítica (>80%), aplica downshift automático (HIGH -> MEDIUM, MEDIUM -> LOW), protegendo a conta contra interrupções abruptas por rate limit.
- **[L-022]** Interceptação do Binário Nativo vs Wrapper e Disambiguação de Keywords em Classificadores de Risco: Quando a CLI Antigravity for invocada via `agy`, o binário original em `~/.local/bin/agy-native` deve ser envelopado por `~/.local/bin/agy` (apontando para `agy-wrapper.sh` -> `agy_effort_router.py`), garantindo que qualquer chamada pelo usuário ou shell alias (`alias agy="agy --mode accept-edits"`) passe pelo roteador. Além disso, argumentos de flags (como `--mode accept-edits`) não devem ser capturados como prompt e a palavra `token` em L3 deve ser restrita a tokens de autenticação (`jwt`, `access token`), impedindo que perguntas sobre tokens LLM sejam promovidas erroneamente para L3 Crítico.
- **[L-023]** Operações Git e CI/CD Ultra-Econômicas em Tokens (< 1.0k tokens por release): O uso de `gh run view --log` e `git diff/show` brutos sem limitadores pode consumir de 10k a 15k tokens de ferramentas em um único turno de release. O kit resolve isso através de: (1) Utilitário `agy-git-ops` com status compacto (`-s`), diffs estatísticos (`--stat`) e push silencioso (`--quiet`), (2) Motor `agy-compact --ci` que extrai apenas a causa raiz e o stacktrace relevante, descartando steps de setup/checkout/teardown de GitHub Actions, e (3) Interceptação ativa no hook `smart_tool_optimizer.py` higienizando chamadas de `gh run` e comandos git não restritos.

---

## [v2.16.0] - Correção do Roteamento de Reasoning Effort e Interceptação Global do Binário no CLI

### Correções Implementadas
1. **Disambiguação de `\btoken\b`:** Separado em tokens de auth/segurança (`jwt`, `bearer`, `access token`) em L3 e perguntas sobre tokens/consumo LLM mapeadas para L0.
2. **Expansão de `L0_KEYWORDS`:** Adicionados padrões de dúvidas conceituais e perguntas em português (`do que se trata`, `o que faz`, `para que serve`, `duvida`, `economiza`, `qual a diferen[çc]a`, `de forma simples`).
3. **Correção de Argument Parsing:** `parse_cli_session_args()` agora reconhece flags com valor (`--mode accept-edits`, `-m`, etc.), evitando que valores de flags sejam capturados como prompt da tarefa.
4. **Interceptação Global do Binário Nativo:** O binário ELF original foi movido para `~/.local/bin/agy-native` e `~/.local/bin/agy` foi convertido em symlink para `agy-wrapper.sh`. Agora, tanto `agy`, `agy-smart`, `agy-fast` quanto `agy-deep` executam através do classificador inteligente com sincronização imediata de `settings.json`.
5. **Anti-False-Positive em `detect_effort`:** Adicionado filtro contra saídas de ferramentas que contêm código-fonte no transcript, evitando que referências literais a `Model Selection` no código sobrescrevam o esforço real.
6. **Implantação Global Universal:** Executada varredura e sincronização em todos os 53 projetos e workspaces locais (`apply_ignore_rules.py` e `install-global.sh`), propagando `.geminiignore`, `.antigravityignore`, symlinks globais do kit e hooks de push para observabilidade.


