#!/usr/bin/env python3
"""
scripts/kit_installer.py
XP Multi-Agent Kit v2 — Motor de Instalação e Portabilidade Unificado (SPEC-002)

Fornece verificação de dependências, instalação global e por projeto,
configuração de PATH e diagnóstico de integridade (agy-kit doctor).
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class DependencyChecker:
    """Verifica e diagnostica dependências do sistema operacional e ambiente."""

    REQUIRED_PYTHON = (3, 8)

    def check_python(self) -> Dict[str, Any]:
        info = sys.version_info
        major = info[0]
        minor = info[1]
        micro = info[2] if len(info) > 2 else 0
        ok = (major, minor) >= self.REQUIRED_PYTHON
        version_str = f"{major}.{minor}.{micro}"
        if ok:
            return {
                "ok": True,
                "major": major,
                "minor": minor,
                "micro": micro,
                "version": version_str,
                "message": f"Python {version_str} (compatível >= 3.8)",
            }
        return {
            "ok": False,
            "major": major,
            "minor": minor,
            "micro": micro,
            "version": version_str,
            "message": f"Python {version_str} incompatível: requer Python >= 3.8",
        }

    def check_command(self, cmd: str, required: bool = True) -> Dict[str, Any]:
        path = shutil.which(cmd)
        if path:
            return {
                "ok": True,
                "command": cmd,
                "path": path,
                "required": required,
                "message": f"{cmd} encontrado em {path}",
            }
        status_msg = "ERRO: Obrigatório" if required else "AVISO: Opcional"
        return {
            "ok": not required,
            "command": cmd,
            "path": None,
            "required": required,
            "message": f"{status_msg} — comando '{cmd}' não encontrado no PATH",
        }

    def detect_package_manager(self) -> Tuple[Optional[str], Optional[str]]:
        system = platform.system().lower()
        if system == "darwin":
            if shutil.which("brew"):
                return "brew", "brew install"
            return "macos", "instale via Homebrew (https://brew.sh)"

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
        gh_check = self.check_command("gh", required=False)
        cargo_check = self.check_command("cargo", required=False)
        rtk_check = self.check_command("rtk", required=False)

        can_proceed = py_check["ok"] and git_check["ok"]
        return {
            "can_proceed": can_proceed,
            "checks": {
                "python": py_check,
                "git": git_check,
                "gh": gh_check,
                "cargo": cargo_check,
                "rtk": rtk_check,
            },
        }


class PathConfigurator:
    """Configura e adiciona caminhos ao PATH de forma idempotente no shell do usuário."""

    def __init__(self, rc_files: Optional[List[Path]] = None):
        if rc_files is not None:
            self.rc_files = rc_files
        else:
            home = Path.home()
            self.rc_files = [
                home / ".bashrc",
                home / ".zshrc",
                home / ".profile",
            ]

    def ensure_path_in_rc(self, bin_dir: str) -> bool:
        added_any = False
        export_line = f'export PATH="{bin_dir}:$PATH"'
        identifier = f'# XP Multi-Agent Kit\n{export_line}\n'

        for rc_file in self.rc_files:
            if not rc_file.exists():
                continue
            try:
                content = rc_file.read_text(encoding="utf-8")
                if bin_dir in content:
                    continue  # Já configurado de forma idempotente
                
                # Adiciona no final com quebra de linha limpa
                new_content = content
                if not new_content.endswith("\n"):
                    new_content += "\n"
                new_content += f"\n{identifier}"
                rc_file.write_text(new_content, encoding="utf-8")
                added_any = True
            except Exception:
                continue

        return added_any


class ProjectInstaller:
    """Injeta e configura a governança do XP Multi-Agent Kit em um projeto isolado."""

    def __init__(self, kit_dir: Optional[Path] = None):
        self.kit_dir = kit_dir or Path(__file__).resolve().parent.parent

    def install_project(
        self,
        project_dir: Path,
        use_symlinks: bool = True,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        actions: List[str] = []
        project_dir = Path(project_dir).resolve()

        if not dry_run:
            project_dir.mkdir(parents=True, exist_ok=True)
        actions.append(f"Diretório do projeto verificado: {project_dir}")

        agents_dir = project_dir / ".agents"
        if not dry_run:
            agents_dir.mkdir(parents=True, exist_ok=True)
        actions.append(f"Diretório .agents criado: {agents_dir}")

        # Sincroniza subpastas do kit
        folders_to_sync = ["policies", "rules", "workflows", "templates"]
        for folder in folders_to_sync:
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
                    dst.symlink_to(src)
                else:
                    shutil.copytree(src, dst)
            actions.append(f"Subpasta .agents/{folder} sincronizada ({'symlink' if use_symlinks else 'cópia'})")

        # Configura AGENTS.md na raiz do projeto
        project_agents_md = project_dir / "AGENTS.md"
        src_agents_md = self.kit_dir / "AGENTS.md"
        if src_agents_md.exists():
            if not dry_run:
                if not project_agents_md.exists():
                    shutil.copy(src_agents_md, project_agents_md)
            actions.append(f"AGENTS.md configurado na raiz de {project_dir}")

        # Configura ignore rules (.geminiignore e .antigravityignore)
        ignore_template = self.kit_dir / "templates" / "universal.geminiignore"
        if ignore_template.exists():
            content = ignore_template.read_text(encoding="utf-8")
            if not dry_run:
                for ign_name in [".geminiignore", ".antigravityignore"]:
                    ign_path = project_dir / ign_name
                    if not ign_path.exists():
                        ign_path.write_text(content, encoding="utf-8")
            actions.append("Arquivos .geminiignore e .antigravityignore implantados")

        # Inicializa PROJECT_MEMORY.md se não existir
        memory_dir = agents_dir / "memory"
        project_memory = memory_dir / "PROJECT_MEMORY.md"
        if not dry_run:
            memory_dir.mkdir(parents=True, exist_ok=True)
            if not project_memory.exists():
                init_mem_script = self.kit_dir / "scripts" / "agy-init-memory"
                initialized = False
                if init_mem_script.exists():
                    try:
                        res = subprocess.run(
                            [sys.executable, str(init_mem_script), "--project-dir", str(project_dir)],
                            capture_output=True,
                            text=True,
                        )
                        if res.returncode == 0 and project_memory.exists():
                            initialized = True
                    except Exception:
                        pass

                if not initialized and not project_memory.exists():
                    template_file = self.kit_dir / "templates" / "PROJECT_MEMORY_TEMPLATE.md"
                    if template_file.exists():
                        raw = template_file.read_text(encoding="utf-8")
                        rendered = raw.replace("{{PROJECT_NAME}}", project_dir.name)
                        rendered = rendered.replace("{{LAST_UPDATED}}", "2026-10-02")
                        rendered = rendered.replace("{{STATUS}}", "BOOTSTRAPPING")
                        rendered = rendered.replace("{{VERSION}}", "v0.1.0")
                        rendered = rendered.replace("{{TECH_STACK}}", "Agnóstico (stack a definir)")
                        rendered = rendered.replace("{{PURPOSE}}", f"Projeto {project_dir.name}")
                        rendered = rendered.replace("{{ARCHITECTURE}}", "Arquitetura inicial modular.")
                        rendered = rendered.replace("{{BUILD_CMD}}", "make build")
                        rendered = rendered.replace("{{TEST_CMD}}", "make test")
                        rendered = rendered.replace("{{LINT_CMD}}", "make lint")
                        rendered = rendered.replace("{{DEV_CMD}}", "make dev")
                        rendered = rendered.replace("{{CI_STATUS}}", "CONFIGURED")
                        rendered = rendered.replace("{{QUALITY_GATE}}", "TDD estrito + Zero Workarounds")
                        rendered = rendered.replace("{{LAST_EVIDENCE}}", "EV-GENESIS-20261002-01")
                        rendered = rendered.replace("{{ENV}}", "Local / Development")
                        project_memory.write_text(rendered, encoding="utf-8")
                    else:
                        project_memory.write_text(
                            f"# Memória do Projeto: {project_dir.name}\n\nStatus: BOOTSTRAPPING\n",
                            encoding="utf-8",
                        )
                actions.append("Memória isolada PROJECT_MEMORY.md inicializada")
            else:
                actions.append("Memória existente preservada sem sobrescrita")

        return {"ok": True, "actions": actions, "project_dir": str(project_dir)}


class GlobalInstaller:
    """Orquestra a instalação e sincronização global do kit em ~/.gemini/config e ~/.local/bin."""

    def __init__(self, kit_dir: Optional[Path] = None, home_dir: Optional[Path] = None):
        self.kit_dir = kit_dir or Path(__file__).resolve().parent.parent
        self.home_dir = home_dir or Path.home()

    def install_global(self, dry_run: bool = False) -> Dict[str, Any]:
        actions: List[str] = []
        if dry_run:
            actions.append(f"[Dry-run] Simulação de instalação global a partir de {self.kit_dir}")
            return {"ok": True, "actions": actions}

        # Invoca o script de instalação global existente
        install_script = self.kit_dir / "scripts" / "install-global.sh"
        if install_script.exists():
            res = subprocess.run(["bash", str(install_script)], capture_output=True, text=True)
            if res.returncode != 0:
                return {"ok": False, "error": res.stderr, "actions": actions}
            actions.append("Script install-global.sh executado com sucesso")

        # Configura PATH
        bin_dir = str(self.home_dir / ".local" / "bin")
        path_cfg = PathConfigurator()
        if path_cfg.ensure_path_in_rc(bin_dir):
            actions.append(f"Caminho {bin_dir} adicionado ao shell RC")
        else:
            actions.append(f"Caminho {bin_dir} já configurado no PATH")

        return {"ok": True, "actions": actions}


class KitDoctor:
    """Audita a integridade do ambiente, dependências e configurações do kit."""

    def __init__(self, kit_dir: Optional[Path] = None, home_dir: Optional[Path] = None):
        self.kit_dir = kit_dir or Path(__file__).resolve().parent.parent
        self.home_dir = home_dir or Path.home()
        self.checker = DependencyChecker()

    def run_diagnostics(self) -> Dict[str, Any]:
        deps = self.checker.check_all()["checks"]
        
        # Diretórios Antigravity
        gemini_dir = self.home_dir / ".gemini"
        config_dir = gemini_dir / "config"
        ide_dir = gemini_dir / "antigravity-ide"
        cli_dir = gemini_dir / "antigravity-cli"
        bin_dir = self.home_dir / ".local" / "bin"

        dirs_status = {
            "gemini_root": gemini_dir.is_dir(),
            "config": config_dir.is_dir(),
            "ide": ide_dir.is_dir(),
            "cli": cli_dir.is_dir(),
            "bin": bin_dir.is_dir(),
        }

        path_env = os.environ.get("PATH", "")
        path_ok = str(bin_dir) in path_env

        # Binários essenciais no bin_dir
        essential_bins = ["agy-tokens", "agy-run", "agy-debt", "agy-health", "agy-kit"]
        installed_bins = {b: (bin_dir / b).exists() for b in essential_bins}

        return {
            "python": deps["python"],
            "git": deps["git"],
            "gh": deps["gh"],
            "rtk": deps["rtk"],
            "antigravity_dirs": {
                "ok": all(dirs_status.values()),
                "status": dirs_status,
                "message": "Diretórios Antigravity verificados",
            },
            "path_ok": path_ok,
            "installed_bins": installed_bins,
        }

    def print_report(self) -> None:
        diag = self.run_diagnostics()
        print("=" * 68)
        print(" 🏥 XP MULTI-AGENT KIT — DIAGNÓSTICO DO AMBIENTE (agy-kit doctor)")
        print("=" * 68)
        py = diag["python"]
        git = diag["git"]
        print(f"• Python : {'✅' if py['ok'] else '❌'} {py['message']}")
        print(f"• Git    : {'✅' if git['ok'] else '❌'} {git['message']}")
        
        dirs = diag["antigravity_dirs"]
        print(f"• Pastas : {'✅' if dirs['ok'] else '⚠️'} ~/.gemini/ (config, ide, cli)")
        print(f"• PATH   : {'✅' if diag['path_ok'] else '⚠️'} ~/.local/bin está no PATH: {diag['path_ok']}")
        
        installed = diag.get("installed_bins", {})
        if installed:
            print("\n📦 Binários Globais:")
            for b, exists in installed.items():
                print(f"  - {b:15}: {'✅ Instalado' if exists else '❌ Ausente'}")
        print("=" * 68)


def interactive_wizard(kit_dir: Path, dry_run: bool = False) -> int:
    """Wizard interativo de instalação do kit."""
    print("=" * 68)
    print(" 🚀 INSTALADOR UNIFICADO — XP MULTI-AGENT KIT v2")
    if dry_run:
        print(" ⚠️  [MODO SIMULAÇÃO / DRY-RUN ATIVO]")
    print("=" * 68)
    print("\nComo deseja instalar o kit?")
    print("  [1] Global (Recomendado)")
    print("      -> Instala ferramentas em ~/.local/bin/ e sincroniza com")
    print("         Antigravity IDE & CLI (~/.gemini/config/).")
    print("  [2] Projeto Específico (Local)")
    print("      -> Injeta .agents/, AGENTS.md e memória isolada apenas em um repositório.")
    print("  [3] Ambos")
    print("      -> Realiza a instalação global E aplica no projeto especificado.\n")

    try:
        choice = input("Escolha uma opção [1/2/3] (padrão: 1): ").strip() or "1"
    except (EOFError, KeyboardInterrupt):
        print("\nOperação cancelada pelo usuário.")
        return 1

    checker = DependencyChecker()
    dep_summary = checker.check_all()
    if not dep_summary["can_proceed"]:
        print("❌ Dependências essenciais ausentes. Por favor, instale Python >= 3.8 e Git.")
        return 1

    if choice == "1":
        print("\n⏳ Executando instalação global...")
        installer = GlobalInstaller(kit_dir=kit_dir)
        res = installer.install_global(dry_run=dry_run)
        if res["ok"]:
            print("✅ Instalação global concluída com sucesso!")
            return 0
        print(f"❌ Falha na instalação global: {res.get('error')}")
        return 1

    elif choice in ["2", "3"]:
        try:
            p_dir_input = input("Informe o caminho do projeto (padrão: diretório atual): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperação cancelada.")
            return 1
        
        target_path = Path(p_dir_input).resolve() if p_dir_input else Path.cwd()
        
        if choice == "3":
            print("\n⏳ Executando instalação global...")
            g_installer = GlobalInstaller(kit_dir=kit_dir)
            g_res = g_installer.install_global(dry_run=dry_run)
            if not g_res["ok"]:
                print(f"❌ Falha na instalação global: {g_res.get('error')}")
                return 1

        print(f"\n⏳ Injetando kit no projeto: {target_path}...")
        p_installer = ProjectInstaller(kit_dir=kit_dir)
        p_res = p_installer.install_project(target_path, use_symlinks=True, dry_run=dry_run)
        if p_res["ok"]:
            print(f"✅ Kit injetado com sucesso no projeto {target_path}!")
            return 0
        print(f"❌ Falha ao injetar no projeto: {p_res.get('error')}")
        return 1

    print("❌ Opção inválida. Operação abortada.")
    return 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="XP Multi-Agent Kit — Instalador e Gerenciador Unificado (agy-kit)",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["install", "doctor", "init", "sync", "version"],
        help="Subcomando opcional",
    )
    parser.add_argument(
        "--global",
        "-g",
        dest="install_global",
        action="store_true",
        help="Instala o kit globalmente para o Antigravity IDE e CLI",
    )
    parser.add_argument(
        "--project",
        "-p",
        dest="project_path",
        type=str,
        help="Injeta o kit em um diretório de projeto específico",
    )
    parser.add_argument(
        "--both",
        dest="both_path",
        type=str,
        help="Instala globalmente E aplica no projeto especificado",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Modo automático / não-interativo (assume respostas padrão)",
    )
    parser.add_argument(
        "--no-deps",
        action="store_true",
        help="Pula verificação de dependências do sistema operacional",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula a execução sem realizar alterações no disco",
    )

    args = parser.parse_args(argv)
    kit_dir = Path(__file__).resolve().parent.parent

    # Subcomando 'version'
    if args.command == "version":
        print("XP Multi-Agent Kit v2.39.0 (Unified Installer & Portability)")
        return 0

    # Subcomando 'doctor'
    if args.command == "doctor":
        doctor = KitDoctor(kit_dir=kit_dir)
        doctor.print_report()
        return 0

    # Checagem de dependências
    if not args.no_deps:
        checker = DependencyChecker()
        summary = checker.check_all()
        if not summary["can_proceed"]:
            print("❌ Falha nas dependências essenciais (Python >= 3.8 ou Git ausentes).")
            return 1

    # Subcomando 'init' (equivalente a --project)
    if args.command == "init":
        p_path = Path(args.project_path or ".").resolve()
        installer = ProjectInstaller(kit_dir=kit_dir)
        res = installer.install_project(p_path, use_symlinks=True, dry_run=args.dry_run)
        if res["ok"]:
            print(f"✅ Kit injetado com sucesso no projeto {p_path}!")
            return 0
        return 1

    # Subcomando 'sync' (equivalente a --global)
    if args.command == "sync":
        installer = GlobalInstaller(kit_dir=kit_dir)
        res = installer.install_global(dry_run=args.dry_run)
        return 0 if res["ok"] else 1

    # Trata flag --both
    if args.both_path:
        p_path = Path(args.both_path).resolve()
        g_installer = GlobalInstaller(kit_dir=kit_dir)
        g_res = g_installer.install_global(dry_run=args.dry_run)
        if not g_res["ok"]:
            return 1
        p_installer = ProjectInstaller(kit_dir=kit_dir)
        p_res = p_installer.install_project(p_path, use_symlinks=True, dry_run=args.dry_run)
        return 0 if p_res["ok"] else 1

    # Trata flag --project
    if args.project_path:
        p_path = Path(args.project_path).resolve()
        p_installer = ProjectInstaller(kit_dir=kit_dir)
        p_res = p_installer.install_project(p_path, use_symlinks=True, dry_run=args.dry_run)
        return 0 if p_res["ok"] else 1

    # Trata flag --global
    if args.install_global:
        g_installer = GlobalInstaller(kit_dir=kit_dir)
        g_res = g_installer.install_global(dry_run=args.dry_run)
        return 0 if g_res["ok"] else 1

    # Se nenhum argumento ou comando foi fornecido
    if not (args.command or args.install_global or args.project_path or args.both_path):
        if sys.stdin.isatty() and not (args.yes or args.dry_run):
            return interactive_wizard(kit_dir, dry_run=args.dry_run)
        else:
            # Default não interativo ou dry-run: instala/simula globalmente
            g_installer = GlobalInstaller(kit_dir=kit_dir)
            g_res = g_installer.install_global(dry_run=args.dry_run)
            if args.dry_run:
                for act in g_res.get("actions", []):
                    print(f"  {act}")
            return 0 if g_res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
