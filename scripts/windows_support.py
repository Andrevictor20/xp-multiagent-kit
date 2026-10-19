#!/usr/bin/env python3
"""
scripts/windows_support.py
Windows-native support: .cmd shims generation, User PATH configuration, and registry helpers.
Part of XP Multi-Agent Kit v3.1 (SPEC-005).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

SHIM_COMMANDS: Dict[str, str] = {
    "xp-spec": "scripts/spec_tool.py",
    "xp-kit": "scripts/kit_installer.py",
    "xp-run": "scripts/agy-run",
    "xp-conformance": "scripts/conformance_report.py",
    "xp-evidence": "scripts/evidence_recorder.py",
    "xp-handoff": "scripts/context_compactor.py",
    "xp-debt": "scripts/debt_tracker.py",
    "xp-design": "scripts/agy_design.py",
    "xp-turn": "scripts/turn_telemetry.py",
    "xp-skill-index": "scripts/skill_index.py",
    "xp-health": "scripts/agy_health.py",
    "xp-effort": "scripts/agy_effort_router.py",
    "xp-pack": "scripts/skill_packer.py",
    "agy-spec": "scripts/spec_tool.py",
    "agy-kit": "scripts/kit_installer.py",
    "agy-run": "scripts/agy-run",
    "agy-turn": "scripts/turn_telemetry.py",
    "agy-evidence": "scripts/evidence_recorder.py",
    "agy-conformance": "scripts/conformance_report.py",
    "agy-skill-index": "scripts/skill_index.py",
    "agy-effort": "scripts/agy_effort_router.py",
    "agy-smart": "scripts/agy_effort_router.py",
    "agy-health": "scripts/agy_health.py",
    "agy-debt": "scripts/debt_tracker.py",
    "agy-pack": "scripts/skill_packer.py",
}


def generate_windows_shims(bin_dir: Path, kit_dir: Path) -> List[Path]:
    """Generates Windows .cmd shims for all kit CLI tools in bin_dir."""
    bin_path = Path(bin_dir)
    bin_path.mkdir(parents=True, exist_ok=True)
    generated: List[Path] = []

    for cmd_name, rel_script in SHIM_COMMANDS.items():
        script_path = (kit_dir / rel_script).resolve()
        shim_file = bin_path / f"{cmd_name}.cmd"
        content = (
            "@echo off\r\n"
            "where python >nul 2>nul\r\n"
            "if %errorlevel% equ 0 (\r\n"
            f'    python "{script_path}" %*\r\n'
            ") else (\r\n"
            f'    py -3 "{script_path}" %*\r\n'
            ")\r\n"
        )
        shim_file.write_text(content, encoding="utf-8")
        generated.append(shim_file)

    return generated


class WindowsPathConfigurator:
    """Configures user-level PATH on Windows via Registry (HKCU\\Environment)."""

    def ensure_path_in_user_env(self, target_dir: str) -> bool:
        """Adds target_dir to Windows user PATH if not already present."""
        try:
            import winreg
        except ImportError:
            return False

        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0,
                winreg.KEY_READ | winreg.KEY_WRITE,
            )
        except Exception:
            return False

        try:
            try:
                current_path, reg_type = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_path, reg_type = "", winreg.REG_EXPAND_SZ

            paths = [p.strip() for p in current_path.split(";") if p.strip()]
            norm_target = os.path.normpath(target_dir).lower()

            if any(os.path.normpath(p).lower() == norm_target for p in paths):
                try:
                    winreg.CloseKey(key)
                except Exception:
                    pass
                return False

            new_path = f"{current_path};{target_dir}" if current_path else target_dir
            winreg.SetValueEx(key, "Path", 0, reg_type, new_path)
            try:
                winreg.CloseKey(key)
            except Exception:
                pass
            return True
        except Exception:
            try:
                winreg.CloseKey(key)
            except Exception:
                pass
            return False
