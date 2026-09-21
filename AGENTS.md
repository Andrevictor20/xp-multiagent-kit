# Regras Globais do Antigravity — XP Multi-Agent Kit v2

Instruções mestras, disciplinas inegociáveis e governança arquitetural do **XP Multi-Agent Kit v2**. Aplicadas estritamente a todo trabalho do Antigravity.

---

## 1. Estratégia de Execução & Roteamento por Risco (Regra de Ouro)
- **Regra de Ouro:** Use SEMPRE o menor número de agentes, skills e etapas para produzir uma alteração correta, testada, segura, acessível, observável e sustentável.
- **Roteamento Automático (Zero-Prompt):** Infira automaticamente o nível de risco e execute o fluxo correspondente sem esperar comandos do usuário:
  - **L0 (Trivial):** Typos, docs, CSS menor → `builder` → validação estática → `archivist` ([trivial.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/workflows/trivial.md)).
  - **L1 (Small):** Ajustes e refatorações isoladas → `navigator` → `test-guardian` (RED) → `builder` (GREEN) → `archivist` → `release-gatekeeper` ([small.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/workflows/small.md)).
  - **L2 (Feature):** Novas funcionalidades/APIs → `navigator` + `designer`/`sentinel` → TDD Matriz → `builder` → `refactor-warden` → `archivist` → `release-gatekeeper` ([feature.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/workflows/feature.md)).
  - **L3 (Critical):** Auth, Pagamentos, Migrações estruturais → Threat Modeling (`sentinel`) → TDD + Segurança → `builder` → Zero-Downtime Plan → `archivist` → `shipper` ([critical.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/workflows/critical.md)).
  - **Bugfix:** `systematic-debugging` (4 fases) → Teste de Regressão RED → Fix Causa Raiz → GREEN → `lesson-learned` + `archivist` ([bugfix.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/workflows/bugfix.md)).
  - **Incident / Release:** Mitigação rápida e rollback ([incident.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/workflows/incident.md)) ou CI Gate rigoroso com Zero-Downtime Canary/Blue-Green ([release.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/workflows/release.md)).
- Toda resposta inicial deve declarar brevemente o **Nível de Risco** e o **Workflow** escolhido antes de iniciar a execução.
- **Modulação Adaptativa de Raciocínio (Thinking Tokens):** Para tarefas mecânicas L0/L1 (docs, CSS, refatoração isolada), configure reasoning effort reduzido (`low` ou `medium`) no CLI ou modelo Flash para poupar entre 3.000 e 8.000 tokens de raciocínio interno por mensagem. Reserve effort `high` para L2/L3.

---

## 2. Test-Driven Development (TDD) & Anti-Test-Bypass Estrito
- **Ciclo ESTRITO:** RED -> GREEN -> REFACTOR ([tdd.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/policies/tdd.md)). Nenhum código de produção sem teste prévio falhando.
- **Matriz de Testes Multi-Camadas:** Unitários (lógica pura), Integração (DB, filas, HTTP), Contrato (schemas API), Regressão (bugs reproduzidos), E2E, Fuzzing e Segurança (SAST/DAST).
- **Anti-Test-Bypass (Tolerância Zero):**
  - **Zero Mocks Cegos:** Permitido mocar apenas I/O externo de terceiros; nunca mocar lógica interna para forçar passagem de teste.
  - **Zero Asserções Vazias:** Proibido testes sem `assert` ou com `assert(true)`.
  - **Zero Skips:** Proibido `.skip`, `xit`, `@pytest.mark.skip` ou flags como `--passWithNoTests`.
  - **Proibido Deletar/Comentar Testes:** Testes quebrados devem ser corrigidos na causa raiz do código de produção.
- **Evidência Obrigatória:** Relatório com output nativo de execução dos testes incluído em `walkthrough.md` ([evidence.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/policies/evidence.md)).

---

