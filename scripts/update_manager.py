#!/usr/bin/env python3
"""
scripts/update_manager.py — Autonomous Update Checker & Synchronizer (xp-kit update)
XP Multi-Agent Kit v3.1

Features:
- Non-blocking 24h cached remote update check
- Discrete single-line notification when update is available
- Atomic git pull & global configuration synchronization
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class UpdateManager:
    """Manages update discovery, caching, and execution for XP Multi-Agent Kit."""

    CACHE_MAX_AGE_SECONDS = 86400  # 24 hours

    def __init__(
        self,
        kit_dir: Optional[Path] = None,
        home_dir: Optional[Path] = None,
        cache_dir: Optional[Path] = None,
    ):
        self.kit_dir = kit_dir or ROOT_DIR
        self.home_dir = home_dir or Path.home()
        self.cache_dir = cache_dir or self.home_dir
        self.cache_file = self.cache_dir / ".xp_kit_update_cache.json"

    def read_cache(self) -> Optional[Dict[str, Any]]:
        if not self.cache_file.is_file():
            return None
        try:
            return json.loads(self.cache_file.read_text(encoding="utf-8"))
        except Exception:
            return None

    def write_cache(self, data: Dict[str, Any]) -> None:
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except Exception:
            pass

    def check_for_updates(self, force: bool = False) -> Dict[str, Any]:
        """Checks for new commits or releases with a 24h cache window."""
        now = time.time()
        cached = self.read_cache()
        if not force and cached and (now - cached.get("checked_at", 0)) < self.CACHE_MAX_AGE_SECONDS:
            return cached

        res_data: Dict[str, Any] = {
            "checked_at": now,
            "has_update": False,
            "latest_version": "v3.1.0",
            "current_version": "v3.1.0",
            "remote_commit": "",
            "local_commit": "",
        }

        git_dir = self.kit_dir / ".git"
        if git_dir.exists():
            try:
                local_rev = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=str(self.kit_dir),
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                if local_rev.returncode == 0:
                    res_data["local_commit"] = local_rev.stdout.strip()

                remote_rev = subprocess.run(
                    ["git", "ls-remote", "origin", "-h", "refs/heads/main"],
                    cwd=str(self.kit_dir),
                    capture_output=True,
                    text=True,
                    timeout=4,
                )
                if remote_rev.returncode == 0 and remote_rev.stdout:
                    parts = remote_rev.stdout.split()
                    if parts:
                        res_data["remote_commit"] = parts[0]
                        if res_data["local_commit"] and res_data["remote_commit"] != res_data["local_commit"]:
                            res_data["has_update"] = True
                            res_data["latest_version"] = "latest"
            except Exception:
                pass

        self.write_cache(res_data)
        return res_data

    def format_update_notice(self, version: str) -> str:
        """Formats an unobtrusive 1-line update notification."""
        return f"💡 [XP-KIT] Nova atualização disponível ({version})! Execute 'xp-kit update' para sincronizar."

    def run_update(self) -> Dict[str, Any]:
        """Pulls latest changes and re-synchronizes global installations."""
        actions = []
        git_dir = self.kit_dir / ".git"
        if git_dir.exists():
            pull_res = subprocess.run(
                ["git", "pull", "--ff-only"],
                cwd=str(self.kit_dir),
                capture_output=True,
                text=True,
            )
            if pull_res.returncode != 0:
                return {
                    "ok": False,
                    "error": f"git pull falhou: {pull_res.stderr.strip()}",
                    "actions": actions,
                }
            actions.append("Repositório atualizado via git pull")

        from scripts.kit_installer import GlobalInstaller

        g_res = GlobalInstaller(kit_dir=self.kit_dir, home_dir=self.home_dir).install_global()
        actions.extend(g_res.get("actions", []))
        self.check_for_updates(force=True)
        return {"ok": True, "actions": actions}


def main(argv: Optional[List[str]] = None) -> int:
    mgr = UpdateManager()
    print("⏳ Verificando atualizações do XP Multi-Agent Kit...")
    info = mgr.check_for_updates(force=True)
    if info.get("has_update"):
        print(f"📦 Nova versão detectada! Atualizando...")
        res = mgr.run_update()
        if res["ok"]:
            print("✅ XP Multi-Agent Kit atualizado com sucesso!")
            for a in res.get("actions", []):
                print(f"   • {a}")
            return 0
        print(f"❌ Falha na atualização: {res.get('error')}", file=sys.stderr)
        return 1
    print("✅ O XP Multi-Agent Kit já está na versão mais recente!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
