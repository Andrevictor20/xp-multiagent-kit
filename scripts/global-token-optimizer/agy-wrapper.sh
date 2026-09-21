#!/usr/bin/env bash
# ==============================================================================
# agy-wrapper.sh: Adaptive Antigravity CLI Execution Wrapper
# Optimizes reasoning effort (thinking tokens) and checks rate-limit budget.
# ==============================================================================
set -e

CALL_NAME="$(basename "$0")"
EFFORT="medium"

if [ "$CALL_NAME" = "agy-fast" ]; then
  EFFORT="low"
elif [ "$CALL_NAME" = "agy-deep" ]; then
  EFFORT="high"
fi

# Optional pre-flight budget warning
if command -v agy-tokens >/dev/null 2>&1; then
  CHECK_OUT="$(agy-tokens --check 2>&1 || true)"
  if echo "$CHECK_OUT" | grep -qi "ALERTA CRÍTICO"; then
    echo "⚠️ [AGY-BUDGET ALERT] Cota de tokens em nível crítico (>80%)!" >&2
    echo "$CHECK_OUT" >&2
    echo "💡 Dica: Use modo cirúrgico atômico ou 'agy-fast' para economizar tokens." >&2
    echo "------------------------------------------------------------------" >&2
  fi
fi

# Locate underlying antigravity / agy binary (avoiding infinite self recursion)
REAL_BIN=""
IFS=':' read -ra ADDR <<< "$PATH"
for p in "${ADDR[@]}"; do
  if [ -x "$p/agy" ] && [ "$(realpath "$p/agy")" != "$(realpath "$0")" ]; then
    REAL_BIN="$p/agy"
    break
  elif [ -x "$p/antigravity" ] && [ "$(realpath "$p/antigravity")" != "$(realpath "$0")" ]; then
    REAL_BIN="$p/antigravity"
    break
  fi
done

if [ -z "$REAL_BIN" ]; then
  echo "⚠️ Executável nativo 'agy' ou 'antigravity' não encontrado em outro PATH."
  echo "Executando em modo de emulação com parâmetros: --effort $EFFORT $*"
  exit 0
fi

# Execute with calibrated effort
exec "$REAL_BIN" --effort "$EFFORT" "$@"
