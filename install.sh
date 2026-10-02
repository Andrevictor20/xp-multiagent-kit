#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# XP Multi-Agent Kit v2 — Instalador Portátil e Unificado (SPEC-002)
#
# Suporta:
#   1. Execução local clonada: ./install.sh [opções]
#   2. Instalação remota direta:
#      curl -fsSL https://raw.githubusercontent.com/Andrevictor20/xp-multiagent-kit/main/install.sh | bash
# ==============================================================================

REPO_URL="https://github.com/Andrevictor20/xp-multiagent-kit.git"
DEFAULT_INSTALL_DIR="$HOME/.xp-multiagent-kit"

# Determina se estamos dentro de um clone local do kit
SCRIPT_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/scripts/kit_installer.py" ]; then
  KIT_DIR="$SCRIPT_DIR"
else
  # Executado via curl / pipe stdin
  echo "📦 Detectada execução remota via curl/pipe. Preparando repositório do kit..."
  if [ ! -d "$DEFAULT_INSTALL_DIR" ]; then
    if ! command -v git >/dev/null 2>&1; then
      echo "❌ Git é obrigatório para clonar o repositório. Por favor, instale o git e tente novamente."
      exit 1
    fi
    echo "Clonando XP Multi-Agent Kit em $DEFAULT_INSTALL_DIR..."
    git clone --depth 1 "$REPO_URL" "$DEFAULT_INSTALL_DIR"
  else
    echo "Repositório existente detectado em $DEFAULT_INSTALL_DIR. Atualizando..."
    (cd "$DEFAULT_INSTALL_DIR" && git pull --ff-only 2>/dev/null || true)
  fi
  KIT_DIR="$DEFAULT_INSTALL_DIR"
fi

# Checagem preliminar de Python 3
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python 3 não foi encontrado no sistema."
  echo "Por favor, instale o Python 3.8 ou superior para prosseguir:"
  if command -v apt-get >/dev/null 2>&1; then
    echo "  sudo apt-get update && sudo apt-get install -y python3 git"
  elif command -v dnf >/dev/null 2>&1; then
    echo "  sudo dnf install -y python3 git"
  elif command -v pacman >/dev/null 2>&1; then
    echo "  sudo pacman -S python git"
  elif command -v brew >/dev/null 2>&1; then
    echo "  brew install python git"
  else
    echo "  Instale python3 via o gerenciador de pacotes da sua distribuição."
  fi
  exit 1
fi

# Torna scripts executáveis
chmod +x "$KIT_DIR/scripts"/* "$KIT_DIR/scripts/hooks"/* 2>/dev/null || true

# Executa o motor Python do instalador com os argumentos repassados
exec python3 "$KIT_DIR/scripts/kit_installer.py" "$@"
