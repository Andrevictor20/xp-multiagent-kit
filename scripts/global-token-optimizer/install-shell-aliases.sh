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
  # Garantir PATH no fish
  if ! grep -q "\.local/bin" "$FISH_CONFIG"; then
    echo 'set -gx PATH "$HOME/.local/bin" $PATH' >> "$FISH_CONFIG"
  fi
  if ! grep -q "agy-ci-heal" "$FISH_CONFIG"; then
    echo "🔗 Injetando aliases em $FISH_CONFIG..."
    cat << 'EOF' >> "$FISH_CONFIG"

# --- Antigravity Token Saver & CI Aliases ---
alias agy="$HOME/.local/bin/agy-smart"
alias agy-fast="agy --effort low"
alias agy-deep="agy --effort high"
alias agy-smart="$HOME/.local/bin/agy-smart"
alias agy-effort="$HOME/.local/bin/agy-effort"
alias xp-tokens="$HOME/.local/bin/xp-tokens"
alias agy-tokens="$HOME/.local/bin/agy-tokens"
alias agy-sanitize="$HOME/.local/bin/agy-sanitize"
alias agy-handoff="$HOME/.local/bin/agy-handoff"
alias agy-audit="$HOME/.local/bin/agy-audit-config"
alias agy-ci="$HOME/.local/bin/agy-ci-heal"
alias agy-ci-heal="$HOME/.local/bin/agy-ci-heal"
alias xp-ci-heal="$HOME/.local/bin/xp-ci-heal"
# ---------------------------------------------
EOF
    echo "   ✅ Aliases configurados no Fish!"
  else
    echo "   ℹ️ Aliases já existentes em $FISH_CONFIG."
  fi
fi

# 2. Configurar no Bash
if [ -L "$BASH_CONFIG" ] && [ ! -e "$BASH_CONFIG" ]; then
  echo "⚠️ Symlink quebrado detectado em $BASH_CONFIG. Criando arquivo real..."
  rm -f "$BASH_CONFIG"
fi

if [ ! -f "$BASH_CONFIG" ]; then
  echo "📄 Criando $BASH_CONFIG..."
  cat << 'EOF' > "$BASH_CONFIG"
# ~/.bashrc
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi
export PATH="$HOME/.local/bin:$PATH"
EOF
fi

if [ -f "$BASH_CONFIG" ]; then
  if ! grep -q "\.local/bin" "$BASH_CONFIG"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$BASH_CONFIG"
  fi
  if ! grep -q "agy-ci-heal" "$BASH_CONFIG"; then
    echo "🔗 Injetando aliases em $BASH_CONFIG..."
    cat << 'EOF' >> "$BASH_CONFIG"

# --- Antigravity Token Saver & CI Aliases ---
alias agy="$HOME/.local/bin/agy-smart"
alias agy-fast="agy --effort low"
alias agy-deep="agy --effort high"
alias agy-smart="$HOME/.local/bin/agy-smart"
alias agy-effort="$HOME/.local/bin/agy-effort"
alias xp-tokens="$HOME/.local/bin/xp-tokens"
alias agy-tokens="$HOME/.local/bin/agy-tokens"
alias agy-sanitize="$HOME/.local/bin/agy-sanitize"
alias agy-handoff="$HOME/.local/bin/agy-handoff"
alias agy-audit="$HOME/.local/bin/agy-audit-config"
alias agy-ci="$HOME/.local/bin/agy-ci-heal"
alias agy-ci-heal="$HOME/.local/bin/agy-ci-heal"
alias xp-ci-heal="$HOME/.local/bin/xp-ci-heal"
# ---------------------------------------------
EOF
    echo "   ✅ Aliases configurados no Bash!"
  else
    echo "   ℹ️ Aliases já existentes em $BASH_CONFIG."
  fi
fi

# 3. Configurar no Zsh se existir
if [ -L "$ZSH_CONFIG" ] && [ ! -e "$ZSH_CONFIG" ]; then
  rm -f "$ZSH_CONFIG"
fi

if [ -f "$ZSH_CONFIG" ]; then
  if ! grep -q "\.local/bin" "$ZSH_CONFIG"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$ZSH_CONFIG"
  fi
  if ! grep -q "agy-ci-heal" "$ZSH_CONFIG"; then
    cat << 'EOF' >> "$ZSH_CONFIG"

# --- Antigravity Token Saver & CI Aliases ---
alias agy="$HOME/.local/bin/agy-smart"
alias agy-fast="agy --effort low"
alias agy-deep="agy --effort high"
alias xp-tokens="$HOME/.local/bin/xp-tokens"
alias agy-smart="$HOME/.local/bin/agy-smart"
alias agy-effort="$HOME/.local/bin/agy-effort"
alias agy-tokens="$HOME/.local/bin/agy-tokens"
alias agy-sanitize="$HOME/.local/bin/agy-sanitize"
alias agy-handoff="$HOME/.local/bin/agy-handoff"
alias agy-audit="$HOME/.local/bin/agy-audit-config"
alias agy-ci="$HOME/.local/bin/agy-ci-heal"
alias agy-ci-heal="$HOME/.local/bin/agy-ci-heal"
alias xp-ci-heal="$HOME/.local/bin/xp-ci-heal"
# ---------------------------------------------
EOF
    echo "   ✅ Aliases configurados no Zsh!"
  fi
fi

echo "===================================================================="
echo "🎉 Aliases instalados com sucesso!"
echo "Comandos disponíveis:"
echo "  • agy-smart    : Executa CLI modulando esforço (low/med/high) automaticamente"
echo "  • agy-effort   : Gerenciador de esforço (classify, apply, status)"
echo "  • agy-fast     : Executa com --effort low (economiza ~80% de thinking tokens)"
echo "  • agy-deep     : Executa com --effort high (para tarefas críticas)"
echo "  • agy-tokens   : Telemetria de tokens em 3 camadas (<usado>/<total>)"
echo "  • agy-sanitize : Sanitiza saídas de terminal antes de entrarem no contexto"
echo "  • agy-handoff  : Gera resumo ultracompacto para resetar chats longos"
echo "  • agy-audit    : Audita inchaço de rules e MCPs globais"
echo "===================================================================="
