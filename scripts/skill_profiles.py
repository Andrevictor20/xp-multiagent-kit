#!/usr/bin/env python3
"""
scripts/skill_profiles.py
Gerenciador de Perfis de Skills (A2 / D3) para o XP Multi-Agent Kit v2.

Permite alternar perfis (core, backend, frontend, all) reduzindo a quantidade de
skills ativas injetadas no contexto do modelo em cada turno.

Uso:
    agy-skills-profile status
    agy-skills-profile list
    agy-skills-profile apply core [--global | --local] [--dry-run]
    agy-skills-profile apply backend
    agy-skills-profile apply frontend
    agy-skills-profile apply all
    agy-skills-profile enable <skill-name>
    agy-skills-profile disable <skill-name>
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

# Constantes e caminhos padrão
HOME = Path.home()
DEFAULT_GLOBAL_SKILLS_DIR = HOME / ".gemini" / "config" / "skills"

# Definições canônicas dos perfis
PROFILES: Dict[str, Set[str]] = {
    "core": {
        "acceptance-test-driven",
        "atomic-commit-discipline",
        "ci-auto-heal",
        "code-deslop-review",
        "conformance-tracker",
        "diff-simplifier-review",
        "lesson-learned",
        "no-workarounds",
        "project-memory",
        "specification-by-example",
        "systematic-debugging",
        "task-routing",
        "tdd-safety-net",
        "test-evidence-walkthrough",
        "token-budget-tracker",
    },
    "backend": {
        # Core
        "acceptance-test-driven",
        "atomic-commit-discipline",
        "ci-auto-heal",
        "code-deslop-review",
        "conformance-tracker",
        "diff-simplifier-review",
        "lesson-learned",
        "no-workarounds",
        "project-memory",
        "specification-by-example",
        "systematic-debugging",
        "task-routing",
        "tdd-safety-net",
        "test-evidence-walkthrough",
        "token-budget-tracker",
        # Backend extensions
        "api-contracts",
        "api-security",
        "authentication-security",
        "authorization-security",
        "availability-security",
        "cloud-security-and-zero-trust",
        "container-security",
        "database-architecture",
        "infrastructure-as-code-governance",
        "integration-testing",
        "migration-safety",
        "observability-instrumentation",
        "security-testing",
        "zero-downtime-deployment",
    },
    "frontend": {
        # Core
        "acceptance-test-driven",
        "atomic-commit-discipline",
        "ci-auto-heal",
        "code-deslop-review",
        "conformance-tracker",
        "diff-simplifier-review",
        "lesson-learned",
        "no-workarounds",
        "project-memory",
        "specification-by-example",
        "systematic-debugging",
        "task-routing",
        "tdd-safety-net",
        "test-evidence-walkthrough",
        "token-budget-tracker",
        # Frontend extensions
        "browser-e2e-playwright",
        "component-architecture",
        "conversion-copywriting",
        "copy-editing-sweeps",
        "cro-landing-pages",
        "design-tokens",
        "frontend-performance",
        "frontend-taste-engineering",
        "image-to-code",
        "marketing-psychology",
        "minimalist-ui",
        "responsive-architecture",
        "visual-direction-studio",
        "visual-regression",
    },
    "all": set(),  # Representa todas as skills disponíveis
}


def get_profile_skills(profile_name: str, all_available: Iterable[str]) -> Set[str]:
    """Retorna o conjunto de skills para um determinado perfil."""
    name = profile_name.lower().strip()
    if name in ("all", "full"):
        return set(all_available)
    if name in PROFILES:
        return set(PROFILES[name])
    raise ValueError(f"Perfil desconhecido '{profile_name}'. Opções válidas: {list(PROFILES.keys())}")


def detect_current_profile(active_skills: Set[str]) -> str:
    """Infere o nome do perfil mais próximo com base nas skills ativas."""
    if not active_skills:
        return "none"
    for name in ("core", "backend", "frontend"):
        if active_skills == PROFILES[name]:
            return name
    return "custom"


def list_active_and_disabled(
    skills_dir: Path,
    disabled_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Lista as skills ativas e inativas em um diretório de skills."""
    active: List[str] = []
    if skills_dir.exists():
        for p in sorted(skills_dir.iterdir()):
            if p.is_dir() or p.is_symlink():
                active.append(p.name)

    disabled: List[str] = []
    if disabled_dir and disabled_dir.exists():
        for p in sorted(disabled_dir.iterdir()):
            if p.is_dir() or p.is_symlink():
                disabled.append(p.name)

    return {
        "active": active,
        "disabled": disabled,
        "total_active": len(active),
        "total_disabled": len(disabled),
    }


