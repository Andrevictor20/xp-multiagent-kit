#!/usr/bin/env bash
# ==============================================================================
# agy-wrapper.sh: Adaptive Antigravity CLI Execution Wrapper
# Optimizes reasoning effort (thinking tokens) and checks rate-limit budget.
# XP Multi-Agent Kit v2
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ROUTER_SCRIPT="$KIT_DIR/scripts/agy_effort_router.py"

CALL_NAME="$(basename "$0")"

# 1. Se o roteador inteligente estiver disponível, delegar com o perfil adequado
if [ -f "$ROUTER_SCRIPT" ]; then
  if [ "$CALL_NAME" = "agy-fast" ]; then
    exec python3 "$ROUTER_SCRIPT" --effort low "$@"
  elif [ "$CALL_NAME" = "agy-deep" ]; then
    exec python3 "$ROUTER_SCRIPT" --effort high "$@"
  else
    # Chamada inteligente padrão (agy-smart, agy ou execução direta)
    exec python3 "$ROUTER_SCRIPT" "$@"
  fi
fi

# 2. Fallback resiliente caso o script python não seja encontrado
EFFORT="medium"
if [ "$CALL_NAME" = "agy-fast" ]; then
  EFFORT="low"
elif [ "$CALL_NAME" = "agy-deep" ]; then
  EFFORT="high"
fi

# Locate underlying antigravity / agy binary
REAL_BIN=""
for candidate in "$HOME/.local/bin/agy-native" "$HOME/.local/bin/agy-bin" "/usr/local/bin/agy-native"; do
  if [ -x "$candidate" ]; then
    REAL_BIN="$candidate"
    break
  fi
done

if [ -z "$REAL_BIN" ]; then
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
fi

if [ -z "$REAL_BIN" ]; then
  echo "⚠️ Executável nativo 'agy' ou 'antigravity' não encontrado em outro PATH."
  echo "Executando em modo de emulação com parâmetros: --effort $EFFORT $*"
  exit 0
fi

exec "$REAL_BIN" --effort "$EFFORT" "$@"
