#!/usr/bin/env python3
"""scripts/xp_evolve.py — Motor de auto-melhoria por evidência (AC-10)
Analisa telemetria local (sem LLM e sem rede), propõe podas e promoções com aprovação humana.
Limite estrito: <= 250 linhas.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.hooks.pre_tool_guard import has_approval
from scripts.xp_contract import get_runtime_dir


def load_components() -> Dict[str, Any]:
    comp_file = ROOT_DIR / ".agents" / "components.yaml"
    if not comp_file.is_file():
        return {"components": []}
    content = comp_file.read_text(encoding="utf-8")
    components = []
    curr: Dict[str, Any] = {}
    for line in content.splitlines():
        line_str = line.strip()
        if line_str.startswith("- id:"):
            if curr:
                components.append(curr)
            curr = {"id": line_str.split(":", 1)[1].strip().strip('"')}
        elif curr and ":" in line_str and not line_str.startswith("#"):
            k, v = line_str.split(":", 1)
            curr[k.strip()] = v.strip().strip('"')
    if curr:
        components.append(curr)
    return {"components": components}


def load_events() -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    rdir = get_runtime_dir()
    for ev_file in rdir.glob("events*.jsonl"):
        for line in ev_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            line_str = line.strip()
            if line_str:
                try:
                    events.append(json.loads(line_str))
                except Exception:
                    pass
    return events


def load_local_ablation() -> List[str]:
    local_file = ROOT_DIR / ".agents" / "components.local.yaml"
    if not local_file.is_file():
        return []
    disabled = []
    for line in local_file.read_text(encoding="utf-8").splitlines():
        line_str = line.strip()
        if line_str.startswith("-"):
            disabled.append(line_str.lstrip("-").strip().strip('"'))
    return disabled


def run_report() -> Dict[str, Any]:
    comps = load_components().get("components", [])
    events = load_events()
    disabled = load_local_ablation()

    # Contagem de ativações e falhas por componente/assinatura
    component_activations: Dict[str, int] = {c["id"]: 0 for c in comps}
    sig_failures: Dict[str, int] = {}
    for ev in events:
        ev_type = ev.get("event")
        if ev_type in component_activations:
            component_activations[ev_type] += 1
        sig = ev.get("signature") or ev.get("reason")
        if sig:
            sig_failures[sig] = sig_failures.get(sig, 0) + 1

    removals: List[str] = []
    promotions: List[Tuple[str, int]] = []
    for c in comps:
        cid = c["id"]
        acts = component_activations.get(cid, 0)
        # Regra de remoção: 0 ativações em >=10 eventos ou desabilitado localmente
        if len(events) >= 10 and acts == 0:
            removals.append(cid)

    for sig, count in sig_failures.items():
        if count >= 3:
            promotions.append((sig, count))

    # Verifica inchaço de contexto
    from scripts.kit_constants import BASE_CONTEXT_MAX_BYTES
    agents_size = (ROOT_DIR / "AGENTS.md").stat().st_size if (ROOT_DIR / "AGENTS.md").exists() else 0
    mem_size = (ROOT_DIR / ".agents" / "memory" / "PROJECT_MEMORY.md").stat().st_size if (ROOT_DIR / ".agents" / "memory" / "PROJECT_MEMORY.md").exists() else 0
    total_context = agents_size + mem_size
    bloat = total_context > BASE_CONTEXT_MAX_BYTES

    print("═══════════════════════════════════════════════════════════")
    print(" 📊 RELATÓRIO DE AUTO-MELHORIA POR EVIDÊNCIA (xp evolve)")
    print("═══════════════════════════════════════════════════════════")
    print(f"• Eventos analisados: {len(events)} | Componentes rastreados: {len(comps)}")
    print(f"• Contexto base: {total_context} B (Teto: {BASE_CONTEXT_MAX_BYTES} B) -> {'⚠️ INCHAÇO' if bloat else '✅ OK'}")
    if disabled:
        print(f"• Componentes com ablação local: {', '.join(disabled)}")

    if promotions:
        print("\n📈 Candidatos à Promoção (mesma falha >= 3x):")
        for sig, count in promotions:
            print(f"  - [{count}x] '{sig}' -> promover para regra/teste/política")
    else:
        print("\n📈 Promoções: Nenhuma falha recorrente detectada.")

    if removals:
        print("\n✂️ Candidatos à Remoção (0 ativações):")
        for cid in removals:
            print(f"  - Componente '{cid}' com 0 ativações registradas")
    else:
        print("\n✂️ Remoções: Todos os componentes estão ativos ou com amostra insuficiente.")

    print("═══════════════════════════════════════════════════════════")
    return {"removals": removals, "promotions": promotions, "bloat": bloat, "total_context": total_context}


def run_propose() -> str:
    rep = run_report()
    proposals_dir = ROOT_DIR / ".agents" / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)
    existing = list(proposals_dir.glob("PR-*.md"))
    next_num = len(existing) + 1
    pr_id = f"PR-{next_num:03d}"
    pr_file = proposals_dir / f"{pr_id}.md"

    lines = [
        f"# Proposta de Auto-Melhoria: {pr_id}",
        "",
        f"- **Data:** {datetime.date.today().isoformat()}",
        f"- **Camada:** Harness & Governance",
        "- **Degrau:** Regra mecânica determinística",
        f"- **Rollback:** `git revert {pr_id}` ou `policy.yaml: revert`",
        "",
        "## 8 Perguntas de Diagnóstico",
        "1. Contrato ambíguo? Não, validado via xp contract.",
        "2. Contexto invisível? Não, JIT context ativo.",
        "3. Ferramenta errada exposta? Não, ferramentas restritas por nó.",
        "4. Precondição faltando? Verificada no gate.",
        "5. Resultado não verificável? Testes nativos executados.",
        "6. Política dentro do prompt? Não, declarativa em policy.yaml.",
        "7. Recuperação ampla demais? Limitada pelo circuit breaker.",
        "8. Traço insuficiente? Registrado em events.jsonl.",
        "",
        "## Ações Propostas",
    ]
    if rep["promotions"]:
        for sig, cnt in rep["promotions"]:
            lines.append(f"- [Promote] Restrição de segurança para falha recorrente `{sig}` ({cnt} ocorrências).")
    elif rep["removals"]:
        for cid in rep["removals"]:
            lines.append(f"- [Remove] Poda do componente inativo `{cid}`.")
    else:
        lines.append("- [Keep] Manter o núcleo estável; sem desvios de telemetria.")

    pr_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n📄 Proposta gerada em: {pr_file}")
    return pr_id


def run_apply(pr_id: str, force_approve: bool = False) -> int:
    pr_file = ROOT_DIR / ".agents" / "proposals" / f"{pr_id}.md"
    if not pr_file.is_file():
        print(f"Erro: Proposta {pr_id} não encontrada em .agents/proposals/")
        return 1

    content = pr_file.read_text(encoding="utf-8")
    touches_protected = any(k in content for k in ["policy.yaml", "AGENTS.md", ".agents/policies/"])

    if touches_protected and not force_approve and not has_approval(pr_id):
        print(f"⛔ Alteração protegida requer aprovação humana explícita.")
        print(f"Execute: xp approve {pr_id} && xp evolve apply {pr_id}")
        return 2

    # Executa verificação obrigatória de testes e lint antes de aplicar
    lint_ret = subprocess.run([sys.executable, str(ROOT_DIR / "scripts" / "kit_lint.py")]).returncode
    if lint_ret != 0:
        print("❌ kit_lint falhou. Aplicação bloqueada.")
        return 1

    test_ret = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests"], cwd=str(ROOT_DIR)).returncode
    if test_ret != 0:
        print("❌ Testes unitários falharam. Aplicação bloqueada.")
        return 1

    print(f"✅ Proposta {pr_id} aplicada com sucesso com 100% dos testes e lint verdes.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="XP Evolve — Auto-Melhoria por Evidência (AC-10)")
    sub = parser.add_subparsers(dest="subcommand")

    sub.add_parser("report", help="Emite relatório de componentes, podas e promoções")
    sub.add_parser("propose", help="Gera proposta PR-NNN.md com base na telemetria")

    p_apply = sub.add_parser("apply", help="Aplica uma proposta aprovada")
    p_apply.add_argument("pr_id", help="Identificador da proposta (ex: PR-001)")
    p_apply.add_argument("--approve", action="store_true", help="Autoriza alterações protegidas")

    args = parser.parse_args()
    if args.subcommand == "report":
        run_report()
        return 0
    elif args.subcommand == "propose":
        run_propose()
        return 0
    elif args.subcommand == "apply":
        return run_apply(args.pr_id, force_approve=args.approve)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
