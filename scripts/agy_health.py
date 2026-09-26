#!/usr/bin/env python3
"""
scripts/agy_health.py
Scanner de Saúde e Diagnóstico Global do Antigravity XP Kit.
Verifica em <100ms:
1. Conexão e latência do Language Server RPC.
2. Status ao vivo das cotas (5h e Semanal com Pre-Flight Gate >80%).
3. Integridade estrutural de plugins com auto-reparo instantâneo.
4. Tamanho e inchaço do PROJECT_MEMORY.md com alerta para agy-memory-archive.
5. Integridade das ferramentas e links simbólicos em ~/.local/bin/.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_PLUGIN_DIR = (
    Path.home() / ".gemini" / "config" / "plugins" / "googlecloudtools.datacloud_telemetry"
)
DEFAULT_MEMORY_FILE = PROJECT_ROOT / ".agents" / "memory" / "PROJECT_MEMORY.md"
DEFAULT_BIN_DIR = Path.home() / ".local" / "bin"
EXPECTED_TOOLS = [
    "agy-tokens",
    "xp-tokens",
    "agy-sanitize",
    "agy-compact",
    "agy-git-ops",
    "agy-memory-archive",
    "agy-ci-heal",
    "agy-handoff",
    "agy-audit",
    "agy-smart",
    "agy-fast",
    "agy-deep",
    "agy-memory-search",
    "agy-resume",
]


def check_plugin_directories(target_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Verifica e repara automaticamente diretórios de plugins necessários."""
    target = target_dir or DEFAULT_PLUGIN_DIR
    if target.is_dir():
        return {
            "name": "Diretórios de Plugins",
            "ok": True,
            "status": "OK",
            "details": f"Presente: {target}",
        }
    try:
        target.mkdir(parents=True, exist_ok=True)
        return {
            "name": "Diretórios de Plugins",
            "ok": True,
            "status": "RECOVERED",
            "details": f"Auto-reparado com sucesso: {target}",
        }
    except Exception as e:
        return {
            "name": "Diretórios de Plugins",
            "ok": False,
            "status": "ERROR",
            "details": f"Falha ao criar {target}: {e}",
        }


def check_memory_health(
    memory_path: Optional[Path] = None, warn_kb: int = 35
) -> Dict[str, Any]:
    """Verifica se o arquivo PROJECT_MEMORY.md está com tamanho saudável."""
    mem_file = memory_path or DEFAULT_MEMORY_FILE
    if not mem_file.is_file():
        return {
            "name": "Memória Contínua",
            "ok": True,
            "status": "NOT_FOUND",
            "details": f"Arquivo não encontrado: {mem_file}",
            "size_kb": 0.0,
        }

    size_bytes = mem_file.stat().st_size
    size_kb = size_bytes / 1024.0

    if size_kb > warn_kb:
        return {
            "name": "Memória Contínua",
            "ok": False,
            "status": "WARN",
            "size_kb": round(size_kb, 1),
            "details": f"{size_kb:.1f} KB (teto recomendado: {warn_kb} KB)",
            "recommendation": "Execute 'agy-memory-archive' para rotacionar a memória viva",
        }

    return {
        "name": "Memória Contínua",
        "ok": True,
        "status": "OK",
        "size_kb": round(size_kb, 1),
        "details": f"{size_kb:.1f} KB (saudável)",
    }


def evaluate_quota_health(
    quotas: Dict[str, Any], threshold: float = 80.0
) -> Dict[str, Any]:
    """Avalia o status das cotas alertando se alguma estiver acima do threshold."""
    critical_warnings = []

    gemini_5h = quotas.get("gemini_5h_used_pct")
    if gemini_5h is not None and gemini_5h >= threshold:
        critical_warnings.append(f"Cota 5h Gemini crítica: {gemini_5h:.1f}% usado")

    gemini_week = quotas.get("gemini_weekly_used_pct")
    if gemini_week is not None and gemini_week >= threshold:
        critical_warnings.append(f"Cota Semanal Gemini crítica: {gemini_week:.1f}% usado")

    p3_5h = quotas.get("3p_5h_used_pct")
    if p3_5h is not None and p3_5h >= threshold:
        critical_warnings.append(f"Cota 5h Claude/GPT crítica: {p3_5h:.1f}% usado")

    p3_week = quotas.get("3p_weekly_used_pct")
    if p3_week is not None and p3_week >= threshold:
        critical_warnings.append(f"Cota Semanal Claude/GPT crítica: {p3_week:.1f}% usado")

    if critical_warnings:
        return {
            "name": "Status de Cotas",
            "ok": False,
            "status": "WARN",
            "details": "; ".join(critical_warnings),
            "recommendation": "Opere com 'agy-fast' (--effort low) ou em Modo Cirúrgico Atômico",
        }

    summary = []
    if gemini_5h is not None:
        summary.append(f"Gemini 5h: {gemini_5h:.1f}%")
    if gemini_week is not None:
        summary.append(f"Gemini Semanal: {gemini_week:.1f}%")

    return {
        "name": "Status de Cotas",
        "ok": True,
        "status": "OK",
        "details": ", ".join(summary) if summary else "Cotas dentro dos limites",
    }


