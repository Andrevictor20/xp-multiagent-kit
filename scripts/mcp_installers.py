#!/usr/bin/env python3
"""
scripts/mcp_installers.py
MCP Server & Auxiliary Tool Installers (OpenDesign, CodeReviewGraph, McpConfigurator)
for XP Multi-Agent Kit v3.0.
"""

from __future__ import annotations

import json
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


class OpenDesignInstaller:
    """Installs and links OpenDesign (od) into ~/.local/share/open-design and ~/.local/bin/od."""

    REPO_URL = "https://github.com/opendesign/open-design.git"

    def __init__(self, kit_dir: Optional[Path] = None, home_dir: Optional[Path] = None):
        self.kit_dir = kit_dir or Path(__file__).resolve().parent.parent
        self.home_dir = home_dir or Path.home()
        self.od_dir = self.home_dir / ".local" / "share" / "open-design"
        self.bin_dir = self.home_dir / ".local" / "bin"

    def _run_clone_or_copy(self) -> Any:
        self.od_dir.parent.mkdir(parents=True, exist_ok=True)
        git_cmd = shutil.which("git")
        if not git_cmd:
            return None
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        return subprocess.run(
            [git_cmd, "clone", "--depth", "1", self.REPO_URL, str(self.od_dir)],
            env=env,
            capture_output=True,
            text=True,
        )

    def install(self) -> Dict[str, Any]:
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        daemon_script = self.od_dir / "apps" / "daemon" / "bin" / "od.mjs"
        if not daemon_script.exists():
            self._run_clone_or_copy()
        if daemon_script.exists():
            try:
                daemon_script.chmod(daemon_script.stat().st_mode | 0o111)
            except Exception:
                pass
            target_link = self.bin_dir / "od"
            if target_link.exists() or target_link.is_symlink():
                try:
                    target_link.unlink()
                except Exception:
                    pass
            try:
                target_link.symlink_to(daemon_script)
            except Exception:
                target_link.write_text(f'#!/usr/bin/env bash\nexec node "{daemon_script}" "$@"\n', encoding="utf-8")
                target_link.chmod(target_link.stat().st_mode | 0o111)
            for alias_name in ("agy-design", "xp-design"):
                alias_link = self.bin_dir / alias_name
                if not alias_link.exists() and not alias_link.is_symlink():
                    try:
                        alias_link.symlink_to(target_link)
                    except Exception:
                        pass
            return {"ok": True, "path": str(target_link), "message": f"OpenDesign instalado em {target_link}"}
        return {"ok": False, "path": None, "message": "Falha ao instalar OpenDesign: od.mjs não encontrado."}


class CodeReviewGraphInstaller:
    """Installs and links CodeReviewGraph into ~/.local/share/code-review-graph and ~/.local/bin."""

    REPO_URL = "https://github.com/tirth8205/code-review-graph.git"

    def __init__(self, kit_dir: Optional[Path] = None, home_dir: Optional[Path] = None):
        self.kit_dir = kit_dir or Path(__file__).resolve().parent.parent
        self.home_dir = home_dir or Path.home()
        self.crg_dir = self.home_dir / ".local" / "share" / "code-review-graph"
        self.bin_dir = self.home_dir / ".local" / "bin"

    def _run_clone_or_copy(self) -> Any:
        self.crg_dir.parent.mkdir(parents=True, exist_ok=True)
        staging_dir = self.kit_dir / "code-review-graph-staging"
        if staging_dir.exists() and (staging_dir / "pyproject.toml").exists():
            if not self.crg_dir.exists():
                shutil.copytree(str(staging_dir), str(self.crg_dir), dirs_exist_ok=True)
            return True
        git_cmd = shutil.which("git")
        if not git_cmd:
            return None
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        return subprocess.run(
            [git_cmd, "clone", "--depth", "1", self.REPO_URL, str(self.crg_dir)],
            env=env,
            capture_output=True,
            text=True,
        )

    def _setup_venv_and_install(self) -> bool:
        venv_dir = self.crg_dir / ".venv"
        real_uv = shutil.which("uv") or str(self.home_dir / ".local" / "bin" / "uv")
        if Path(real_uv).exists() or shutil.which("uv"):
            res = subprocess.run([real_uv, "venv", str(venv_dir)], cwd=str(self.crg_dir), capture_output=True, text=True)
            if res.returncode == 0:
                subprocess.run([real_uv, "pip", "install", "-e", "."], cwd=str(self.crg_dir), capture_output=True, text=True)
                return True
        py_cmd = shutil.which("python3") or sys.executable
        res = subprocess.run([py_cmd, "-m", "venv", str(venv_dir)], cwd=str(self.crg_dir), capture_output=True, text=True)
        if res.returncode == 0:
            subprocess.run([str(venv_dir / "bin" / "pip"), "install", "-e", "."], cwd=str(self.crg_dir), capture_output=True, text=True)
            return True
        return False

    def install(self) -> Dict[str, Any]:
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        venv_bin = self.crg_dir / ".venv" / "bin" / "code-review-graph"
        if not venv_bin.exists():
            self._run_clone_or_copy()
            self._setup_venv_and_install()
        if venv_bin.exists():
            try:
                venv_bin.chmod(venv_bin.stat().st_mode | 0o111)
            except Exception:
                pass
            created_links = []
            for link_name in ["code-review-graph", "agy-graph", "agy-crg", "xp-graph"]:
                target_link = self.bin_dir / link_name
                if target_link.exists() or target_link.is_symlink():
                    try:
                        target_link.unlink()
                    except Exception:
                        pass
                try:
                    target_link.symlink_to(venv_bin)
                except Exception:
                    target_link.write_text(f'#!/usr/bin/env bash\nexec "{venv_bin}" "$@"\n', encoding="utf-8")
                    target_link.chmod(target_link.stat().st_mode | 0o111)
                created_links.append(str(target_link))
            return {"ok": True, "path": str(self.bin_dir / "code-review-graph"), "aliases": created_links, "message": "CodeReviewGraph instalado"}
        return {"ok": False, "path": None, "message": "Falha ao instalar CodeReviewGraph."}


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

