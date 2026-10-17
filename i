#!/usr/bin/env sh
set -eu
(set -o pipefail 2>/dev/null) && set -o pipefail

# ==============================================================================
# XP Multi-Agent Kit v3.1 — Unified Bootstrapper (POSIX sh / bash / zsh / fish)
# Supports Antigravity, OpenCode, Cursor, Qoder, and Codex (IDE & CLI)
# ==============================================================================

REPO_URL="${XP_KIT_REPO_URL:-https://github.com/Andrevictor20/xp-multiagent-kit.git}"
DEFAULT_CLONE_DIR="$HOME/.local/share/xp-multiagent-kit"

# Detect system language (pt or en) using POSIX case
SYS_LANG="${XP_LANG:-${LC_ALL:-${LC_MESSAGES:-${LANG:-en}}}}"
IS_PT=0
case "$SYS_LANG" in
  pt*|PT*|Pt*)
    IS_PT=1
    MSG_PY_ERR="❌ Erro: Python 3 é obrigatório para executar o instalador do XP Multi-Agent Kit."
    MSG_GIT_ERR="❌ Erro: Git é obrigatório para baixar o kit."
    MSG_DL="⬇️  Baixando XP Multi-Agent Kit em"
    MSG_UPD="🔄 Atualizando instalação existente em"
    ;;
  *)
    MSG_PY_ERR="❌ Error: Python 3 is required to run the XP Multi-Agent Kit installer."
    MSG_GIT_ERR="❌ Error: Git is required to download the kit."
    MSG_DL="⬇️  Downloading XP Multi-Agent Kit to"
    MSG_UPD="🔄 Updating existing installation at"
    ;;
esac

try_install_pkg() {
  pkg="$1"
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y "$pkg"
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y "$pkg"
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --noconfirm "$pkg"
  elif command -v brew >/dev/null 2>&1; then
    brew install "$pkg"
  elif command -v apk >/dev/null 2>&1; then
    apk add --no-cache "$pkg"
  elif command -v zypper >/dev/null 2>&1; then
    sudo zypper install -y "$pkg"
  fi
}

if ! command -v python3 >/dev/null 2>&1; then
  echo "⏳ Python 3 ausente. Tentando instalar dependência automaticamente..."
  try_install_pkg python3 || true
  if ! command -v python3 >/dev/null 2>&1; then
    echo "$MSG_PY_ERR"
    exit 1
  fi
fi

if [ $# -eq 0 ] && [ ! -t 0 ]; then
  set -- --global --target all --yes
fi

INSTALLER_DIR=""
if [ -f "$0" ]; then
  CANDIDATE_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd || true)"
  if [ -n "$CANDIDATE_DIR" ] && [ -f "$CANDIDATE_DIR/scripts/kit_installer.py" ]; then
    INSTALLER_DIR="$CANDIDATE_DIR"
  fi
fi

if [ -z "$INSTALLER_DIR" ]; then
  if ! command -v git >/dev/null 2>&1; then
    echo "⏳ Git ausente. Tentando instalar dependência automaticamente..."
    try_install_pkg git || true
    if ! command -v git >/dev/null 2>&1; then
      echo "$MSG_GIT_ERR"
      exit 1
    fi
  fi

  if [ -d "$DEFAULT_CLONE_DIR/.git" ]; then
    echo "$MSG_UPD $DEFAULT_CLONE_DIR..."
    git -C "$DEFAULT_CLONE_DIR" pull --ff-only --quiet || true
  else
    echo "$MSG_DL $DEFAULT_CLONE_DIR..."
    mkdir -p "$(dirname "$DEFAULT_CLONE_DIR")"
    git clone --depth 1 "$REPO_URL" "$DEFAULT_CLONE_DIR"
  fi
  INSTALLER_DIR="$DEFAULT_CLONE_DIR"
fi

python3 "$INSTALLER_DIR/scripts/kit_installer.py" "$@"

USER_SHELL="$(basename "${SHELL:-sh}")"
echo ""
if [ "$IS_PT" -eq 1 ]; then
  echo "🐚 Shell detectado: $USER_SHELL (~/.local/bin configurado automaticamente)"
  case "$USER_SHELL" in
    fish) echo "👉 Para ativar os comandos agora no Fish, rode: source ~/.config/fish/config.fish (ou exec fish)" ;;
    zsh)  echo "👉 Para ativar os comandos agora no Zsh, rode:  source ~/.zshrc (ou exec zsh)" ;;
    bash) echo "👉 Para ativar os comandos agora no Bash, rode: source ~/.bashrc (ou exec bash)" ;;
    *)    echo "👉 Para ativar os comandos agora, abra um novo terminal ou rode: export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
  esac
else
  echo "🐚 Detected shell: $USER_SHELL (~/.local/bin configured automatically)"
  case "$USER_SHELL" in
    fish) echo "👉 To activate commands now in Fish, run: source ~/.config/fish/config.fish (or exec fish)" ;;
    zsh)  echo "👉 To activate commands now in Zsh, run:  source ~/.zshrc (or exec zsh)" ;;
    bash) echo "👉 To activate commands now in Bash, run: source ~/.bashrc (or exec bash)" ;;
    *)    echo "👉 To activate commands now, open a new terminal or run: export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
  esac
fi



