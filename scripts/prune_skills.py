#!/usr/bin/env python3
"""
scripts/prune_skills.py
Poda semântica das descrições de skills no frontmatter YAML de .agents/skills/*/SKILL.md.
Reduz drasticamente o consumo de tokens de entrada injetados no bloco <skills>.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict

CONCISE_DESCRIPTIONS: Dict[str, str] = {
    "accessibility-engineering": "Acessibilidade: teclado, contraste WCAG AA e ARIA.",
    "adr-architect-tracker": "ADRs MADR 3.0 e detecção de desvio arquitetural.",
    "api-contracts": "Design e versionamento de contratos OpenAPI e schemas.",
    "api-security": "Segurança de APIs e OWASP API Security Top 10.",
    "atomic-commit-discipline": "Commits atômicos, categorizados e testados.",
    "authentication-security": "Auditoria de autenticação, JWT, sessões e MFA.",
    "authorization-security": "Controle de acesso, permissões e prevenção BOLA/IDOR.",
    "availability-security": "Proteção contra DoS, Rate Limiting e sobrecarga.",
    "browser-e2e-playwright": "Testes E2E headless com Playwright e traces.",
    "ci-auto-heal": "Monitoramento de CI/CD e autocorreção autônoma (máx 3).",
    "ci-security-gate": "Pipeline CI com lint, testes, auditoria e SAST.",
    "cloud-security-and-zero-trust": "Zero Trust, OIDC federado, Cosign e mTLS.",
    "codebase-cartography": "Mapeamento estrutural de dependências e impacto.",
    "code-deslop-review": "Remoção de código redundante e regra No God Files.",
    "component-architecture": "Componentes modulares, estados e micro-interações.",
    "component-registry": "Registro e governança de componentes reaproveitáveis.",
    "container-security": "Hardening de Dockerfiles, imagens non-root e builds.",
    "conversion-copywriting": "Copywriting de conversão e ponte de benefícios.",
    "copy-editing-sweeps": "Edição de copy em 7 passadas contra clichês.",
    "cro-landing-pages": "Otimização de conversão (CRO) e redução de atrito.",
    "crypto-guardian": "Auditoria de primitivas criptográficas e chaves.",
    "database-architecture": "Modelagem SQL/NoSQL, índices e concorrência.",
    "dependency-governance": "Avaliação de risco e governança de novas dependências.",
    "deploy-pipeline-conductor": "Condução de CD, contêineres e rollout gradual.",
    "design-system-architecture": "Governança de Design System de tokens a páginas.",
    "design-tokens": "Tokens visuais semânticos com Color e Shape Locks.",
    "diff-simplifier-review": "Revisão minimalista de diff e remoção de over-engineering.",
    "frontend-performance": "Core Web Vitals (LCP, INP, CLS) e renderização GPU-safe.",
    "frontend-taste-engineering": "Direção estética Anti-Slop e calibração por dials.",
    "git-worktree-workspace": "Isolamento de subagentes em Git Worktrees limpos.",
    "high-end-visual-design": "Design visual $150k+: Double-Bezel e física de mola.",
    "image-to-code": "Pipeline image-first para implementação de UI fiel.",
    "industrial-brutalist-ui": "Engenharia de UI brutalista industrial e grid 90°.",
    "infrastructure-as-code-governance": "Governança e segurança em IaC (Terraform, K8s).",
    "integration-testing": "Testes de integração em banco, filas e APIs reais.",
    "lesson-learned": "Captura e formalização de lições aprendidas (L-NNN).",
    "living-docs-keeper": "Manutenção contínua de documentação viva e decisões.",
    "marketing-psychology": "Economia comportamental (Hick, Ancoragem) em UI.",
    "mcp-server-governance": "Governança, segurança e integração de servidores MCP.",
    "migration-safety": "Migrações de banco expand-and-contract sem downtime.",
    "minimalist-ui": "Interfaces minimalistas, Linear/Notion e whitespace.",
    "mutation-testing-sentinel": "Auditoria de robustez de testes via injeção de mutações.",
    "no-workarounds": "Correção na causa raiz, proibindo remendos e casts.",
    "observability-and-slo-engineering": "Engenharia de observabilidade: logs JSON, métricas RED e SLOs.",
    "observability-instrumentation": "Instrumentação de telemetria pós-deploy.",
    "pair-navigator": "Navegação em pair programming e combate ao over-engineering.",
    "privacy-review": "Revisão de privacidade, LGPD/GDPR e proteção de PII.",
    "project-brief-architect": "Entrevista técnica e requisitos no Momento Zero.",
    "project-memory": "Memória contínua em 4 Tiers, Fast Bootstrap e Onboarding.",
    "property-based-testing": "Testes baseados em propriedades e fuzzing estruturado.",
    "redesign-ui-audit": "Auditoria e modernização de UI sem quebrar layout.",
    "refactor-watchdog": "Vigilância contra duplicação e arquivos grandes (>500 linhas).",
    "responsive-architecture": "Arquitetura de layout fluido e responsividade real.",
    "secrets-guardian": "Prevenção contra vazamento de credenciais e chaves.",
    "security-observability": "Monitoramento e auditoria em tempo real de segurança.",
    "security-sentinel-review": "Revisão proativa de segurança e superfícies sensíveis.",
    "security-testing": "Casos de teste SAST/DAST contra injeções e falhas.",
    "seo-content-engine": "SEO On-Page, Schema.org JSON-LD e AI Search (GEO/AEO).",
    "spec-driven-development": "Engenharia guiada por especificação formal (SDD).",
    "supply-chain-security": "Segurança de dependências e integridade de cadeia (SCA).",
    "systematic-debugging": "Debugging sistemático em 4 fases e investigação de causa raiz.",
    "task-routing": "Roteamento de tarefas por superfícies e níveis de risco (L0-L3).",
    "tdd-safety-net": "Ciclo RED-GREEN-REFACTOR e Anti-Test-Bypass estrito.",
    "test-evidence-walkthrough": "Validação de evidência de testes nativos por risco.",
    "test-harness-bootstrap": "Harness de testes no Momento Zero antes de features.",
    "threat-modeling": "Modelagem de ameaças usando STRIDE e Trust Boundaries.",
    "token-budget-tracker": "Telemetria de tokens em 3 camadas e Modo Cirúrgico.",
    "ui-quality-gate": "Checklist pré-release: WCAG AA, 100dvh e qualidade visual.",
    "visual-direction-studio": "Definição de direção visual deliberada sem UI genérica.",
    "visual-regression": "Controle e testes de regressão visual para fidelidade de UI.",
    "zero-downtime-deployment": "Deploy Zero-Downtime (Blue/Green, Canary) e rollback.",
}


def prune_skill_file(skill_path: Path, new_desc: str, apply: bool = False) -> tuple[int, int]:
    """Lê SKILL.md, atualiza a description no frontmatter e retorna bytes antes/depois."""
    content = skill_path.read_text(encoding="utf-8")
    original_len = len(content)

    # Expressão para localizar description no frontmatter YAML
    pattern = r"(^---\n(?:.*\n)*?description:\s*)([^\n]+)(\n(?:.*\n)*?---)"
    match = re.search(pattern, content, re.MULTILINE)

    if not match:
        return original_len, original_len

    old_desc = match.group(2).strip()
    # Se a descrição já for idêntica, mantém
    if old_desc == new_desc:
        return original_len, original_len

    new_content = content[: match.start(2)] + new_desc + content[match.end(2) :]
    new_len = len(new_content)

    if apply:
        skill_path.write_text(new_content, encoding="utf-8")

    return original_len, new_len


def main() -> int:
    parser = argparse.ArgumentParser(description="Poda semântica de descrições de skills")
    parser.add_argument("--apply", action="store_true", help="Aplica as alterações em disco")
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=Path(".agents/skills"),
        help="Diretório de skills",
    )
    args = parser.parse_args()

    skills_dir: Path = args.skills_dir
    if not skills_dir.exists():
        print(f"Erro: diretório {skills_dir} não encontrado.", file=sys.stderr)
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
    saved_chars = saved_bytes  # Aprox 1:1 UTF-8 ASCII/PT-BR
    saved_tokens = int(saved_chars / 3.8)

    action_label = "Aplicadas" if args.apply else "Simuladas (Dry-run)"
    print(f"[{action_label}] {updated_count} skills atualizadas.")
    print(f"Economia estimada: {saved_chars} caracteres (~{saved_tokens} tokens) por turno!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
