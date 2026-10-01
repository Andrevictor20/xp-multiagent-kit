## 2. Protocolo de Auto-Onboarding & Recaptura Retroativa de Contexto (Passo 0-A)

Quando o kit é adicionado a um **repositório existente** (que já possui histórico de commits, arquitetura e código antes da introdução dos agentes) ou quando um projeto novo é aberto:

### Gatilhos de Auto-Onboarding:
O agente aciona o Auto-Onboarding se detectar que `PROJECT_MEMORY.md`:
- Não existe ou está vazio.
- Contém variáveis de template não preenchidas (ex: `{{LAST_UPDATED}}`, `{{Tech Stack}}`).
- Descreve um projeto ou propósito divergente do workspace atual (ex: descreve o próprio kit multiagente quando o workspace atual contém uma aplicação real em React, Python, Go, Rust, Java, etc.).

### 2.1 Engenharia Reversa & Ingestão de Histórico Git (Reverse Ingestion):
Se o projeto já possui histórico no Git, o agente executa a **Recaptura Retroativa de Contexto**:
1. **Auditoria de Commits Recentes:**
   - Executa `git log -n 10 --oneline` (ou `git log -n 5 --stat`) para extrair os últimos marcos, convenções de commit, arquivos alterados e autores.
   - Converte os commits mais relevantes nas 5 a 10 entradas da tabela `Recent Changes & Activity Log (Episodic Memory)`, mapeando o tipo (`FEAT`, `FIX`, `REFACTOR`, `CHORE`), descrição concisa e arquivos modificados.
2. **Inspeção de Código e Arquitetura (Semantic Memory):**
   - Inspeciona os arquivos raiz de manifesto (`package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `Gemfile`, `pom.xml`, `Makefile`, etc.).
   - Lê o `README.md` e a pasta de documentação (`docs/`, `doc/`, `architecture/`) para extrair propósito e visão de produto.
   - Analisa entrypoints e a árvore de diretórios (`src/`, `cmd/`, `app/`, `internal/`, `components/`, `routes/`, `models/`) para identificar padrões arquiteturais (ex: Clean Arch, Hexagonal, Next.js App Router, MVC) e preencher a seção `Architectural Decisions & Domain Models (Semantic Memory)`.
3. **Mapeamento de Toolchain & Testes (Current Health):**
   - Identifica runners de teste e ferramentas de lint configuradas no repositório.
   - Identifica pipelines de CI existentes (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`).
   - Define comandos essenciais de Dev, Testes e Build/Lint.
4. **Derivação de Backlog & Pendências (Active Backlog):**
   - Inspeciona pendências a partir de commits recentes, branches abertas ou comentários `TODO`/`FIXME` para preencher o `Active Backlog`.
5. **Persistência Imediata & Construção Contínua:**
   - Salva o `.agents/memory/PROJECT_MEMORY.md` gerado sob medida.
   - **Continuidade:** Todas as tarefas futuras passam a construir incrementalmente em cima desse histórico real recapturado.

---
