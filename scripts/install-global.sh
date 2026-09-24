#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Script de Instalação e Sincronização Global do XP Multi-Agent Kit v2
# Otimizado para alta eficiência de tokens no Antigravity (~/.gemini/config/)
# ==============================================================================

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GLOBAL_CONFIG_DIR="$HOME/.gemini/config"
GLOBAL_SKILLS_DIR="$GLOBAL_CONFIG_DIR/skills"
GLOBAL_RULES_DIR="$GLOBAL_CONFIG_DIR/rules"
GLOBAL_PLUGIN_DIR="$GLOBAL_CONFIG_DIR/plugins/xp-multiagent-kit"

echo "===================================================================="
echo "🚀 Sincronizando XP Multi-Agent Kit v2 no Antigravity"
echo "📂 Origem: $KIT_DIR"
echo "🌐 Destino Global: $GLOBAL_CONFIG_DIR"
echo "===================================================================="

# 1. Limpar regras e links legados redundantes que causavam estouro de tokens
rm -rf "$GLOBAL_RULES_DIR"/*
rm -rf "$GLOBAL_PLUGIN_DIR"
rm -f "$HOME/.gemini/AGENTS.md" "$HOME/.gemini/GEMINI.md" "$GLOBAL_CONFIG_DIR/GEMINI.md"

# 2. Criar pastas estruturais necessárias
mkdir -p "$GLOBAL_SKILLS_DIR" "$GLOBAL_RULES_DIR"

# 3. Configurar AGENTS.md como Regra Mestre Global Única
echo "🔗 Vinculando AGENTS.md mestre global..."
ln -sf "$KIT_DIR/AGENTS.md" "$GLOBAL_CONFIG_DIR/AGENTS.md"

# 3.1. Reorganizar skills legadas de GCP em plugin dedicado para não estourar o orçamento de skills
GCP_PLUGIN_SKILLS="$GLOBAL_CONFIG_DIR/plugins/googlecloudtools.datacloud_telemetry/skills"
mkdir -p "$GCP_PLUGIN_SKILLS"
for existing_skill in "$GLOBAL_SKILLS_DIR"/*; do
  if [ -d "$existing_skill" ] && [ ! -L "$existing_skill" ]; then
    sname="$(basename "$existing_skill")"
    echo "📦 Isolando skill legado em plugin: $sname"
    mv "$existing_skill" "$GCP_PLUGIN_SKILLS/"
  fi
done

# 4. Vincular todas as Skills globais dinamicamente
echo "🔗 Sincronizando Skills globais do kit..."
skill_count=0
for skill_path in "$KIT_DIR/.agents/skills"/*; do
  if [ -d "$skill_path" ]; then
    skill_name="$(basename "$skill_path")"
    ln -sfn "$skill_path" "$GLOBAL_SKILLS_DIR/$skill_name"
    skill_count=$((skill_count + 1))
  fi
done
echo "   ✅ $skill_count skills sincronizadas em $GLOBAL_SKILLS_DIR!"

# 4.1. Vincular Agents, Workflows, Policies e Templates
ln -sfn "$KIT_DIR/.agents/agents" "$GLOBAL_CONFIG_DIR/agents"
ln -sfn "$KIT_DIR/.agents/workflows" "$GLOBAL_CONFIG_DIR/workflows"
ln -sfn "$KIT_DIR/.agents/policies" "$GLOBAL_CONFIG_DIR/policies"
ln -sfn "$KIT_DIR/.agents/templates" "$GLOBAL_CONFIG_DIR/templates"
ln -sfn "$KIT_DIR/.agents/memory" "$GLOBAL_CONFIG_DIR/memory"

# 4.2. Garantir paridade com Antigravity CLI
CLI_DIR="$HOME/.gemini/antigravity-cli"
if [ -d "$CLI_DIR" ]; then
  echo "🔗 Sincronizando paridade com Antigravity CLI ($CLI_DIR)..."
  ln -sfn "$GLOBAL_CONFIG_DIR/agents" "$CLI_DIR/agents"
  ln -sfn "$GLOBAL_CONFIG_DIR/workflows" "$CLI_DIR/workflows"
  ln -sfn "$GLOBAL_CONFIG_DIR/skills" "$CLI_DIR/skills"
  ln -sfn "$GLOBAL_CONFIG_DIR/rules" "$CLI_DIR/rules"
  ln -sfn "$GLOBAL_CONFIG_DIR/policies" "$CLI_DIR/policies"
  ln -sfn "$GLOBAL_CONFIG_DIR/templates" "$CLI_DIR/templates"
  ln -sfn "$KIT_DIR/.agents/memory" "$CLI_DIR/memory"
  ln -sfn "$KIT_DIR/AGENTS.md" "$CLI_DIR/AGENTS.md"
  ln -sfn "$KIT_DIR/AGENTS.md" "$CLI_DIR/GEMINI.md"
  [ -f "$GLOBAL_CONFIG_DIR/mcp_config.json" ] && ln -sf "$GLOBAL_CONFIG_DIR/mcp_config.json" "$CLI_DIR/mcp_config.json"
  [ -f "$KIT_DIR/.agents/hooks.json" ] && ln -sf "$KIT_DIR/.agents/hooks.json" "$CLI_DIR/hooks.json"
  [ -f "$KIT_DIR/.agents/hooks.json" ] && ln -sf "$KIT_DIR/.agents/hooks.json" "$GLOBAL_CONFIG_DIR/hooks.json"
fi

# 4.3. Garantir paridade com Antigravity IDE
IDE_DIR="$HOME/.gemini/antigravity-ide"
if [ -d "$IDE_DIR" ]; then
  echo "🔗 Sincronizando paridade com Antigravity IDE ($IDE_DIR)..."
  ln -sfn "$GLOBAL_CONFIG_DIR/agents" "$IDE_DIR/agents"
  ln -sfn "$GLOBAL_CONFIG_DIR/workflows" "$IDE_DIR/workflows"
  ln -sfn "$GLOBAL_CONFIG_DIR/skills" "$IDE_DIR/skills"
  ln -sfn "$GLOBAL_CONFIG_DIR/rules" "$IDE_DIR/rules"
  ln -sfn "$GLOBAL_CONFIG_DIR/policies" "$IDE_DIR/policies"
  ln -sfn "$GLOBAL_CONFIG_DIR/templates" "$IDE_DIR/templates"
  ln -sfn "$KIT_DIR/.agents/memory" "$IDE_DIR/memory"
  ln -sfn "$KIT_DIR/AGENTS.md" "$IDE_DIR/AGENTS.md"
  ln -sfn "$KIT_DIR/AGENTS.md" "$IDE_DIR/GEMINI.md"
  [ -f "$GLOBAL_CONFIG_DIR/mcp_config.json" ] && ln -sf "$GLOBAL_CONFIG_DIR/mcp_config.json" "$IDE_DIR/mcp_config.json"
  [ -f "$KIT_DIR/.agents/hooks.json" ] && ln -sf "$KIT_DIR/.agents/hooks.json" "$IDE_DIR/hooks.json"
  if [ -f "$CLI_DIR/settings.json" ] && [ ! -f "$IDE_DIR/settings.json" ]; then
    cp "$CLI_DIR/settings.json" "$IDE_DIR/settings.json"
  fi
fi

# 4.4. Implantar universal .geminiignore e .antigravityignore em todos os projetos
if [ -f "$KIT_DIR/scripts/apply_ignore_rules.py" ]; then
  echo "📄 Implantando .geminiignore & .antigravityignore em todos os projetos da IDE e CLI..."
  python3 "$KIT_DIR/scripts/apply_ignore_rules.py" || true
fi

# 5. Instalar executáveis CLI globais em ~/.local/bin/
echo "🔗 Instalando ferramentas globais de otimização de tokens em ~/.local/bin/..."
mkdir -p "$HOME/.local/bin"
chmod +x "$KIT_DIR/scripts"/* "$KIT_DIR/scripts/hooks"/* "$KIT_DIR/scripts/global-token-optimizer"/* 2>/dev/null || true

ln -sf "$KIT_DIR/scripts/token_tracker.py" "$HOME/.local/bin/xp-tokens"
ln -sf "$KIT_DIR/scripts/token_tracker.py" "$HOME/.local/bin/agy-tokens"
ln -sf "$KIT_DIR/scripts/agy-sanitize" "$HOME/.local/bin/agy-sanitize"
ln -sf "$KIT_DIR/scripts/agy-handoff" "$HOME/.local/bin/agy-handoff"
ln -sf "$KIT_DIR/scripts/agy-audit-config" "$HOME/.local/bin/agy-audit-config"
ln -sf "$KIT_DIR/scripts/agy-audit-config" "$HOME/.local/bin/agy-audit"
ln -sf "$KIT_DIR/scripts/apply_ignore_rules.py" "$HOME/.local/bin/agy-apply-ignore"
ln -sf "$KIT_DIR/scripts/global-token-optimizer/agy-wrapper.sh" "$HOME/.local/bin/agy-fast"
ln -sf "$KIT_DIR/scripts/global-token-optimizer/agy-wrapper.sh" "$HOME/.local/bin/agy-deep"
ln -sf "$KIT_DIR/scripts/ci_healer.py" "$HOME/.local/bin/agy-ci-heal"
ln -sf "$KIT_DIR/scripts/ci_healer.py" "$HOME/.local/bin/xp-ci-heal"

echo "   ✅ agy-tokens, xp-tokens, agy-sanitize, agy-handoff, agy-audit, agy-apply-ignore, agy-ci-heal disponíveis no PATH!"

# 6. Configurar Git Hooks globais para o CI/CD Auto-Healer
echo "🔗 Configurando Git Hooks globais (post-push watcher)..."
GLOBAL_GIT_HOOKS="$HOME/.config/git/hooks"
mkdir -p "$GLOBAL_GIT_HOOKS"
ln -sf "$KIT_DIR/scripts/hooks/post-push-watcher.sh" "$GLOBAL_GIT_HOOKS/pre-push"
ln -sf "$KIT_DIR/scripts/hooks/post-push-watcher.sh" "$GLOBAL_GIT_HOOKS/post-push"
chmod +x "$GLOBAL_GIT_HOOKS/pre-push" "$GLOBAL_GIT_HOOKS/post-push"
git config --global core.hooksPath "$GLOBAL_GIT_HOOKS"

# Hook local do repositório
if [ -d "$KIT_DIR/.git/hooks" ]; then
  ln -sf "$KIT_DIR/scripts/hooks/post-push-watcher.sh" "$KIT_DIR/.git/hooks/pre-push"
  ln -sf "$KIT_DIR/scripts/hooks/post-push-watcher.sh" "$KIT_DIR/.git/hooks/post-push"
  chmod +x "$KIT_DIR/.git/hooks/pre-push" "$KIT_DIR/.git/hooks/post-push"
fi
echo "   ✅ Git Hooks configurados (Global + Local)!"

# 7. Configurar aliases no shell do usuário
if [ -f "$KIT_DIR/scripts/global-token-optimizer/install-shell-aliases.sh" ]; then
  bash "$KIT_DIR/scripts/global-token-optimizer/install-shell-aliases.sh"
fi

echo "===================================================================="
echo "🎉 XP Multi-Agent Kit v2 otimizado e instalado com sucesso!"
echo "⚡ Tokens de Rules e Skills otimizados + Telemetria (Janela, 5h e Semanal) ativa."
echo "🔄 Paridade total Antigravity IDE <-> CLI estabelecida."
echo "🤖 CI/CD Auto-Healer acoplado globalmente via Git Push Hook."
echo "===================================================================="
