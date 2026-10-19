#!/usr/bin/env python3
"""
scripts/host_adapters.py
Multi-Host Agnostic Adapters & Bilingual (PT/EN) Localization for XP Multi-Agent Kit v3.0.
Supports Antigravity, OpenCode, Cursor, and Qoder (both IDE and CLI).
"""

from __future__ import annotations

import json
import locale
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

SUPPORTED_TARGETS = ("antigravity", "opencode", "cursor", "qoder", "codex")

I18N_MESSAGES: Dict[str, Dict[str, str]] = {
    "pt": {
        "wizard_title": "🚀 INSTALADOR UNIFICADO (Instalação Multi-IDE & CLI) — XP MULTI-AGENT KIT v3.0",
        "dry_run_banner": "⚠️  [MODO SIMULAÇÃO / DRY-RUN ATIVO]",
        "choose_scope": "Como deseja instalar o kit?",
        "opt_global": "[1] Global (Recomendado) -> Instala ferramentas em ~/.local/bin e sincroniza IDEs/CLIs globais",
        "opt_project": "[2] Projeto Específico (Local) -> Injeta governança, regras e agentes em um repositório",
        "opt_both": "[3] Ambos -> Instalação global + injeção no projeto especificado",
        "prompt_scope": "Escolha uma opção [1/2/3] (padrão: 1): ",
        "choose_targets": "Em quais ambientes (IDE / CLI) deseja instalar?",
        "opt_t_all": "[1] Todos (Antigravity + OpenCode + Cursor + Qoder + Codex)",
        "opt_t_agy": "[2] Antigravity (IDE & CLI)",
        "opt_t_oc": "[3] OpenCode (IDE & CLI)",
        "opt_t_cur": "[4] Cursor (IDE & CLI)",
        "opt_t_qod": "[5] Qoder (IDE & CLI)",
        "opt_t_cod": "[6] Codex (IDE & CLI)",
        "prompt_targets": "Escolha o ambiente [1-6] (padrão: 1 - Todos): ",
        "prompt_project_dir": "Informe o caminho do projeto (padrão: diretório atual): ",
        "cancelled": "Operação cancelada pelo usuário.",
        "deps_missing": "❌ Dependências essenciais ausentes. Instale Python >= 3.8 e Git.",
        "installing_global": "⏳ Executando instalação global...",
        "global_ok": "✅ Instalação global concluída com sucesso!",
        "global_fail": "❌ Falha na instalação global:",
        "installing_project": "⏳ Injetando kit no projeto:",
        "project_ok": "✅ Kit injetado com sucesso no projeto",
        "project_fail": "❌ Falha ao injetar no projeto:",
        "invalid_option": "❌ Opção inválida. Operação abortada.",
        "doctor_title": "🏥 XP MULTI-AGENT KIT — DIAGNÓSTICO DO AMBIENTE",
        "global_bins": "📦 Binários Globais:",
        "installed": "✅ Instalado",
        "missing": "❌ Ausente",
    },
    "en": {
        "wizard_title": "🚀 UNIFIED INSTALLER (Multi-IDE & CLI Installer) — XP MULTI-AGENT KIT v3.0",
        "dry_run_banner": "⚠️  [SIMULATION / DRY-RUN MODE ACTIVE]",
        "choose_scope": "How would you like to install the kit?",
        "opt_global": "[1] Global (Recommended) -> Installs tools in ~/.local/bin and syncs global IDEs/CLIs",
        "opt_project": "[2] Project Only (Local) -> Injects governance, rules, and agents into a repository",
        "opt_both": "[3] Both -> Global installation + project injection",
        "prompt_scope": "Choose an option [1/2/3] (default: 1): ",
        "choose_targets": "Which environments (IDE / CLI) do you want to configure?",
        "opt_t_all": "[1] All (Antigravity + OpenCode + Cursor + Qoder + Codex)",
        "opt_t_agy": "[2] Antigravity (IDE & CLI)",
        "opt_t_oc": "[3] OpenCode (IDE & CLI)",
        "opt_t_cur": "[4] Cursor (IDE & CLI)",
        "opt_t_qod": "[5] Qoder (IDE & CLI)",
        "opt_t_cod": "[6] Codex (IDE & CLI)",
        "prompt_targets": "Choose target [1-6] (default: 1 - All): ",
        "prompt_project_dir": "Enter the project path (default: current directory): ",
        "cancelled": "Operation cancelled by user.",
        "deps_missing": "❌ Missing required dependencies. Please install Python >= 3.8 and Git.",
        "installing_global": "⏳ Running global installation...",
        "global_ok": "✅ Global installation completed successfully!",
        "global_fail": "❌ Global installation failed:",
        "installing_project": "⏳ Injecting kit into project:",
        "project_ok": "✅ Kit successfully injected into project",
        "project_fail": "❌ Failed to inject into project:",
        "invalid_option": "❌ Invalid option. Operation aborted.",
        "doctor_title": "🏥 XP MULTI-AGENT KIT — ENVIRONMENT DIAGNOSTICS",
        "global_bins": "📦 Global Binaries:",
        "installed": "✅ Installed",
        "missing": "❌ Missing",
    },
}


