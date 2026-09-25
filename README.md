# XP Multi-Agent Kit v2 (Antigravity)

Kit de skills, agentes, workflows e políticas para desenvolvimento em pair programming multi-agente, baseado na metodologia XP com IA e focado no roteamento adaptativo de tarefas (Task Routing) guiado pelo risco. É flexível (L0 a L3), orquestrando disciplinas essenciais: **TDD Estrito & Matriz Multi-Camadas**, **Política Anti-Test-Bypass (Proibição de Burlar Testes)**, Secure Software Development (SSDLC), **Engenharia de Causa Raiz & Anti-Workaround**, **Code Deslop & Limpeza de Código de IA**, **DevOps & Zero-Downtime Deployments**, **Engenharia de Observabilidade & SLOs**, **Cloud Security & Zero Trust Architecture**, Arquitetura de Dados, **Engenharia de Frontend Anti-Slop**, **Motor de Conversion Copywriting & SEO Semântico** e **Memória Contínua em 4 Tiers (Karpathy LLM Wiki Pattern)**.

> **Regra de Ouro**: Use o menor número de agentes, skills e etapas capaz de produzir uma mudança correta, testada, segura, acessível, observável e sustentável.

## Estrutura do Kit

```text
.agents/
├── agents/                 # Agentes responsáveis pela execução de papéis específicos
│   ├── orchestrator        # Roteamento baseado em risco e Fast Context Bootstrap
│   ├── navigator           # Analisa intenção, arquitetura, público, SEO e critérios de aceite
│   ├── designer            # Direção estética Anti-Slop, Copywriting, CRO, QA de UI e acessibilidade
│   ├── sentinel            # Modelagem de ameaças, CloudSec Zero Trust, IaC Governance e SSDLC
│   ├── test-guardian       # TDD: Matriz multi-testes, debugging sistemático, anti-test-bypass e GREEN
│   ├── builder             # Implementa código (somente o necessário para o GREEN, sem workarounds)
│   ├── refactor-warden     # Refatorações (Code Deslop, No God Files, eliminação de workarounds)
│   ├── archivist           # Memória contínua em 4 Tiers, Handoffs, Lições Aprendidas e Memory Lint
│   ├── release-gatekeeper  # Valida CI, scans de segurança, auditoria anti-test-bypass e commits
│   ├── shipper             # CD, Zero-Downtime (Blue/Green/Canary), Telemetria e Rollback
│   └── genesis             # Setup inicial no momento zero (Scaffold, Test Harness, CI e Memory)
│
├── memory/                 # Diretório de memória viva e arquivo histórico
│   ├── PROJECT_MEMORY.md   # Snapshot ativo de contexto (< 300 linhas, 4 Tiers)
│   ├── REPO_MAP.md         # AST Repo Map de símbolos e estrutura (anti-exploração cega)
│   ├── TOKEN_TELEMETRY.md  # Telemetria em 3 camadas e histórico de consumo
│   ├── README.md           # Guia de governança de memória
│   └── archive/            # Histórico acumulado de entregas podadas
│       └── HISTORY.md
│
├── hooks.json              # Configuração nativa de hooks do ciclo de vida
│
├── skills/                 # Capabilities granulares que os agentes utilizam (71 Skills)
│   ├── tdd-safety-net                  # Matriz de testes (Unit, Integration, Contract, E2E, Fuzzing) e Anti-Test-Bypass
│   ├── test-evidence-walkthrough       # Exigência de evidências reais L0 a L4
│   ├── integration-testing             # Testes de integração em fronteiras de dados e APIs
│   ├── systematic-debugging            # 4 Fases de debugging, rastreamento reverso e regra dos 3 fixes
│   ├── no-workarounds                  # Proibição de remendos: corrija a fonte, nunca silencie o sinal
│   ├── code-deslop-review              # Remoção de slop de IA, comentários redundantes e No God Files
│   ├── token-budget-tracker            # Telemetria em 3 camadas, Pre-Flight Budget Gate e Modo Cirúrgico Atômico
│   ├── ci-auto-heal                    # Monitoramento de CI e autocorreção sistemática (máx 3 tentativas)
│   ├── zero-downtime-deployment        # Blue/Green, Canary graduais, Probes e Expand-and-Contract
│   ├── infrastructure-as-code-governance # Governança e segurança de Terraform, Kubernetes e Compose
│   ├── observability-and-slo-engineering # Logs JSON, Métricas RED (OpenTelemetry), Tracing e SLOs
│   ├── cloud-security-and-zero-trust   # Autenticação OIDC, Cosign/SBOM, WAF, Rate Limit e Zero Trust
│   ├── lesson-learned                  # Formalização institucional de lições aprendidas (L-001..L-NNN)
│   ├── project-memory                  # Governança de 4 Tiers, Fast Bootstrap, Handoffs e Memory Lint
│   ├── conversion-copywriting          # Escrita persuasiva de alta conversão, headlines magnéticas e CTAs
│   ├── cro-landing-pages               # Otimização de conversão, redução de atrito e prova social
│   ├── seo-content-engine              # SEO On-page, metatags, Schema.org JSON-LD e AI Search (GEO/AEO)
│   ├── marketing-psychology            # Modelos mentais aplicados a UI (Ancoragem, Aversão à Perda, Hick's Law)
│   ├── copy-editing-sweeps             # Protocolo de 7 passadas de edição de texto e corte de clichês
│   ├── frontend-taste-engineering      # Framework Anti-Slop mestre (Brief inference, Dials, Skeletons)
│   ├── visual-direction-studio         # Direção de arte em duas passadas, disciplina de hero e anti-clichê
│   ├── minimalist-ui                   # Estética editorial e utilitarian minimalism (Linear/Notion vibes)
│   ├── industrial-brutalist-ui         # Estética industrial, terminal militar e tipografia suíça
│   ├── high-end-visual-design          # Design de agência $150k+ (Double-Bezel, Button-in-Button, mola)
│   ├── redesign-ui-audit               # Protocolo Scan->Diagnose->Fix para modernização de código legado
│   ├── image-to-code                   # Pipeline image-first para criação de UI de alta fidelidade
│   ├── ui-quality-gate                 # Validação pré-release de acessibilidade, viewport e anti-slop
│   ├── (skills especializadas de Segurança: threat-modeling, api-security, secrets-guardian, etc.)
│   ├── (skills especializadas de Dados: database-architecture, migration-safety, etc.)
│   └── (skills de fundação: task-routing, codebase-cartography, atomic-commit-discipline, etc.)
│
├── scripts/                # Utilitários CLI, rotadores de esforço, hooks e telemetria
│   ├── agy-effort / agy-smart  # Roteamento inteligente de reasoning effort (low/med/high)
│   ├── agy-repo-map        # Gerador do AST Repo Map compacto anti-busca cega
│   ├── agy-tokens          # Telemetria de tokens em 3 camadas e auditoria de cota
│   ├── agy-ci-heal         # CI/CD Auto-Healer autônomo (máx 3 tentativas)
│   ├── agy-worktree        # Gerenciador de Git Worktrees para isolamento de subagentes
│   ├── agy-sanitize        # Sanitizador de saídas verbosas para redução de payload
│   ├── agy-handoff         # Gerador de handoff packets estruturados entre sessões/agentes
│   ├── install-global.sh   # Instalador e sincronizador de comandos e hooks globais
│   └── hooks/              # Implementações de hooks PreToolUse, PreInvocation e PostToolUse
│
├── workflows/              # Definições das rotas de execução
│   ├── trivial.md          # L0: Alterações mínimas (ex: typo). Pula TDD e validações pesadas.
│   ├── small.md            # L1: Alterações simples. Foco no TDD básico.
│   ├── feature.md          # L2: Funcionalidade média. Avaliações de design e segurança condicionais.
│   ├── critical.md         # L3: Auth, Dados, Pagamentos. Threat model e gates rigorosos.
│   ├── spec-driven.md      # SDD: Especificação executável formal (Gherkin BDD) como fonte da verdade.
│   ├── migration.md        # Migração estrutural segura com Expand-and-Contract e Zero Downtime.
│   ├── performance-benchmark.md # Otimização de performance com profiling e baseline de SLOs.
│   ├── bugfix.md           # Debugging sistemático, no-workarounds e regressão provada antes de corrigir.
│   ├── incident.md         # Mitigação rápida em produção.
│   └── release.md          # Conexão CI/CD com zero-downtime, telemetria e rollback automatizado.
│
├── policies/               # Diretrizes globais baseadas no risco e impacto
│   ├── tdd.md              # Matriz de 8 tipos de testes, ciclo RED-GREEN e regras Anti-Test-Bypass
│   ├── release.md          # Deploy sem downtime, autenticação OIDC, telemetria e rollback imediato
│   ├── memory.md           # Política de 4 Tiers, Untrusted History, token budget e handoffs
│   ├── frontend.md         # Política de frontend anti-slop, copywriting, WCAG AA, dials e viewport
│   ├── design-system.md    # Locks de consistência de cores, formas e raios concêntricos
│   ├── security.md
│   ├── database.md
│   └── evidence.md
│
└── templates/              # Templates reutilizáveis para novos projetos
    └── PROJECT_MEMORY_TEMPLATE.md
```

