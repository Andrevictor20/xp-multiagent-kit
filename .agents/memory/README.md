# 🧠 Diretório de Memória Contínua do Projeto (`.agents/memory/`)

Este diretório gerencia a memória viva, o rastreamento de estado, o arquivo histórico, a **recaptura retroativa de histórico Git (Reverse Ingestion)** e o auto-onboarding do projeto, mantidos pelo agente `archivist` e consumidos pelo `orchestrator` para o **Fast Context Bootstrap** com autonomia total (Zero-Prompt).

## Estrutura do Diretório

```text
.agents/memory/
├── PROJECT_MEMORY.md    # Snapshot ativo (< 300 linhas, 4 Tiers) lido a cada novo chat
├── README.md            # Guia de governança de memória
└── archive/             # Arquivamento de logs e decisões podadas da memória ativa
    └── HISTORY.md       # Histórico cumulativo de entregas e versões consolidadas
```

## Como Funciona

1. **Auto-Onboarding & Recaptura Retroativa de Repositório Existente (Passo 0-A):**
   - Ao adicionar o kit a um **repositório existente** (que já possui histórico e commits anteriores aos agentes) ou ao abrir um projeto novo, o agente detecta se `PROJECT_MEMORY.md` está ausente, vazio, com placeholders ou dados de outro projeto.
   - De forma 100% autônoma e no primeiro turno:
     - Analisa os commits recentes (`git log`) e arquivos modificados para popular a tabela `Recent Changes & Activity Log` com o passado factual do repositório.
     - Inspeciona manifestos (`package.json`, `go.mod`, `Cargo.toml`, etc.), `README.md`, entrypoints e suíte de testes.
     - Gera o `PROJECT_MEMORY.md` sob medida para o projeto real e passa a construir todo o desenvolvimento futuro em cima dessa base viva recapturada.

2. **Memória Ativa (`PROJECT_MEMORY.md`):**
   - É consultada imediatamente pelo `orchestrator` no **Passo 0** de qualquer novo chat ou tarefa.
   - Contém o resumo da arquitetura, saúde dos testes, as últimas 5 a 10 entregas, gotchas procedurais (`[L-NNN]`) e o backlog ativo.
   - Mantida estritamente enxuta (< 300 linhas, < 2.000 tokens) para evitar desperdício de contexto.

3. **Uso Autônomo Incondicional (Zero-Prompt Lifecycle):**
   - O agente nunca espera o usuário pedir para usar, ler ou salvar na memória.
   - Toda tarefa finalizada aciona automaticamente o `archivist` para sincronizar `PROJECT_MEMORY.md` com a alteração entregue, arquivos modificados e evidências reais de teste.

4. **Arquivo Histórico (`archive/HISTORY.md`):**
   - Quando o log de alterações de `PROJECT_MEMORY.md` ultrapassa 10 entradas, as entradas mais antigas são movidas para `archive/HISTORY.md`.
   - Garante que nenhum histórico seja perdido, ao mesmo tempo em que a memória ativa permanece ultra-rápida e barata de ler.
