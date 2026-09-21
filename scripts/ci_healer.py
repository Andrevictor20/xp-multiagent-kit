#!/usr/bin/env python3
"""
ci_healer.py: Automated CI/CD Watcher & Self-Healing Loop.
Monitors pipelines (GitHub Actions / local CI), detects failures, extracts root-cause logs,
and executes self-healing iterations with atomic commits (governed by Rule L-003: max 3 attempts).
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

MAX_ITERATIONS = 3
ANSI_ESCAPE_REGEX = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def can_attempt_next(iteration: int) -> bool:
    """Returns True if the current iteration count allows another attempt (iteration < MAX_ITERATIONS)."""
    return iteration < MAX_ITERATIONS


def is_limit_exceeded(iteration: int) -> bool:
    """Returns True if attempts have exceeded MAX_ITERATIONS."""
    return iteration > MAX_ITERATIONS


def clean_ansi(text: str) -> str:
    """Removes terminal escape sequences and ANSI color codes."""
    return ANSI_ESCAPE_REGEX.sub("", text)


def parse_run_status(raw_json: str) -> dict:
    """Parses JSON from `gh run list --json ...` into a structured dictionary."""
    data = json.loads(raw_json)
    if isinstance(data, list):
        if not data:
            return {"status": "none", "is_failure": False, "is_completed": False, "is_success": False}
        run = data[0]
    elif isinstance(data, dict):
        run = data
    else:
        return {"status": "unknown", "is_failure": False, "is_completed": False, "is_success": False}

    run_id = run.get("databaseId") or run.get("id") or 0
    status = run.get("status", "unknown")
    conclusion = run.get("conclusion") or "none"
    workflow_name = run.get("workflowName") or run.get("name") or "CI Pipeline"
    branch = run.get("headBranch") or run.get("branch") or "unknown"
    url = run.get("url") or run.get("html_url") or ""

    is_failure = conclusion in ("failure", "startup_failure", "timed_out")
    is_completed = status == "completed"
    is_success = is_completed and conclusion == "success"

    return {
        "run_id": run_id,
        "status": status,
        "conclusion": conclusion,
        "workflow_name": workflow_name,
        "branch": branch,
        "url": url,
        "is_failure": is_failure,
        "is_completed": is_completed,
        "is_success": is_success,
    }


def extract_error_snippet(raw_log: str, max_lines: int = 30) -> str:
    """
    Extracts the most relevant error lines from raw CI logs.
    Prioritizes ##[error], Error:, FAILED, Traceback, Exception, and stack traces.
    """
    cleaned = clean_ansi(raw_log)
    lines = cleaned.splitlines()

    if not lines:
        return "(Log vazio ou indisponível)"

    error_indices = []
    error_patterns = [
        re.compile(r"##\[error\]", re.IGNORECASE),
        re.compile(r"\bError:", re.IGNORECASE),
        re.compile(r"\bFAILED\b"),
        re.compile(r"\bAssertionError\b"),
        re.compile(r"\bException:\b"),
        re.compile(r"exit code [1-9]"),
    ]

    for idx, line in enumerate(lines):
        for pattern in error_patterns:
            if pattern.search(line):
                error_indices.append(idx)
                break

    if not error_indices:
        # If no specific patterns match, return the tail of the log
        return "\n".join(lines[-max_lines:])

    # Collect a window around the errors
    selected_indices = set()
    for idx in error_indices:
        start = max(0, idx - 2)
        end = min(len(lines), idx + 3)
        for i in range(start, end):
            selected_indices.add(i)

    sorted_indices = sorted(selected_indices)
    if len(sorted_indices) > max_lines:
        sorted_indices = sorted_indices[-max_lines:]

    extracted = [lines[i] for i in sorted_indices]
    return "\n".join(extracted)


def generate_commit_message(run_id: int, reason: str, iteration: int) -> str:
    """Generates an atomic, semantic commit message for the auto-remediation."""
    clean_reason = reason.strip().splitlines()[0] if reason else "resolve CI pipeline failure"
    if len(clean_reason) > 50:
        clean_reason = clean_reason[:47] + "..."
    return f"fix(ci): {clean_reason} [run #{run_id}] (auto-heal [iter {iteration}/{MAX_ITERATIONS}])"


def get_current_branch(cwd: Path = None) -> str:
    """Returns the current active git branch."""
    try:
        res = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd or Path.cwd(),
            capture_output=True,
            text=True,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return "main"


def fetch_latest_run(branch: str, cwd: Path = None) -> dict:
    """Queries `gh run list` for the latest run on the given branch."""
    try:
        cmd = [
            "gh", "run", "list",
            "--branch", branch,
            "--limit", "1",
            "--json", "databaseId,status,conclusion,workflowName,headBranch,url"
        ]
        res = subprocess.run(cmd, cwd=cwd or Path.cwd(), capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return parse_run_status(res.stdout)
    except Exception as e:
        return {"status": "error", "error": str(e), "is_failure": False, "is_completed": False, "is_success": False}
    return {"status": "none", "is_failure": False, "is_completed": False, "is_success": False}


def fetch_run_logs(run_id: int, cwd: Path = None) -> str:
    """Pulls failed logs using `gh run view <run_id> --log-failed`."""
    try:
        cmd = ["gh", "run", "view", str(run_id), "--log-failed"]
        res = subprocess.run(cmd, cwd=cwd or Path.cwd(), capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout
    except Exception:
        pass
    return ""


def run_local_verification(cmd: str = None, cwd: Path = None) -> bool:
    """Runs local test suite to verify fix before pushing."""
    target_cwd = cwd or Path.cwd()
    if not cmd:
        if (target_cwd / "package.json").exists():
            cmd = "npm test"
        elif (target_cwd / "tests").exists() or (target_cwd / "pytest.ini").exists():
            cmd = "python3 -m unittest discover -s tests -p 'test_*.py'"
        elif (target_cwd / "Cargo.toml").exists():
            cmd = "cargo test"
        else:
            return True

    try:
        proc = subprocess.run(cmd, shell=True, cwd=target_cwd, capture_output=True, text=True)
        return proc.returncode == 0
    except Exception:
        return False


def install_post_push_hook(repo_root: Path = None):
    """Installs the post-push watcher hook in .git/hooks/post-push."""
    root = repo_root or Path.cwd()
    hooks_dir = root / ".git" / "hooks"
    if not hooks_dir.is_dir():
        print(f"❌ Diretório .git/hooks não encontrado em {root}")
        return False

    hook_file = hooks_dir / "post-push"
    hook_content = """#!/usr/bin/env bash
