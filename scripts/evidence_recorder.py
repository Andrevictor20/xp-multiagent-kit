#!/usr/bin/env python3
"""
scripts/evidence_recorder.py
Registro estruturado de evidência de execução (E1).

Problema resolvido: a política de evidência exigia colar o output NATIVO dos
testes em walkthrough.md. Esse texto era relido por outros agentes e por
sessões seguintes, multiplicando o custo. A auditabilidade é preservada
gravando o log completo em disco e referenciando apenas o resumo no documento.

Uso:
    agy-evidence record --command "pytest tests/test_x.py" --exit-code 0 \
        --log-file /tmp/out.log --risk L1 --summary "3 passed"
    agy-evidence render            # markdown para colar em walkthrough.md
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kit_constants import runtime_dir  # noqa: E402

EVIDENCE_DIR = "evidence"
INDEX_FILE = "index.jsonl"

PASS_PATTERN = re.compile(r"(\d+)\s+passed", re.IGNORECASE)
FAIL_PATTERN = re.compile(r"(\d+)\s+(?:failed|errors?)", re.IGNORECASE)
OK_PATTERN = re.compile(r"^OK(?:\s|$)", re.MULTILINE)
UNITTEST_PATTERN = re.compile(r"Ran\s+(\d+)\s+tests?")


def parse_test_summary(output: str) -> Dict[str, int]:
    """Extrai contagens de testes do output sem preservar o log inteiro."""
    passed = 0
    failed = 0
    total = 0

    match = PASS_PATTERN.search(output)
    if match:
        passed = int(match.group(1))
    match = FAIL_PATTERN.search(output)
    if match:
        failed = int(match.group(1))

    unittest_match = UNITTEST_PATTERN.search(output)
    if unittest_match:
        total = int(unittest_match.group(1))
        if OK_PATTERN.search(output):
            passed = total
            failed = 0

    if not total:
        total = passed + failed
    return {"total": total, "passed": passed, "failed": failed}


def store_log(command: str, output: str, exit_code: int) -> Path:
    """Grava o log completo fora do contexto e devolve o caminho de referência."""
    directory = runtime_dir() / EVIDENCE_DIR
    directory.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(f"{command}{time.time()}".encode("utf-8")).hexdigest()[:12]
    log_path = directory / f"{digest}.log"
    log_path.write_text(output, encoding="utf-8")
    return log_path


def record(
    command: str,
    exit_code: int,
    output: Optional[str] = None,
    log_file: Optional[Path] = None,
    risk_level: str = "L1",
    summary: str = "",
) -> Dict[str, Any]:
    """Registra uma evidência e devolve o resumo estruturado."""
    if output is None and log_file:
        output = Path(log_file).read_text(encoding="utf-8", errors="ignore")
    output = output or ""

    stored = store_log(command, output, exit_code)
    counts = parse_test_summary(output)

    entry = {
        "ts": round(time.time(), 3),
        "command": command,
        "exit_code": exit_code,
        "risk_level": risk_level,
        "status": "PASS" if exit_code == 0 and counts["failed"] == 0 else "FAIL",
        "summary": summary or f"{counts['passed']}/{counts['total']} testes aprovados",
        "tests": counts,
        "log_path": str(stored),
        "log_sha256": hashlib.sha256(output.encode("utf-8", errors="ignore")).hexdigest()[:16],
        "log_bytes": len(output),
    }

    index_path = runtime_dir() / EVIDENCE_DIR / INDEX_FILE
    with index_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def load_entries() -> list:
    index_path = runtime_dir() / EVIDENCE_DIR / INDEX_FILE
    if not index_path.is_file():
        return []
    entries = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def render_markdown(entries: Optional[list] = None) -> str:
    """
    Gera o bloco de evidência para walkthrough.md: resumo + ponteiro para o log.
    Nenhum output bruto entra no documento (e, portanto, no contexto).
    """
    entries = entries if entries is not None else load_entries()
    if not entries:
        return "_Nenhuma evidência registrada._\n"

    lines = [
        "| # | Comando | Exit | Status | Testes | Log (fora do contexto) |",
        "|---|---------|------|--------|--------|------------------------|",
    ]
    for i, entry in enumerate(entries, start=1):
        counts = entry.get("tests", {})
        lines.append(
            f"| {i} | `{entry['command']}` | {entry['exit_code']} | {entry['status']} | "
            f"{counts.get('passed', 0)}/{counts.get('total', 0)} | "
            f"`{entry['log_path']}` (`{entry['log_sha256']}`) |"
        )
    return "\n".join(lines) + "\n"


def run_and_record(command: str, risk_level: str = "L1") -> int:
    """Executa o comando, registra a evidência e devolve o exit code real."""
    proc = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    entry = record(command, proc.returncode, output=proc.stdout, risk_level=risk_level)
    tail = "\n".join((proc.stdout or "").splitlines()[-5:])
    print(f"[evidence] {entry['status']} | {entry['summary']} | log: {entry['log_path']}")
    if entry["status"] == "FAIL" and tail:
        print(tail)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Evidência estruturada de execução (E1)")
    sub = parser.add_subparsers(dest="action", required=True)

    rec = sub.add_parser("record", help="Registra evidência de um comando já executado")
    rec.add_argument("--command", required=True)
    rec.add_argument("--exit-code", type=int, required=True)
    rec.add_argument("--log-file")
    rec.add_argument("--risk", default="L1")
    rec.add_argument("--summary", default="")

    run = sub.add_parser("run", help="Executa o comando e registra a evidência")
    run.add_argument("command")
    run.add_argument("--risk", default="L1")

    sub.add_parser("render", help="Emite o bloco markdown para walkthrough.md")

    args = parser.parse_args()

    if args.action == "record":
        entry = record(args.command, args.exit_code, log_file=args.log_file,
                       risk_level=args.risk, summary=args.summary)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return 0

    if args.action == "run":
        return run_and_record(args.command, args.risk)

    sys.stdout.write(render_markdown())
    return 0


if __name__ == "__main__":
    sys.exit(main())
