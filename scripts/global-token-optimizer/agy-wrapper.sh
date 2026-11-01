#!/usr/bin/env bash
# ==============================================================================
# agy-wrapper.sh: Adaptive Antigravity CLI Execution Wrapper
# Optimizes reasoning effort (thinking tokens) and checks rate-limit budget.
# XP Multi-Agent Kit v2
# ==============================================================================
set -e

# Resolve physical path of script (traversing symlinks)
TARGET_SOURCE="${BASH_SOURCE[0]}"
while [ -L "$TARGET_SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$TARGET_SOURCE")" && pwd)"
  TARGET_SOURCE="$(readlink "$TARGET_SOURCE")"
  [[ $TARGET_SOURCE != /* ]] && TARGET_SOURCE="$DIR/$TARGET_SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$TARGET_SOURCE")" && pwd)"
KIT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Locate user real home
USER_REAL_HOME="$(getent passwd "$(id -un 2>/dev/null || whoami)" 2>/dev/null | cut -d: -f6)"
USER_REAL_HOME="${USER_REAL_HOME:-$HOME}"

# Discover router script in kit or standard locations
ROUTER_SCRIPT=""
for candidate in \
  "$KIT_DIR/scripts/agy_effort_router.py" \
  "$USER_REAL_HOME/.local/share/xp-multiagent-kit/scripts/agy_effort_router.py" \
  "$USER_REAL_HOME/Downloads/xp-multiagent-kit/scripts/agy_effort_router.py" \
  "$USER_REAL_HOME/.xp-multiagent-kit/scripts/agy_effort_router.py"; do
  if [ -f "$candidate" ]; then
    ROUTER_SCRIPT="$candidate"
    break
  fi
done

# Locate underlying native agy binary

REAL_BIN=""
INVOKE_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for candidate in \
  "$INVOKE_DIR/agy-native" \
  "$SCRIPT_DIR/agy-native" \
  "$USER_REAL_HOME/.local/bin/agy-native" \
  "/usr/local/bin/agy-native" \
  "$INVOKE_DIR/agy-bin" \
  "$SCRIPT_DIR/agy-bin" \
  "$USER_REAL_HOME/.local/bin/agy-bin" \
  "/usr/local/bin/agy-bin"; do
  if [ -x "$candidate" ] && [ "$(realpath "$candidate")" != "$(realpath "${BASH_SOURCE[0]}")" ]; then
    REAL_BIN="$candidate"
    break
  fi
done

if [ -z "$REAL_BIN" ]; then
  for bin_name in agy-native agy-bin antigravity-native; do
    p="$(which "$bin_name" 2>/dev/null || true)"
    if [ -x "$p" ] && [ "$(realpath "$p")" != "$(realpath "${BASH_SOURCE[0]}")" ]; then
      REAL_BIN="$p"
      break
    fi
  done
fi

if [ -z "$REAL_BIN" ]; then
  IFS=':' read -ra ADDR <<< "$PATH"
  for p in "${ADDR[@]}"; do
    if [ -x "$p/agy" ] && [ "$(realpath "$p/agy")" != "$(realpath "${BASH_SOURCE[0]}")" ]; then
      REAL_BIN="$p/agy"
      break
    elif [ -x "$p/antigravity" ] && [ "$(realpath "$p/antigravity")" != "$(realpath "${BASH_SOURCE[0]}")" ]; then
      REAL_BIN="$p/antigravity"
      break
    fi
  done
fi

CALL_NAME="$(basename "$0")"

# Bypass effort router completely for CLI subcommands or version/help flags
case "$1" in
  models|agent|agents|changelog|help|install|mcp|mic-serve|plugin|plugins|remote-control|update|--version|-v|--help|-h)
    if [ -n "$REAL_BIN" ]; then
      exec "$REAL_BIN" "$@"
    fi
    ;;
esac

# 1. Se o roteador inteligente estiver disponível, delegar com o perfil adequado
if [ -n "$ROUTER_SCRIPT" ] && [ -f "$ROUTER_SCRIPT" ]; then
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

if [ -z "$REAL_BIN" ]; then
  echo "⚠️ Executável nativo 'agy' ou 'antigravity' não encontrado em outro PATH." >&2
  exit 1
fi

exec "$REAL_BIN" --dangerously-skip-permissions --mode accept-edits --effort "$EFFORT" "$@"
