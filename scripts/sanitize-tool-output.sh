#!/usr/bin/env bash
# ==============================================================================
# scripts/sanitize-tool-output.sh
# Executor de comandos com sanitização anti-flood para economia de tokens
# XP Multi-Agent Kit v2
# ==============================================================================
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "Uso: $0 <comando> [argumentos...]"
  echo "Exemplo: $0 pytest -v"
  exit 1
fi

SCRATCH_DIR="${KIT_SCRATCH_DIR:-/tmp/antigravity-scratch}"
mkdir -p "$SCRATCH_DIR"
LOG_FILE="$SCRATCH_DIR/cmd_$(date +%s).log"

set +e
"$@" > "$LOG_FILE" 2>&1
EXIT_CODE=$?
set -e

TOTAL_LINES=$(wc -l < "$LOG_FILE")
TOTAL_BYTES=$(wc -c < "$LOG_FILE")

if [ "$EXIT_CODE" -eq 0 ]; then
  echo "✅ [SUCCESS] Comando: '$*'"
  echo "📊 Linhas: $TOTAL_LINES | Bytes: $TOTAL_BYTES | Log completo: $LOG_FILE"
  echo "--- Resumo (últimas 10 linhas) ---"
  tail -n 10 "$LOG_FILE"
else
  echo "❌ [FAILED - Exit Code $EXIT_CODE] Comando: '$*'"
  echo "📊 Linhas: $TOTAL_LINES | Bytes: $TOTAL_BYTES | Log completo: $LOG_FILE"
  echo "--- Diagnóstico de Erro (últimas 25 linhas) ---"
  tail -n 25 "$LOG_FILE"
fi

exit $EXIT_CODE
