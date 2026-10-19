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

# 1. Configurar no Fish (se existir ~/.config/fish, binário fish ou $SHELL=fish)
if [ -d "$HOME/.config/fish" ] || command -v fish >/dev/null 2>&1 || [[ "${SHELL:-}" == *fish* ]]; then
  mkdir -p "$HOME/.config/fish/conf.d"
  touch "$FISH_CONFIG"
  if ! grep -q "\.local/bin" "$FISH_CONFIG"; then
    cat << 'EOF' >> "$FISH_CONFIG"

# XP Multi-Agent Kit
if not contains "$HOME/.local/bin" $PATH
    set -gx PATH "$HOME/.local/bin" $PATH
end
EOF
  fi
  cat << 'EOF' > "$HOME/.config/fish/conf.d/xp-kit.fish"
# XP Multi-Agent Kit — Fish Auto-Loader
if not contains "$HOME/.local/bin" $PATH
    set -gx PATH "$HOME/.local/bin" $PATH
end
alias agy="$HOME/.local/bin/agy-smart"
alias agy-fast="agy --effort low"
alias agy-deep="agy --effort high"
alias agy-smart="$HOME/.local/bin/agy-smart"
alias agy-effort="$HOME/.local/bin/agy-effort"
alias xp-kit="$HOME/.local/bin/xp-kit"
alias agy-kit="$HOME/.local/bin/agy-kit"
alias xp-spec="$HOME/.local/bin/xp-spec"
alias agy-spec="$HOME/.local/bin/agy-spec"
alias agy-sanitize="$HOME/.local/bin/agy-sanitize"
alias agy-handoff="$HOME/.local/bin/agy-handoff"
alias agy-audit="$HOME/.local/bin/agy-audit-config"
alias agy-ci="$HOME/.local/bin/agy-ci-heal"
alias agy-ci-heal="$HOME/.local/bin/agy-ci-heal"
alias xp-ci-heal="$HOME/.local/bin/xp-ci-heal"
EOF
  echo "   ✅ PATH e Aliases configurados no Fish ($FISH_CONFIG & conf.d/xp-kit.fish)!"
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
alias xp-kit="$HOME/.local/bin/xp-kit"
alias agy-kit="$HOME/.local/bin/agy-kit"
alias xp-spec="$HOME/.local/bin/xp-spec"
alias agy-spec="$HOME/.local/bin/agy-spec"
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

# 3. Configurar no Zsh (se existir .zshrc, binário zsh ou $SHELL=zsh)
if [ -L "$ZSH_CONFIG" ] && [ ! -e "$ZSH_CONFIG" ]; then
  rm -f "$ZSH_CONFIG"
fi

if [ -f "$ZSH_CONFIG" ] || command -v zsh >/dev/null 2>&1 || [[ "${SHELL:-}" == *zsh* ]]; then
  touch "$ZSH_CONFIG"
  if ! grep -q "\.local/bin" "$ZSH_CONFIG"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$ZSH_CONFIG"
  fi
  if ! grep -q "agy-ci-heal" "$ZSH_CONFIG"; then
    cat << 'EOF' >> "$ZSH_CONFIG"

# --- Antigravity Token Saver & CI Aliases ---
alias agy="$HOME/.local/bin/agy-smart"
alias agy-fast="agy --effort low"
alias agy-deep="agy --effort high"
alias agy-smart="$HOME/.local/bin/agy-smart"
alias agy-effort="$HOME/.local/bin/agy-effort"
alias xp-kit="$HOME/.local/bin/xp-kit"
alias agy-kit="$HOME/.local/bin/agy-kit"
alias xp-spec="$HOME/.local/bin/xp-spec"
alias agy-spec="$HOME/.local/bin/agy-spec"
alias agy-sanitize="$HOME/.local/bin/agy-sanitize"
alias agy-handoff="$HOME/.local/bin/agy-handoff"
alias agy-audit="$HOME/.local/bin/agy-audit-config"
alias agy-ci="$HOME/.local/bin/agy-ci-heal"
alias agy-ci-heal="$HOME/.local/bin/agy-ci-heal"
alias xp-ci-heal="$HOME/.local/bin/xp-ci-heal"
# ---------------------------------------------
EOF
    echo "   ✅ PATH e Aliases configurados no Zsh ($ZSH_CONFIG)!"
  fi
fi

# 4. Garantir fallback POSIX em ~/.profile
PROFILE_CONFIG="$HOME/.profile"
if [ -f "$PROFILE_CONFIG" ]; then
  if ! grep -q "\.local/bin" "$PROFILE_CONFIG"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$PROFILE_CONFIG"
  fi
fi

echo "===================================================================="
echo "🎉 Aliases instalados com sucesso!"
echo "Comandos disponíveis:"
echo "  • agy-smart    : Executa CLI modulando esforço (low/med/high) automaticamente"
echo "  • agy-effort   : Gerenciador de esforço (classify, apply, status)"
echo "  • agy-fast     : Executa com --effort low (economiza ~80% de thinking tokens)"
echo "  • agy-deep     : Executa com --effort high (para tarefas críticas)"
echo "  • agy-sanitize : Sanitiza saídas de terminal antes de entrarem no contexto"
echo "  • agy-handoff  : Gera resumo ultracompacto para resetar chats longos"
echo "  • agy-audit    : Audita inchaço de rules e MCPs globais"
echo "===================================================================="