---

## 🧪 Matriz de Diversidade de Testes & Política Anti-Test-Bypass

1. **A Matriz Multi-Camadas de Testes:**
   - **Unitários:** Testam funções puras, cálculos de domínio e regras de negócio de forma isolada.
   - **Integração:** Validam fronteiras reais com banco de dados, transações ACID, filas e endpoints HTTP.
   - **Contrato / Schema:** Validam tipagem e compatibilidade de contratos de API entre frontend e backend.
   - **Regressão:** Testes prévios criados antes de qualquer correção de bug para provar a falha e blindar o sistema.
   - **End-to-End (E2E):** Validam fluxos completos de jornada crítica do usuário.
   - **Propriedade / Fuzzing:** Testam invariantes com centenas de entradas pseudo-randômicas.
   - **Segurança (SAST/DAST):** Testam controle de acesso (BOLA/IDOR), injeção e sanitização de dados.
   - **Performance:** Avaliam latência sob carga e concorrência.
2. **Política Inegociável Anti-Test-Bypass (Os 7 Pecados Capitais):**
   - **Zero Mocks Cegos:** Proibição de mocar a própria lógica em teste ou usar mocks excessivos que não executam o código real.
   - **Zero Asserções Vazias:** Proibição de testes sem `assert` ou com asserções tautológicas (`expect(true).toBe(true)`).
   - **Zero Skips Não Autorizados:** Proibição de adicionar `.skip`, `xit` ou `@pytest.mark.skip` para esconder testes falhando.
   - **Proibido Deletar Testes Quebrados:** Erros devem ser corrigidos na causa raiz do código de produção, nunca silenciados.
   - **Asserção de Valor:** Obrigatoriedade de validar os dados reais de negócio (`id`, `status`), não apenas `typeof`.

