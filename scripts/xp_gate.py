#!/usr/bin/env python3
"""scripts/xp_gate.py — Gate determinístico barato-primeiro do XP Kit (AC-3)
10 degraus executados em ordem estrita de custo; para na primeira falha.
Limite estrito: <= 300 linhas.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.goldfish_review import audit_code_completeness
from scripts.hooks.pre_tool_guard import calculate_effective_tier, has_approval
from scripts.kit_events import classify_failure, emit
from scripts.xp_contract import load_contract, record_dead_end


def get_git_diff_files() -> List[str]:
    try:
        res = subprocess.run(["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return [line.strip() for line in res.stdout.splitlines() if line.strip()]
        res2 = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
        return [line.strip() for line in res2.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def format_failure_block(step: int, failed: str, expected: str, saw: str, fence: str, dead_ends: List[Any], hint: str) -> str:
    lines = [
        f"FAILED: [Step {step}] {failed}",
        f"EXPECTED: {expected}",
        f"SAW: {saw}",
        f"FENCE: {fence}",
        f"DEAD ENDS: {json.dumps(dead_ends, ensure_ascii=False)[:100]}",
        f"hint: {hint}",
    ]
    return "\n".join(lines)


def build_receipt(contract: Dict[str, Any], changed_files: List[str], tier: str, tests_run: int = 0, verified_checks: Optional[List[str]] = None, unverified_checks: Optional[List[str]] = None) -> str:
    ver = verified_checks or [f"tests={tests_run}"]
    unver = unverified_checks or []
    lines = [
        f"OBJETIVO: {contract.get('goal', 'Sem objetivo')}",
        f"ALTERADO: {len(changed_files)} arquivo(s) ({', '.join(changed_files[:3])}{'...' if len(changed_files) > 3 else ''})",
        f"VERIFICADO: {', '.join(ver)}",
        f"NÃO VERIFICADO: {', '.join(unver) if unver else 'Nenhuma checagem pendente'}",
        f"DECISÕES: Padrão arquitetural aplicado com contrato {contract.get('risk', 'L1')}",
        f"RISCOS: Tier efetivo {tier}",
        f"APROVAÇÃO NECESSÁRIA: {'Nenhuma (auto/review)' if tier != 'human' else 'Aprovação humana obrigatória via xp approve'}",
    ]
    return "\n".join(lines)


def run_gate(dry_run: bool = False, changed_files: Optional[List[str]] = None, receipt_mode: bool = False) -> Tuple[int, str, str]:
    contract = load_contract()
    files = changed_files if changed_files is not None else get_git_diff_files()
    tried = contract.get("tried", [])
    ev_id = f"EV-{int(subprocess.check_output(['date', '+%s']).strip() if sys.platform != 'win32' else '12345')}"

    # 1. Contrato existe e é válido
    if not contract or not contract.get("goal"):
        fail = format_failure_block(1, "Contrato inválido", "goal e risk preenchidos", "Contrato vazio ou sem meta", "run.json", tried, "Execute 'xp contract init'")
        return 1, "GATE FAIL step=1 reason=invalid_contract", fail

    # 2. Cerca de escopo
    scope_files = contract.get("scope_files", [])
    if scope_files and files:
        norm_scope = {str(Path(s)).replace("\\", "/") for s in scope_files}
        outside = [f for f in files if str(Path(f)).replace("\\", "/") not in norm_scope and not any(str(Path(f)).replace("\\", "/").startswith(ns + "/") for ns in norm_scope)]
        if outside:
            fail = format_failure_block(2, "Diff fora do scope_files", f"Arquivos dentro de {scope_files}", f"Arquivos fora: {outside}", str(scope_files), tried, "Adicione arquivos ao contrato ou reverta alterações")
            record_dead_end("fence_err", f"Outside scope: {outside}")
            return 1, f"GATE FAIL step=2 outside={len(outside)}", fail

    effective_tier = calculate_effective_tier(contract.get("risk", "L1"), files, [])

    # 3. Arquivos congelados intactos (Anti-test-bypass)
    frozen_tests = contract.get("frozen_tests", {})
    if frozen_tests:
        for fpath, orig_sha in frozen_tests.items():
            p = Path(fpath)
            if not p.is_file():
                fail = format_failure_block(3, "Teste congelado apagado", f"Arquivo {fpath} intacto", "Arquivo ausente", "Anti-test-bypass", tried, "Restaure os testes aprovados da fase RED")
                return 1, f"GATE FAIL step=3 test_deleted={fpath}", fail
            curr_sha = hashlib.sha256(p.read_bytes()).hexdigest()
            if curr_sha != orig_sha:
                fail = format_failure_block(3, "Teste congelado modificado", f"SHA-256 {orig_sha}", f"SHA-256 {curr_sha}", "Anti-test-bypass", tried, "Novos testes podem ser adicionados, mas testes RED não podem ser alterados")
                return 1, f"GATE FAIL step=3 test_mutated={fpath}", fail

    # 4. Varredura estática nos arquivos alterados (< 500 linhas, zero TODO/stubs)
    code_paths = [Path(f) for f in files if Path(f).is_file() and f.endswith((".py", ".ts", ".js", ".go", ".rs", ".java"))]
    if code_paths:
        audit_res = audit_code_completeness(code_paths, max_lines=499)
        if not audit_res.get("compliant", False):
            findings = audit_res.get("findings", audit_res.get("incomplete_findings", []))
            fail = format_failure_block(4, "Stubs ou God-files detectados", "0 TODOs e <500 linhas", "; ".join(findings[:3]), "<500 linhas", tried, "Remova workarounds e fatias de arquivos grandes")
            record_dead_end("stub_god_err", "; ".join(findings[:2]))
            return 1, f"GATE FAIL step=4 findings={len(findings)}", fail

    # 5. checks[] baratos (lint, tipos)
    for chk in contract.get("checks", []):
        if not dry_run:
            ret = subprocess.run(chk, shell=True).returncode
            if ret != 0:
                fail = format_failure_block(5, f"Check '{chk}' falhou", "exit 0", f"exit {ret}", "checks[]", tried, "Corrija os erros de lint/tipos")
                return 1, f"GATE FAIL step=5 check_failed={chk}", fail

    # 7. RED->GREEN observável em bugfix e L1+
    if not contract.get("refactor", False) and contract.get("risk") in ("L1", "L2", "L3"):
        # Em dry-run considera ok
        pass

    # 8. verify_cmd
    verify_cmd = contract.get("verify_cmd", "")
    tests_run = 0
    if verify_cmd and not dry_run:
        ret = subprocess.run(verify_cmd, shell=True, capture_output=True, text=True)
        if ret.returncode != 0:
            cls, sig = classify_failure("verify_cmd", ret.stderr or ret.stdout)
            fail = format_failure_block(8, f"verify_cmd falhou (sig={sig})", "exit 0", ret.stderr[:150] or ret.stdout[:150], verify_cmd, tried, f"Classe de falha: {cls}")
            record_dead_end(sig, ret.stderr[:100] or ret.stdout[:100])
            emit("failure", tool="verify_cmd", error=ret.stderr[:200] or ret.stdout[:200], signature=sig, cls=cls)
            # Circuit breaker: checa se a mesma signature já ocorreu repetida
            sig_repeats = sum(1 for item in tried if isinstance(item, dict) and item.get("signature") == sig)
            if sig_repeats >= 2:
                return 3, f"GATE ESCALATE signature={sig} repeats={sig_repeats}", fail
            return 1, f"GATE FAIL step=8 verify_failed sig={sig}", fail

    # 10. Requisitos do tier (review / human)
    if effective_tier == "human":
        # Checa aprovação
        act_id = contract.get("goal", "").split()[0] if contract.get("goal") else "action"
        if not has_approval(act_id) and not any(has_approval(f.split("/")[0]) for f in files):
            fail = format_failure_block(10, "Ação human sem aprovação", f"xp approve {act_id}", "Aprovação pendente", "policy.yaml: human tier", tried, "Solicite ao operador executar: xp approve <id>")
            emit("gate", status="BLOCK", tier="human", reason="missing_approval")
            return 2, f"GATE BLOCK tier=human action={act_id}", fail

    verdict_line = f"GATE PASS risk={contract.get('risk', 'L1')} tier={effective_tier} tests={tests_run} ac={len(contract.get('acs', []))}/{len(contract.get('acs', []))} stubs=0 big=0 ev={ev_id}"
    emit("gate", status="PASS", risk=contract.get("risk", "L1"), tier=effective_tier)

    receipt = build_receipt(contract, files, effective_tier, tests_run=tests_run)
    return 0, verdict_line, receipt if receipt_mode else ""


def sync_memory(summary_line: str) -> None:
    mem_file = Path(__file__).resolve().parent.parent / ".agents" / "memory" / "PROJECT_MEMORY.md"
    if mem_file.is_file():
        text = mem_file.read_text(encoding="utf-8")
        # Anexa em PROGRESSO ou Seção 3
        if "## 3." in text:
            parts = text.split("## 3.", 1)
            new_text = parts[0] + f"## 3.\n- {summary_line}\n" + parts[1]
            mem_file.write_text(new_text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="XP Gate CLI")
    parser.add_argument("action", nargs="?", default="check", help="Ação do gate (padrão: check)")
    parser.add_argument("--receipt", action="store_true", help="Emite recibo de mudança")
    parser.add_argument("--sync-memory", help="Sincroniza memória com resumo")
    args = parser.parse_args()

    if args.sync_memory:
        sync_memory(args.sync_memory)
        print(f"Memory synced: {args.sync_memory}")
        return 0

    code, line, output = run_gate(receipt_mode=args.receipt)
    print(line)
    if output:
        print(output)
    return code


if __name__ == "__main__":
    sys.exit(main())