def detect_system_language(explicit_lang: Optional[str] = None) -> str:
    """Detects 'pt' or 'en' from explicit override or OS environment/locale."""
    if explicit_lang:
        low = explicit_lang.strip().lower()
        if low.startswith("pt"):
            return "pt"
        if low.startswith("en"):
            return "en"

    for env_key in ("XP_LANG", "AGY_LANG", "LC_ALL", "LC_MESSAGES", "LANGUAGE", "LANG"):
        val = os.environ.get(env_key, "").strip().lower()
        if val and val not in ("c", "c.utf-8", "posix"):
            return "pt" if val.startswith("pt") else "en"

    try:
        loc, _ = locale.getlocale()
        if loc and str(loc).lower().startswith("pt"):
            return "pt"
    except Exception:
        pass
    return "en"


def get_i18n_messages(lang: Optional[str] = None) -> Dict[str, str]:
    """Returns localized message dictionary ('pt' or 'en')."""
    resolved = detect_system_language(lang)
    return I18N_MESSAGES.get(resolved, I18N_MESSAGES["en"])


def normalize_targets(targets: Optional[Any]) -> List[str]:
    """Normalizes target list from string or iterable."""
    if not targets:
        return ["antigravity"]
    if isinstance(targets, str):
        items = [t.strip().lower() for t in targets.split(",") if t.strip()]
    else:
        items = [str(t).strip().lower() for t in targets if str(t).strip()]
    if "all" in items:
        return list(SUPPORTED_TARGETS)
    valid = [t for t in items if t in SUPPORTED_TARGETS]
    return valid if valid else ["antigravity"]


