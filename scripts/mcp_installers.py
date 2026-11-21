#!/usr/bin/env python3
"""
scripts/mcp_installers.py
MCP Server & Auxiliary Tool Installers (McpConfigurator)
for XP Multi-Agent Kit v3.0.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.host_adapters import build_mcp_servers_dict


class McpConfigurator:
    """Configures MCP auto-approval and server entries across Antigravity profiles."""

    def __init__(self, home_dir: Optional[Path] = None):
        self.home_dir = home_dir or Path.home()

    def configure_all(self) -> Dict[str, Any]:
        gemini_dir = self.home_dir / ".gemini"
        settings_update = {
            "approval_mode": "auto",
            "auto_approve": True,
            "autoApprove": True,
            "auto_approve_mcp": True,
            "permissions": {
                "call_mcp_tool": "allow",
                "read_resource": "allow",
                "list_resources": "allow",
                "browser_subagent": "allow",
                "read_url_content": "allow",
                "run_command": "allow",
            },
        }
        for p in [
            gemini_dir / "config" / "settings.json",
            gemini_dir / "antigravity-ide" / "settings.json",
            gemini_dir / "antigravity-cli" / "settings.json",
            gemini_dir / "settings.json",
        ]:
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
                data.update(settings_update)
                p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            except Exception:
                pass

        servers = build_mcp_servers_dict(self.home_dir)
        for p in [
            gemini_dir / "config" / "mcp_config.json",
            gemini_dir / "antigravity-ide" / "mcp_config.json",
            gemini_dir / "mcp_config.json",
        ]:
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                mcp_data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"mcpServers": {}}
                if "mcpServers" not in mcp_data:
                    mcp_data["mcpServers"] = {}
                for s_name, s_cfg in servers.items():
                    cur = mcp_data["mcpServers"].get(s_name, {})
                    cur.update(s_cfg)
                    cur.pop("autoApprove", None)
                    cur.pop("alwaysAllow", None)
                    mcp_data["mcpServers"][s_name] = cur
                for root_key in ("autoApprove", "auto_approve", "approval_mode"):
                    mcp_data.pop(root_key, None)
                p.write_text(json.dumps(mcp_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            except Exception:
                pass
        return {"ok": True, "message": "Configurações MCP sincronizadas com sucesso"}


class RtkInstaller:
    """Installs or verifies RTK (Rust Token Killer) binary in ~/.local/bin/rtk."""

    RELEASE_BASE_URL = "https://github.com/rtk-ai/rtk/releases/latest/download"

    def __init__(self, kit_dir: Optional[Path] = None, home_dir: Optional[Path] = None):
        self.kit_dir = kit_dir or Path(__file__).resolve().parent.parent
        self.home_dir = home_dir or Path.home()
        self.bin_dir = self.home_dir / ".local" / "bin"

    def get_download_url(self) -> Optional[str]:
        system = platform.system().lower()
        machine = platform.machine().lower()
        if "linux" in system:
            arch = "x86_64" if machine in ("x86_64", "amd64") else ("aarch64" if "arm" in machine or "aarch64" in machine else "x86_64")
            return f"{self.RELEASE_BASE_URL}/rtk-{arch}-unknown-linux-musl.tar.gz"
        elif "darwin" in system:
            arch = "aarch64" if "arm" in machine or "aarch64" in machine else "x86_64"
            return f"{self.RELEASE_BASE_URL}/rtk-{arch}-apple-darwin.tar.gz"
        return None

    def install(self) -> Dict[str, Any]:
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        rtk_target = self.bin_dir / "rtk"
        if rtk_target.exists():
            return {"ok": True, "path": str(rtk_target), "message": f"RTK already installed at {rtk_target}"}

        existing = shutil.which("rtk")
        if existing:
            try:
                rtk_target.symlink_to(existing)
            except Exception:
                pass
            return {"ok": True, "path": existing, "message": f"RTK found at {existing}"}

        cargo_cmd = shutil.which("cargo")
        if cargo_cmd:
            res = subprocess.run([cargo_cmd, "install", "rtk", "--root", str(self.home_dir / ".local")], capture_output=True, text=True)
            if res.returncode == 0 and rtk_target.exists():
                return {"ok": True, "path": str(rtk_target), "message": f"RTK installed via cargo at {rtk_target}"}

        return {
            "ok": True,
            "path": None,
            "fallback": True,
            "message": "RTK binary optional: Python smart-tool-optimizer fallback active."
        }


class AletheInstaller:
    """Installs and links Alethe Orchestrator into ~/.local/share/alethe-orchestrate and ~/.local/bin."""

    REPO_URL = "https://github.com/Kc1t/alethe-orchestrate-skill.git"

    def __init__(self, kit_dir: Optional[Path] = None, home_dir: Optional[Path] = None):
        self.kit_dir = kit_dir or Path(__file__).resolve().parent.parent
        self.home_dir = home_dir or Path.home()
        self.alethe_dir = self.home_dir / ".local" / "share" / "alethe-orchestrate"
        self.bin_dir = self.home_dir / ".local" / "bin"

    def _run_clone_or_copy(self, source_dir: Optional[Path] = None) -> bool:
        self.alethe_dir.parent.mkdir(parents=True, exist_ok=True)
        if source_dir and source_dir.exists():
            src_skill = source_dir / "skills" / "alethe" if (source_dir / "skills" / "alethe").exists() else source_dir
            if (src_skill / "scripts" / "orchestrate.py").exists():
                if self.alethe_dir.exists():
                    shutil.rmtree(self.alethe_dir)
                shutil.copytree(src_skill, self.alethe_dir)
                return True
        staging = self.kit_dir / "alethe-orchestrate-skill-main" / "skills" / "alethe"
        if staging.exists():
            if self.alethe_dir.exists():
                shutil.rmtree(self.alethe_dir)
            shutil.copytree(staging, self.alethe_dir)
            return True
        git_cmd = shutil.which("git")
        if git_cmd:
            env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
            temp_target = self.alethe_dir.with_name("alethe-temp")
            if temp_target.exists():
                shutil.rmtree(temp_target)
            res = subprocess.run(
                [git_cmd, "clone", "--depth", "1", self.REPO_URL, str(temp_target)],
                env=env,
                capture_output=True,
                text=True,
            )
            if res.returncode == 0 and (temp_target / "skills" / "alethe").exists():
                if self.alethe_dir.exists():
                    shutil.rmtree(self.alethe_dir)
                shutil.copytree(temp_target / "skills" / "alethe", self.alethe_dir)
                shutil.rmtree(temp_target)
                return True
        return False

    def install(self, source_dir: Optional[Path] = None) -> Dict[str, Any]:
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        orchestrate_script = self.alethe_dir / "scripts" / "orchestrate.py"
        if not orchestrate_script.exists():
            self._run_clone_or_copy(source_dir)

        if orchestrate_script.exists():
            try:
                orchestrate_script.chmod(orchestrate_script.stat().st_mode | 0o111)
            except Exception:
                pass

            launcher_content = f'#!/usr/bin/env bash\nexec python3 "{orchestrate_script}" "$@"\n'
            target_bin = self.bin_dir / "alethe"
            created_links = []
            for bin_name in ("alethe", "xp-alethe", "agy-alethe"):
                b_path = self.bin_dir / bin_name
                try:
                    b_path.write_text(launcher_content, encoding="utf-8")
                    b_path.chmod(b_path.stat().st_mode | 0o111)
                    created_links.append(bin_name)
                except Exception:
                    pass

            gemini_skills = self.home_dir / ".gemini" / "config" / "skills"
            if gemini_skills.exists():
                skill_link = gemini_skills / "alethe"
                if not skill_link.exists() and not skill_link.is_symlink():
                    try:
                        skill_link.symlink_to(self.alethe_dir)
                    except Exception:
                        pass

            return {
                "ok": True,
                "path": str(target_bin),
                "aliases": created_links,
                "message": f"Alethe Orchestrator instalado em {target_bin}",
            }
        return {"ok": False, "path": None, "message": "Falha ao instalar Alethe: orchestrate.py não encontrado."}