## 3. Evidência de Execução de Toolchain Nativa
- Afirmações verbais ("testes passaram") são estritamente rejeitadas.
- Execute os comandos reais (`npm test`, `pytest`, `cargo test`, linters) e observe o output real ([test-evidence-walkthrough](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/test-evidence-walkthrough/SKILL.md)). Nunca force exit codes artificiais.

---

## 4. Segurança SSDLC & Zero Trust
- Aplique **Threat Modeling (STRIDE)** para auth, pagamentos, privacidade e integrações ([security.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/policies/security.md), [threat-modeling](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/threat-modeling/SKILL.md)).
- Governança de segredos ([secrets-guardian](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/secrets-guardian/SKILL.md)), criptografia robusta, hardening de containers non-root e Zero Trust via OIDC/Cosign. Vulnerabilidades altas bloqueiam releases.

---

## 5. Protocolo de Handoff Estruturado
- Transições entre agentes e fechamentos de sessão exigem o **Handoff Packet Estruturado** ([agent-handoff.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/policies/agent-handoff.md)) com: `from_agent`, `to_agent`, `summary`, `files_touched`, `open_questions`, `next_steps` e `verification_evidence`.

---

## 6. Release Gatekeeper, CI/CD Auto-Healer & Deploy Zero-Downtime
- CI estrito, validação de segurança estática, commits atômicos ([atomic-commit-discipline](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/atomic-commit-discipline/SKILL.md)) e verificação completa antes de merge ([release.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/policies/release.md)).
- **CI/CD Auto-Healer & Loop de Autocorreção:** Monitoramento autônomo de esteiras remotas (GitHub Actions) e locais. Em caso de falha, extração cirúrgica de causa raiz (`agy-ci-heal`), correção sistemática no código/configuração e re-tentativa atômica limitada a **no máximo 3 iterações consecutivas** (Regra [L-003]) ([ci-auto-heal](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/ci-auto-heal/SKILL.md)).
- Deploys em produção utilizam Blue/Green ou Canary gradual com telemetria RED e gatilho de rollback automatizado ([zero-downtime-deployment](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/zero-downtime-deployment/SKILL.md)).

---

## 7. Memória Contínua em 4 Tiers & Persistência Forçada em Disco
- **Hard-Enforcement Gate:** PROIBIDO encerrar tarefas sem **gravar fisicamente em disco** o arquivo `.agents/memory/PROJECT_MEMORY.md`.
- **Fast Bootstrap (Passo 0):** Consulte `.agents/memory/PROJECT_MEMORY.md` no início da sessão ([project-memory](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/project-memory/SKILL.md)).
- **Auto-Onboarding (Passo 0-A):** Se ausente ou vazio, popule via `git log -n 10 --oneline`, manifestos do projeto, testes e crie o arquivo via template.
- **Hierarquia 4 Tiers:** *Working Memory* (sessão), *Episodic* (log recente + [archive/HISTORY.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/memory/archive/HISTORY.md)), *Semantic* (ADRs e arquitetura) e *Procedural* (lições aprendidas `[L-NNN]` via [lesson-learned](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/lesson-learned/SKILL.md)).
- **Telemetria de Tokens em 3 Camadas & Exibição Obrigatória em Rodapé:** Monitore ativamente a Janela de Mensagem, a Janela Móvel de 5 Horas e a Cota Semanal via `xp-tokens` ou `agy-tokens` (<usado>/<total>).
  - **Rodapé Obrigatório em Cada Resposta (IDE & CLI):** Toda resposta final enviada pelo assistente (no Antigravity CLI ou na IDE, tanto para modelos Google quanto Claude/OpenAI/outros) DEVE obrigatoriamente incluir no rodapé o bloco padronizado com o consumo desta mensagem (delta de entrada, ferramentas e resposta) e a telemetria acumulada em 3 camadas (`agy-tokens --turn`).
  - **Pre-Flight Gate:** Se qualquer camada estiver crítica (>80% em 5h/Semana ou >70% em Contexto), alerte o usuário antes de iniciar tarefas substantivas. Se o usuário insistir em prosseguir, opere em **Modo Cirúrgico Atômico**: execute estritamente o que for cabível no orçamento restante, garantindo um checkpoint completo, testado e estável, sem deixar trabalho pela metade ([token-budget-tracker](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/token-budget-tracker/SKILL.md)).