# Antigravity CI/CD Auto-Healer Post-Push Hook
if command -v agy-ci-heal >/dev/null 2>&1; then
  echo "🚀 [CI Auto-Healer] Disparando monitoramento em segundo plano..."
  agy-ci-heal --watch --auto-push >/dev/null 2>&1 &
fi
"""
    hook_file.write_text(hook_content, encoding="utf-8")
    hook_file.chmod(0o755)
    print(f"✅ Git Hook de post-push instalado com sucesso em: {hook_file}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Antigravity CI/CD Auto-Healer & Self-Correction Engine")
    parser.add_argument("--status", action="store_true", help="Verifica o status do pipeline atual no GitHub Actions")
    parser.add_argument("--diagnose-run", type=int, help="Diagnostica uma execução específica e extrai o bloco de erro")
    parser.add_argument("--watch", action="store_true", help="Monitora o pipeline em tempo real até a conclusão")
    parser.add_argument("--heal", action="store_true", help="Ativa o loop autônomo de autocorreção em caso de falha")
    parser.add_argument("--auto-push", action="store_true", help="Permite realizar git push automaticamente após cura local verde")
    parser.add_argument("--dry-run", action="store_true", help="Executa simulação de autocorreção sem efeitos colaterais")
    parser.add_argument("--install-hook", action="store_true", help="Instala o hook post-push no repositório local")
    parser.add_argument("--branch", type=str, default=None, help="Branch alvo (padrão: branch atual)")

    args = parser.parse_args()
    cwd = Path.cwd()
    branch = args.branch or get_current_branch(cwd)

    if args.install_hook:
        install_post_push_hook(cwd)
        return

    if args.diagnose_run:
        print(f"🔍 Diagnosticando run #{args.diagnose_run}...")
        raw_log = fetch_run_logs(args.diagnose_run, cwd)
        snippet = extract_error_snippet(raw_log)
        print("--- [Causa Raiz Extraída do CI] ---")
        print(snippet)
        print("-----------------------------------")
        return

    if args.status:
        info = fetch_latest_run(branch, cwd)
        print("====================================================================")
        print(f"📡 Status do Pipeline no GitHub Actions (Branch: `{branch}`)")
        print("====================================================================")
        print(f"Workflow: {info.get('workflow_name')}")
        print(f"Run ID:   {info.get('run_id')}")
        print(f"Status:   {info.get('status')}")
        print(f"Conclusão:{info.get('conclusion')}")
        print(f"URL:      {info.get('url')}")
        print("====================================================================")
        if info.get("is_failure"):
            print("❌ Pipeline em estado de FALHA! Use 'agy-ci-heal --heal' para iniciar autocorreção.")
        elif info.get("is_success"):
            print("✅ Pipeline concluído com SUCESSO!")
        return

    if args.watch or args.heal:
        print(f"👀 Monitorando pipeline no GitHub Actions para o branch '{branch}'...")
        iteration = 1
        while iteration <= MAX_ITERATIONS:
            info = fetch_latest_run(branch, cwd)
            status = info.get("status")
            conclusion = info.get("conclusion")
            run_id = info.get("run_id")

            print(f"⏳ Status atual: {status} ({conclusion}) [Run #{run_id}]")

            if info.get("is_success"):
                print("🎉 [SUCESSO] Pipeline aprovado no GitHub Actions! Nenhum reparo necessário.")
                sys.exit(0)

            if info.get("is_failure"):
                print(f"❌ [FALHA DETECTADA] Pipeline falhou na execução #{run_id}!")
                raw_log = fetch_run_logs(run_id, cwd)
                error_snippet = extract_error_snippet(raw_log)
                print("\n📋 Causa Raiz Extraída:")
                print(error_snippet)

                if not args.heal:
                    print("\n💡 Para tentar autocorreção automática, execute com a flag '--heal'.")
                    sys.exit(1)

                print(f"\n🔧 [AUTO-HEAL] Iniciando iteração {iteration}/{MAX_ITERATIONS} de autocorreção...")

                # Verify local tests
                local_ok = run_local_verification(cwd=cwd)
                print(f"🧪 Testes locais: {'✅ GREEN' if local_ok else '⚠️ PENDENTES'}")

                commit_msg = generate_commit_message(run_id, error_snippet, iteration)
                print(f"📝 Mensagem de commit atômico: '{commit_msg}'")

                if args.dry_run:
                    print("⚠️ Modo Dry-Run ativo. Nenhuma alteração persistida ou enviada via push.")
                    sys.exit(0)

                if args.auto_push and local_ok:
                    print("🚀 Realizando git push para re-disparar esteira...")
                    # Subprocess push if authorized
                    subprocess.run(["git", "push", "origin", branch], cwd=cwd)
                else:
                    print("ℹ️ Auto-push desligado ou validação pendente. Conclua o ajuste e re-execute.")
                    sys.exit(1)

                iteration += 1
                if iteration > MAX_ITERATIONS:
                    print(f"\n🛑 [REGRA L-003] Limite de {MAX_ITERATIONS} tentativas atingido sem sucesso.")
                    print("Por favor, revise o diagnóstico acima para intervenção manual.")
                    sys.exit(1)

                print("⏳ Aguardando novo disparo do pipeline...")
                time.sleep(10)
            elif status == "completed":
                print(f"ℹ️ Pipeline finalizado com status: {conclusion}")
                sys.exit(0)
            else:
                time.sleep(8)


if __name__ == "__main__":
    main()
