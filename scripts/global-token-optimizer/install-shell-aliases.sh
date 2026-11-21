#!/usr/bin/env bash
# ==============================================================================
# install-shell-aliases.sh — Aliases enxutos do XP Multi-Agent Kit v4
# ==============================================================================
set -euo pipefail

ALIAS_BLOCK='
# --- XP Multi-Agent Kit v4 Aliases ---
alias agy="$HOME/.local/bin/agy-smart"
alias agy-fast="agy --effort low"
alias agy-deep="agy --effort high"
alias agy-smart="$HOME/.local/bin/agy-smart"
alias xp="$HOME/.local/bin/xp"
alias xp-kit="$HOME/.local/bin/xp-kit"
alias xp-spec="$HOME/.local/bin/xp-spec"
alias xp-ci-heal="$HOME/.local/bin/xp-ci-heal"
alias agy-sanitize="$HOME/.local/bin/agy-sanitize"
# -------------------------------------'

if [ -d "$HOME/.config/fish" ] || command -v fish >/dev/null 2>&1 || [[ "${SHELL:-}" == *fish* ]]; then
  mkdir -p "$HOME/.config/fish/conf.d"
  cat << 'EOF' > "$HOME/.config/fish/conf.d/xp-kit.fish"
# XP Multi-Agent Kit v4 — Fish Auto-Loader
if not contains "$HOME/.local/bin" $PATH
    set -gx PATH "$HOME/.local/bin" $PATH
end
alias agy="$HOME/.local/bin/agy-smart"
alias agy-fast="agy --effort low"
alias agy-deep="agy --effort high"
alias agy-smart="$HOME/.local/bin/agy-smart"
alias xp="$HOME/.local/bin/xp"
alias xp-kit="$HOME/.local/bin/xp-kit"
alias xp-spec="$HOME/.local/bin/xp-spec"
alias xp-ci-heal="$HOME/.local/bin/xp-ci-heal"
alias agy-sanitize="$HOME/.local/bin/agy-sanitize"
EOF
  echo "   ✅ Aliases v4 configurados no Fish!"
fi

for RC in "$HOME/.bashrc" "$HOME/.zshrc"; do
  [ -L "$RC" ] && [ ! -e "$RC" ] && rm -f "$RC"
  if [ -f "$RC" ]; then
    grep -q "\.local/bin" "$RC" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$RC"
    grep -q "XP Multi-Agent Kit v4 Aliases" "$RC" || printf "%s\n" "$ALIAS_BLOCK" >> "$RC"
  fi
done
echo "🎉 Aliases v4 instalados!"
