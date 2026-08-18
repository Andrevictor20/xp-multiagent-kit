# XP Multi-Agent Kit v2 (Antigravity)

Kit de skills, agentes, workflows e políticas para desenvolvimento em pair programming multi-agente, baseado na metodologia XP com IA e focado no roteamento adaptativo de tarefas (Task Routing) guiado pelo risco.

A V2 substitui o pipeline linear (onde todos os agentes executam em sequência) por um workflow dinâmico e flexível (L0 a L3), orquestrando disciplinas essenciais: TDD Estrito, Secure Software Development (SSDLC), Arquitetura de Dados e Design System/Frontend.

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

## TDD e Evidence Walkthrough

TDD continua sendo o pilar do Kit. Porém, sem métricas arbitrárias de volume de código.
Foca-se em Behavior Coverage e na prova inegável de execução de testes: afirmações verbais (ex: "Os testes passaram") sem a saída colada do terminal/runner não permitem que a tarefa avance de RED para GREEN, ou de GREEN para Release.

## Instalação no Antigravity

Copie o diretório `.agents/` para a raiz do seu projeto. O Antigravity IDE descobre automaticamente as `skills` e `agents` ali presentes.
O agente de entrada principal de delegação não-trivial é o **`orchestrator`**.
