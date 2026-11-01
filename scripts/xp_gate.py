#!/usr/bin/env python3
"""scripts/xp_gate.py — Gate determinístico barato-primeiro do XP Kit (AC-3)
10 degraus executados em ordem estrita de custo; para na primeira falha.
Limite estrito: <= 320 linhas.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.evidence_recorder import load_entries, parse_test_summary, record
from scripts.goldfish_review import audit_code_completeness
from scripts.hooks.pre_tool_guard import (
    calculate_effective_tier,
    compute_action_id,
    evaluate_policy_for_files_and_commands,
    has_approval,
    load_reviews,
    record_review,
)
from scripts.kit_events import classify_failure, emit
from scripts.xp_contract import load_contract, record_dead_end


def get_git_diff_files() -> List[str]:
    for target in ("HEAD", ""):
        args = ["git", "diff", "--name-only"] + ([target] if target else [])
        res = subprocess.run(args, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return [line.strip() for line in res.stdout.splitlines() if line.strip()]
    return []


def get_git_diff_hash() -> str:
    for target in ("HEAD", ""):
        args = ["git", "diff"] + ([target] if target else [])
        res = subprocess.run(args, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout:
            return hashlib.sha256(res.stdout.encode("utf-8")).hexdigest()[:16]
    return ""


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


def build_receipt(contract: Dict[str, Any], changed_files: List[str], tier: str, tests_run: Any = "?") -> str:
    lines = [
        f"OBJETIVO: {contract.get('goal', 'Sem objetivo')}",
        f"ALTERADO: {len(changed_files)} arquivo(s) ({', '.join(changed_files[:3])}{'...' if len(changed_files) > 3 else ''})",
        f"VERIFICADO: tests={tests_run}",
        "NÃO VERIFICADO: Nenhuma checagem pendente",
        f"DECISÕES: Padrão arquitetural aplicado com contrato {contract.get('risk', 'L1')}",
        f"RISCOS: Tier efetivo {tier}",
        f"APROVAÇÃO NECESSÁRIA: {'Nenhuma (auto/review)' if tier != 'human' else 'Aprovação humana obrigatória via xp approve'}",
    ]
    return "\n".join(lines)


def run_gate(dry_run: bool = False, changed_files: Optional[List[str]] = None, receipt_mode: bool = False) -> Tuple[int, str, str]:
    contract = load_contract()
    files = changed_files if changed_files is not None else get_git_diff_files()
    tried = contract.get("tried", []) if contract else []
    ev_id = f"EV-{int(time.time())}"

    # 1. Contrato existe e é válido
    if not contract or not contract.get("goal"):
        fail = format_failure_block(1, "Contrato inválido", "goal e risk preenchidos", "Contrato vazio ou sem meta", "run.json", tried, "Execute 'xp contract init'")
        return 1, "GATE FAIL step=1 reason=invalid_contract", fail

    risk = contract.get("risk", "L1")

    # 2. Cerca de escopo
    scope_files = contract.get("scope_files", [])
    if scope_files and files:
        norm_scope = {str(Path(s)).replace("\\", "/") for s in scope_files}
        outside = [f for f in files if str(Path(f)).replace("\\", "/") not in norm_scope and not any(str(Path(f)).replace("\\", "/").startswith(ns + "/") for ns in norm_scope)]
        if outside:
            fail = format_failure_block(2, "Diff fora do scope_files", f"Arquivos dentro de {scope_files}", f"Arquivos fora: {outside}", str(scope_files), tried, "Adicione arquivos ao contrato ou reverta alterações")
            record_dead_end("fence_err", f"Outside scope: {outside}")
            return 1, f"GATE FAIL step=2 outside={len(outside)}", fail

    effective_tier = calculate_effective_tier(risk, files, [])

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
    stubs_count = 0
    big_count = 0
    if code_paths:
        audit_res = audit_code_completeness(code_paths, max_lines=499)
        findings = audit_res.get("findings", audit_res.get("incomplete_findings", []))
        stubs_count = sum(1 for f in findings if "TODO" in f or "Stub" in f or "Workaround" in f)
        big_count = sum(1 for f in findings if "No-God-Files" in f or "excede" in f)
        if not audit_res.get("compliant", False):
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

    # 10. Requisitos do tier (review / human)
    if effective_tier == "human":
        _, _, human_matches = evaluate_policy_for_files_and_commands(files, [])
        act_id = compute_action_id("human", human_matches or files)
        if not has_approval(act_id):
            fail = format_failure_block(10, f"Ação human sem aprovação (action={act_id})", f"xp approve {act_id}", "Aprovação pendente", "policy.yaml: human tier", tried, f"Solicite ao operador executar: xp approve {act_id}")
            emit("gate", status="BLOCK", tier="human", reason="missing_approval")
            return 2, f"GATE BLOCK tier=human action={act_id}", fail

    if effective_tier == "review":
        reviews = load_reviews()
        curr_diff_hash = get_git_diff_hash()
        approved = any(
            r.get("verdict") == "approve"
            and r.get("diff_hash") == curr_diff_hash
            and r.get("reviewer", "").lower() != "builder"
            for r in reviews
        )
        if not approved:
            fail = format_failure_block(10, "Tier review requer registro de aprovação de revisor", "xp review record --reviewer <nome> --verdict approve", "Nenhum registro de revisão para o diff atual", "policy.yaml: review tier", tried, "Execute: xp review record --reviewer <nome> --verdict approve (convenção)")
            emit("gate", status="BLOCK", tier="review", reason="missing_review")
            return 2, "GATE BLOCK tier=review reason=missing_review", fail

    # 9. Conformidade AC->teste (ordem barata antes da execução)
    acs = contract.get("acs", [])
    ac_declared = len(acs)
    ac_tracked = 0
    if acs:
        from scripts.conformance_report import index_tests
        test_roots = [Path("tests")] if Path("tests").is_dir() else [Path(".")]
        mapping = index_tests(test_roots)
        missing_acs = [ac for ac in acs if not mapping.get(ac)]
        ac_tracked = ac_declared - len(missing_acs)
        if missing_acs:
            fail = format_failure_block(9, f"ACs sem testes: {', '.join(missing_acs)}", "Todos os ACs referenciados em testes", f"Critérios não rastreados: {missing_acs}", "conformance_report", tried, "Adicione testes referenciando os ACs")
            return 1, f"GATE FAIL step=9 missing_acs={len(missing_acs)}", fail

    # 8. verify_cmd
    verify_cmd = contract.get("verify_cmd", "")
    tests_run: Any = "?"
    verify_status = "not_run"
    if risk in ("L1", "L2", "L3") and not verify_cmd and not dry_run:
        fail = format_failure_block(8, "verify_cmd obrigatório em L1+", "verify_cmd configurado no contrato", "verify_cmd vazio", "run.json", tried, "Configure verify_cmd no contrato")
        return 1, "GATE FAIL step=8 reason=missing_verify_cmd", fail

    if verify_cmd and not dry_run:
        ret = subprocess.run(verify_cmd, shell=True, capture_output=True, text=True)
        counts = parse_test_summary(ret.stdout + ret.stderr)
        if counts["total"] > 0:
            tests_run = counts["total"]
        if ret.returncode != 0:
            verify_status = "fail"
            cls, sig = classify_failure("verify_cmd", ret.stderr or ret.stdout)
            record_dead_end(sig, ret.stderr[:100] or ret.stdout[:100])
            contract = load_contract()
            tried = contract.get("tried", [])
            fail = format_failure_block(8, f"verify_cmd falhou (sig={sig})", "exit 0", ret.stderr[:150] or ret.stdout[:150], verify_cmd, tried, f"Classe de falha: {cls}")
            emit("failure", tool="verify_cmd", error=ret.stderr[:200] or ret.stdout[:200], signature=sig, cls=cls)
            sig_repeats = sum(item.get("count", 1) for item in tried if isinstance(item, dict) and item.get("signature") == sig)
            if sig_repeats >= 2 or len(tried) >= contract.get("max_attempts", 3):
                return 3, f"GATE ESCALATE signature={sig} repeats={sig_repeats}", fail
            return 1, f"GATE FAIL step=8 verify_failed sig={sig}", fail
        verify_status = "pass"

    # 6. Frescor da evidência
    evidence_entries = load_entries()
    pass_entries = [e for e in evidence_entries if e.get("exit_code") == 0 or e.get("status") == "PASS"]
    if pass_entries and not dry_run:
        last_pass = pass_entries[-1]
        last_ts = last_pass.get("ts", 0)
        last_hash = last_pass.get("diff_hash", "")
        curr_hash = get_git_diff_hash()
        files_to_check = files or contract.get("scope_files", [])
        stale = False
        for f in files_to_check:
            fp = Path(f)
            if fp.is_file() and fp.stat().st_mtime > last_ts and curr_hash != last_hash:
                stale = True
                break
        if stale:
            fail = format_failure_block(6, "Evidência obsoleta", "Execução após última modificação dos arquivos", "Arquivos alterados após evidência aprovada", "Evidence freshness", tried, "Execute 'xp gate record -- <cmd>' novamente")
            return 1, "GATE FAIL step=6 reason=stale_evidence", fail

    # 7. RED->GREEN observável em bugfix e L1+
    if not contract.get("refactor", False) and risk in ("L1", "L2", "L3") and not dry_run:
        red_found = any(e.get("exit_code") != 0 or e.get("status") == "FAIL" for e in evidence_entries)
        green_found = any(e.get("exit_code") == 0 or e.get("status") == "PASS" for e in evidence_entries)
        if not (red_found and green_found):
            fail = format_failure_block(7, "Ciclo RED->GREEN não comprovado", "Execução RED registrada antes de GREEN", "Nenhuma execução RED registrada", "RED->GREEN cycle", tried, "Execute e registre o teste falhando com 'xp gate record -- <cmd>' antes de fazê-lo passar")
            return 1, "GATE FAIL step=7 reason=missing_red_evidence", fail

    if pass_entries:
        ev_id = f"EV-{pass_entries[-1].get('log_sha256', ev_id)}"

    verdict_line = f"GATE PASS risk={risk} tier={effective_tier} verify={verify_status} tests={tests_run} ac={ac_tracked}/{ac_declared} stubs={stubs_count} big={big_count} ev={ev_id}"
    emit("gate", status="PASS", risk=risk, tier=effective_tier)

    receipt = build_receipt(contract, files, effective_tier, tests_run=tests_run)
    return 0, verdict_line, receipt if receipt_mode else ""


def sync_memory(summary_line: str, root_dir: Optional[Path] = None) -> bool:
    root = root_dir or Path.cwd()
    mem_file = root / ".agents" / "memory" / "PROJECT_MEMORY.md"
    if not mem_file.is_file():
        mem_file = Path(__file__).resolve().parent.parent / ".agents" / "memory" / "PROJECT_MEMORY.md"
    if not mem_file.is_file():
        print(f"❌ Arquivo de memória não encontrado: {mem_file}", file=sys.stderr)
        return False

    text = mem_file.read_text(encoding="utf-8")
    header_pattern = re.compile(r"^(##\s+3\.[^\n]*)$", re.MULTILINE)
    match = header_pattern.search(text)
    if not match:
        print("❌ Seção 3 não encontrada no arquivo de memória", file=sys.stderr)
        return False

    end_of_header = match.end()
    new_text = text[:end_of_header] + f"\n- {summary_line}" + text[end_of_header:]
    mem_file.write_text(new_text, encoding="utf-8")

    from scripts.memory_archiver import archive_memory
    hist_file = mem_file.parent / "archive" / "HISTORY.md"
    archive_memory(mem_file, history_path=hist_file, max_bytes=3000)

    final_size = mem_file.stat().st_size
    if final_size > 3000:
        print(f"❌ Memória excede o orçamento após rotação ({final_size} B > 3000 B)", file=sys.stderr)
        return False
    return True


def record_execution(command: str) -> int:
    contract = load_contract()
    risk = contract.get("risk", "L1") if contract else "L1"
    proc = subprocess.run(command, shell=True, capture_output=True, text=True)
    diff_hash = get_git_diff_hash()
    entry = record(command, proc.returncode, output=proc.stdout + proc.stderr, risk_level=risk, diff_hash=diff_hash)
    print(f"[gate-record] {entry['status']} (exit={proc.returncode}) diff={diff_hash[:8]} | {entry['summary']}")
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="XP Gate CLI")
    parser.add_argument("action", nargs="?", default="check", help="Ação do gate (check|record)")
    parser.add_argument("--receipt", action="store_true", help="Emite recibo de mudança")
    parser.add_argument("--sync-memory", help="Sincroniza memória com resumo")
    parser.add_argument("cmd_args", nargs="*", help="Comando para ação record")
    args, extra = parser.parse_known_args()
    all_cmd = args.cmd_args + extra

    if args.sync_memory:
        ok = sync_memory(args.sync_memory)
        if ok:
            print(f"Memory synced: {args.sync_memory}")
            return 0
        return 1

    if args.action == "review":
        rev = all_cmd[all_cmd.index("--reviewer") + 1] if "--reviewer" in all_cmd else "reviewer"
        verd = all_cmd[all_cmd.index("--verdict") + 1] if "--verdict" in all_cmd else "approve"
        diff_h = get_git_diff_hash()
        record_review(rev, verd, diff_h)
        print(f"[review-record] {rev} -> {verd} (diff={diff_h[:8]})")
        return 0

    if args.action == "record":
        cmd = " ".join(all_cmd).strip()
        if not cmd:
            print("❌ Comando não fornecido para 'xp gate record -- <comando>'", file=sys.stderr)
            return 1
        return record_execution(cmd)

    code, line, output = run_gate(receipt_mode=args.receipt)
    print(line)
    if output:
        print(output)
    return code


if __name__ == "__main__":
    sys.exit(main())
