#!/usr/bin/env python3
"""scripts/xp_gate.py — Gate determinístico barato-primeiro do XP Kit (AC-3); <= 300 linhas."""
from __future__ import annotations

import argparse
import hashlib
import json
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

def git(args: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, capture_output=True, text=True)

def get_git_diff_files() -> List[str]:
    for target in ("HEAD", ""):
        res = git(["diff", "--name-only"] + ([target] if target else []))
        if res.returncode == 0 and res.stdout.strip():
            return [l.strip() for l in res.stdout.splitlines() if l.strip()]
    return []

def get_git_untracked_files() -> List[str]:
    res = git(["ls-files", "--others", "--exclude-standard"])
    if res.returncode == 0:
        return [l.strip() for l in res.stdout.splitlines() if l.strip()]
    return []

def get_git_diff_hash() -> str:
    for target in ("HEAD", ""):
        res = git(["diff"] + ([target] if target else []))
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

def build_receipt(
    contract: Dict[str, Any],
    changed_files: List[str],
    tier: str,
    tests_run: Any = "?",
    verify_status: str = "not_run",
    ac_tracked: int = 0,
    ac_declared: int = 0,
) -> str:
    verified = tests_run != "?" and verify_status == "pass"
    v_label = f"{tests_run} teste(s) aprovado(s)" if verified else "não verificado"
    missing = ac_declared - ac_tracked
    nv_label = f"{missing} AC(s) sem teste" if ac_declared else "sem ACs declarados"
    lines = [
        f"OBJETIVO: {contract.get('goal', 'Sem objetivo')}",
        f"ALTERADO: {len(changed_files)} arquivo(s) ({', '.join(changed_files[:3])}{'...' if len(changed_files) > 3 else ''})",
        f"VERIFICADO: {v_label}",
        f"NÃO VERIFICADO: {nv_label}",
        f"RASTREADOS: {ac_tracked}/{ac_declared} ACs",
        f"DECISÕES: Padrão arquitetural aplicado com contrato {contract.get('risk', 'L1')}",
        f"RISCOS: Tier efetivo {tier}",
        f"APROVAÇÃO NECESSÁRIA: {'Nenhuma (auto/review)' if tier != 'human' else 'Aprovação humana obrigatória via xp approve'}",
    ]
    return "\n".join(lines)

def _fail(step, failed, expected, saw, fence, tried, hint):
    return format_failure_block(step, failed, expected, saw, fence, tried, hint)