def check_symlinks_health(bin_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Verifica se as ferramentas CLI globais estão presentes e funcionais."""
    b_dir = bin_dir or DEFAULT_BIN_DIR
    valid = 0
    missing = []

    for tool in EXPECTED_TOOLS:
        tool_path = b_dir / tool
        if tool_path.exists():
            valid += 1
        else:
            missing.append(tool)

    if missing:
        return {
            "name": "Ferramentas no PATH",
            "ok": False,
            "status": "WARN",
            "details": f"{valid}/{len(EXPECTED_TOOLS)} ferramentas presentes. Ausentes: {', '.join(missing)}",
            "recommendation": "Execute './scripts/install-global.sh' para restabelecer os links",
        }

    return {
        "name": "Ferramentas no PATH",
        "ok": True,
        "status": "OK",
        "details": f"{valid}/{len(EXPECTED_TOOLS)} ferramentas ativas em {b_dir}",
    }


def check_language_server_rpc() -> Dict[str, Any]:
    """Testa a conectividade com o Language Server RPC."""
    start_time = time.time()
    try:
        from scripts.token_tracker import fetch_live_antigravity_quota

        quota_obj = fetch_live_antigravity_quota(force_refresh=True)
        elapsed_ms = round((time.time() - start_time) * 1000, 1)

        if quota_obj and quota_obj.is_live:
            quotas_summary: Dict[str, Any] = {}
            if quota_obj.gemini_5h:
                quotas_summary["gemini_5h_used_pct"] = round(
                    (1.0 - quota_obj.gemini_5h.remaining_fraction) * 100, 1
                )
            if quota_obj.gemini_weekly:
                quotas_summary["gemini_weekly_used_pct"] = round(
                    (1.0 - quota_obj.gemini_weekly.remaining_fraction) * 100, 1
                )
            if quota_obj.claude_5h:
                quotas_summary["3p_5h_used_pct"] = round(
                    (1.0 - quota_obj.claude_5h.remaining_fraction) * 100, 1
                )
            if quota_obj.claude_weekly:
                quotas_summary["3p_weekly_used_pct"] = round(
                    (1.0 - quota_obj.claude_weekly.remaining_fraction) * 100, 1
                )

            return {
                "name": "Language Server RPC",
                "ok": True,
                "status": "OK",
                "latency_ms": elapsed_ms,
                "details": f"Conectado ao vivo ({elapsed_ms}ms)",
                "quotas": quotas_summary,
            }
        else:
            err = quota_obj.error if quota_obj else "Sem resposta"
            return {
                "name": "Language Server RPC",
                "ok": True,
                "status": "OFFLINE",
                "details": f"Fallback ativo ({err})",
                "quotas": {},
            }
    except Exception as e:
        return {
            "name": "Language Server RPC",
            "ok": True,
            "status": "OFFLINE",
            "details": f"Sem resposta RPC ({e})",
            "quotas": {},
        }


def run_system_health_check(
    plugin_dir: Optional[Path] = None,
    memory_file: Optional[Path] = None,
    bin_dir: Optional[Path] = None,
    mock_rpc: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Executa todos os diagnósticos e retorna um relatório consolidado."""
    checks = []

    # 1. Plugin directories
    checks.append(check_plugin_directories(plugin_dir))

    # 2. Memory health
    checks.append(check_memory_health(memory_file))

    # 3. Symlinks
    checks.append(check_symlinks_health(bin_dir))

    # 4. Language Server & Quotas
    if mock_rpc is not None:
        rpc_check = {
            "name": "Language Server RPC",
            "ok": True,
            "status": "OK",
            "details": "Mock RPC Conectado",
            "quotas": mock_rpc,
        }
        quota_check = evaluate_quota_health(mock_rpc)
    else:
        rpc_check = check_language_server_rpc()
        quota_check = evaluate_quota_health(rpc_check.get("quotas", {}))

    checks.append(rpc_check)
    checks.append(quota_check)

    all_ok = all(c["ok"] for c in checks)
    return {
        "overall_healthy": all_ok,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "checks": checks,
    }


def format_health_report(report: Dict[str, Any]) -> str:
    """Formata o relatório para exibição visual no terminal."""
    lines = [
        "=======================================================",
        "🩺 Antigravity XP Kit — Diagnóstico de Saúde do Sistema",
        "=======================================================",
    ]
    recommendations = []

    for check in report.get("checks", []):
        status = check["status"]
        name = check["name"]
        details = check["details"]

        if status in ("OK", "RECOVERED"):
            badge = f"[{status}]".ljust(7)
        elif status == "WARN":
            badge = "[WARN] ".ljust(7)
        else:
            badge = "[FAIL] ".ljust(7)

        lines.append(f"{badge} {name.ljust(22)} : {details}")

        rec = check.get("recommendation")
        if rec:
            recommendations.append(f"  • {rec}")

    lines.append("=======================================================")
    if report["overall_healthy"]:
        lines.append("Status Geral: SAUDÁVEL (Todos os sistemas operacionais)")
    else:
        lines.append("Status Geral: ATENÇÃO (Ações recomendadas disponíveis)")

    if recommendations:
        lines.append("\n💡 Recomendações:")
        lines.extend(recommendations)

    lines.append("=======================================================")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="XP Kit — Diagnóstico Global de Saúde e Integridade"
    )
    parser.add_argument("--json", action="store_true", help="Exibe o relatório em JSON")
    args = parser.parse_args()

    report = run_system_health_check()

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(format_health_report(report))

    return 0 if report["overall_healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
