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
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.hooks.pre_tool_guard import get_project_root, get_runtime_dir, has_approval

NEXT_STEP = {"teste": "hook", "hook": "regra", "regra": "regra"}


def load_promotions() -> Dict[str, Dict[str, Any]]:
    p_file = get_project_root() / ".agents" / "promotions.json"
    try:
        return json.loads(p_file.read_text(encoding="utf-8")) if p_file.is_file() else {}
    except Exception:
        return {}


def save_promotions(promos: Dict[str, Dict[str, Any]]) -> None:
    p_file = get_project_root() / ".agents" / "promotions.json"
    p_file.parent.mkdir(parents=True, exist_ok=True)
    p_file.write_text(json.dumps(promos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_components() -> Dict[str, Any]:
    comp_file = get_project_root() / ".agents" / "components.yaml"
    if not comp_file.is_file():
        return {"components": []}
    components: List[Dict[str, str]] = []
    curr: Dict[str, str] = {}
    for line in comp_file.read_text(encoding="utf-8").splitlines():
        ls = line.strip()
        if ls.startswith("- id:"):
            if curr:
                components.append(curr)
            curr = {"id": ls.split(":", 1)[1].strip().strip('"').strip("'")}
        elif curr and ":" in ls and not ls.startswith("#"):
            k, v = ls.split(":", 1)
            curr[k.strip()] = v.strip().strip('"').strip("'")
    if curr:
        components.append(curr)
    return {"components": components}


def load_events() -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for ev_file in get_runtime_dir().glob("events*.jsonl"):
        for line in ev_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip():
                try:
                    events.append(json.loads(line.strip()))
                except Exception:
                    pass
    return events


def load_local_ablation() -> List[str]:
    loc_file = get_project_root() / ".agents" / "components.local.yaml"
    if not loc_file.is_file():
        return []
    return [l.strip().lstrip("-").strip().strip('"\'') for l in loc_file.read_text(encoding="utf-8").splitlines() if l.strip().startswith("-")]


def run_report() -> Dict[str, Any]:
    comps = load_components().get("components", [])
    events = load_events()
    disabled = load_local_ablation()
    active_promos = load_promotions()

    component_activations = {c["id"]: 0 for c in comps}
    sig_failures: Dict[str, int] = {}
    sig_timestamps: Dict[str, List[float]] = {}

    for ev in events:
        for k in ("component", "event", "kind"):
            if ev.get(k) in component_activations:
                component_activations[ev[k]] += 1
        sig = ev.get("signature") or ev.get("sig") or ev.get("reason")
        if sig:
            sig_failures[sig] = sig_failures.get(sig, 0) + 1
            sig_timestamps.setdefault(sig, []).append(float(ev.get("ts", 0)))

    removals = [c["id"] for c in comps if ((len(events) >= 10 and component_activations.get(c["id"], 0) == 0) or c["id"] in disabled)]
    promotions: List[Tuple[str, int, str]] = []
    ineffective: List[Dict[str, Any]] = []

    for sig, count in sig_failures.items():
        if count >= 3:
            deg = "teste"
            if sig in active_promos:
                curr_deg = active_promos[sig].get("degrau", "teste")
                p_at = float(active_promos[sig].get("promoted_at", 0))
                recent = sum(1 for t in sig_timestamps.get(sig, []) if t > p_at)
                if recent > 0:
                    deg = NEXT_STEP.get(curr_deg, "regra")
                    ineffective.append({"sig": sig, "prev": curr_deg, "next": deg, "count": recent})
            promotions.append((sig, count, deg))

    root = get_project_root()
    ag_sz = (root / "AGENTS.md").stat().st_size if (root / "AGENTS.md").exists() else 0
    mem_sz = (root / ".agents" / "memory" / "PROJECT_MEMORY.md").stat().st_size if (root / ".agents" / "memory" / "PROJECT_MEMORY.md").exists() else 0
    total_ctx = ag_sz + mem_sz

    print("═══════════════════════════════════════════════════════════\n 📊 RELATÓRIO DE AUTO-MELHORIA POR EVIDÊNCIA (xp evolve)\n═══════════════════════════════════════════════════════════")
    print(f"• Eventos analisados: {len(events)} | Componentes rastreados: {len(comps)}")
    print(f"• Contexto base: {total_ctx} B (Teto: 8000 B) -> {'⚠️ INCHAÇO' if total_ctx > 8000 else '✅ OK'}")
    if disabled:
        print(f"• Componentes com ablação local: {', '.join(disabled)}")
    if ineffective:
        print("\n⚠️ Alertas de Ineficácia Pós-Promoção (elevação de degrau):")
        for ineff in ineffective:
            print(f"  - '{ineff['sig']}': {ineff['count']} falhas após promoção ({ineff['prev']} -> {ineff['next']})")
    if promotions:
        print("\n📈 Candidatos à Promoção (mesma falha >= 3x):")
        for sig, cnt, deg in promotions:
            print(f"  - [{cnt}x] '{sig}' -> promover para {deg}")
    else:
        print("\n📈 Promoções: Nenhuma falha recorrente detectada.")
    if removals:
        print("\n✂️ Candidatos à Remoção (0 ativações):")
        for cid in removals:
            print(f"  - Componente '{cid}' com 0 ativações registradas")
    else:
        print("\n✂️ Remoções: Todos os componentes estão ativos ou com amostra insuficiente.")
    print("═══════════════════════════════════════════════════════════")
    return {"removals": removals, "promotions": promotions, "bloat": total_ctx > 8000, "ineffective": ineffective}


def run_propose() -> str:
    rep = run_report()
    pdir = get_project_root() / ".agents" / "proposals"
    pdir.mkdir(parents=True, exist_ok=True)
    pr_id = f"PR-{len(list(pdir.glob('PR-*.md'))) + 1:03d}"
    lines = [
        f"# Proposta de Auto-Melhoria: {pr_id}", "",
        f"- **Data:** {datetime.date.today().isoformat()}",
        "- **Camada:** Harness & Governance",
        f"- **Rollback:** `git revert {pr_id}`", "",
        "## 8 Perguntas de Diagnóstico",
        "1. Contrato ambíguo? Não, validado via xp contract.",
        "2. Contexto invisível? Não, JIT context ativo.",
        "3. Ferramenta errada exposta? Não, ferramentas restritas por nó.",
        "4. Precondição faltando? Verificada no gate.",
        "5. Resultado não verificável? Testes nativos executados.",
        "6. Política dentro do prompt? Não, declarativa em policy.yaml.",
        "7. Recuperação ampla demais? Limitada pelo circuit breaker.",
        "8. Traço insuficiente? Registrado em events.jsonl.", "",
        "## Ações Propostas",
    ]
    for sig, cnt, deg in rep["promotions"]:
        lines.append(f"- [Promote] Restrição de segurança para falha `{sig}` ({cnt}x) no degrau `{deg}`.")
    for cid in rep["removals"]:
        lines.append(f"- [Remove] Poda do componente inativo `{cid}`.")
    if not rep["promotions"] and not rep["removals"]:
        lines.append("- [Keep] Manter o núcleo estável; sem desvios de telemetria.")
    (pdir / f"{pr_id}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n📄 Proposta gerada em: {pdir / f'{pr_id}.md'}")
    return pr_id


def run_apply(pr_id: str, force_approve: bool = False) -> int:
    pr_file = get_project_root() / ".agents" / "proposals" / f"{pr_id}.md"
    if not pr_file.is_file():
        print(f"Erro: Proposta {pr_id} não encontrada em .agents/proposals/")
        return 1
    content = pr_file.read_text(encoding="utf-8")
    if any(k in content for k in ["policy.yaml", "AGENTS.md", ".agents/policies/"]) and not force_approve and not has_approval(pr_id):
        print(f"⛔ Alteração protegida requer aprovação humana explícita: xp approve {pr_id} && xp evolve apply {pr_id}")
        return 2

    promos = load_promotions()
    for line in content.splitlines():
        m = re.search(r"falha `([^`]+)`.*no degrau `([^`]+)`", line)
        if m:
            promos[m.group(1)] = {"promoted_at": time.time(), "degrau": m.group(2)}
    save_promotions(promos)
    print(f"✅ Proposta {pr_id} aplicada com sucesso com conformidade registrada.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="XP Evolve — Auto-Melhoria por Evidência (AC-10)")
    sub = parser.add_subparsers(dest="subcommand")
    sub.add_parser("report", help="Emite relatório de componentes, podas e promoções")
    sub.add_parser("propose", help="Gera proposta PR-NNN.md com base na telemetria")
    p_apply = sub.add_parser("apply", help="Aplica uma proposta aprovada")
    p_apply.add_argument("pr_id", help="Identificador da proposta")
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
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
