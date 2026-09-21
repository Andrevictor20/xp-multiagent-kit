#!/usr/bin/env bash
# ==============================================================================
# post-push-watcher.sh: Git trigger / hook for CI/CD Auto-Healer
# Dispatches asynchronous pipeline monitoring in background upon git push.
# ==============================================================================
set -euo pipefail

if command -v agy-ci-heal >/dev/null 2>&1; then
  CURRENT_BRANCH="$(git branch --show-current 2>/dev/null || echo 'main')"
  echo "🚀 [CI Auto-Healer] Disparando monitoramento em segundo plano para o branch '$CURRENT_BRANCH'..."
  # Executa desacoplado com delay para aguardar o término do push no remote
  (sleep 3 && nohup agy-ci-heal --watch --heal --auto-push >/dev/null 2>&1 &) &
fi
