#!/usr/bin/env python3
"""
scripts/prune_skills.py
Semantic pruning of YAML frontmatter descriptions in .agents/skills/*/SKILL.md.
Reduces input token overhead injected into the <skills> context block.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict

CONCISE_DESCRIPTIONS: Dict[str, str] = {
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
    'design-intelligence': 'Offline design catalog search (product archetypes, palettes, fonts, UX rules, charts) generating a persistent design-system MASTER.md.',
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
    'mobile-app-design': 'Native and cross-platform mobile app UI/UX: platform units, safe areas, thumb zone, navigation, accessibility, and mobile design systems.',
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


def prune_skill_file(skill_path: Path, new_desc: str, apply: bool = False) -> tuple[int, int]:
    """Read SKILL.md, update YAML frontmatter description, and return (before_bytes, after_bytes)."""
    content = skill_path.read_text(encoding="utf-8")
    original_len = len(content)

    pattern = r"(^---\n(?:.*\n)*?description:\s*)([^\n]+)(\n(?:.*\n)*?---)"
    match = re.search(pattern, content, re.MULTILINE)

    if not match:
        return original_len, original_len

    old_desc = match.group(2).strip()
    if old_desc == new_desc:
        return original_len, original_len

    new_content = content[: match.start(2)] + new_desc + content[match.end(2) :]
    new_len = len(new_content)

    if apply:
        skill_path.write_text(new_content, encoding="utf-8")

    return original_len, new_len


def main() -> int:
    parser = argparse.ArgumentParser(description="Semantic pruning of skill descriptions")
    parser.add_argument("--apply", action="store_true", help="Write changes to disk")
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=Path(".agents/skills"),
        help="Skills directory",
    )
    args = parser.parse_args()

    skills_dir: Path = args.skills_dir
    if not skills_dir.exists():
        print(f"Error: directory {skills_dir} not found.", file=sys.stderr)
        return 1

    total_orig = 0
    total_new = 0
    updated_count = 0

    for skill_name, concise_desc in CONCISE_DESCRIPTIONS.items():
        skill_file = skills_dir / skill_name / "SKILL.md"
        if not skill_file.exists():
            continue

        orig_len, new_len = prune_skill_file(skill_file, concise_desc, apply=args.apply)
        total_orig += orig_len
        total_new += new_len
        if orig_len != new_len:
            updated_count += 1

    saved_bytes = total_orig - total_new
    saved_tokens = int(saved_bytes / 3.8)

    action_label = "Applied" if args.apply else "Dry-run"
    print(f"[{action_label}] {updated_count} skills updated.")
    print(f"Estimated savings: {saved_bytes} chars (~{saved_tokens} tokens) per turn!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
