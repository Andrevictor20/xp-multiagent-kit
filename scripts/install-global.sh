#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Instalação e Sincronização Global — XP Multi-Agent Kit v4 (Thin Harness)
# ==============================================================================

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GLOBAL_CONFIG_DIR="$HOME/.gemini/config"
GLOBAL_SKILLS_DIR="$GLOBAL_CONFIG_DIR/skills"

echo "===================================================================="
echo "🚀 Sincronizando XP Multi-Agent Kit v4 no Antigravity"
echo "📂 Origem: $KIT_DIR"
echo "🌐 Destino Global: $GLOBAL_CONFIG_DIR"
echo "===================================================================="

# 1. Limpar regras legadas redundantes
rm -rf "$GLOBAL_CONFIG_DIR/plugins/xp-multiagent-kit"
rm -f "$HOME/.gemini/AGENTS.md" "$HOME/.gemini/GEMINI.md" "$GLOBAL_CONFIG_DIR/GEMINI.md"
mkdir -p "$GLOBAL_SKILLS_DIR"

# 2. Global Dispatcher minimalista (~270 B, sem duplicação com AGENTS.md local)
cat << 'EOF' > "$GLOBAL_CONFIG_DIR/AGENTS.md"
# XP Kit v4 — Global Dispatcher

1. Follow workspace `AGENTS.md` as single source of truth.
2. Prioritize 100% completeness (Heilmeier + Zero-Decision Plan + EGM).
3. When requested, dispatch subagents in Turn 1.
4. ALL user-facing responses MUST be in Português (PT-BR).
EOF