---

## 🚀 Motor de DevOps, Zero-Downtime Deployments & Observabilidade

- **Zero-Downtime Deployments (`zero-downtime-deployment`):** Blue/Green, Canary Releases com tráfego gradual (1% $\rightarrow$ 10% $\rightarrow$ 50% $\rightarrow$ 100%) e Rolling Updates com Probes.
- **Padrão Expand-and-Contract:** Compatibilidade paralela para migrações de banco e versões de API.
- **Rollback Instantâneo Automatizado:** Abort imediato se taxa de erro 5xx > 1% ou latência p99 subir > 50%.
- **Governança de IaC (`infrastructure-as-code-governance`):** Validação estática de Terraform, Kubernetes e Docker Compose.
- **Engenharia de Observabilidade & SLOs (`observability-and-slo-engineering`):** Logs JSON com `correlation_id`, Métricas RED (OpenTelemetry) e Error Budgets.
- **Cloud Security Zero Trust (`cloud-security-and-zero-trust`):** Pipelines OIDC sem segredos estáticos e assinatura Cosign/SBOM.

---

## 🛠️ Suíte de Engenharia de Causa Raiz & Anti-Slop de Código

- **Debugging Sistemático (`systematic-debugging`):** 4 Fases de investigação e a Regra dos 3 Fixes.
- **Proibição Estrita de Remendos (`no-workarounds`):** Corrija a fonte, nunca silencie o sinal.
- **Limpeza e Deslop de Código (`code-deslop-review`):** Eliminação de código redundante e regra "No God Files" (< 500 linhas).
- **Catálogo de Lições Aprendidas (`lesson-learned`):** Registro de armadilhas superadas na Memória Procedural.