def apply_profile_symlinks(
    profile_name: str,
    master_dir: Path,
    target_dir: Path,
    dry_run: bool = False,
) -> Tuple[List[str], List[str]]:
    """
    Aplica um perfil gerenciando symlinks em target_dir apontando para master_dir.
    Não altera os arquivos do repositório master_dir.
    """
    if not master_dir.exists():
        raise FileNotFoundError(f"Diretório mestre não encontrado: {master_dir}")

    target_dir.mkdir(parents=True, exist_ok=True)
    all_available = [p.name for p in master_dir.iterdir() if p.is_dir() and (p / "SKILL.md").exists()]
    target_skills = get_profile_skills(profile_name, all_available)

    active_created: List[str] = []
    removed: List[str] = []

    # 1. Remover symlinks existentes que não estão no perfil
    for item in list(target_dir.iterdir()):
        if item.name not in target_skills:
            removed.append(item.name)
            if not dry_run:
                if item.is_symlink() or item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)

    # 2. Criar ou manter symlinks para skills do perfil
    for skill_name in target_skills:
        src = master_dir / skill_name
        dest = target_dir / skill_name
        if src.exists():
            active_created.append(skill_name)
            if not dry_run and not dest.exists():
                dest.symlink_to(src.resolve())

    return active_created, removed


def apply_profile_move(
    profile_name: str,
    skills_dir: Path,
    disabled_dir: Path,
    dry_run: bool = False,
) -> Tuple[List[str], List[str]]:
    """
    Aplica um perfil movendo fisicamente pastas entre skills_dir e disabled_dir.
    Usado para ambientes isolados locais que não usam symlinks.
    """
    skills_dir.mkdir(parents=True, exist_ok=True)
    disabled_dir.mkdir(parents=True, exist_ok=True)

    # Coletar todas as skills em ambos os diretórios
    active_now = {p.name: p for p in skills_dir.iterdir() if p.is_dir()}
    disabled_now = {p.name: p for p in disabled_dir.iterdir() if p.is_dir()}
    all_available = sorted(set(active_now.keys()) | set(disabled_now.keys()))

    target_skills = get_profile_skills(profile_name, all_available)

    active_result: List[str] = []
    disabled_result: List[str] = []

    # Mover de active -> disabled
    for name, path in active_now.items():
        if name not in target_skills:
            disabled_result.append(name)
            if not dry_run:
                dest = disabled_dir / name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.move(str(path), str(dest))
        else:
            active_result.append(name)

    # Mover de disabled -> active
    for name, path in disabled_now.items():
        if name in target_skills:
            active_result.append(name)
            if not dry_run:
                dest = skills_dir / name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.move(str(path), str(dest))
        else:
            disabled_result.append(name)

    # Limpar pasta disabled se vazia
    if not dry_run and disabled_dir.exists():
        if not any(disabled_dir.iterdir()):
            disabled_dir.rmdir()

    return sorted(active_result), sorted(disabled_result)


def enable_skill(skill_name: str, skills_dir: Path, disabled_dir: Path) -> bool:
    """Move uma skill específica de disabled_dir para skills_dir."""
    src = disabled_dir / skill_name
    if not src.exists():
        return False
    skills_dir.mkdir(parents=True, exist_ok=True)
    dest = skills_dir / skill_name
    if dest.exists():
        return True
    shutil.move(str(src), str(dest))
    return True


def disable_skill(skill_name: str, skills_dir: Path, disabled_dir: Path) -> bool:
    """Move uma skill específica de skills_dir para disabled_dir."""
    src = skills_dir / skill_name
    if not src.exists():
        return False
    disabled_dir.mkdir(parents=True, exist_ok=True)
    dest = disabled_dir / skill_name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.move(str(src), str(dest))
    return True


