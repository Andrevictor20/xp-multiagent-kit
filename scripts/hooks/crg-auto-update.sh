#!/usr/bin/env bash
# ==============================================================================
# crg-auto-update.sh: Hook leve para atualização incremental do CodeReviewGraph
# Disparado pós-edição ou pós-commit se o repositório contiver um grafo ativo.
# ==============================================================================
set -euo pipefail

# Só executa se agy-graph ou code-review-graph estiver no PATH
GRAPH_BIN=""
if command -v agy-graph >/dev/null 2>&1; then
  GRAPH_BIN="agy-graph"
elif command -v code-review-graph >/dev/null 2>&1; then
  GRAPH_BIN="code-review-graph"
fi

if [ -n "$GRAPH_BIN" ]; then
  # Procura .code-review-graph no diretório corrente ou raízes Git
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  if [ -f "$REPO_ROOT/.code-review-graph/graph.db" ]; then
    # Executa desacoplado em background para não bloquear o fluxo
    (nohup "$GRAPH_BIN" update --skip-flows --repo "$REPO_ROOT" >/dev/null 2>&1 &) &
  fi
fi
