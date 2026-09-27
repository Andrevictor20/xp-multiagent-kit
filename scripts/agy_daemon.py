#!/usr/bin/env python3
"""
scripts/agy_daemon.py
Daemon Leve de Background & Supervisor do XP Multi-Agent Kit.
Executa de forma desacoplada do terminal/IDE para monitoramento contínuo de CI/CD,
rotação automática de memória episódica e limpeza de worktrees temporários.
"""
from __future__ import annotations

import argparse
import datetime
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_PID_FILE = Path.home() / ".gemini" / "antigravity-cli" / "daemon.pid"
DEFAULT_LOG_FILE = Path.home() / ".gemini" / "antigravity-cli" / "daemon.log"


def log_message(msg: str, log_file: Optional[Path] = None) -> None:
    """Registra mensagem com timestamp no log do daemon e stdout."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{now_str}] {msg}"
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(formatted + "\n")
        except Exception:
            pass


def is_process_running(pid: int) -> bool:
    """Verifica se um processo com determinado PID está vivo."""
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def read_pid(pid_file: Path, check_alive: bool = True) -> Optional[int]:
    """Lê o PID armazenado no arquivo se for válido."""
    if not pid_file.is_file():
        return None
    try:
        content = pid_file.read_text(encoding="utf-8").strip()
        pid = int(content)
        if not check_alive:
            return pid
        return pid if is_process_running(pid) else None
    except Exception:
        return None


def write_pid_file(pid_file: Path, pid: int) -> None:
    """Grava o PID no arquivo de controle."""
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(pid), encoding="utf-8")


def remove_pid_file(pid_file: Path) -> bool:
    """Remove o arquivo de PID se existir."""
    if pid_file.is_file():
        try:
            pid_file.unlink()
            return True
        except Exception:
            pass
    return False


def get_daemon_status(pid_file: Path) -> Dict[str, Any]:
    """Retorna o status do daemon em execução."""
    pid = read_pid(pid_file)
    return {
        "running": pid is not None,
        "pid": pid,
        "pid_file": str(pid_file),
    }


def send_desktop_notification(title: str, body: str) -> None:
    """Envia notificação de desktop via notify-send se disponível no Linux."""
    try:
        subprocess.run(
            ["notify-send", "-a", "Antigravity Kit", title, body],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
        )
    except Exception:
        pass


def check_ci_status_task(workspace: Path, log_file: Optional[Path] = None) -> str:
    """Verifica status de runs do GitHub Actions."""
    try:
        res = subprocess.run(
            ["gh", "run", "list", "-L", "1", "--json", "status,conclusion,name,databaseId"],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=8,
        )
        if res.returncode == 0 and res.stdout.strip():
            import json
            runs = json.loads(res.stdout)
            if runs:
                latest = runs[0]
                status = latest.get("status")
                conclusion = latest.get("conclusion")
                if status == "completed" and conclusion == "failure":
                    name = latest.get("name", "CI")
                    log_message(f"⚠️ CI Falhou na run {latest.get('databaseId')} ({name})", log_file)
                    send_desktop_notification("⚠️ Falha de CI/CD", f"A esteira '{name}' falhou. Execute 'agy-ci-heal' para corrigir.")
                    return f"FAILED ({name})"
                return f"OK ({status}/{conclusion})"
    except Exception:
        pass
    return "SKIPPED (no gh/git)"


def check_and_rotate_memory_task(workspace: Path, log_file: Optional[Path] = None) -> str:
    """Verifica e executa rotação automática de memória se > 35KB."""
    mem_file = workspace / ".agents" / "memory" / "PROJECT_MEMORY.md"
    if not mem_file.is_file():
        return "NO_MEMORY_FILE"

    size_kb = mem_file.stat().st_size / 1024.0
    if size_kb > 35.0:
        try:
            kit_root = Path(__file__).resolve().parent.parent
            sys.path.insert(0, str(kit_root))
            from scripts.memory_archiver import archive_memory
            retained, archived = archive_memory(mem_file)
            log_message(f"🗜️ Rotação de memória executada: {retained} mantidas, {archived} arquivadas", log_file)
            return f"ROTATED ({archived} archived)"
        except Exception as e:
            return f"ERROR ({e})"
    return f"HEALTHY ({size_kb:.1f} KB)"


def prune_worktrees_task(workspace: Path, log_file: Optional[Path] = None) -> str:
    """Executa limpeza de worktrees temporários órfãos."""
    try:
        res = subprocess.run(
            ["git", "worktree", "prune"],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            return "PRUNED"
    except Exception:
        pass
    return "SKIPPED"


def sync_live_quota_task(workspace: Path, log_file: Optional[Path] = None) -> str:
    """Verifica e sincroniza cota ao vivo com o Language Server, persistindo snapshot oficial."""
    try:
        kit_root = Path(__file__).resolve().parent.parent
        if str(kit_root) not in sys.path:
            sys.path.insert(0, str(kit_root))
        from scripts.token_tracker import (
            fetch_live_antigravity_quota,
            save_quota_snapshot,
            calculate_rolling_windows,
        )

        rolling = calculate_rolling_windows()
        quota = fetch_live_antigravity_quota(force_refresh=True, rolling=rolling)
        if quota.is_live:
            save_quota_snapshot(quota, rolling.tokens_5h, rolling.tokens_7d)
            pct_5h = (quota.gemini_5h.remaining_fraction * 100.0) if quota.gemini_5h else 0.0
            pct_7d = (quota.gemini_weekly.remaining_fraction * 100.0) if quota.gemini_weekly else 0.0
            log_message(f"⚡ Cota oficial sincronizada com Language Server (5h: {pct_5h:.1f}% rem, Semanal: {pct_7d:.1f}% rem)", log_file)
            return f"SYNCED (5h: {pct_5h:.1f}%, 7d: {pct_7d:.1f}%)"
        elif quota.is_projected:
            return "PROJECTED (snapshot mantido)"
        return "OFFLINE (sem snapshot)"
    except Exception as e:
        return f"ERROR ({e})"


def run_maintenance_cycle(workspace: Path, log_file: Optional[Path] = None) -> Dict[str, Any]:
    """Executa um ciclo completo de manutenção preventiva."""
    workspace = workspace.resolve()
    log_message("⚡ Iniciando ciclo de manutenção periódica", log_file)

    quota_result = sync_live_quota_task(workspace, log_file)
    mem_result = check_and_rotate_memory_task(workspace, log_file)
    ci_result = check_ci_status_task(workspace, log_file)
    worktree_result = prune_worktrees_task(workspace, log_file)

    log_message(f"✅ Ciclo concluído: Quota={quota_result}, Memória={mem_result}, CI={ci_result}, Worktrees={worktree_result}", log_file)

    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "quota": quota_result,
        "memory": mem_result,
        "ci": ci_result,
        "worktree": worktree_result,
    }


def daemon_loop(workspace: Path, pid_file: Path, log_file: Path, interval: int = 60) -> None:
    """Loop principal de execução do daemon em background."""
    write_pid_file(pid_file, os.getpid())
    log_message(f"🚀 agy-daemon iniciado com PID {os.getpid()} (Intervalo: {interval}s)", log_file)

    def sig_handler(signum, frame):
        log_message("🛑 Recebido sinal de parada, encerrando agy-daemon...", log_file)
        remove_pid_file(pid_file)
        sys.exit(0)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    try:
        while True:
            run_maintenance_cycle(workspace, log_file)
            time.sleep(interval)
    except Exception as e:
        log_message(f"❌ Erro fatal no daemon: {e}", log_file)
    finally:
        remove_pid_file(pid_file)


def start_daemon_process(
    workspace: Path,
    pid_file: Path = DEFAULT_PID_FILE,
    log_file: Path = DEFAULT_LOG_FILE,
    interval: int = 60,
) -> int:
    """Inicia o daemon em segundo plano (desacoplado do terminal)."""
    pid = read_pid(pid_file)
    if pid is not None:
        print(f"ℹ️ agy-daemon já está em execução (PID: {pid}).")
        return pid

    # Inicia subprocess desacoplado
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--run-daemon",
        "--workspace", str(workspace.resolve()),
        "--pid-file", str(pid_file),
        "--log-file", str(log_file),
        "--interval", str(interval),
    ]

    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as out:
        proc = subprocess.Popen(
            cmd,
            stdout=out,
            stderr=out,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

    # Aguarda gravação do PID
    time.sleep(0.5)
    write_pid_file(pid_file, proc.pid)
    print(f"✅ agy-daemon iniciado com sucesso em background (PID: {proc.pid})")
    print(f"📄 Logs: {log_file}")
    return proc.pid


def stop_daemon_process(pid_file: Path = DEFAULT_PID_FILE) -> bool:
    """Para o processo do daemon enviando SIGTERM."""
    pid = read_pid(pid_file)
    if pid is None:
        remove_pid_file(pid_file)
        print("ℹ️ agy-daemon não está em execução.")
        return False

    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.5)
        if is_process_running(pid):
            os.kill(pid, signal.SIGKILL)
        remove_pid_file(pid_file)
        print(f"✅ agy-daemon (PID {pid}) encerrado com sucesso.")
        return True
    except Exception as e:
        print(f"❌ Erro ao parar daemon: {e}")
        remove_pid_file(pid_file)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Daemon de Background do XP Multi-Agent Kit (agy-daemon)")
    parser.add_argument("action", nargs="?", default="status", choices=["start", "stop", "status", "run-once", "logs"], help="Ação a executar")
    parser.add_argument("--workspace", default=".", help="Diretório de trabalho a monitorar")
    parser.add_argument("--interval", type=int, default=60, help="Intervalo de verificação em segundos (padrão: 60)")
    parser.add_argument("--pid-file", default=str(DEFAULT_PID_FILE), help="Caminho do arquivo PID")
    parser.add_argument("--log-file", default=str(DEFAULT_LOG_FILE), help="Caminho do arquivo de log")
    parser.add_argument("-n", "--lines", type=int, default=20, help="Número de linhas para o comando logs")
    parser.add_argument("--run-daemon", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()
    ws = Path(args.workspace)
    pid_file = Path(args.pid_file)
    log_file = Path(args.log_file)

    if args.run_daemon:
        daemon_loop(ws, pid_file, log_file, interval=args.interval)
        return 0

    if args.action == "start":
        start_daemon_process(ws, pid_file, log_file, interval=args.interval)
        return 0
    elif args.action == "stop":
        stop_daemon_process(pid_file)
        return 0
    elif args.action == "status":
        status = get_daemon_status(pid_file)
        if status["running"]:
            print(f"🟢 agy-daemon está ATIVO (PID: {status['pid']})")
        else:
            print("⚪ agy-daemon está PARADO")
        print(f"   PID File : {status['pid_file']}")
        print(f"   Log File : {log_file}")
        return 0
    elif args.action == "run-once":
        res = run_maintenance_cycle(ws, log_file)
        print("✅ Manutenção concluída:")
        print(f"   • Memória  : {res['memory']}")
        print(f"   • CI/CD    : {res['ci']}")
        print(f"   • Worktree : {res['worktree']}")
        return 0
    elif args.action == "logs":
        if not log_file.is_file():
            print(f"ℹ️ Nenhum log encontrado em {log_file}")
            return 0
        lines = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        print("\n".join(lines[-args.lines:]))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
