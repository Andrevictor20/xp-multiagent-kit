---
name: codebase-cartography
description: Mapeamento estrutural de dependências e impacto.
---

# Codebase Cartography (CodeReviewGraph)

Mapeamento estrutural determinístico baseado em AST (Tree-sitter) e grafo de dependências via MCP e CLI (`agy-graph` / `code-review-graph`). Substitui varreduras ingênuas por contexto cirúrgico de ~100 a 800 tokens.

## 1. Ferramentas MCP Essenciais (Ordem de Uso)

1. **Contexto Inicial Cirúrgico (~100 tokens):**
   - Chame `get_minimal_context_tool(task="<descrição da tarefa>")` antes de inspecionar qualquer arquivo.
2. **Raio de Explosão (Blast Radius):**
   - Chame `get_impact_radius_tool(files=[...])` para mapear todos os chamadores transitivos, dependentes e módulos downstream afetados.
3. **Mapeamento de Chamadas e Testes:**
   - Chame `query_graph_tool(pattern="callers_of", target="<símbolo>")` para saber quem invoca a função/classe.
   - Chame `query_graph_tool(pattern="tests_for", target="<símbolo>")` para identificar testes diretos ou indiretos existentes e lacunas de teste (*test gaps*).
4. **Análise de Mudança e Risco:**
   - Chame `detect_changes_tool(detail_level="minimal")` para obter pontuação de risco (Alto, Médio, Baixo), fluxos de execução afetados e funções não testadas.
5. **Visão Arquitetural & Comunidades:**
   - Chame `get_architecture_overview_tool()` para compreender os clusters funcionais (Leiden) e dependências entre módulos sem ler arquivos inteiros.

## 2. CLI de Apoio (`agy-graph` / `code-review-graph`)

Em ambientes de terminal ou pipelines:
- `agy-graph query callers_of <symbol>`: Chamadores diretos e indiretos.
- `agy-graph query tests_for <symbol>`: Casos de teste que cobrem o símbolo.
- `agy-graph dead-code`: Funções e classes sem chamadores ou testes.
- `agy-graph detect-changes --brief`: Painel de risco e economia de tokens.
- `agy-graph update --skip-flows`: Atualização incremental rápida (~2s) após edições.

## 3. Disciplina de Economia de Tokens
- Sempre prefira consultas estruturadas de grafo em vez de ler arquivos inteiros com `view_file`.
- Mantenha `detail_level="minimal"` como padrão. Use "standard" apenas se os nós retornados forem insuficientes.
- Orçamento padrão: no máximo 3 chamadas de grafo (~800 tokens totais) por ciclo de análise.
- O grafo serve para delimitar o escopo cirúrgico; leia apenas os trechos estritamente necessários antes de editar.