def estimate_tokens(skill_count: int, avg_chars_per_skill: int = 190) -> int:
    """Estima tokens de cabeçalho com base na quantidade de skills."""
    return int((skill_count * avg_chars_per_skill) / 3.8)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agy-skills-profile",
        description="Gerenciador de Perfis de Skills do XP Kit (A2 / D3)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # list
    subparsers.add_parser("list", help="Lista todos os perfis disponíveis")

    # status
    subparsers.add_parser("status", help="Mostra o status das skills ativas e inativas")

    # apply
    apply_parser = subparsers.add_parser("apply", help="Aplica um perfil de skills")
    apply_parser.add_argument("profile", choices=["core", "backend", "frontend", "all", "full"], help="Nome do perfil")
    apply_parser.add_argument("--global", dest="is_global", action="store_true", default=True, help="Aplica em ~/.gemini/config/skills/ (padrão)")
    apply_parser.add_argument("--local", dest="is_local", action="store_true", help="Aplica no repositório local (.agents/skills)")
    apply_parser.add_argument("--dry-run", action="store_true", help="Apenas simula a operação")

    # enable / disable
    enable_parser = subparsers.add_parser("enable", help="Habilita uma skill individual")
    enable_parser.add_argument("skill", help="Nome da skill")

    disable_parser = subparsers.add_parser("disable", help="Desabilita uma skill individual")
    disable_parser.add_argument("skill", help="Nome da skill")

    args = parser.parse_args(argv)

    if not args.command or args.command == "status":
        kit_dir = Path(__file__).resolve().parent.parent
        local_skills = kit_dir / ".agents" / "skills"
        local_disabled = kit_dir / ".agents" / "skills_disabled"
        global_skills = DEFAULT_GLOBAL_SKILLS_DIR

        print("📊 Status de Perfis de Skills")
        print("────────────────────────────────────────────────────────")
        if global_skills.exists():
            g_active = [p.name for p in global_skills.iterdir() if p.is_dir() or p.is_symlink()]
            g_prof = detect_current_profile(set(g_active))
            tok = estimate_tokens(len(g_active))
            print(f"Global (~/.gemini/config/skills/):")
            print(f"  • Ativas: {len(g_active)} skills  |  Perfil: [{g_prof}]  |  Custo: ~{tok} tokens/turno")

        if local_skills.exists():
            l_info = list_active_and_disabled(local_skills, local_disabled)
            l_prof = detect_current_profile(set(l_info["active"]))
            print(f"Local (.agents/skills/):")
            print(f"  • Ativas: {l_info['total_active']}  |  Inativas: {l_info['total_disabled']}  |  Perfil: [{l_prof}]")
        print("────────────────────────────────────────────────────────")
        return 0

    if args.command == "list":
        print("📋 Perfis de Skills Disponíveis")
        print("────────────────────────────────────────────────────────")
        for name, skills in PROFILES.items():
            count_label = f"{len(skills)} skills" if skills else "todas as 74 skills"
            tok = estimate_tokens(len(skills)) if skills else estimate_tokens(74)
            print(f"  • {name.upper():<10} : {count_label:<20} (~{tok} tokens/turno)")
        print("────────────────────────────────────────────────────────")
        return 0

    if args.command == "apply":
        kit_dir = Path(__file__).resolve().parent.parent
        master_skills = kit_dir / ".agents" / "skills"

        if args.is_local:
            skills_dir = master_skills
            disabled_dir = kit_dir / ".agents" / "skills_disabled"
            active, disabled = apply_profile_move(args.profile, skills_dir, disabled_dir, dry_run=args.dry_run)
            prefix = "[Dry-run] " if args.dry_run else ""
            print(f"✅ {prefix}Perfil local '{args.profile}' aplicado: {len(active)} ativas, {len(disabled)} inativas.")
        else:
            target_skills = DEFAULT_GLOBAL_SKILLS_DIR
            active, removed = apply_profile_symlinks(args.profile, master_skills, target_skills, dry_run=args.dry_run)
            prefix = "[Dry-run] " if args.dry_run else ""
            tok = estimate_tokens(len(active))
            print(f"✅ {prefix}Perfil global '{args.profile}' aplicado com sucesso!")
            print(f"   • Skills ativas em {target_skills}: {len(active)} (~{tok} tokens/turno)")
            if removed:
                print(f"   • Skills desvinculadas: {len(removed)}")
        return 0

    if args.command == "enable":
        kit_dir = Path(__file__).resolve().parent.parent
        skills_dir = kit_dir / ".agents" / "skills"
        disabled_dir = kit_dir / ".agents" / "skills_disabled"
        ok = enable_skill(args.skill, skills_dir, disabled_dir)
        if ok:
            print(f"✅ Skill '{args.skill}' habilitada com sucesso.")
            return 0
        else:
            print(f"❌ Skill '{args.skill}' não encontrada em {disabled_dir}.", file=sys.stderr)
            return 1

    if args.command == "disable":
        kit_dir = Path(__file__).resolve().parent.parent
        skills_dir = kit_dir / ".agents" / "skills"
        disabled_dir = kit_dir / ".agents" / "skills_disabled"
        ok = disable_skill(args.skill, skills_dir, disabled_dir)
        if ok:
            print(f"✅ Skill '{args.skill}' desabilitada com sucesso.")
            return 0
        else:
            print(f"❌ Skill '{args.skill}' não encontrada em {skills_dir}.", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
