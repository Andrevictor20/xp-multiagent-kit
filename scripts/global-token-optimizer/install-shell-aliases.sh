#!/usr/bin/env bash
# ==============================================================================
# install-shell-aliases.sh
# Injeta aliases e funções de economia global de tokens para Fish e Bash/Zsh
# ==============================================================================
set -euo pipefail

FISH_CONFIG="$HOME/.config/fish/config.fish"
BASH_CONFIG="$HOME/.bashrc"
ZSH_CONFIG="$HOME/.zshrc"

echo "===================================================================="
echo "⚡ Configurando Aliases Globais de Economia de Tokens"
echo "===================================================================="

# 1. Configurar no Fish
if [ -f "$FISH_CONFIG" ]; then
  if ! grep -q "agy-fast" "$FISH_CONFIG"; then
    echo "🔗 Injetando aliases em $FISH_CONFIG..."
    cat << 'EOF' >> "$FISH_CONFIG"

# --- Antigravity Token Saver Aliases ---
alias agy-fast="agy --effort low"
alias agy-deep="agy --effort high"
alias xp-tokens="$HOME/.local/bin/xp-tokens"
alias agy-tokens="$HOME/.local/bin/agy-tokens"
alias agy-sanitize="$HOME/.local/bin/agy-sanitize"
alias agy-handoff="$HOME/.local/bin/agy-handoff"
alias agy-audit="$HOME/.local/bin/agy-audit-config"
alias agy-ci="$HOME/.local/bin/agy-ci-heal"
alias agy-ci-heal="$HOME/.local/bin/agy-ci-heal"
# ---------------------------------------
EOF
    echo "   ✅ Aliases configurados no Fish!"
  else
    echo "   ℹ️ Aliases já existentes em $FISH_CONFIG."
  fi
fi

# 2. Configurar no Bash
if [ -f "$BASH_CONFIG" ]; then
  if ! grep -q "agy-fast" "$BASH_CONFIG"; then
    echo "🔗 Injetando aliases em $BASH_CONFIG..."
    cat << 'EOF' >> "$BASH_CONFIG"

# --- Antigravity Token Saver Aliases ---
alias agy-fast="agy --effort low"
alias agy-deep="agy --effort high"
alias xp-tokens="$HOME/.local/bin/xp-tokens"
alias agy-tokens="$HOME/.local/bin/agy-tokens"
alias agy-sanitize="$HOME/.local/bin/agy-sanitize"
alias agy-handoff="$HOME/.local/bin/agy-handoff"
alias agy-audit="$HOME/.local/bin/agy-audit-config"
alias agy-ci="$HOME/.local/bin/agy-ci-heal"
alias agy-ci-heal="$HOME/.local/bin/agy-ci-heal"
# ---------------------------------------
EOF
    echo "   ✅ Aliases configurados no Bash!"
  else
    echo "   ℹ️ Aliases já existentes em $BASH_CONFIG."
  fi
fi

# 3. Configurar no Zsh se existir
if [ -f "$ZSH_CONFIG" ]; then
  if ! grep -q "agy-fast" "$ZSH_CONFIG"; then
    cat << 'EOF' >> "$ZSH_CONFIG"

# --- Antigravity Token Saver Aliases ---
alias agy-fast="agy --effort low"
alias agy-deep="agy --effort high"
alias xp-tokens="$HOME/.local/bin/xp-tokens"
alias agy-tokens="$HOME/.local/bin/agy-tokens"
alias agy-sanitize="$HOME/.local/bin/agy-sanitize"
alias agy-handoff="$HOME/.local/bin/agy-handoff"
alias agy-audit="$HOME/.local/bin/agy-audit-config"
alias agy-ci="$HOME/.local/bin/agy-ci-heal"
alias agy-ci-heal="$HOME/.local/bin/agy-ci-heal"
# ---------------------------------------
EOF
    echo "   ✅ Aliases configurados no Zsh!"
  fi
fi

echo "===================================================================="
echo "🎉 Aliases instalados com sucesso!"
echo "Comandos disponíveis:"
echo "  • agy-fast     : Executa com --effort low (economiza ~80% de thinking tokens)"
echo "  • agy-deep     : Executa com --effort high (para tarefas críticas)"
echo "  • agy-tokens   : Telemetria de tokens em 3 camadas (<usado>/<total>)"
echo "  • agy-sanitize : Sanitiza saídas de terminal antes de entrarem no contexto"
echo "  • agy-handoff  : Gera resumo ultracompacto para resetar chats longos"
echo "  • agy-audit    : Audita inchaço de rules e MCPs globais"
echo "===================================================================="
