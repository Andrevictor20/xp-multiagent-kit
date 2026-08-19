# XP Multi-Agent Kit  (Antigravity)

Kit de skills, agentes, workflows e políticas para desenvolvimento em pair programming multi-agente, baseado na metodologia XP com IA e focado no roteamento adaptativo de tarefas (Task Routing) guiado pelo risco. É flexível (L0 a L3), orquestrando disciplinas essenciais: TDD Estrito, Secure Software Development (SSDLC), Arquitetura de Dados e Design System/Frontend.

> **Regra de Ouro**: Use o menor número de agentes, skills e etapas capaz de produzir uma mudança correta, testada, segura, acessível, observável e sustentável.

## Estrutura do Kit

```text
.agents/
├── agents/                 # Agentes responsáveis pela execução de papéis específicos
│   ├── orchestrator        # Roteamento baseado em risco (decide qual workflow usar)
│   ├── navigator           # Analisa intenção, arquitetura, e critérios de aceite
│   ├── designer            # Direção estética, QA de UI, acessibilidade
│   ├── sentinel            # Modelagem de ameaças e revisão de segurança (SSDLC)
│   ├── test-guardian       # TDD: escreve o RED e valida o GREEN
│   ├── builder             # Implementa código (somente o necessário para o GREEN)
│   ├── refactor-warden     # Refatorações (evitar drift, prop explosion, duplicações)
│   ├── release-gatekeeper  # Valida pipelines de CI, Scans de segurança, evidences e commits
│   ├── shipper             # CD, Deploy, Rollback, Monitoramento pós-deploy
│   └── archivist           # Memória de arquitetura, registro de decisões (ADRs) e dívida
│
├── skills/                 # Capabilities granulares que os agentes utilizam
│   ├── (várias skills de Segurança, como threat-modeling, api-security, etc.)
│   ├── (várias skills de Frontend, como design-tokens, accessibility-engineering, etc.)
│   ├── (várias skills de Dados, como database-architecture, migration-safety, etc.)
│   └── (skills de fundação, como task-routing e codebase-cartography)
│
├── workflows/              # Definições das rotas de execução
│   ├── trivial.md          # L0: Alterações mínimas (ex: typo). Pula TDD e validações pesadas.
│   ├── small.md            # L1: Alterações simples. Foco no TDD básico.
│   ├── feature.md          # L2: Funcionalidade média. Avaliações de design e segurança condicionais.
│   ├── critical.md         # L3: Auth, Dados, Pagamentos. Threat model e gates rigorosos.
│   ├── bugfix.md           # Regressão provada antes de corrigir.
│   ├── incident.md         # Mitigação rápida em produção.
│   └── release.md          # Conexão CI/CD.
│
└── policies/               # Diretrizes globais baseadas no risco e impacto
    ├── tdd.md
    ├── security.md
    ├── database.md
    ├── frontend.md
    ├── design-system.md
    ├── evidence.md
    └── release.md
```

## Como funciona o Task Routing

O `orchestrator` lê o pedido, preenche conceitualmente um **Task Contract** (Size, Risk, Surfaces afetadas) e decide o nível do workflow:

- **L0 (Trivial)**: Não use o pipeline completo para atualizar documentação ou CSS simples. `builder` e validação direta.
- **L1 (Small)**: `navigator` → RED → `builder` → GREEN → refactor.
- **L2 (Feature)**: Aciona o `sentinel` e `designer` apenas se aplicável. Requer níveis maiores de evidência.
- **L3 (Critical)**: Passagem obrigatória pelo `sentinel` para Threat Modeling, revisão de design, testes extensos e validação antes do release.

## TDD e Native Toolchain Execution Evidence

TDD continua sendo o pilar do Kit. Porém, sem métricas arbitrárias de volume de código ou dependências de scripts estritos de runtime legados.
Foca-se em Behavior Coverage e na prova inegável da execução **nativa** da toolchain do seu projeto (ex: `npm test`, `pytest`, `cargo test`). Afirmações verbais (ex: "Os testes passaram") sem a saída e o comando reais executados não permitem que a tarefa avance de RED para GREEN, e muito menos para um Release.

## Instalação no Antigravity

Copie o diretório `.agents/` e o arquivo `AGENTS.md` para a raiz do seu novo projeto. O Antigravity IDE descobre automaticamente as `skills`, `agents` e regras globais ali presentes.
O agente de entrada principal de delegação não-trivial é o **`orchestrator`**.

---

### Project-Agnostic Core
A partir da versão mais recente, o XP Multi-Agent Kit tornou-se puramente agnóstico de projetos. Toda a inteligência do kit (workflows, policies, skills e agents) está contida estritamente na pasta `.agents/`.
Para novos projetos, basta colar esta pasta e seguir com os prompts descritivos no Antigravity IDE. A infraestrutura de CI/CD não está mais acoplada.