- **Protocolo Anti-Flood de Ferramentas:** Proibido despejar saídas gigantes de terminal ou arquivos inteiros no histórico da conversa. Use fatiamento cirúrgico em `view_file` (máx 50-100 linhas com `StartLine`/`EndLine`), flags silenciosas (`--silent`, `-q`) ou [sanitize-tool-output.sh](file:///home/andrevmp/Downloads/xp-multiagent-kit/scripts/sanitize-tool-output.sh) para truncar logs extensos.
- **Session Reset aos 25 Turnos / 70k Tokens:** Ao atingir 25 turnos ou 70k tokens na sessão ativa, execute o checkpoint no [PROJECT_MEMORY.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/memory/PROJECT_MEMORY.md) e recomende abrir um chat limpo via Fast Bootstrap (Passo 0), eliminando até 80% do histórico acumulado.

---

## 8. Frontend Anti-Slop, Design Systems & Copywriting de Conversão
- **Anti-Slop Framework:** Proibido UI genérica de IA e em-dashes (—) excessivos ([frontend.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/policies/frontend.md), [frontend-taste-engineering](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/frontend-taste-engineering/SKILL.md)).
- **Calibração Visual & Tokens:** Calibre Dials (VARIANCE/MOTION/DENSITY), aplique Color Consistency Lock e Shape Lock com raios concêntricos ($R_{inner} = R_{outer} - P$) ([design-system.md](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/policies/design-system.md), [design-tokens](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/design-tokens/SKILL.md)).
- **Copywriting & CRO:** Headlines orientadas a benefício ("E daí?"), redução de atrito e SEO semântico ([conversion-copywriting](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/conversion-copywriting/SKILL.md), [seo-content-engine](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/seo-content-engine/SKILL.md)).
- **UI Quality Gate:** Validação WCAG AA, navegação por teclado, viewport `100dvh` e responsividade real ([ui-quality-gate](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/ui-quality-gate/SKILL.md)).

---

## 9. Causa Raiz, Anti-Workarounds & Code Deslop
- **No Workarounds:** Corrija na fonte. Proibido mascarar erros com `as any`, `@ts-ignore`, casts forçados ou sleeps artificiais ([no-workarounds](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/no-workarounds/SKILL.md)).
- **Code Deslop:** Elimine comentários óbvios, código morto e imponha a regra *No God Files* (< 500 linhas por arquivo) ([code-deslop-review](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/code-deslop-review/SKILL.md), [refactor-watchdog](file:///home/andrevmp/Downloads/xp-multiagent-kit/.agents/skills/refactor-watchdog/SKILL.md)).

---

## 🗺️ Mapa de Diretórios e Recursos do Kit
- **Agentes (`.agents/agents/`):** `orchestrator`, `navigator`, `designer`, `sentinel`, `test-guardian`, `builder`, `refactor-warden`, `archivist`, `release-gatekeeper`, `shipper`, `genesis`.
- **Workflows (`.agents/workflows/`):** `trivial.md` (L0), `small.md` (L1), `feature.md` (L2), `critical.md` (L3), `bugfix.md`, `incident.md`, `release.md`.
- **Políticas (`.agents/policies/`):** `tdd.md`, `release.md`, `memory.md`, `frontend.md`, `design-system.md`, `security.md`, `database.md`, `evidence.md`, `agent-handoff.md`.
- **Memória (`.agents/memory/`):** `PROJECT_MEMORY.md`, `archive/HISTORY.md`, `TOKEN_TELEMETRY.md`.
- **Skills (`.agents/skills/`):** 63 skills especializadas carregadas sob demanda.