def run_gate(dry_run: bool = False, changed_files: Optional[List[str]] = None, receipt_mode: bool = False) -> Tuple[int, str, str]:
    contract = load_contract()
    if changed_files is not None:
        files = changed_files
    else:
        files = list(dict.fromkeys(get_git_diff_files() + get_git_untracked_files()))
    tried = contract.get("tried", []) if contract else []
    ev_id = f"EV-{int(time.time())}"
    if not contract or not contract.get("goal"):
        fail = _fail(1, "Contrato inválido", "goal e risk preenchidos", "Contrato vazio ou sem meta", "run.json", tried, "Execute 'xp contract init'")
        return 1, "GATE FAIL step=1 reason=invalid_contract", fail
    risk = contract.get("risk", "L1")
    verify_cmd = contract.get("verify_cmd", "")
    tests_run: Any = "?"
    verify_status = "not_run"
    acs = contract.get("acs", [])
    ac_declared = len(acs)
    ac_tracked = 0
    scope_files = contract.get("scope_files", [])
    if scope_files and files:
        norm_scope = {str(Path(s)).replace("\\", "/") for s in scope_files}
        outside = [f for f in files if str(Path(f)).replace("\\", "/") not in norm_scope and not any(str(Path(f)).replace("\\", "/").startswith(ns + "/") for ns in norm_scope)]
        if outside:
            fail = _fail(2, "Diff fora do scope_files", f"Arquivos dentro de {scope_files}", f"Arquivos fora: {outside}", str(scope_files), tried, "Adicione arquivos ao contrato ou reverta alterações")
            record_dead_end("fence_err", f"Outside scope: {outside}")
            return 1, f"GATE FAIL step=2 outside={len(outside)}", fail
    effective_tier = calculate_effective_tier(risk, files, [])
    frozen_tests = contract.get("frozen_tests", {})
    if frozen_tests:
        for fpath, orig_sha in frozen_tests.items():
            p = Path(fpath)
            if not p.is_file():
                fail = _fail(3, "Teste congelado apagado", f"Arquivo {fpath} intacto", "Arquivo ausente", "Anti-test-bypass", tried, "Restaure os testes aprovados da fase RED")
                return 1, f"GATE FAIL step=3 test_deleted={fpath}", fail
            if hashlib.sha256(p.read_bytes()).hexdigest() != orig_sha:
                fail = _fail(3, "Teste congelado modificado", f"SHA-256 {orig_sha}", "SHA-256 divergente", "Anti-test-bypass", tried, "Testes RED não podem ser alterados")
                return 1, f"GATE FAIL step=3 test_mutated={fpath}", fail

    code_paths = [Path(f) for f in files if Path(f).is_file() and f.endswith((".py", ".ts", ".js", ".go", ".rs", ".java"))]
    stubs_count = big_count = 0
    if code_paths:
        audit_res = audit_code_completeness(code_paths, max_lines=499)
        findings = audit_res.get("findings", audit_res.get("incomplete_findings", []))
        stubs_count = sum(1 for f in findings if "TODO" in f or "Stub" in f or "Workaround" in f)
        big_count = sum(1 for f in findings if "No-God-Files" in f or "excede" in f)
        if not audit_res.get("compliant", False):
            fail = _fail(4, "Stubs ou God-files detectados", "0 TODOs e <500 linhas", "; ".join(findings[:3]), "<500 linhas", tried, "Remova workarounds e fatias de arquivos grandes")
            record_dead_end("stub_god_err", "; ".join(findings[:2]))
            return 1, f"GATE FAIL step=4 findings={len(findings)}", fail

    for chk in contract.get("checks", []):
        if not dry_run and subprocess.run(chk, shell=True).returncode != 0:
            fail = _fail(5, f"Check '{chk}' falhou", "exit 0", f"exit {subprocess.run(chk, shell=True).returncode}", "checks[]", tried, "Corrija os erros de lint/tipos")
            return 1, f"GATE FAIL step=5 check_failed={chk}", fail

    evidence_entries = load_entries()
    pass_entries = [e for e in evidence_entries if e.get("exit_code") == 0 or e.get("status") == "PASS"]
    if pass_entries and not dry_run:
        last_pass = pass_entries[-1]
        last_ts = last_pass.get("ts", 0)
        last_hash = last_pass.get("diff_hash", "")
        curr_hash = get_git_diff_hash()
        stale = any(
            Path(f).is_file() and Path(f).stat().st_mtime > last_ts and curr_hash != last_hash
            for f in (files or contract.get("scope_files", []))
        )
        if stale:
            fail = _fail(6, "Evidência obsoleta", "Execução após última modificação dos arquivos", "Arquivos alterados após evidência aprovada", "Evidence freshness", tried, "Execute 'xp gate record -- <cmd>' novamente")
            return 1, "GATE FAIL step=6 reason=stale_evidence", fail

    if not contract.get("refactor", False) and risk in ("L1", "L2", "L3") and not dry_run:
        red_seen = green_ok = False
        for e in sorted(evidence_entries, key=lambda x: x.get("ts", 0)):
            is_fail = e.get("exit_code", 1) != 0 or e.get("status") == "FAIL"
            is_pass = e.get("exit_code") == 0 and e.get("status") != "FAIL"
            if is_fail:
                red_seen = True
                green_ok = False
            elif is_pass:
                if not red_seen:
                    fail = _fail(7, "GREEN antes de RED", "RED registrado antes de GREEN", "Execução GREEN sem RED anterior", "RED->GREEN cycle", tried, "Registre o teste falhando com 'xp gate record -- <cmd>' antes de fazê-lo passar")
                    return 1, "GATE FAIL step=7 reason=green_before_red", fail
                green_ok = True
        if not green_ok:
            fail = _fail(7, "Ciclo RED->GREEN não comprovado", "Execução RED registrada antes de GREEN", "Nenhuma execução RED->GREEN válida", "RED->GREEN cycle", tried, "Execute o teste falhando com 'xp gate record -- <cmd>' antes de fazê-lo passar")
            return 1, "GATE FAIL step=7 reason=missing_red_evidence", fail

    if risk in ("L1", "L2", "L3") and not verify_cmd and not dry_run:
        fail = _fail(8, "verify_cmd obrigatório em L1+", "verify_cmd configurado no contrato", "verify_cmd vazio", "run.json", tried, "Configure verify_cmd no contrato")
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
            fail = _fail(8, f"verify_cmd falhou (sig={sig})", "exit 0", ret.stderr[:150] or ret.stdout[:150], verify_cmd, tried, f"Classe de falha: {cls}")
            emit("failure", tool="verify_cmd", error=ret.stderr[:200] or ret.stdout[:200], signature=sig, cls=cls)
            sig_repeats = sum(item.get("count", 1) for item in tried if isinstance(item, dict) and item.get("signature") == sig)
            if sig_repeats >= 2 or len(tried) >= contract.get("max_attempts", 3):
                return 3, f"GATE ESCALATE signature={sig} repeats={sig_repeats}", fail
            return 1, f"GATE FAIL step=8 verify_failed sig={sig}", fail
        verify_status = "pass"

    if acs:
        from scripts.conformance_report import index_tests
        test_roots = [Path("tests")] if Path("tests").is_dir() else [Path(".")]
        mapping = index_tests(test_roots)
        missing_acs = [ac for ac in acs if not mapping.get(ac)]
        ac_tracked = ac_declared - len(missing_acs)
        if missing_acs:
            fail = _fail(9, f"ACs sem testes: {', '.join(missing_acs)}", "Todos os ACs referenciados em testes", f"Critérios não rastreados: {missing_acs}", "conformance_report", tried, "Adicione testes referenciando os ACs")
            return 1, f"GATE FAIL step=9 missing_acs={len(missing_acs)}", fail

    if effective_tier == "human":
        _, _, human_matches = evaluate_policy_for_files_and_commands(files, [])
        act_id = compute_action_id("human", human_matches or files)
        if not has_approval(act_id):
            fail = _fail(10, f"Ação human sem aprovação (action={act_id})", f"xp approve {act_id}", "Aprovação pendente", "policy.yaml: human tier", tried, f"Solicite ao operador executar: xp approve {act_id}")
            emit("gate", status="BLOCK", tier="human", reason="missing_approval")
            return 2, f"GATE BLOCK tier=human action={act_id}", fail

    if effective_tier == "review":
        reviews = load_reviews()
        curr_diff_hash = get_git_diff_hash()
        approved = any(r.get("verdict") == "approve" and r.get("diff_hash") == curr_diff_hash and r.get("reviewer", "").lower() != "builder" for r in reviews)
        if not approved:
            fail = _fail(10, "Tier review requer registro de aprovação de revisor", "xp review record --reviewer <nome> --verdict approve", "Nenhum registro de revisão para o diff atual", "policy.yaml: review tier", tried, "Execute: xp review record --reviewer <nome> --verdict approve (convenção)")
            emit("gate", status="BLOCK", tier="review", reason="missing_review")
            return 2, "GATE BLOCK tier=review reason=missing_review", fail

    if pass_entries:
        ev_id = f"EV-{pass_entries[-1].get('log_sha256', ev_id)}"

    verdict_line = f"GATE PASS risk={risk} tier={effective_tier} verify={verify_status} tests={tests_run} ac={ac_tracked}/{ac_declared} stubs={stubs_count} big={big_count} ev={ev_id}"
    emit("gate", status="PASS", risk=risk, tier=effective_tier)

    receipt = build_receipt(contract, files, effective_tier, tests_run=tests_run, verify_status=verify_status, ac_tracked=ac_tracked, ac_declared=ac_declared)
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
    match = re.compile(r"^(##\s+3\.[^\n]*)$", re.MULTILINE).search(text)
    if not match:
        print("❌ Seção 3 não encontrada no arquivo de memória", file=sys.stderr)
        return False
    mem_file.write_text(text[: match.end()] + f"\n- {summary_line}" + text[match.end():], encoding="utf-8")
    from scripts.memory_archiver import archive_memory
    archive_memory(mem_file, history_path=mem_file.parent / "archive" / "HISTORY.md", max_bytes=3000)
    if mem_file.stat().st_size > 3000:
        print(f"❌ Memória excede o orçamento após rotação", file=sys.stderr)
        return False
    return True

def record_execution(command: str) -> int:
    contract = load_contract()
    risk = contract.get("risk", "L1") if contract else "L1"
    proc = subprocess.run(command, shell=True, capture_output=True, text=True)
    entry = record(command, proc.returncode, output=proc.stdout + proc.stderr, risk_level=risk, diff_hash=get_git_diff_hash())
    print(f"[gate-record] {entry['status']} (exit={proc.returncode}) diff={entry['diff_hash'][:8]} | {entry['summary']}")
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
        record_review(rev, verd, get_git_diff_hash())
        print(f"[review-record] {rev} -> {verd} (diff={get_git_diff_hash()[:8]})")
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