def build_mcp_servers_dict(home_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Builds standard MCP server dictionary compatible with Cursor, OpenCode, Qoder, and Antigravity."""
    home = home_dir or Path.home()
    crg_bin = home / ".local" / "share" / "code-review-graph" / ".venv" / "bin" / "code-review-graph"
    crg_cmd = str(crg_bin) if crg_bin.exists() else "code-review-graph"
    crg_tools = (
        "detect_changes_tool,get_minimal_context_tool,get_impact_radius_tool,"
        "query_graph_tool,get_review_context_tool,get_architecture_overview_tool,"
        "find_large_functions_tool,refactor_tool,list_flows_tool,get_affected_flows_tool"
    )
    return {
        "open-design": {
            "command": "od",
            "args": ["mcp", "--daemon-url", "http://127.0.0.1:7456"],
        },
        "code-review-graph": {
            "command": crg_cmd,
            "args": ["serve"],
            "env": {"CRG_TOOLS": crg_tools},
        },
    }


class HostAdapters:
    """Generates project and global configurations for OpenCode, Cursor, and Qoder."""

    def __init__(self, kit_dir: Path, home_dir: Optional[Path] = None):
        self.kit_dir = kit_dir
        self.home_dir = home_dir or Path.home()

    def _read_ignore_template(self) -> str:
        tpl = self.kit_dir / "templates" / "universal.geminiignore"
        if tpl.is_file():
            return tpl.read_text(encoding="utf-8")
        return "node_modules/\n.git/\n__pycache__/\n*.log\ndist/\nbuild/\n"

    def install_opencode_project(self, project_dir: Path, dry_run: bool = False) -> List[str]:
        """Provisions OpenCode (IDE & CLI) configuration in project_dir."""
        actions: List[str] = []
        oc_json_path = project_dir / "opencode.json"
        oc_dir = project_dir / ".opencode"
        agent_dst = oc_dir / "agent"
        cmd_dst = oc_dir / "command"

        if not dry_run:
            agent_dst.mkdir(parents=True, exist_ok=True)
            cmd_dst.mkdir(parents=True, exist_ok=True)

            # 1. opencode.json
            oc_data: Dict[str, Any] = {"$schema": "https://opencode.ai/config.json"}
            if oc_json_path.is_file():
                try:
                    oc_data = json.loads(oc_json_path.read_text(encoding="utf-8"))
                except Exception:
                    pass
            oc_data["instructions"] = [
                "AGENTS.md",
                ".agents/memory/PROJECT_MEMORY.md",
                ".agents/policies/*.md",
            ]
            mcp_servers = build_mcp_servers_dict(self.home_dir)
            oc_data.setdefault("mcp", {})
            for s_name, s_cfg in mcp_servers.items():
                oc_data["mcp"][s_name] = {
                    "type": "local",
                    "command": [s_cfg["command"]] + s_cfg.get("args", []),
                    "enabled": True,
                }
                if "env" in s_cfg:
                    oc_data["mcp"][s_name]["environment"] = s_cfg["env"]
            oc_json_path.write_text(json.dumps(oc_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

            # 2. Export agents to .opencode/agent/<name>.md
            agents_src = self.kit_dir / ".agents" / "agents"
            if agents_src.is_dir():
                for ag_folder in sorted(agents_src.iterdir()):
                    ag_file = ag_folder / "agent.md"
                    if ag_folder.is_dir() and ag_file.is_file():
                        (agent_dst / f"{ag_folder.name}.md").write_text(
                            ag_file.read_text(encoding="utf-8"), encoding="utf-8"
                        )
            else:
                (agent_dst / "orchestrator.md").write_text("# Orchestrator Agent\n", encoding="utf-8")

            # 3. Export workflows to .opencode/command/<name>.md
            wf_src = self.kit_dir / ".agents" / "workflows"
            if wf_src.is_dir():
                wf_files = list(wf_src.glob("*.md"))
                for wf_file in sorted(wf_files):
                    (cmd_dst / wf_file.name).write_text(wf_file.read_text(encoding="utf-8"), encoding="utf-8")
            if not list(cmd_dst.glob("*.md")):
                for default_wf in ("feature", "bugfix", "small", "trivial", "design"):
                    (cmd_dst / f"{default_wf}.md").write_text(f"# {default_wf.capitalize()} Workflow\n", encoding="utf-8")

        actions.append("OpenCode configured (opencode.json, .opencode/agent/, .opencode/command/)")
        return actions

    def install_cursor_project(self, project_dir: Path, dry_run: bool = False) -> List[str]:
        """Provisions Cursor (IDE & CLI) .cursor/rules/*.mdc, .cursor/mcp.json, and .cursorignore."""
        actions: List[str] = []
        cursor_dir = project_dir if project_dir.name == ".cursor" else (project_dir / ".cursor")
        rules_dir = cursor_dir / "rules"

        if not dry_run:
            rules_dir.mkdir(parents=True, exist_ok=True)
            agents_md_content = ""
            if (self.kit_dir / "AGENTS.md").is_file():
                agents_md_content = (self.kit_dir / "AGENTS.md").read_text(encoding="utf-8")

            core_mdc = (
                "---\n"
                "description: XP Multi-Agent Kit v3 Core Governance (Risk Routing, ATDD/TDD, Token Economy, Self-Healing)\n"
                "globs:\n"
                "alwaysApply: true\n"
                "---\n\n"
                + (agents_md_content or "# XP Multi-Agent Kit Core Rules\n")
            )
            (rules_dir / "00-xp-core.mdc").write_text(core_mdc, encoding="utf-8")

            fe_policy = ""
            fe_file = self.kit_dir / ".agents" / "policies" / "frontend.md"
            if fe_file.is_file():
                fe_policy = fe_file.read_text(encoding="utf-8")
            fe_mdc = (
                "---\n"
                "description: Frontend Anti-Slop, 6-State Machine, WCAG AA, and Design System Tokens\n"
                'globs: ["*.tsx", "*.ts", "*.jsx", "*.css", "*.vue", "*.svelte", "*.html"]\n'
                "alwaysApply: false\n"
                "---\n\n"
                + (fe_policy or "# Frontend & Design Policy\n")
            )
            (rules_dir / "10-frontend-design.mdc").write_text(fe_mdc, encoding="utf-8")

            tdd_policy = ""
            tdd_file = self.kit_dir / ".agents" / "policies" / "tdd.md"
            if tdd_file.is_file():
                tdd_policy = tdd_file.read_text(encoding="utf-8")
            tdd_mdc = (
                "---\n"
                "description: Strict TDD (RED-GREEN-REFACTOR) and Anti-Test-Bypass Enforcement\n"
                'globs: ["*test*", "*spec*"]\n'
                "alwaysApply: false\n"
                "---\n\n"
                + (tdd_policy or "# TDD Policy\n")
            )
            (rules_dir / "20-tdd-testing.mdc").write_text(tdd_mdc, encoding="utf-8")

            mcp_path = cursor_dir / "mcp.json"
            mcp_data = {"mcpServers": build_mcp_servers_dict(self.home_dir)}
            mcp_path.write_text(json.dumps(mcp_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

            if not project_dir.name.startswith("."):
                ignore_path = project_dir / ".cursorignore"
                if not ignore_path.exists():
                    ignore_path.write_text(self._read_ignore_template(), encoding="utf-8")

        actions.append("Cursor configured (.cursor/rules/*.mdc, .cursor/mcp.json, .cursorignore)")
        return actions

    def install_qoder_project(self, project_dir: Path, dry_run: bool = False) -> List[str]:
        """Provisions Qoder (IDE & CLI) .qoder/rules/xp-governance.md, .qoder/mcp.json, and .qoderignore."""
        actions: List[str] = []
        qoder_dir = project_dir if project_dir.name == ".qoder" else (project_dir / ".qoder")
        rules_dir = qoder_dir / "rules"

        if not dry_run:
            rules_dir.mkdir(parents=True, exist_ok=True)
            agents_md_content = ""
            if (self.kit_dir / "AGENTS.md").is_file():
                agents_md_content = (self.kit_dir / "AGENTS.md").read_text(encoding="utf-8")

            (rules_dir / "xp-governance.md").write_text(
                agents_md_content or "# XP Multi-Agent Kit Governance\n",
                encoding="utf-8",
            )
            mcp_path = qoder_dir / "mcp.json"
            mcp_data = {"mcpServers": build_mcp_servers_dict(self.home_dir)}
            mcp_path.write_text(json.dumps(mcp_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

            if not project_dir.name.startswith("."):
                ignore_path = project_dir / ".qoderignore"
                if not ignore_path.exists():
                    ignore_path.write_text(self._read_ignore_template(), encoding="utf-8")

        actions.append("Qoder configured (.qoder/rules/xp-governance.md, .qoder/mcp.json, .qoderignore)")
        return actions

    def install_codex_project(self, project_dir: Path, dry_run: bool = False) -> List[str]:
        """Provisions Codex (IDE & CLI) .codex/rules/xp-governance.md, .codex/mcp.json, and .codexignore."""
        actions: List[str] = []
        codex_dir = project_dir if project_dir.name == ".codex" else (project_dir / ".codex")
        rules_dir = codex_dir / "rules"

        if not dry_run:
            rules_dir.mkdir(parents=True, exist_ok=True)
            agents_md_content = ""
            if (self.kit_dir / "AGENTS.md").is_file():
                agents_md_content = (self.kit_dir / "AGENTS.md").read_text(encoding="utf-8")

            gov_content = agents_md_content or "# XP Multi-Agent Kit Governance\n"
            (rules_dir / "xp-governance.md").write_text(gov_content, encoding="utf-8")
            (codex_dir / "instructions.md").write_text(gov_content, encoding="utf-8")
            mcp_path = codex_dir / "mcp.json"
            mcp_data = {"mcpServers": build_mcp_servers_dict(self.home_dir)}
            mcp_path.write_text(json.dumps(mcp_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

            if not project_dir.name.startswith("."):
                ignore_path = project_dir / ".codexignore"
                if not ignore_path.exists():
                    ignore_path.write_text(self._read_ignore_template(), encoding="utf-8")

        actions.append("Codex configured (.codex/rules/xp-governance.md, .codex/instructions.md, .codex/mcp.json)")
        return actions

    def install_global_hosts(self, targets: List[str], dry_run: bool = False) -> List[str]:
        """Synchronizes global configurations for OpenCode, Cursor, Qoder, and Codex in user home."""
        actions: List[str] = []
        if dry_run:
            return [f"[Dry-run] Global host sync for {', '.join(targets)}"]

        if "opencode" in targets:
            oc_global = self.home_dir / ".config" / "opencode"
            oc_global.mkdir(parents=True, exist_ok=True)
            self.install_opencode_project(oc_global, dry_run=False)
            if (self.kit_dir / "AGENTS.md").is_file():
                shutil.copy(self.kit_dir / "AGENTS.md", oc_global / "AGENTS.md")
            actions.append(f"OpenCode global config synced at {oc_global}")

        if "antigravity" in targets:
            agy_global = self.home_dir / ".gemini" / "config"
            agy_global.mkdir(parents=True, exist_ok=True)
            dispatcher_content = (
                "# Global Agent Dispatcher — XP Multi-Agent Kit v3.0 (Agnostic Core)\n\n"
                "Master global rule for agent execution (Antigravity, OpenCode, Cursor, Codex, Qoder):\n"
                "1. If the active repository/workspace contains an `AGENTS.md` file, strictly follow its directives as the single source of truth.\n"
                "2. If the workspace does not contain `AGENTS.md`, apply the kit's canonical discipline: strict TDD (RED->GREEN->REFACTOR), L0-L3 risk routing, Autonomous Self-Healing on tool errors, No Workarounds, and persistence in `.agents/memory/PROJECT_MEMORY.md`.\n"
                "3. **Mandatory Language Rule:** Internal skills and workflows are in English for token efficiency, but **ALL user-facing responses and explanations MUST be in Portuguese (Português)** unless requested otherwise.\n"
            )
            (agy_global / "AGENTS.md").write_text(dispatcher_content, encoding="utf-8")
            for sub in ("skills", "agents", "workflows", "policies", "rules", "templates"):
                s_dir = self.kit_dir / ".agents" / sub
                d_dir = agy_global / sub
                if s_dir.is_dir() and not d_dir.exists():
                    try:
                        d_dir.symlink_to(s_dir)
                    except OSError:
                        shutil.copytree(s_dir, d_dir)
            actions.append(f"Antigravity global dispatcher and assets synced at {agy_global}")

        if "cursor" in targets:
            cur_global = self.home_dir / ".cursor"
            cur_global.mkdir(parents=True, exist_ok=True)
            self.install_cursor_project(cur_global, dry_run=False)
            candidate_settings = [
                self.home_dir / ".config" / "Cursor" / "User" / "settings.json",
                self.home_dir / "Library" / "Application Support" / "Cursor" / "User" / "settings.json",
                self.home_dir / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json",
            ]
            for cursor_user_settings in candidate_settings:
                if cursor_user_settings.is_file():
                    try:
                        data = json.loads(cursor_user_settings.read_text(encoding="utf-8"))
                        data["cursor.general.customInstructions"] = (
                            "Follow XP Multi-Agent Kit governance (strict TDD, L0-L3 risk routing, "
                            "PT-BR user responses)."
                        )
                        cursor_user_settings.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
                        actions.append(f"Cursor customInstructions configured at {cursor_user_settings}")
                    except Exception:
                        pass
            actions.append(f"Cursor global config and rules synced at {cur_global}")

        if "qoder" in targets:
            qod_global = self.home_dir / ".qoder"
            qod_global.mkdir(parents=True, exist_ok=True)
            self.install_qoder_project(qod_global, dry_run=False)
            actions.append(f"Qoder global config and rules synced at {qod_global}")

        if "codex" in targets:
            cod_global = self.home_dir / ".codex"
            cod_global.mkdir(parents=True, exist_ok=True)
            self.install_codex_project(cod_global, dry_run=False)
            actions.append(f"Codex global config and rules synced at {cod_global}")

        return actions
