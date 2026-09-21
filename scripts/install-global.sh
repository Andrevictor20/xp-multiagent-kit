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

# 2. Criar pastas estruturais necessárias
mkdir -p "$GLOBAL_SKILLS_DIR" "$GLOBAL_RULES_DIR"

# 3. Configurar AGENTS.md como Regra Mestre Global Única
echo "🔗 Vinculando AGENTS.md mestre global..."
ln -sf "$KIT_DIR/AGENTS.md" "$GLOBAL_CONFIG_DIR/AGENTS.md"

# 4. Vincular todas as Skills globais dinamicamente
echo "🔗 Sincronizando Skills globais..."
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

# 4.2. Garantir paridade com Antigravity CLI
CLI_DIR="$HOME/.gemini/antigravity-cli"
if [ -d "$CLI_DIR" ]; then
  echo "🔗 Sincronizando paridade com Antigravity CLI ($CLI_DIR)..."
  ln -sfn "$GLOBAL_CONFIG_DIR/agents" "$CLI_DIR/agents"
  ln -sfn "$GLOBAL_CONFIG_DIR/workflows" "$CLI_DIR/workflows"
  ln -sfn "$GLOBAL_CONFIG_DIR/skills" "$CLI_DIR/skills"
  ln -sfn "$KIT_DIR/AGENTS.md" "$CLI_DIR/AGENTS.md"
  ln -sfn "$KIT_DIR/AGENTS.md" "$CLI_DIR/GEMINI.md"
  ln -sfn "$KIT_DIR/.agents/policies" "$CLI_DIR/policies"
  ln -sfn "$KIT_DIR/.agents/templates" "$CLI_DIR/templates"
fi

# 5. Instalar executáveis CLI globais em ~/.local/bin/
echo "🔗 Instalando ferramentas globais de otimização de tokens em ~/.local/bin/..."
mkdir -p "$HOME/.local/bin"
ln -sf "$KIT_DIR/scripts/token_tracker.py" "$HOME/.local/bin/xp-tokens"
ln -sf "$KIT_DIR/scripts/token_tracker.py" "$HOME/.local/bin/agy-tokens"
ln -sf "$KIT_DIR/scripts/agy-sanitize" "$HOME/.local/bin/agy-sanitize"
ln -sf "$KIT_DIR/scripts/agy-handoff" "$HOME/.local/bin/agy-handoff"
ln -sf "$KIT_DIR/scripts/agy-audit-config" "$HOME/.local/bin/agy-audit-config"
ln -sf "$KIT_DIR/scripts/agy-audit-config" "$HOME/.local/bin/agy-audit"
ln -sf "$KIT_DIR/scripts/global-token-optimizer/agy-wrapper.sh" "$HOME/.local/bin/agy-fast"
ln -sf "$KIT_DIR/scripts/global-token-optimizer/agy-wrapper.sh" "$HOME/.local/bin/agy-deep"
ln -sf "$KIT_DIR/scripts/ci_healer.py" "$HOME/.local/bin/agy-ci-heal"
ln -sf "$KIT_DIR/scripts/ci_healer.py" "$HOME/.local/bin/xp-ci-heal"

echo "   ✅ agy-tokens, xp-tokens, agy-sanitize, agy-handoff, agy-audit, agy-ci-heal disponíveis no PATH!"

# 6. Configurar aliases no shell do usuário
if [ -f "$KIT_DIR/scripts/global-token-optimizer/install-shell-aliases.sh" ]; then
  bash "$KIT_DIR/scripts/global-token-optimizer/install-shell-aliases.sh"
fi

echo "===================================================================="
echo "🎉 XP Multi-Agent Kit v2 otimizado e instalado com sucesso!"
echo "⚡ Tokens de Rules e Skills otimizados + Telemetria (Janela, 5h e Semanal) ativa."
echo "===================================================================="
