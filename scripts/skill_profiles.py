#!/usr/bin/env python3
"""
scripts/skill_profiles.py
Gerenciador de Perfis de Skills do XP Multi-Agent Kit v4 (xp skills-profile).
Alterna perfis (core, backend, frontend, all) sobre as 23 skills reais do v4,
lendo descrições diretamente do frontmatter de `.agents/skills/*/SKILL.md`.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
HOME = Path.home()
DEFAULT_GLOBAL_SKILLS_DIR = HOME / ".gemini" / "config" / "skills"

CORE_SKILLS: Set[str] = {
    "ci-auto-heal",
    "code-hygiene-review",
    "coderabbit-review",
    "git-worktree-workspace",
    "project-memory",
    "spec-pyramid",
    "tdd-safety-net",
}

BACKEND_SKILLS: Set[str] = CORE_SKILLS | {
    "api-contracts",
    "async-messaging-and-resilience",
    "cloud-and-iac-security",
    "database-architecture",
    "release-and-deploy",
    "security-review",
    "threat-modeling",
}

FRONTEND_SKILLS: Set[str] = CORE_SKILLS | {
    "browser-e2e-playwright",
    "conversion-and-seo",
    "craft",
    "craft-critique",
    "craft-explore",
    "craft-setup",
    "craft-states",
    "craft-sync",
    "craft-system",
}

PROFILES: Dict[str, Set[str]] = {
    "core": set(CORE_SKILLS),
    "backend": set(BACKEND_SKILLS),
    "frontend": set(FRONTEND_SKILLS),
    "all": set(),
}

PROFILE_META: Dict[str, Dict[str, str]] = {
    "core": {"label": "Core XP & Governance", "description": "TDD, Spec Pyramid, hygiene, memory, worktree, CI auto-heal."},
    "backend": {"label": "Backend, Data & Security", "description": "Core + APIs, DB, async resilience, Zero Trust, STRIDE, deploy."},
    "frontend": {"label": "Frontend, UI/UX & Craft", "description": "Core + Craft design suite, CRO/SEO, Playwright E2E."},
    "all": {"label": "Full Kit Catalog", "description": "All 23 v4 skills enabled."},
}


def load_skill_descriptions(skills_dir: Optional[Path] = None) -> Dict[str, str]:
    """Lê descrições direto do frontmatter de cada SKILL.md (fonte única)."""
    base = skills_dir or (ROOT_DIR / ".agents" / "skills")
    result: Dict[str, str] = {}
    if not base.is_dir():
        return result
    for path in sorted(base.glob("*/SKILL.md")):
        txt = path.read_text(encoding="utf-8", errors="ignore")
        m = re.match(r"^---\s*\n(.*?)\n---", txt, re.DOTALL)
        if m:
            dm = re.search(r"^description:\s*(.+)$", m.group(1), re.MULTILINE)
            result[path.parent.name] = dm.group(1).strip().strip("'\"") if dm else ""
    return result


SKILL_DESCRIPTIONS: Dict[str, str] = load_skill_descriptions()


def get_profile_skills(profile_name: str, all_available: Iterable[str]) -> Set[str]:
    name = profile_name.lower().strip()
    if name in ("all", "full"):
        return set(all_available)
    if name in PROFILES:
        return set(PROFILES[name])
    raise ValueError(f"Unknown profile {profile_name!r}. Valid options: {list(PROFILES.keys())}")


def detect_current_profile(active_skills: Set[str]) -> str:
    if not active_skills:
        return "none"
    for name in ("core", "backend", "frontend"):
        if active_skills == PROFILES[name]:
            return name
    return "custom"


def list_active_and_disabled(skills_dir: Path, disabled_dir: Optional[Path] = None) -> Dict[str, Any]:
    active = [p.name for p in sorted(skills_dir.iterdir()) if p.is_dir() or p.is_symlink()] if skills_dir.exists() else []
    disabled = [p.name for p in sorted(disabled_dir.iterdir()) if p.is_dir() or p.is_symlink()] if (disabled_dir and disabled_dir.exists()) else []
    return {"active": active, "disabled": disabled, "total_active": len(active), "total_disabled": len(disabled)}


def apply_profile_symlinks(
    profile_name: str,
    master_dir: Path,
    target_dir: Path,
    dry_run: bool = False,
) -> Tuple[List[str], List[str]]:
    if not master_dir.exists():
        raise FileNotFoundError(f"Master skills directory not found: {master_dir}")
    target_dir.mkdir(parents=True, exist_ok=True)
    all_master = sorted(p.name for p in master_dir.iterdir() if p.is_dir())
    desired = get_profile_skills(profile_name, all_master)

    active: List[str] = []
    removed: List[str] = []
    for name in all_master:
        dst = target_dir / name
        if name in desired:
            active.append(name)
            if not dry_run and not dst.exists() and not dst.is_symlink():
                dst.symlink_to(master_dir / name)
        else:
            if dst.is_symlink() or dst.exists():
                removed.append(name)
                if not dry_run:
                    if dst.is_symlink() or dst.is_file():
                        dst.unlink()
                    else:
                        shutil.rmtree(dst)
    return active, removed


def apply_profile_move(
    profile_name: str,
    skills_dir: Path,
    disabled_dir: Path,
    dry_run: bool = False,
) -> Tuple[List[str], List[str]]:
    if not skills_dir.exists():
        raise FileNotFoundError(f"Skills directory not found: {skills_dir}")
    all_names: Set[str] = {p.name for p in skills_dir.iterdir() if p.is_dir()}
    if disabled_dir.exists():
        all_names |= {p.name for p in disabled_dir.iterdir() if p.is_dir()}
    desired = get_profile_skills(profile_name, all_names)

    active: List[str] = []
    disabled: List[str] = []
    if not dry_run:
        disabled_dir.mkdir(parents=True, exist_ok=True)
    for name in sorted(all_names):
        src_act = skills_dir / name
        src_dis = disabled_dir / name
        if name in desired:
            active.append(name)
            if not src_act.exists() and src_dis.exists() and not dry_run:
                shutil.move(str(src_dis), str(src_act))
        else:
            disabled.append(name)
            if src_act.exists() and not dry_run:
                if src_dis.exists():
                    shutil.rmtree(src_dis)
                shutil.move(str(src_act), str(src_dis))
    return active, disabled


def enable_skill(skill_name: str, skills_dir: Path, disabled_dir: Path) -> bool:
    src = disabled_dir / skill_name
    dst = skills_dir / skill_name
    if dst.exists():
        return True
    if src.exists():
        shutil.move(str(src), str(dst))
        return True
    return False


def disable_skill(skill_name: str, skills_dir: Path, disabled_dir: Path) -> bool:
    src = skills_dir / skill_name
    dst = disabled_dir / skill_name
    if not src.exists():
        return dst.exists()
    disabled_dir.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.move(str(src), str(dst))
    return True


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="XP Kit v4 Skill Profile Manager")
    parser.add_argument("action", choices=["status", "list", "apply", "enable", "disable"])
    parser.add_argument("target", nargs="?", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--global", dest="use_global", action="store_true")
    parser.add_argument("--local", dest="use_local", action="store_true")
    args = parser.parse_args(argv)

    master = ROOT_DIR / ".agents" / "skills"
    target_dir = DEFAULT_GLOBAL_SKILLS_DIR if (args.use_global or not args.use_local) else master
    disabled_dir = target_dir.parent / "skills_disabled"

    if args.action == "list":
        for pname, meta in PROFILE_META.items():
            cnt = len(PROFILES[pname]) if pname != "all" else len(list(master.glob("*/SKILL.md")))
            print(f"• {pname:<10} ({cnt:2d} skills) — {meta['label']}: {meta['description']}")
        return 0

    if args.action == "status":
        info = list_active_and_disabled(target_dir, disabled_dir)
        prof = detect_current_profile(set(info["active"]))
        print(f"Perfil: {prof} | Ativas: {info['total_active']} | Desativadas: {info['total_disabled']}")
        return 0

    if args.action == "apply":
        if not args.target:
            print("Erro: informe o perfil (core|backend|frontend|all)", file=sys.stderr)
            return 1
        if args.use_local:
            act, dis = apply_profile_move(args.target, master, disabled_dir, dry_run=args.dry_run)
            print(f"{'[dry-run] ' if args.dry_run else ''}Perfil '{args.target}': {len(act)} ativas, {len(dis)} desativadas.")
        else:
            act, rem = apply_profile_symlinks(args.target, master, target_dir, dry_run=args.dry_run)
            print(f"{'[dry-run] ' if args.dry_run else ''}Perfil '{args.target}': {len(act)} ativas, {len(rem)} removidas.")
        return 0

    if args.action == "enable" and args.target:
        return 0 if enable_skill(args.target, master, disabled_dir) else 1
    if args.action == "disable" and args.target:
        return 0 if disable_skill(args.target, master, disabled_dir) else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