---

## 🧠 Sistema de Memória Contínua em 4 Tiers, Auto-Onboarding & Recaptura Retroativa de Contexto Git

- **Auto-Onboarding & Recaptura de Repositório Existente (Passo 0-A):** Ao adicionar o kit a um **repositório existente** (que já possui histórico de commits e arquitetura anteriores) ou a um projeto novo, o agente detecta se `PROJECT_MEMORY.md` está ausente, com dados de template ou divergente. De forma 100% autônoma, audita o `git log` recente (commits, autores, arquivos modificados), inspeciona manifestos, entrypoints e comandos de teste, gerando o `PROJECT_MEMORY.md` sob medida e construindo o desenvolvimento futuro em cima da história real do projeto.
- **Uso 100% Autônomo (Zero-Prompt Lifecycle):** O ciclo completo (Passo 0 Leitura/Bootstrap com Recaptura -> Execução com Gotchas Procedurais -> Passo Final Auto-Sync de Encerramento com o `archivist`) roda nativamente em todas as tarefas, sem nunca depender de solicitação manual do usuário.
- **Hierarquia em 4 Tiers:** Working (sessão atual), Episodic (log recente e `archive/HISTORY.md`), Semantic (arquitetura e ADRs) e Procedural (gotchas `[L-NNN]` e lições aprendidas).
- **Fast Context Bootstrap (Passo 0):** Leitura em 1 passo de `PROJECT_MEMORY.md` (< 2.000 tokens) para carregar todo o estado do projeto.
- **Contrato de Handoff Estruturado:** Pacote formal com `summary`, `files_touched`, `open_questions`, `next_steps` e `verification_evidence`.
- **Segurança de Dados Históricos (Untrusted History):** Todo log passado é estritamente evidência factual não executável.
- **Memory Lint & Poda (FIFO):** Sliding window de 5 a 10 alterações com rotação para `archive/HISTORY.md`.

---

## 🛡️ Governança Quádrupla de Ferramentas & Hooks Nativos

Implementado via `.agents/hooks.json` com interceptação em tempo de execução para economia drástica de tokens e proteção contra loops:
- **PreToolUse (`smart-tool-optimizer`):**
  - **Loop Detection & Anti-Repetição:** Bloqueia automaticamente com `deny` ferramentas executadas 3x consecutivas com os mesmos argumentos.
  - **Proteção de Workspace (`list_dir`):** Bloqueia listagens na raiz do projeto; exige uso do `REPO_MAP.md` ou caminhos específicos.
  - **Filtro de Ruído em Busca (`grep_search`):** Injeta exclusão automática de diretórios ruidosos (`node_modules`, `.git`, `dist`, `__pycache__`, etc.).
  - **Clamp Cirúrgico (`view_file`):** Teto estrito de no máximo 40 linhas por leitura (`EndLine - StartLine <= 40`).
  - **Sanitização Mandatória (`run_command`):** Injeção automática de `agy-sanitize` em comandos verbosos sem limitador.
- **PostToolUse (`tool-size-guard`):** Trunca saídas volumosas de ferramentas (> 2.5KB / 15 linhas) com aviso explicativo, impedindo poluição do contexto.
- **PostInvocation (`token-badge`):** Injeta crachá de telemetria no encerramento de cada turno.
- **PreInvocation (`dynamic-effort-router`):** Auto-modulação dinâmica turno a turno para CLI (`agy-smart`, `agy-effort`).

---

## ⚡ Modulação Inteligente de Raciocínio & CLI Effort Router

- **Roteamento por Risco (Regra [L-019]):**
  - **L0/L1 (Trivial/Small):** Opera em `--effort low`, economizando entre 3.000 e 8.000 tokens de raciocínio por turno em dúvidas, documentação e refatorações isoladas.
  - **L2 (Feature):** Padrão `medium`. Exige Stop Gate explícito caso haja complexidade de integração.
  - **L3 (Critical/Auth/Security):** Elabora plano e emite Stop Gate obrigatório para elevação do modelo para `high` antes de tocar em código.
