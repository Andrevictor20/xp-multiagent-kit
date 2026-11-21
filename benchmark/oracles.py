"""Ground-truth oracles for the XP kit benchmark.

Each oracle inspects a sandbox repository WITHOUT calling the kit's gate or
hook. The oracle decides whether the change is defective; the arms under test
then independently decide whether to block it. This separation keeps the
"detection rate" from being circular.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

SECRET_PATTERNS = (
    re.compile(r"sk_live_[0-9a-zA-Z]{8,}"),
    re.compile(r"sk_test_[0-9a-zA-Z]{8,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[0-9a-zA-Z]{20,}"),
    re.compile(r"(?i)\b[Aa][Pp][Ii][_\-]?[Kk][Ee][Yy]\b\s*[:=]\s*['\"][0-9a-zA-Z\-_]{16,}['\"]"),
)


def _run(repo: Path, cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True)


def changed_paths(repo: Path) -> List[str]:
    """Return every path touched relative to HEAD (modifications + untracked)."""
    out = _run(repo, ["git", "status", "--porcelain", "-uall"]).stdout
    paths: List[str] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        raw = line[3:].strip()
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        paths.append(raw.strip('"'))
    return paths


def _changed_python(repo: Path, extra_globs: Tuple[str, ...] = ()) -> List[Path]:
    files = []
    for rel in changed_paths(repo):
        p = repo / rel
        if p.suffix in (".py", ".ts", ".tsx", ".js"):
            files.append(p)
    return [p for p in files if p.is_file()]


def todo_marker(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    hits = []
    for p in _changed_python(repo):
        for idx, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            if re.search(r"(?:#|//)\s*(?:TODO|TBD|FIXME|HACK)\b", line, re.I):
                hits.append(f"{p.relative_to(repo)}:{idx}")
    return bool(hits), hits


def god_file(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    hits = []
    for p in _changed_python(repo):
        n = len(p.read_text(errors="ignore").splitlines())
        if n > 500:
            hits.append(f"{p.relative_to(repo)}={n}linhas")
    return bool(hits), hits


def test_removed(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    hits = []
    for rel in base:
        if not rel.startswith("tests/") or not rel.endswith(".py"):
            continue
        p = repo / rel
        if not p.is_file():
            hits.append(f"removido:{rel}")
            continue
        if p.stat().st_size and base[rel] and p.read_text(errors="ignore") != base[rel]:
            hits.append(f"modificado:{rel}")
    return bool(hits), hits


def ac_untraced(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    corpus = "\n".join(
        p.read_text(errors="ignore") for p in (repo / "tests").rglob("*.py")
    )
    missing = []
    for ac in sc.acs:
        number = ac.replace("AC-", "")
        if ac not in corpus and f"ac_{number}" not in corpus and f"ac{number}" not in corpus:
            missing.append(ac)
    return bool(missing), missing


def failing_tests(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    res = _run(repo, ["python3", "-m", "unittest", "discover", "-s", "tests", "-q"])
    if res.returncode == 0:
        return False, []
    tail = (res.stderr or res.stdout).strip().splitlines()
    return True, tail[-3:] if tail else ["unittest failed"]


def out_of_scope(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    allowed = [s.rstrip("/") for s in sc.scope]
    outside = []
    for rel in changed_paths(repo):
        if any(rel == a or rel.startswith(a + "/") for a in allowed):
            continue
        outside.append(rel)
    return bool(outside), outside


def no_red_evidence(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    index = repo / ".agents" / "runtime" / "evidence" / "index.jsonl"
    if not index.is_file():
        return True, ["sem-registro-de-evidencia"]
    entries = []
    for line in index.read_text(errors="ignore").splitlines():
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    has_fail = any(e.get("exit_code", 0) != 0 or e.get("status") == "FAIL" for e in entries)
    return (not has_fail), ([] if has_fail else ["nenhum-RED-registrado"])


def review_not_recorded(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    path = repo / ".agents" / "runtime" / "reviews.json"
    return not path.is_file(), ([] if path.is_file() else ["sem-review-registrada"])


def approval_not_recorded(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    path = repo / ".agents" / "runtime" / "approvals.json"
    return not path.is_file(), ([] if path.is_file() else ["sem-aprovacao-registrada"])


def skip_bypass(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    hits = []
    for p in (repo / "tests").rglob("*.py"):
        for idx, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            if re.search(r"@unittest\.skip|\.skipTest\(|pytest\.mark\.skip", line):
                hits.append(f"{p.relative_to(repo)}:{idx}")
    return bool(hits), hits


def hardcoded_secret(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Detecta segredo em qualquer arquivo do repositório (não só o diff).

    A baseline normalmente não tem varredura de segredo; o kit também
    não cobre o caso de 'segredo legado fora do diff'. O oráculo
    escaneia o repositório inteiro para ser consistente com uma
    política de zero-trust (ex.: secret-scanner rodando no CI).
    """
    hits = []
    for p in repo.rglob("*"):
        if p.suffix not in (".py", ".ts", ".tsx", ".js", ".env", ".yaml", ".yml", ".json"):
            continue
        if "__pycache__" in str(p) or ".git" in str(p):
            continue
        try:
            text = p.read_text(errors="ignore")
        except Exception:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                hits.append(str(p.relative_to(repo)))
                break
    return bool(hits), hits


def clean(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    return False, []


ORACLES = {
    "todo_marker": todo_marker,
    "god_file": god_file,
    "test_removed": test_removed,
    "ac_untraced": ac_untraced,
    "failing_tests": failing_tests,
    "out_of_scope": out_of_scope,
    "no_red_evidence": no_red_evidence,
    "review_not_recorded": review_not_recorded,
    "approval_not_recorded": approval_not_recorded,
    "skip_bypass": skip_bypass,
    "hardcoded_secret": hardcoded_secret,
    "clean": clean,
}


def evaluate(repo: Path, sc, base: Dict[str, str]) -> Tuple[bool, List[str]]:
    return ORACLES[sc.oracle](repo, sc, base)
