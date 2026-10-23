# SPEC-004: Dynamic Multi-Agent Engine (Heterogeneous Boss-Worker Execution)

> **Status:** DRAFT (Awaiting Human Stop Gate Approval)  
> **Risco:** L2 (Feature)  
> **Autor:** Antigravity (Pair Navigator)  
> **Data:** 2026-10-23  

---

## 1. Contexto & Problema de Negócio

- **Por que estamos construindo isso?**
  Atualmente, a execução de tarefas complexas (L2/L3) ocorre de forma predominantemente sequencial dentro de uma única sessão CLI ou IDE. Quando um modelo pesado (como Gemini 4 Argon ou Claude Opus) é utilizado para a tarefa inteira, consome tokens excessivos e tem latência elevada em tarefas mecânicas (geração de DTOs, interfaces, scaffolding e testes unitários simples).
  Por outro lado, utilizar apenas modelos rápidos (como Gemini 3.8 Flash) pode resultar em perdas sutis de coerência arquitetural e segurança em refatorações amplas.

- **Impacto esperado:**
  - Habilitar o padrão heterogêneo **Boss-Worker**: Orquestrador em modelo de alta capacidade (`argon` / `pro` em `high`) governando workers paralelos em modelos de alta velocidade e baixo custo (`gemini-3.8-flash` em `low` / `medium`).
  - Redução de ~60% a 75% no custo e latência de tarefas L2/L3 com paralelismo real por grupos (`execution_group`).
  - Garantia de isolamento e auto-healing com escalada de esforço e hand-off de modelo.
  - Compatibilidade multiplataforma (Linux, macOS, Windows) e multi-host agnóstica (Antigravity, OpenCode, Cursor, Codex, Qoder).

- **Restrições não negociáveis:**
  - Zero regressão nos 318 testes existentes do kit.
  - Arquitetura estritamente agnóstica de SO e host.
  - Proibição de comandos inexistentes da CLI (`agy exec` substituído por chamadas nativas compatíveis).
  - Isolamento de execução contra colisões de concorrência.

---

## 2. Acceptance Criteria (ATDD)

### AC-1: Schema e Validação do Manifesto de Missão (`active-mission.json`)
- **Dado:** Um arquivo JSON definindo uma missão (`active-mission.json`).
- **Quando:** O validador do manifesto for invocado via Python API ou CLI.
- **Então:** Deve validar os campos obrigatórios (`mission_id`, `feature_name`, `orchestrator`, `tasks`, cada task contendo `task_id`, `subagent`, `model`, `effort`, `execution_group`, `allowed_paths`, `objective`, `verification_cmd`).
- **Métrica:** Retornar objeto validado ou erro de schema explícito com código de saída diferente de 0.

### AC-2: Agrupamento e Paralelismo por `execution_group`
- **Dado:** Uma lista de N tarefas divididas em diferentes `execution_group` (ex: grupo 1 com DTOs, grupo 2 com 2 serviços independentes).
- **Quando:** O motor de orquestração executar a missão.
- **Então:** As tarefas do mesmo `execution_group` devem ser executadas concorrentemente em paralelo; o grupo seguinte só deve iniciar após o sucesso de todas as tarefas do grupo anterior.
- **Métrica:** Ordem de execução respeitada e tempos de tarefas simultâneas compatíveis com concorrência paralela.

### AC-3: Gatekeeping de Verificação por Tarefa (`verification_cmd`)
- **Dado:** Uma tarefa executada por um worker.
- **Quando:** O worker concluir o seu código.
- **Então:** O motor executa o `verification_cmd` associado à tarefa e valida se apenas arquivos em `allowed_paths` foram modificados.
- **Métrica:** Se o comando retornar código 0, tarefa marcada como `PASS`; se retornar != 0, tarefa aciona auto-healing.

### AC-4: Auto-Healing com Escalada de Esforço / Hand-off
- **Dado:** Uma tarefa cujo `verification_cmd` falhou.
- **Quando:** Ocorrer a falha.
- **Então:** 
  - Tentativa 1: O motor reexecuta o worker injetando o stacktrace capturado.
  - Tentativa 2: Se falhar novamente, o motor escala o esforço para `high` ou transfere a tarefa para resolução pelo Orquestrador (Argon/Pro).
- **Métrica:** Registro explícito no relatório da missão das tentativas e escalada acionada.

### AC-5: Validação Global e Geração do `mission-report.md`
- **Dado:** Conclusão de todos os grupos de tarefas.
- **Quando:** A etapa de encerramento for atingida.
- **Então:** O motor executa o `global_verification_cmd` e escreve o `.agents/mission-report.md` consolidando tarefas, modelos utilizados, tentativas de retry e status final.
- **Métrica:** Arquivo `mission-report.md` criado no disco contendo resumo executivo legível.

### AC-6: Disponibilidade Multi-Host e Binários de Linha de Comando
- **Dado:** Instalação global ou no projeto.
- **Quando:** O usuário executar `xp-orchestrate` ou `agy-orchestrate` no terminal (Linux/macOS ou Windows `.cmd`).
- **Então:** O executável CLI deve estar disponível no PATH, com subcomandos de validação, dry-run e execução.
- **Métrica:** Comandos retornam help text e executam em Linux, macOS e Windows.

---

## 3. Specification by Example (SbE)

| Cenário | execution_groups | Resultado de Teste Task | Tentativas | Ação de Auto-Healing | Status Final |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Fluxo Feliz Puro | G1 (1 task), G2 (2 tasks) | Todos retornam exit 0 | 1 tentativa | Nenhuma | PASS (Todos Green) |
| Falha Simples Curada | G1 (1 task) | Tentativa 1: exit 1, Tentativa 2: exit 0 | 2 tentativas | Reexecuta worker com erro | PASS (Recuperado) |
| Escalada para Orquestrador | G1 (1 task) | Tentativa 1: exit 1, Tentativa 2: exit 1 | 3 tentativas | Escala esforço para High / Argon | PASS (Curado no Argon) ou FAIL |
| Erro de Schema | N/A (JSON inválido) | N/A | 0 | Aborta antes de disparar | FAIL (Erro no Manifesto) |

---

## 4. Gherkin Scenarios

```gherkin
Funcionalidade: Orquestração Dinâmica Heterogênea de Subagentes

  Cenário: Execução sequencial de grupos e paralela dentro do grupo
    Dado um manifesto de missão com grupo 1 ("contratos") e grupo 2 ("serviço A", "serviço B")
    Quando o orquestrador executa a missão
    Então o grupo 1 é executado primeiro
    E após a conclusão do grupo 1, "serviço A" e "serviço B" rodam simultaneamente
    E o relatório final é gerado com status SUCESSO

  Cenário: Falha de compilação em worker dispara retry com stacktrace
    Dado que o worker do "serviço A" gerou um erro de sintaxe
    Quando o comando de verificação da tarefa falha com exit code 1
    Então o orquestrador captura o stacktrace
    E reinsere o erro como prompt de auto-healing para a tentativa 2
```
