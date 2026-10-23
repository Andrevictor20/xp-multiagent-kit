#!/usr/bin/env python3
"""
scripts/kit_installer.py
XP Multi-Agent Kit v3.0 — Unified Agnostic Installer & Portability Engine (SPEC-002 & SPEC-003)

Supports:
- 4 Host Environments (IDE & CLI): Antigravity, OpenCode, Cursor, Qoder
- Automatic Bilingual Localization (PT / EN) detected from OS locale or --lang
- Global & Project-level installation, MCP auto-configuration, and health diagnostics
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.host_adapters import (
    HostAdapters,
    SUPPORTED_TARGETS,
    build_mcp_servers_dict,
    detect_system_language,
    get_i18n_messages,
    normalize_targets,
)
from scripts.windows_support import (
    SHIM_COMMANDS,
    WindowsPathConfigurator,
    generate_windows_shims,
)


class DependencyChecker:
    """Verifies OS and runtime dependencies."""

    REQUIRED_PYTHON = (3, 8)

    def check_python(self) -> Dict[str, Any]:
        info = sys.version_info
        major, minor = info[0], info[1]
        micro = info[2] if len(info) > 2 else 0
        ok = (major, minor) >= self.REQUIRED_PYTHON
        version_str = f"{major}.{minor}.{micro}"
        msg = (
            f"Python {version_str} (compatível >= 3.8)"
            if ok
            else f"Python {version_str} incompatível: requer Python >= 3.8"
        )
        return {"ok": ok, "major": major, "minor": minor, "micro": micro, "version": version_str, "message": msg}

    def check_command(self, cmd: str, required: bool = True) -> Dict[str, Any]:
        path = shutil.which(cmd)
        if path:
            return {"ok": True, "command": cmd, "path": path, "required": required, "message": f"{cmd} encontrado em {path}"}
        status_msg = "ERRO: Obrigatório" if required else "AVISO: Opcional"
        return {
            "ok": not required,
            "command": cmd,
            "path": None,
            "required": required,
            "message": f"{status_msg} — comando '{cmd}' não encontrado no PATH",
        }

    def detect_package_manager(self) -> Tuple[Optional[str], Optional[str]]:
        if platform.system().lower() == "darwin":
            return ("brew", "brew install") if shutil.which("brew") else ("macos", "instale via Homebrew (https://brew.sh)")
        pms = [
            ("apt-get", "apt", "sudo apt-get update && sudo apt-get install -y"),
            ("dnf", "dnf", "sudo dnf install -y"),
            ("pacman", "pacman", "sudo pacman -S --noconfirm"),
            ("apk", "apk", "apk add --no-cache"),
            ("zypper", "zypper", "sudo zypper install -y"),
        ]
        for binary, name, install_cmd in pms:
            if shutil.which(binary):
                return name, install_cmd
        return None, None

    def check_all(self) -> Dict[str, Any]:
        py_check = self.check_python()
        git_check = self.check_command("git", required=True)
        return {
            "can_proceed": py_check["ok"] and git_check["ok"],
            "checks": {
                "python": py_check,
                "git": git_check,
                "gh": self.check_command("gh", required=False),
                "cargo": self.check_command("cargo", required=False),
                "rtk": self.check_command("rtk", required=False),
                "od": self.check_command("od", required=False),
            },
        }


class PathConfigurator:
    """Idempotently configures ~/.local/bin in user shell RC files (bash, zsh, fish, ksh, profile)."""

    def __init__(self, rc_files: Optional[List[Path]] = None, home_dir: Optional[Path] = None):
        self.home = home_dir or Path.home()
        if rc_files is not None:
            self.rc_files = rc_files
        else:
            zdot = Path(os.environ["ZDOTDIR"]) if os.environ.get("ZDOTDIR") else self.home
            self.rc_files = [
                self.home / ".bashrc",
                zdot / ".zshrc",
                self.home / ".profile",
                zdot / ".zprofile",
                self.home / ".bash_profile",
                self.home / ".kshrc",
                self.home / ".config" / "fish" / "config.fish",
            ]

    def _ensure_active_shell_rc_exists(self) -> None:
        shell_env = os.environ.get("SHELL", "").lower()
        target: Optional[Path] = None
        if "fish" in shell_env:
            target = self.home / ".config" / "fish" / "config.fish"
        elif "zsh" in shell_env:
            zdot = Path(os.environ["ZDOTDIR"]) if os.environ.get("ZDOTDIR") else self.home
            target = zdot / ".zshrc"
        elif "bash" in shell_env:
            target = self.home / ".bashrc"
        elif "ksh" in shell_env:
            target = self.home / ".kshrc"

        if target is not None:
            if target not in self.rc_files:
                self.rc_files.append(target)
            if not target.exists():
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("", encoding="utf-8")
                except Exception:
                    pass

    @staticmethod
    def _format_snippet(rc_file: Path, bin_dir: str) -> str:
        if rc_file.suffix == ".fish" or rc_file.name == "config.fish":
            return (
                "# XP Multi-Agent Kit\n"
                f'if not contains "{bin_dir}" $PATH\n'
                f'    set -gx PATH "{bin_dir}" $PATH\n'
                "end\n"
            )
        return f'# XP Multi-Agent Kit\nexport PATH="{bin_dir}:$PATH"\n'

    def ensure_path_in_rc(self, bin_dir: str) -> bool:
        self._ensure_active_shell_rc_exists()
        added_any = False
        for rc_file in self.rc_files:
            if not rc_file.exists():
                continue
            try:
                content = rc_file.read_text(encoding="utf-8")
                if bin_dir in content:
                    continue
                if content and not content.endswith("\n"):
                    content += "\n"
                snippet = self._format_snippet(rc_file, bin_dir)
                rc_file.write_text(f"{content}\n{snippet}" if content else snippet, encoding="utf-8")
                added_any = True
            except Exception:
                continue
        return added_any



class ProjectInstaller:
    """Injects XP Multi-Agent Kit governance into a project for Antigravity, OpenCode, Cursor, and/or Qoder."""

    def __init__(self, kit_dir: Optional[Path] = None):
        self.kit_dir = kit_dir or Path(__file__).resolve().parent.parent

    def install_project(
        self,
        project_dir: Path,
        use_symlinks: bool = True,
        dry_run: bool = False,
        targets: Optional[Any] = None,
    ) -> Dict[str, Any]:
        actions: List[str] = []
        project_dir = Path(project_dir).resolve()
        resolved_targets = normalize_targets(targets)

        if not dry_run:
            project_dir.mkdir(parents=True, exist_ok=True)
        actions.append(f"Diretório do projeto verificado: {project_dir}")

        agents_dir = project_dir / ".agents"
        if not dry_run:
            agents_dir.mkdir(parents=True, exist_ok=True)
        actions.append(f"Diretório .agents criado: {agents_dir}")

        for folder in ["policies", "rules", "workflows", "templates", "skills", "agents"]:
            src = self.kit_dir / ".agents" / folder
            dst = agents_dir / folder
            if not src.exists():
                continue
            if not dry_run:
                if dst.exists() or dst.is_symlink():
                    if dst.is_symlink() or dst.is_file():
                        dst.unlink()
                    elif dst.is_dir():
                        shutil.rmtree(dst)
                if use_symlinks:
                    try:
                        dst.symlink_to(src)
                    except OSError:
                        shutil.copytree(src, dst)
                else:
                    shutil.copytree(src, dst)
            actions.append(f"Subpasta .agents/{folder} sincronizada ({'symlink' if use_symlinks else 'cópia'})")

        project_agents_md = project_dir / "AGENTS.md"
        src_agents_md = self.kit_dir / "AGENTS.md"
        if src_agents_md.exists():
            if not dry_run:
                shutil.copy(src_agents_md, project_agents_md)
            actions.append(f"AGENTS.md configurado na raiz de {project_dir}")

        ignore_template = self.kit_dir / "templates" / "universal.geminiignore"
        if ignore_template.exists():
            content = ignore_template.read_text(encoding="utf-8")
            if not dry_run:
                for ign_name in [".geminiignore", ".antigravityignore"]:
                    ign_path = project_dir / ign_name
                    if not ign_path.exists():
                        ign_path.write_text(content, encoding="utf-8")
            actions.append("Arquivos .geminiignore e .antigravityignore implantados")

        memory_dir = agents_dir / "memory"
        project_memory = memory_dir / "PROJECT_MEMORY.md"
        if not dry_run:
            memory_dir.mkdir(parents=True, exist_ok=True)
            if not project_memory.exists():
                template_file = self.kit_dir / "templates" / "PROJECT_MEMORY_TEMPLATE.md"
                if template_file.exists():
                    raw = template_file.read_text(encoding="utf-8")
                    replacements = {
                        "{{PROJECT_NAME}}": project_dir.name,
                        "{{LAST_UPDATED}}": "2026-10-16",
                        "{{STATUS}}": "BOOTSTRAPPING",
                        "{{VERSION}}": "v0.1.0",
                        "{{TECH_STACK}}": "Agnostic",
                        "{{PURPOSE}}": f"Project {project_dir.name}",
                        "{{ARCHITECTURE}}": "Modular architecture",
                        "{{BUILD_CMD}}": "make build",
                        "{{TEST_CMD}}": "make test",
                        "{{LINT_CMD}}": "make lint",
                        "{{DEV_CMD}}": "make dev",
                        "{{CI_STATUS}}": "CONFIGURED",
                        "{{QUALITY_GATE}}": "Strict TDD + Zero Workarounds",
                        "{{LAST_EVIDENCE}}": "EV-GENESIS-01",
                        "{{ENV}}": "Local / Development",
                    }
                    for k, v in replacements.items():
                        raw = raw.replace(k, v)
                    project_memory.write_text(raw, encoding="utf-8")
                else:
                    project_memory.write_text(f"# Project Memory: {project_dir.name}\n\nStatus: BOOTSTRAPPING\n", encoding="utf-8")
                actions.append("Memória isolada PROJECT_MEMORY.md inicializada")
            else:
                actions.append("Memória existente preservada sem sobrescrita")

        # Multi-Host Adapters (OpenCode, Cursor, Qoder)
        adapters = HostAdapters(kit_dir=self.kit_dir)
        if "opencode" in resolved_targets:
            actions.extend(adapters.install_opencode_project(project_dir, dry_run=dry_run))
        if "cursor" in resolved_targets:
            actions.extend(adapters.install_cursor_project(project_dir, dry_run=dry_run))
        if "qoder" in resolved_targets:
            actions.extend(adapters.install_qoder_project(project_dir, dry_run=dry_run))
        if "codex" in resolved_targets:
            actions.extend(adapters.install_codex_project(project_dir, dry_run=dry_run))

        return {"ok": True, "actions": actions, "project_dir": str(project_dir), "targets": resolved_targets}


from scripts.mcp_installers import (  # noqa: E402, F401
    CodeReviewGraphInstaller,
    McpConfigurator,
    OpenDesignInstaller,
    RtkInstaller,
)


class GlobalInstaller:
    """Orchestrates global kit installation across Antigravity, OpenCode, Cursor, and Qoder."""

    def __init__(self, kit_dir: Optional[Path] = None, home_dir: Optional[Path] = None):
        self.kit_dir = kit_dir or Path(__file__).resolve().parent.parent
        self.home_dir = home_dir or Path.home()

    def install_global(self, dry_run: bool = False, targets: Optional[Any] = None) -> Dict[str, Any]:
        actions: List[str] = []
        resolved_targets = normalize_targets(targets or "all")
        if dry_run:
            return {"ok": True, "actions": [f"[Dry-run] Global install from {self.kit_dir} for {resolved_targets}"]}

        install_script = self.kit_dir / "scripts" / "install-global.sh"
        if install_script.exists() and platform.system() != "Windows" and shutil.which("bash"):
            res = subprocess.run(["bash", str(install_script)], capture_output=True, text=True)
            if res.returncode != 0:
                return {"ok": False, "error": res.stderr, "actions": actions}
            actions.append("Script install-global.sh executado com sucesso")

        bin_path = self.home_dir / ".local" / "bin"
        bin_dir = str(bin_path)
        if platform.system() == "Windows":
            shims = generate_windows_shims(bin_path, self.kit_dir)
            actions.append(f"{len(shims)} shims .cmd gerados em {bin_dir}")
            WindowsPathConfigurator().ensure_path_in_user_env(bin_dir)
        else:
            PathConfigurator(home_dir=self.home_dir).ensure_path_in_rc(bin_dir)
        McpConfigurator(home_dir=self.home_dir).configure_all()
        OpenDesignInstaller(kit_dir=self.kit_dir, home_dir=self.home_dir).install()
        CodeReviewGraphInstaller(kit_dir=self.kit_dir, home_dir=self.home_dir).install()
        RtkInstaller(kit_dir=self.kit_dir, home_dir=self.home_dir).install()
        adapters = HostAdapters(kit_dir=self.kit_dir, home_dir=self.home_dir)
        actions.extend(adapters.install_global_hosts(resolved_targets, dry_run=dry_run))

        # Auto-discover and upgrade existing projects on the machine
        project_installer = ProjectInstaller(kit_dir=self.kit_dir)
        known_roots = [
            self.home_dir / d
            for d in (
                "Downloads", "Projects", "workspace", "dev", "code", "src",
                "source/repos", "source", "Documents"
            )
        ]
        for root in known_roots:
            if root.is_dir():
                for child in root.iterdir():
                    if child.is_dir() and child.resolve() != self.kit_dir.resolve() and child.name != "xp-multiagent-kit":
                        if (child / ".agents").is_dir() or (child / "AGENTS.md").is_file():
                            p_res = project_installer.install_project(
                                child, use_symlinks=True, dry_run=dry_run, targets=resolved_targets
                            )
                            if p_res.get("ok"):
                                actions.append(f"Projeto existente sincronizado: {child.name}")

        return {"ok": True, "actions": actions, "targets": resolved_targets}


class KitDoctor:
    """Audits environment health, dependencies, and multi-IDE installations."""

    def __init__(self, kit_dir: Optional[Path] = None, home_dir: Optional[Path] = None):
        self.kit_dir = kit_dir or Path(__file__).resolve().parent.parent
        self.home_dir = home_dir or Path.home()
        self.checker = DependencyChecker()

    def run_diagnostics(self) -> Dict[str, Any]:
        deps = self.checker.check_all()["checks"]
        gemini_dir = self.home_dir / ".gemini"
        bin_dir = self.home_dir / ".local" / "bin"
        dirs_status = {
            "gemini_root": gemini_dir.is_dir(),
            "config": (gemini_dir / "config").is_dir(),
            "ide": (gemini_dir / "antigravity-ide").is_dir(),
            "cli": (gemini_dir / "antigravity-cli").is_dir(),
            "bin": bin_dir.is_dir(),
        }
        essential_bins = [
            "agy-run", "xp-run", "agy-spec", "xp-spec",
            "agy-debt", "agy-health", "agy-kit", "xp-kit", "od", "agy-design",
            "code-review-graph", "agy-graph", "agy-crg", "agy-pack", "xp-pack",
            "agy-orchestrate", "xp-orchestrate",
        ]
        hosts_status = {
            "antigravity": (self.home_dir / ".gemini" / "config" / "AGENTS.md").is_file(),
            "opencode": (self.home_dir / ".config" / "opencode" / "opencode.json").is_file(),
            "cursor": (self.home_dir / ".cursor" / "rules" / "00-xp-core.mdc").is_file(),
            "qoder": (self.home_dir / ".qoder" / "rules" / "xp-governance.md").is_file(),
            "codex": (self.home_dir / ".codex" / "rules" / "xp-governance.md").is_file(),
        }
        update_info = {}
        try:
            from scripts.update_manager import UpdateManager
            update_info = UpdateManager(kit_dir=self.kit_dir, home_dir=self.home_dir).check_for_updates()
        except Exception:
            pass

        return {
            "python": deps["python"],
            "git": deps["git"],
            "gh": deps["gh"],
            "rtk": deps["rtk"],
            "antigravity_dirs": {"ok": all(dirs_status.values()), "status": dirs_status, "message": "Diretórios verificados"},
            "path_ok": str(bin_dir) in os.environ.get("PATH", ""),
            "installed_bins": {b: (bin_dir / b).exists() for b in essential_bins},
            "hosts_status": hosts_status,
            "update_info": update_info,
        }

    def print_report(self, lang: Optional[str] = None) -> None:
        m = get_i18n_messages(lang)
        diag = self.run_diagnostics()
        print("=" * 68)
        print(f" {m['doctor_title']} (xp-kit / agy-kit doctor)")
        print("=" * 68)
        for k in ("python", "git"):
            item = diag[k]
            print(f"• {k.capitalize():7}: {'✅' if item['ok'] else '❌'} {item['message']}")

        hosts = diag.get("hosts_status", {})
        if hosts:
            print("\n💻 Ambientes IDE / CLI:")
            for h_name, ok in hosts.items():
                print(f"  - {h_name.capitalize():13}: {'✅ Configurado' if ok else '⚪ Não detectado'}")

        installed = diag.get("installed_bins", {})
        if installed:
            print(f"\n{m['global_bins']}")
            for b, exists in installed.items():
                print(f"  - {b:18}: {m['installed'] if exists else m['missing']}")

        up = diag.get("update_info", {})
        if up.get("has_update"):
            print("\n" + "=" * 68)
            print(f"💡 [XP-KIT] Nova atualização disponível ({up.get('latest_version')})!")
            print("   Execute 'xp-kit update' para sincronizar com as últimas correções.")
        print("=" * 68)


def interactive_wizard(kit_dir: Path, dry_run: bool = False, lang: Optional[str] = None) -> int:
    """Bilingual (PT/EN) interactive installation wizard with multi-IDE/CLI target selection."""
    m = get_i18n_messages(lang)
    print("=" * 68)
    print(f" {m['wizard_title']}")
    if dry_run:
        print(f" {m['dry_run_banner']}")
    print("=" * 68)
    print(f"\n{m['choose_scope']}")
    print(f"  {m['opt_global']}")
    print(f"  {m['opt_project']}")
    print(f"  {m['opt_both']}\n")

    try:
        choice = input(m["prompt_scope"]).strip() or "1"
        print(f"\n{m['choose_targets']}")
        for opt_key in ("opt_t_all", "opt_t_agy", "opt_t_oc", "opt_t_cur", "opt_t_qod", "opt_t_cod"):
            print(f"  {m[opt_key]}")
        t_choice = input(f"\n{m['prompt_targets']}").strip() or "1"
    except (EOFError, KeyboardInterrupt):
        print(f"\n{m['cancelled']}")
        return 1

    target_map = {"1": "all", "2": "antigravity", "3": "opencode", "4": "cursor", "5": "qoder", "6": "codex"}
    targets = normalize_targets(target_map.get(t_choice, "all"))

    if not DependencyChecker().check_all()["can_proceed"]:
        print(m["deps_missing"])
        return 1

    if choice == "1":
        print(f"\n{m['installing_global']}")
        res = GlobalInstaller(kit_dir=kit_dir).install_global(dry_run=dry_run, targets=targets)
        print(m["global_ok"] if res["ok"] else f"{m['global_fail']} {res.get('error')}")
        return 0 if res["ok"] else 1

    if choice in ("2", "3"):
        try:
            p_input = input(m["prompt_project_dir"]).strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{m['cancelled']}")
            return 1
        target_path = Path(p_input).resolve() if p_input else Path.cwd()
        if choice == "3":
            print(f"\n{m['installing_global']}")
            g_res = GlobalInstaller(kit_dir=kit_dir).install_global(dry_run=dry_run, targets=targets)
            if not g_res["ok"]:
                print(f"{m['global_fail']} {g_res.get('error')}")
                return 1
        print(f"\n{m['installing_project']} {target_path}...")
        p_res = ProjectInstaller(kit_dir=kit_dir).install_project(target_path, use_symlinks=True, dry_run=dry_run, targets=targets)
        print(f"{m['project_ok']} {target_path}!" if p_res["ok"] else f"{m['project_fail']} {p_res.get('error')}")
        return 0 if p_res["ok"] else 1

    print(m["invalid_option"])
    return 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="XP Multi-Agent Kit v3.1 — Unified Agnostic Installer (xp-kit / agy-kit)")
    parser.add_argument("command", nargs="?", choices=["install", "doctor", "init", "sync", "version", "update"])
    parser.add_argument("path", nargs="?", default=None, help="Optional project path for init/install")
    parser.add_argument("--global", "-g", dest="install_global", action="store_true", help="Install globally")
    parser.add_argument("--project", "-p", dest="project_path", type=str, help="Inject into specific project directory")
    parser.add_argument("--both", dest="both_path", type=str, help="Install globally and inject into project")
    parser.add_argument("--target", "-t", default="all", help="Target host(s): all, antigravity, opencode, cursor, qoder, codex")
    parser.add_argument("--lang", "-l", default=None, choices=["pt", "en", "auto"], help="Language override (pt, en, auto)")
    parser.add_argument("--yes", "-y", action="store_true", help="Non-interactive mode")
    parser.add_argument("--no-deps", action="store_true", help="Skip OS dependency checks")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without writing to disk")
    parser.add_argument("--configure-mcp", action="store_true", help="Configure MCP servers and auto-approval")
    parser.add_argument("--install-opendesign", action="store_true", help="Install OpenDesign (od)")
    parser.add_argument("--install-graph", action="store_true", help="Install CodeReviewGraph (crg)")

    args = parser.parse_args(argv)
    kit_dir = Path(__file__).resolve().parent.parent
    lang = None if args.lang == "auto" else args.lang
    m = get_i18n_messages(lang)
    targets = normalize_targets(args.target)

    if args.command == "version":
        print("XP Multi-Agent Kit v3.1.0")
        return 0
    if args.command == "update":
        from scripts.update_manager import main as update_main
        return update_main()
    if args.command == "doctor":
        KitDoctor(kit_dir=kit_dir).print_report(lang=lang)
        return 0
    if args.configure_mcp:
        return 0 if McpConfigurator().configure_all()["ok"] else 1
    if args.install_opendesign:
        return 0 if OpenDesignInstaller(kit_dir=kit_dir).install()["ok"] else 1
    if args.install_graph:
        return 0 if CodeReviewGraphInstaller(kit_dir=kit_dir).install()["ok"] else 1
    if args.path and not args.project_path:
        args.project_path = str(Path(args.path).resolve())
    if args.command == "init" and not args.project_path:
        args.project_path = str(Path.cwd())
    if args.command == "sync" and not args.install_global and not args.project_path:
        args.install_global = True

    if not args.no_deps and (args.install_global or args.project_path or args.both_path or args.yes):
        if not DependencyChecker().check_all()["can_proceed"]:
            print(m["deps_missing"])
            return 1

    if args.both_path:
        print(f"\n{m['installing_global']}")
        g_res = GlobalInstaller(kit_dir=kit_dir).install_global(dry_run=args.dry_run, targets=targets)
        if not g_res["ok"]:
            print(f"{m['global_fail']} {g_res.get('error', '')}")
            return 1
        print(f"{m['global_ok']}")
        for a in g_res.get("actions", []):
            print(f"  • {a}")
        print(f"\n{m['installing_project']} {args.both_path}")
        p_res = ProjectInstaller(kit_dir=kit_dir).install_project(Path(args.both_path), use_symlinks=True, dry_run=args.dry_run, targets=targets)
        if p_res["ok"]:
            print(f"{m['project_ok']}: {args.both_path}")
            return 0
        else:
            print(f"{m['project_fail']} {p_res.get('error', '')}")
            return 1

    if args.install_global or (args.yes and not args.project_path):
        print(f"\n{m['installing_global']}")
        res = GlobalInstaller(kit_dir=kit_dir).install_global(dry_run=args.dry_run, targets=targets)
        if res["ok"]:
            print(f"{m['global_ok']}")
            print(f"🎯 Hosts configurados: {', '.join(res.get('targets', []))}")
            for a in res.get("actions", []):
                print(f"  • {a}")
            return 0
        else:
            print(f"{m['global_fail']} {res.get('error', '')}")
            return 1

    if args.project_path:
        print(f"\n{m['installing_project']} {args.project_path}")
        p_installer = ProjectInstaller(kit_dir=kit_dir)
        res = p_installer.install_project(Path(args.project_path), use_symlinks=True, dry_run=args.dry_run, targets=targets)
        if res["ok"]:
            print(f"{m['project_ok']}: {args.project_path}")
            for a in res.get("actions", []):
                print(f"  • {a}")
            return 0
        else:
            print(f"{m['project_fail']} {res.get('error', '')}")
            return 1

    return interactive_wizard(kit_dir=kit_dir, dry_run=args.dry_run, lang=lang)


if __name__ == "__main__":
    sys.exit(main())