# 3. Isolar skills não-symlink legadas
GCP_PLUGIN_SKILLS="$GLOBAL_CONFIG_DIR/plugins_disabled/googlecloudtools.datacloud_telemetry/skills"
mkdir -p "$GCP_PLUGIN_SKILLS"
for existing_skill in "$GLOBAL_SKILLS_DIR"/*; do
  if [ -d "$existing_skill" ] && [ ! -L "$existing_skill" ]; then
    sname="$(basename "$existing_skill")"
    rm -rf "$GCP_PLUGIN_SKILLS/$sname"
    mv "$existing_skill" "$GCP_PLUGIN_SKILLS/"
  fi
done
mkdir -p "$GLOBAL_CONFIG_DIR/plugins/googlecloudtools.datacloud_telemetry"

# 4. Sincronizar Skills e ativos v4
for existing_link in "$GLOBAL_SKILLS_DIR"/*; do
  if [ -L "$existing_link" ]; then
    rm -f "$existing_link"
  fi
done
skill_count=0
for skill_path in "$KIT_DIR/.agents/skills"/*; do
  if [ -d "$skill_path" ]; then
    ln -sfn "$skill_path" "$GLOBAL_SKILLS_DIR/$(basename "$skill_path")"
    skill_count=$((skill_count + 1))
  fi
done
echo "   ✅ $skill_count skills sincronizadas em $GLOBAL_SKILLS_DIR"

for sub in agents policies templates memory graph packs; do
  if [ -d "$KIT_DIR/.agents/$sub" ]; then
    ln -sfn "$KIT_DIR/.agents/$sub" "$GLOBAL_CONFIG_DIR/$sub"
  fi
done
for stale in workflows rules; do
  if [ -L "$GLOBAL_CONFIG_DIR/$stale" ]; then
    rm -f "$GLOBAL_CONFIG_DIR/$stale"
  fi
done

# 5. Renderizar hooks.json com caminhos absolutos
HOOKS_SRC="$GLOBAL_CONFIG_DIR/hooks.json"
if [ -f "$KIT_DIR/.agents/hooks.json" ]; then
  python3 -c "
import json
src, dst, kit = '$KIT_DIR/.agents/hooks.json', '$HOOKS_SRC', '$KIT_DIR'
d = json.loads(open(src).read().replace('\${KIT_ROOT}', kit).replace('\$KIT_ROOT', kit))
open(dst, 'w').write(json.dumps(d, indent=2) + '\n')
" 2>/dev/null || true
fi

# 6. Paridade Antigravity CLI e IDE
for TARGET_DIR in "$HOME/.gemini/antigravity-cli" "$HOME/.gemini/antigravity-ide"; do
  if [ -d "$TARGET_DIR" ]; then
    for sub in agents skills policies templates memory; do
      if [ -e "$GLOBAL_CONFIG_DIR/$sub" ]; then
        ln -sfn "$GLOBAL_CONFIG_DIR/$sub" "$TARGET_DIR/$sub"
      fi
    done
    for stale in workflows rules; do
      if [ -L "$TARGET_DIR/$stale" ]; then
        rm -f "$TARGET_DIR/$stale"
      fi
    done
    rm -f "$TARGET_DIR/GEMINI.md"
    ln -sf "$GLOBAL_CONFIG_DIR/AGENTS.md" "$TARGET_DIR/AGENTS.md"
    ln -sf "$HOOKS_SRC" "$TARGET_DIR/hooks.json"
    if [ -f "$GLOBAL_CONFIG_DIR/mcp_config.json" ]; then
      ln -sf "$GLOBAL_CONFIG_DIR/mcp_config.json" "$TARGET_DIR/mcp_config.json"
    fi
  fi
done

# 7. Ignore rules + permissões MCP
[ -f "$KIT_DIR/scripts/apply_ignore_rules.py" ] && python3 "$KIT_DIR/scripts/apply_ignore_rules.py" || true
python3 "$KIT_DIR/scripts/kit_installer.py" --configure-mcp || true

# 8. CLI unificada `xp` + essenciais em ~/.local/bin/
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
chmod +x "$KIT_DIR/scripts"/* "$KIT_DIR/scripts/hooks"/* "$KIT_DIR/scripts/global-token-optimizer"/* 2>/dev/null || true

# Limpar shims depreciados/mortos
rm -f "$BIN_DIR"/{agy-handoff,xp-handoff,agy-resume,agy-daemon,agy-dashboard,agy-session-compact,agy-pack,xp-pack,agy-audit-config,agy-audit,agy-health,xp-health,agy-init-memory,agy-compact,xp-compact,agy-context,xp-context,agy-debt,xp-debt,agy-effort,xp-effort,agy-memory-archive,agy-memory-search,agy-repo-map,agy-skills-profile,agy-skills,agy-worktree,xp-worktree}

if [ -f "$BIN_DIR/agy" ] && [ ! -L "$BIN_DIR/agy" ]; then
  mv "$BIN_DIR/agy" "$BIN_DIR/agy-native"
fi

ln -sf "$KIT_DIR/scripts/xp" "$BIN_DIR/xp"
ln -sf "$KIT_DIR/scripts/xp_gate.py" "$BIN_DIR/xp-gate"
ln -sf "$KIT_DIR/scripts/xp_contract.py" "$BIN_DIR/xp-contract"
ln -sf "$KIT_DIR/scripts/xp_flow.py" "$BIN_DIR/xp-flow"
ln -sf "$KIT_DIR/scripts/xp_evolve.py" "$BIN_DIR/xp-evolve"
ln -sf "$KIT_DIR/scripts/kit_installer.py" "$BIN_DIR/xp-kit"
ln -sf "$KIT_DIR/scripts/kit_installer.py" "$BIN_DIR/agy-kit"
ln -sf "$KIT_DIR/scripts/spec_tool.py" "$BIN_DIR/xp-spec"
ln -sf "$KIT_DIR/scripts/spec_tool.py" "$BIN_DIR/agy-spec"
ln -sf "$KIT_DIR/scripts/goldfish_review.py" "$BIN_DIR/xp-goldfish"
ln -sf "$KIT_DIR/scripts/goldfish_review.py" "$BIN_DIR/agy-goldfish"
ln -sf "$KIT_DIR/scripts/conformance_report.py" "$BIN_DIR/xp-conformance"
ln -sf "$KIT_DIR/scripts/evidence_recorder.py" "$BIN_DIR/xp-evidence"
ln -sf "$KIT_DIR/scripts/turn_telemetry.py" "$BIN_DIR/xp-turn"
ln -sf "$KIT_DIR/scripts/skill_index.py" "$BIN_DIR/xp-skill-index"
ln -sf "$KIT_DIR/scripts/ci_healer.py" "$BIN_DIR/xp-ci-heal"
ln -sf "$KIT_DIR/scripts/agy-run" "$BIN_DIR/xp-run"
ln -sf "$KIT_DIR/scripts/agy-run" "$BIN_DIR/agy-run"
ln -sf "$KIT_DIR/scripts/agy-sanitize" "$BIN_DIR/agy-sanitize"
ln -sf "$KIT_DIR/scripts/agy-git-ops" "$BIN_DIR/agy-git-ops"
ln -sf "$KIT_DIR/scripts/global-token-optimizer/agy-wrapper.sh" "$BIN_DIR/agy"
ln -sf "$KIT_DIR/scripts/global-token-optimizer/agy-wrapper.sh" "$BIN_DIR/agy-fast"
ln -sf "$KIT_DIR/scripts/global-token-optimizer/agy-wrapper.sh" "$BIN_DIR/agy-deep"
ln -sf "$KIT_DIR/scripts/global-token-optimizer/agy-wrapper.sh" "$BIN_DIR/agy-smart"

# 9. Git Hooks globais (CI Auto-Healer)
GLOBAL_GIT_HOOKS="$HOME/.config/git/hooks"
mkdir -p "$GLOBAL_GIT_HOOKS"
ln -sf "$KIT_DIR/scripts/hooks/post-push-watcher.sh" "$GLOBAL_GIT_HOOKS/pre-push"
ln -sf "$KIT_DIR/scripts/hooks/post-push-watcher.sh" "$GLOBAL_GIT_HOOKS/post-push"
chmod +x "$GLOBAL_GIT_HOOKS/pre-push" "$GLOBAL_GIT_HOOKS/post-push"
git config --global core.hooksPath "$GLOBAL_GIT_HOOKS"

# 10. Shell aliases
[ -f "$KIT_DIR/scripts/global-token-optimizer/install-shell-aliases.sh" ] && bash "$KIT_DIR/scripts/global-token-optimizer/install-shell-aliases.sh"

echo "===================================================================="
echo "🎉 XP Multi-Agent Kit v4 sincronizado com sucesso! CLI canônica: xp"
echo "===================================================================="