- **CLI Wrappers Inteligentes:**
  - `agy-smart`: Analisa o prompt antes da chamada e seleciona automaticamente o esforço (`low`, `medium` ou `high`).
  - `agy-effort <low|medium|high>`: Permite forçar o nível de esforço de raciocínio para qualquer comando.
  - `agy-fast`: Atalho rápido para tarefas mecânicas com `--effort low`.
  - `agy-deep`: Atalho para tarefas críticas ou salvaguarda de cota >80% com `--effort high`.

---

## 📊 Telemetria de Tokens em 3 Camadas & Pre-Flight Gate

- **3 Camadas de Monitoramento (`token-budget-tracker` / `agy-tokens`):**
  1. **Janela de Mensagem / Turno:** Controle do payload de entrada, ferramentas e resposta.
  2. **Janela Móvel de 5 Horas:** Monitoramento em tempo real do Language Server contra exaustão de cota de curto prazo.
  3. **Cota Semanal:** Acompanhamento do limite semanal da conta.
- **Rodapé Padronizado Obrigatório:** Toda resposta na IDE ou CLI inclui o consumo detalhado e porcentagens consumidas.
- **Pre-Flight Gate & Modo Cirúrgico Atômico:** Alerta preventivo se o consumo ultrapassar 80% (5h ou Semana) ou 70% (Contexto), ativando commits atômicos imediatos para evitar perda de trabalho.
- **Relatório Exaustivo sob Demanda:** Consultas sobre consumo no chat detalham limites, decomposição do consumo e tempo exato de renovação das cotas.

---

## 🤖 CI/CD Auto-Healer & Loop de Autocorreção

- **Monitoramento Autônomo (`ci-auto-heal` / `agy-ci-heal`):** Inspeciona pipelines de CI remotos (GitHub Actions via `gh run`) e locais.
- **Extração Cirúrgica de Causa Raiz:** Isola a falha exata sem poluir o contexto com logs gigantes.
- **Regra dos 3 Ciclos (Regra [L-003]):** Autocorreção atômica limitada a no máximo 3 iterações consecutivas, impedindo loops infinitos em caso de falha externa persistente.

---

## 🗺️ AST Repo Map & Anti-Exploração Cega

- **Visão Imediata da Arquitetura (`REPO_MAP.md` / `agy-repo-map`):** Gera um mapa compacto em árvore com arquivos e símbolos exportados (classes, funções, interfaces).
- **Passo 0 Anti-Busca Cega:** Elimina rodadas inteiras de `list_dir` e `grep_search` redundantes no início de tarefas.

---

## 🚀 Instalação e Configuração

### 1. No Projeto (Local)
Copie o diretório `.agents/` e o arquivo `AGENTS.md` para a raiz de qualquer projeto (novo ou existente):
```bash
cp -r /caminho/para/xp-multiagent-kit/.agents ./
cp /caminho/para/xp-multiagent-kit/AGENTS.md ./
```
O Antigravity IDE descobre automaticamente as `skills`, `agents`, `workflows`, `policies`, `hooks` e a governança de memória. O kit executará a **Recaptura Retroativa de Histórico Git e Auto-Onboarding** de forma totalmente autônoma logo na primeira interação.

### 2. Instalação Global de Ferramentas CLI & Hooks
Para instalar os utilitários CLI e sincronizar os hooks com a instalação global do Antigravity (`~/.gemini/antigravity-cli/`):
```bash
./scripts/install-global.sh
```
Isso disponibiliza em seu `PATH` (`~/.local/bin`):
- `agy-smart`: Roteador inteligente de raciocínio baseado no prompt.
- `agy-effort`: Executor com esforço parametrizado (`low`, `medium`, `high`).
- `agy-tokens`: Relatório ao vivo de telemetria em 3 camadas.
- `agy-repo-map`: Gerador e atualizador de AST Repo Map.
- `agy-ci-heal`: Scanner e auto-healer de pipelines CI/CD.
- `agy-sanitize`: Sanitizador de saídas verbosas para ferramentas.
- `agy-handoff`: Gerador de pacotes de transição e handoff estruturado.


