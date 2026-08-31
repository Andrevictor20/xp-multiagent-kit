#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Script de Instalação e Sincronização Global do XP Multi-Agent Kit v2
# Configura o kit no diretório global do Antigravity (~/.gemini/config/)
# ==============================================================================

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GLOBAL_CONFIG_DIR="$HOME/.gemini/config"
GLOBAL_SKILLS_DIR="$GLOBAL_CONFIG_DIR/skills"
GLOBAL_RULES_DIR="$GLOBAL_CONFIG_DIR/rules"
GLOBAL_PLUGIN_DIR="$GLOBAL_CONFIG_DIR/plugins/xp-multiagent-kit"

echo "===================================================================="
echo "🚀 Instalando XP Multi-Agent Kit v2 Globalmente no Antigravity"
echo "📂 Origem: $KIT_DIR"
echo "🌐 Destino Global: $GLOBAL_CONFIG_DIR"
echo "===================================================================="

# 1. Criação das pastas de destino
mkdir -p "$GLOBAL_SKILLS_DIR" "$GLOBAL_RULES_DIR" "$GLOBAL_PLUGIN_DIR/rules" "$GLOBAL_PLUGIN_DIR/skills"

# 2. Configurar AGENTS.md como Regra Mestre Global
echo "🔗 Vinculando AGENTS.md mestre..."
ln -sf "$KIT_DIR/AGENTS.md" "$GLOBAL_CONFIG_DIR/AGENTS.md"
ln -sf "$KIT_DIR/AGENTS.md" "$GLOBAL_RULES_DIR/00-agents-master.md"

# 3. Vincular todas as 61 Skills
echo "🔗 Vinculando 61 Skills globais..."
skill_count=0
for skill_path in "$KIT_DIR/.agents/skills"/*; do
  if [ -d "$skill_path" ]; then
    skill_name="$(basename "$skill_path")"
    ln -sfn "$skill_path" "$GLOBAL_SKILLS_DIR/$skill_name"
    ln -sfn "$skill_path" "$GLOBAL_PLUGIN_DIR/skills/$skill_name"
    skill_count=$((skill_count + 1))
  fi
done
echo "   ✅ $skill_count skills vinculadas com sucesso!"

# 4. Vincular todas as Políticas (Policies)
echo "🔗 Vinculando 9 Políticas globais..."
policy_count=0
for policy_path in "$KIT_DIR/.agents/policies"/*.md; do
  if [ -f "$policy_path" ]; then
    policy_name="$(basename "$policy_path")"
    ln -sf "$policy_path" "$GLOBAL_RULES_DIR/policy-$policy_name"
    ln -sf "$policy_path" "$GLOBAL_PLUGIN_DIR/rules/policy-$policy_name"
    policy_count=$((policy_count + 1))
  fi
done
echo "   ✅ $policy_count políticas vinculadas com sucesso!"

# 5. Vincular todos os Workflows
echo "🔗 Vinculando 7 Workflows globais..."
workflow_count=0
for workflow_path in "$KIT_DIR/.agents/workflows"/*.md; do
  if [ -f "$workflow_path" ]; then
    workflow_name="$(basename "$workflow_path")"
    ln -sf "$workflow_path" "$GLOBAL_RULES_DIR/workflow-$workflow_name"
    ln -sf "$workflow_path" "$GLOBAL_PLUGIN_DIR/rules/workflow-$workflow_name"
    workflow_count=$((workflow_count + 1))
  fi
done
echo "   ✅ $workflow_count workflows vinculados com sucesso!"

# 6. Vincular todos os Agentes
echo "🔗 Vinculando 11 Agentes globais..."
agent_count=0
for agent_path in "$KIT_DIR/.agents/agents"/*; do
  if [ -d "$agent_path" ]; then
    agent_name="$(basename "$agent_path")"
    if [ -f "$agent_path/agent.md" ]; then
      ln -sf "$agent_path/agent.md" "$GLOBAL_RULES_DIR/agent-$agent_name.md"
      ln -sf "$agent_path/agent.md" "$GLOBAL_PLUGIN_DIR/rules/agent-$agent_name.md"
      agent_count=$((agent_count + 1))
    fi
  fi
done
echo "   ✅ $agent_count agentes vinculados com sucesso!"

# 7. Criar Manifesto do Plugin Global (plugin.json)
echo "📦 Gerando manifesto do plugin global..."
cat << 'EOF' > "$GLOBAL_PLUGIN_DIR/plugin.json"
{
  "name": "xp-multiagent-kit",
  "displayName": "XP Multi-Agent Kit v2",
  "version": "2.0.0",
  "description": "Kit global para pair programming multi-agente com TDD Estrito, Anti-Test-Bypass, Memória em 4 Tiers, Frontend Anti-Slop e Roteamento por Risco L0-L3."
}
EOF

echo "===================================================================="
echo "🎉 XP Multi-Agent Kit v2 instalado globalmente com sucesso!"
echo "✨ Todas as skills, workflows, policies e regras agora estão ativas"
echo "   em qualquer projeto aberto no Antigravity."
echo "===================================================================="
