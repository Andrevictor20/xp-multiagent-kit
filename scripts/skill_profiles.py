#!/usr/bin/env python3
"""
scripts/skill_profiles.py
Skill Profile Manager (A2 / D3) for XP Multi-Agent Kit.

Switches active skill profiles (core, backend, frontend, all) to reduce per-turn
context overhead injected into the model.

Usage:
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

HOME = Path.home()
DEFAULT_GLOBAL_SKILLS_DIR = HOME / ".gemini" / "config" / "skills"

CORE_SKILLS: Set[str] = {
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
}

BACKEND_SKILLS: Set[str] = CORE_SKILLS | {
    "api-contracts",
    "api-security",
    "async-messaging-and-resilience",
    "authentication-security",
    "authorization-security",
    "availability-security",
    "backend-performance-testing",
    "caching-architecture",
    "cloud-security-and-zero-trust",
    "container-security",
    "database-architecture",
    "infrastructure-as-code-governance",
    "integration-testing",
    "migration-safety",
    "observability-and-slo-engineering",
    "security-testing",
    "software-evolution-and-roadmapping",
    "zero-downtime-deployment",
}

FRONTEND_SKILLS: Set[str] = CORE_SKILLS | {
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
}

PROFILES: Dict[str, Set[str]] = {
    "core": set(CORE_SKILLS),
    "backend": set(BACKEND_SKILLS),
    "frontend": set(FRONTEND_SKILLS),
    "all": set(),  # Represents all available skills
}

PROFILE_META: Dict[str, Dict[str, str]] = {
    "core": {
        "label": "Core XP & Governance",
        "description": "Essential ATDD/TDD, debugging, memory, deslop, and token-budget skills.",
    },
    "backend": {
        "label": "Backend, Data & Cloud Security",
        "description": "Core skills plus APIs, databases, caching, async messaging, IaC, and SLOs.",
    },
    "frontend": {
        "label": "Frontend, UI/UX & Conversion",
        "description": "Core skills plus Anti-Slop design direction, tokens, components, CRO, and E2E.",
    },
    "all": {
        "label": "Full Kit Catalog",
        "description": "All 77 skills enabled simultaneously.",
    },
}

SKILL_DESCRIPTIONS: Dict[str, str] = {
    'acceptance-test-driven': 'ATDD/BDD with human-AI contract separation and Specification Pyramid.',
    'accessibility-engineering': 'Web accessibility: keyboard navigation, WCAG AA contrast, and semantic ARIA.',
    'adr-architect-tracker': 'MADR 3.0 Architectural Decision Records and architectural drift detection.',
    'api-contracts': 'OpenAPI contract design, versioning, DTO schemas, and error modeling.',
    'api-security': 'API security hardening and OWASP API Security Top 10 controls.',
    'async-messaging-and-resilience': 'Async messaging, EDA, Outbox Pattern, DLQ, idempotency, and Circuit Breaker.',
    'atomic-commit-discipline': 'Atomic, categorized, CI-verified commits and token-efficient Git ops.',
    'authentication-security': 'Authentication auditing: password hashing, JWT validation, sessions, MFA.',
    'authorization-security': 'Access control, RBAC/ABAC permissions, tenant isolation, and BOLA/IDOR defense.',
    'availability-security': 'DoS protection, rate limiting, timeouts, and resource exhaustion defense.',
    'backend-performance-testing': 'Backend load, stress, spike, and soak testing, profiling, and SLO gates.',
    'browser-e2e-playwright': 'Headless E2E browser testing with Playwright, auto-wait locators, and traces.',
    'caching-architecture': 'Redis/Memcached caching, Cache-Aside, and stampede/avalanche/penetration defense.',
    'ci-auto-heal': 'Autonomous CI/CD failure diagnosis and root-cause self-healing (max 3 iterations).',
    'ci-security-gate': 'Mandatory CI pipeline gate with linting, dependency audit, SAST, and tests.',
    'cloud-security-and-zero-trust': 'Zero Trust cloud security, federated OIDC CI/CD, Cosign signing, and mTLS.',
    'code-deslop-review': 'Systematic AI code cleanup, dead-code removal, and <500-line No God Files rule.',
    'codebase-cartography': 'AST dependency graph mapping and blast-radius analysis via code-review-graph.',
    'component-architecture': 'Modular UI components, token anchoring, 6-state machine, and mobile ergonomics.',
    'component-registry': 'Catalog and governance of reusable UI components to prevent duplication.',
    'conformance-tracker': 'Traceability between Acceptance Criteria and tests via Conformance Report.',
    'container-security': 'Dockerfile hardening, non-root execution, minimal base images, and SBOMs.',
    'conversion-copywriting': 'High-conversion UI copywriting, benefit bridges, hero headlines, and CTAs.',
    'copy-editing-sweeps': '7-sweep copy editing framework to eliminate AI cliches and weak prose.',
    'cro-landing-pages': 'Conversion Rate Optimization (CRO), 5-second test, CTA hierarchy, and forms.',
    'crypto-guardian': 'Cryptographic primitive auditing, key management, and ban on weak ciphers.',
    'database-architecture': 'SQL/NoSQL schema modeling, indexing, ACID concurrency, and N+1 prevention.',
    'dependency-governance': 'Third-party dependency risk evaluation, license audit, and bloat prevention.',
    'deploy-pipeline-conductor': 'Continuous deployment (CD) pipelines, staging promotion, health checks, rollback.',
    'design-system-architecture': 'Design System governance from semantic tokens and primitives to page templates.',
    'design-tokens': 'Semantic visual tokens with Color Consistency Lock and Concentric Shape Lock.',
    'diff-simplifier-review': 'Minimalist git diff review, YAGNI enforcement, and over-engineering removal.',
    'frontend-performance': 'Core Web Vitals (LCP, INP, CLS), 60fps GPU animations, and scroll optimization.',
    'frontend-taste-engineering': 'Anti-Slop aesthetic direction, 3-dial calibration, and design system routing.',
    'git-worktree-workspace': 'Subagent isolation in clean Git Worktrees via agy-worktree.',
    'high-end-visual-design': '$150k+ Awwwards-tier visual design: Double-Bezel chassis and spring physics.',
    'image-to-code': 'Image-first UI pipeline: reference generation, token extraction, and code.',
    'industrial-brutalist-ui': 'Industrial brutalist UI engineering: 90-degree grids, Swiss print, CRT telemetry.',
    'infrastructure-as-code-governance': 'IaC governance and security for Terraform, OpenTofu, Kubernetes, and Docker.',
    'integration-testing': 'Boundary integration tests across real databases, queues, and external APIs.',
    'lesson-learned': 'Capture and formalize procedural lessons learned ([L-NNN]) in project memory.',
    'living-docs-keeper': 'Continuous maintenance of living project documentation and technical decisions.',
    'marketing-psychology': "Behavioral economics (Loss Aversion, Price Anchoring, Hick's Law) in UI.",
    'mcp-server-governance': 'Zero Trust security, payload sanitization, and governance for MCP servers.',
    'migration-safety': 'Zero-downtime database migrations using the expand-and-contract pattern.',
    'minimalist-ui': 'Utilitarian minimalist UI (Linear/Notion aesthetic), 1px borders, whitespace.',
    'mutation-testing-sentinel': 'Test suite robustness auditing via mutation injection and >=80% mutation score.',
    'no-workarounds': 'Root-cause fixes only: ban workarounds, type casts, linter suppression, sleeps.',
    'observability-and-slo-engineering': 'Observability engineering: JSON logs, RED metrics, OpenTelemetry tracing, SLOs.',
    'pair-navigator': 'Pair programming navigation, minimal viable proposals, anti-over-engineering.',
    'privacy-review': 'Privacy review, GDPR/LGPD compliance, data minimization, and PII protection.',
    'project-brief-architect': 'Zero-Moment technical interview and structured project brief for Genesis.',
    'project-memory': '4-Tier continuous project memory, Fast Context Bootstrap, and auto-onboarding.',
    'property-based-testing': 'Property-Based Testing (PBT), invariant verification, and structured fuzzing.',
    'redesign-ui-audit': 'Surgical UI audit and modernization without breaking existing layouts.',
    'refactor-watchdog': 'Continuous refactoring watchdog against duplication and God files (>500 lines).',
    'responsive-architecture': 'Fluid responsive layout architecture, mobile hierarchy, and 48px touch targets.',
    'secrets-guardian': 'Credential leak prevention across code, .env, Git history, and build artifacts.',
    'security-observability': 'Real-time security monitoring, audit logging, and PII/secret log redaction.',
    'security-sentinel-review': 'Proactive security architecture review across auth, PII, payments, and inputs.',
    'security-testing': 'Proactive SAST/DAST and negative security test cases against auth bypass/injection.',
    'seo-content-engine': 'Technical On-Page SEO, Schema.org JSON-LD, and AI Search optimization (GEO/AEO).',
    'software-evolution-and-roadmapping': 'Technical roadmapping, Now/Next/Later horizons, Strangler Fig, and RFC 8594.',
    'spec-driven-development': 'Formal Specification-Driven Development (SDD) as single source of truth.',
    'specification-by-example': 'Convert ambiguous business rules into executable Specification by Example tables.',
    'supply-chain-security': 'Software supply chain security (SCA), lockfile integrity, and anti-typosquatting.',
    'systematic-debugging': '4-phase scientific debugging, backward tracing, and the 3-Fix Circuit Breaker.',
    'task-routing': 'Risk-based task routing (L0-L3) and surface-to-skill capability mapping.',
    'tdd-safety-net': 'Strict RED-GREEN-REFACTOR cycle, Anti-Test-Bypass, and surgical test execution.',
    'test-evidence-walkthrough': 'Native test execution evidence recording and verification by risk level.',
    'test-harness-bootstrap': 'Moment-Zero test harness setup: runner, directory layout, CI step, smoke test.',
    'threat-modeling': 'STRIDE threat modeling, trust boundaries, and security test derivation for L3.',
    'ui-quality-gate': 'Pre-release UI checklist: WCAG AA contrast, 100dvh viewport, and Anti-Slop gate.',
    'visual-direction-studio': 'Deliberate $150k+ visual direction, Hero discipline, and Anti-Slop layout rules.',
    'visual-regression': 'Visual regression testing across viewports, interactive states, and dark mode.',
    'zero-downtime-deployment': 'Zero-downtime deployment (Blue/Green, Canary, Rolling) and automated rollback.',
}


def get_profile_skills(profile_name: str, all_available: Iterable[str]) -> Set[str]:
    """Return the set of skills for the requested profile."""
    name = profile_name.lower().strip()
    if name in ("all", "full"):
        return set(all_available)
    if name in PROFILES:
        return set(PROFILES[name])
    raise ValueError(f"Unknown profile {profile_name!r}. Valid options: {list(PROFILES.keys())}")


def detect_current_profile(active_skills: Set[str]) -> str:
    """Infer the closest profile name based on currently active skills."""
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
    """List active and disabled skills in a skills directory."""
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
    """Apply a skill profile by managing symlinks in target_dir pointing to master_dir."""
    if not master_dir.exists():
        raise FileNotFoundError(f"Master skills directory not found: {master_dir}")

    target_dir.mkdir(parents=True, exist_ok=True)
    all_available = [p.name for p in master_dir.iterdir() if p.is_dir() and (p / "SKILL.md").exists()]
    target_skills = get_profile_skills(profile_name, all_available)

    active_created: List[str] = []
    removed: List[str] = []

    for item in list(target_dir.iterdir()):
        if item.name not in target_skills:
            removed.append(item.name)
            if not dry_run:
                if item.is_symlink() or item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)

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
    """Apply a profile by moving skill directories between skills_dir and disabled_dir."""
    skills_dir.mkdir(parents=True, exist_ok=True)
    disabled_dir.mkdir(parents=True, exist_ok=True)

    active_now = {p.name: p for p in skills_dir.iterdir() if p.is_dir()}
    disabled_now = {p.name: p for p in disabled_dir.iterdir() if p.is_dir()}
    all_available = sorted(set(active_now.keys()) | set(disabled_now.keys()))

    target_skills = get_profile_skills(profile_name, all_available)

    active_result: List[str] = []
    disabled_result: List[str] = []

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

    if not dry_run and disabled_dir.exists():
        if not any(disabled_dir.iterdir()):
            disabled_dir.rmdir()

    return sorted(active_result), sorted(disabled_result)


def enable_skill(skill_name: str, skills_dir: Path, disabled_dir: Path) -> bool:
    """Move a single skill from disabled_dir to skills_dir."""
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
    """Move a single skill from skills_dir to disabled_dir."""
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
    """Estimate header tokens based on active skill count."""
    return int((skill_count * avg_chars_per_skill) / 3.8)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agy-skills-profile",
        description="XP Kit Skill Profile Manager (A2 / D3)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("list", help="List all available skill profiles")
    subparsers.add_parser("status", help="Show active and disabled skills status")

    apply_parser = subparsers.add_parser("apply", help="Apply a skill profile")
    apply_parser.add_argument("profile", choices=["core", "backend", "frontend", "all", "full"], help="Profile name")
    apply_parser.add_argument("--global", dest="is_global", action="store_true", default=True, help="Apply in ~/.gemini/config/skills/ (default)")
    apply_parser.add_argument("--local", dest="is_local", action="store_true", help="Apply in local repository (.agents/skills)")
    apply_parser.add_argument("--dry-run", action="store_true", help="Simulate operation without changing files")

    enable_parser = subparsers.add_parser("enable", help="Enable an individual skill")
    enable_parser.add_argument("skill", help="Skill name")

    disable_parser = subparsers.add_parser("disable", help="Disable an individual skill")
    disable_parser.add_argument("skill", help="Skill name")

    args = parser.parse_args(argv)

    if not args.command or args.command == "status":
        kit_dir = Path(__file__).resolve().parent.parent
        local_skills = kit_dir / ".agents" / "skills"
        local_disabled = kit_dir / ".agents" / "skills_disabled"
        global_skills = DEFAULT_GLOBAL_SKILLS_DIR

        print("📊 Skill Profiles Status")
        print("────────────────────────────────────────────────────────")
        if global_skills.exists():
            g_active = [p.name for p in global_skills.iterdir() if p.is_dir() or p.is_symlink()]
            g_prof = detect_current_profile(set(g_active))
            tok = estimate_tokens(len(g_active))
            print("Global (~/.gemini/config/skills/):")
            print(f"  • Active: {len(g_active)} skills  |  Profile: [{g_prof}]  |  Cost: ~{tok} tokens/turn")

        if local_skills.exists():
            l_info = list_active_and_disabled(local_skills, local_disabled)
            l_prof = detect_current_profile(set(l_info["active"]))
            print("Local (.agents/skills/):")
            print(f"  • Active: {l_info['total_active']}  |  Disabled: {l_info['total_disabled']}  |  Profile: [{l_prof}]")
        print("────────────────────────────────────────────────────────")
        return 0

    if args.command == "list":
        print("📋 Available Skill Profiles")
        print("────────────────────────────────────────────────────────")
        for name, skills in PROFILES.items():
            count_label = f"{len(skills)} skills" if skills else f"all {len(SKILL_DESCRIPTIONS)} skills"
            tok = estimate_tokens(len(skills)) if skills else estimate_tokens(len(SKILL_DESCRIPTIONS))
            desc = PROFILE_META.get(name, {}).get("description", "")
            print(f"  • {name.upper():<10} : {count_label:<16} (~{tok} tokens/turn) — {desc}")
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
            print(f"✅ {prefix}Local profile {args.profile!r} applied: {len(active)} active, {len(disabled)} disabled.")
        else:
            target_skills = DEFAULT_GLOBAL_SKILLS_DIR
            active, removed = apply_profile_symlinks(args.profile, master_skills, target_skills, dry_run=args.dry_run)
            prefix = "[Dry-run] " if args.dry_run else ""
            tok = estimate_tokens(len(active))
            print(f"✅ {prefix}Global profile {args.profile!r} applied successfully!")
            print(f"   • Active skills in {target_skills}: {len(active)} (~{tok} tokens/turn)")
            if removed:
                print(f"   • Unlinked skills: {len(removed)}")
        return 0

    if args.command == "enable":
        kit_dir = Path(__file__).resolve().parent.parent
        skills_dir = kit_dir / ".agents" / "skills"
        disabled_dir = kit_dir / ".agents" / "skills_disabled"
        ok = enable_skill(args.skill, skills_dir, disabled_dir)
        if ok:
            print(f"✅ Skill {args.skill!r} enabled.")
            return 0
        print(f"❌ Skill {args.skill!r} not found in {disabled_dir}.", file=sys.stderr)
        return 1

    if args.command == "disable":
        kit_dir = Path(__file__).resolve().parent.parent
        skills_dir = kit_dir / ".agents" / "skills"
        disabled_dir = kit_dir / ".agents" / "skills_disabled"
        ok = disable_skill(args.skill, skills_dir, disabled_dir)
        if ok:
            print(f"✅ Skill {args.skill!r} disabled.")
            return 0
        print(f"❌ Skill {args.skill!r} not found in {skills_dir}.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
