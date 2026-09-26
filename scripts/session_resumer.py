#!/usr/bin/env python3
"""
scripts/session_resumer.py
Motor de Checkpoint Durável de Sessão e Retomada Instantânea para o XP Multi-Agent Kit.
Salva e reconstitui o estado de sessões interrompidas em .agents/memory/.session_state.json,
permitindo retomar exatamente onde parou sem desperdício de tokens na reexplicação do contexto.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

STATE_FILENAME = ".session_state.json"


def get_state_file_path(workspace: Path) -> Path:
    """Retorna o caminho do arquivo de estado da sessão."""
    return workspace.resolve() / ".agents" / "memory" / STATE_FILENAME


def get_git_status_snapshot(workspace: Path) -> Tuple[str, List[str], str]:
    """Obtém branch, lista de arquivos alterados e último commit."""
    branch = "unknown"
    files_changed: List[str] = []
    last_commit = "none"

    try:
        res = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        if res.returncode == 0 and res.stdout.strip():
            branch = res.stdout.strip()
    except Exception:
        pass

    try:
        res = subprocess.run(
            ["git", "status", "--short"],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            files_changed = [line.strip() for line in res.stdout.splitlines() if line.strip()][:10]
    except Exception:
        pass

    try:
        res = subprocess.run(
            ["git", "log", "-1", "--oneline"],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        if res.returncode == 0 and res.stdout.strip():
            last_commit = res.stdout.strip()
    except Exception:
        pass

    return branch, files_changed, last_commit


def save_session_state(
    workspace: Path,
    goal: Optional[str] = None,
    next_steps: Optional[str] = None,
    active_agent: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    """Salva um snapshot estruturado da sessão ativa em disco."""
    workspace = workspace.resolve()
    state_file = get_state_file_path(workspace)
    state_file.parent.mkdir(parents=True, exist_ok=True)

    branch, files_changed, last_commit = get_git_status_snapshot(workspace)
    now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    state_data: Dict[str, Any] = {
        "timestamp": now_iso,
        "branch": branch,
        "last_commit": last_commit,
        "goal": goal or f"Sessão em andamento na branch '{branch}'",
        "next_steps": next_steps or "Prosseguir com o plano de implementação e rodar testes.",
        "active_agent": active_agent or "orchestrator",
        "files_changed": files_changed,
        "metadata": metadata or {},
    }

    state_file.write_text(json.dumps(state_data, indent=2, ensure_ascii=False), encoding="utf-8")
    return state_file


def load_session_state(workspace: Path) -> Optional[Dict[str, Any]]:
    """Carrega o snapshot da sessão se existir."""
    state_file = get_state_file_path(workspace)
    if not state_file.is_file():
        return None

    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        return None


def clear_session_state(workspace: Path) -> bool:
    """Remove o snapshot de sessão após conclusão."""
    state_file = get_state_file_path(workspace)
    if state_file.is_file():
        try:
            state_file.unlink()
            return True
        except Exception:
            pass
    return False


def generate_resume_prompt(state: Dict[str, Any]) -> str:
    """Gera prompt ultracompacto (< 15 linhas / ~120 tokens) para reiniciar a sessão."""
    branch = state.get("branch", "unknown")
    goal = state.get("goal", "")
    next_steps = state.get("next_steps", "")
    files = state.get("files_changed", [])
    files_str = ", ".join([f"`{f}`" for f in files[:5]]) if files else "Nenhum arquivo pendente"

    lines = [
        "🔄 **Retomada de Sessão (XP Kit Fast Bootstrap)**",
        f"- **Branch:** `{branch}` | **Timestamp:** {state.get('timestamp', '')}",
        f"- **Meta:** {goal}",
        f"- **Arquivos Ativos:** {files_str}",
        f"- **Próximos Passos:** {next_steps}",
        "👉 *Instrução:* Continue diretamente a execução a partir dos Próximos Passos sem repetir análises prévias.",
    ]
    return "\n".join(lines)


def format_status_display(state: Dict[str, Any]) -> str:
    """Formata visualmente o estado da sessão para o terminal."""
    lines = [
        "=======================================================",
        "📦 Antigravity — Checkpoint Durável de Sessão Ativa",
        "=======================================================",
        f"📅 Data/Hora     : {state.get('timestamp', 'N/A')}",
        f"🌿 Branch        : {state.get('branch', 'unknown')}",
        f"📌 Último Commit : {state.get('last_commit', 'none')}",
        f"🎯 Meta / Status : {state.get('goal', 'N/A')}",
        f"🚀 Próximo Passo : {state.get('next_steps', 'N/A')}",
        f"🤖 Agente Ativo  : {state.get('active_agent', 'orchestrator')}",
    ]
    files = state.get("files_changed", [])
    if files:
        lines.append("📝 Arquivos Pendentes:")
        for f in files[:8]:
            lines.append(f"   • {f}")
    lines.append("=======================================================")
    lines.append("💡 Dica: Use `agy-resume --prompt` para gerar o prompt de reinício.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Motor de Checkpoint Durável e Retomada de Sessão (XP Kit)")
    parser.add_argument("--workspace", default=".", help="Diretório raiz do projeto")
    parser.add_argument("--save", action="store_true", help="Salva o estado atual da sessão")
    parser.add_argument("--goal", help="Meta ou progresso atual")
    parser.add_argument("--next", help="Próximo passo imediato")
    parser.add_argument("--agent", help="Nome do subagente ativo")
    parser.add_argument("--prompt", action="store_true", help="Imprime apenas o prompt ultracompacto para colar no chat")
    parser.add_argument("--json", action="store_true", help="Imprime o estado bruto em formato JSON")
    parser.add_argument("--clear", action="store_true", help="Limpa o checkpoint salvo")

    args = parser.parse_args()
    ws = Path(args.workspace)

    if args.clear:
        if clear_session_state(ws):
            print("✅ Checkpoint de sessão limpo com sucesso.")
        else:
            print("ℹ️ Nenhum checkpoint ativo encontrado para limpar.")
        return 0

    if args.save:
        state_file = save_session_state(ws, goal=args.goal, next_steps=args.next, active_agent=args.agent)
        print(f"✅ Checkpoint de sessão salvo com sucesso em: {state_file}")
        return 0

    state = load_session_state(ws)
    if not state:
        print("ℹ️ Nenhum checkpoint de sessão encontrado em `.agents/memory/.session_state.json`.")
        print("👉 Para salvar o estado atual, use: `agy-resume --save --goal '...' --next '...'`")
        return 0

    if args.prompt:
        print(generate_resume_prompt(state))
        return 0

    if args.json:
        print(json.dumps(state, indent=2, ensure_ascii=False))
        return 0

    print(format_status_display(state))
    return 0


if __name__ == "__main__":
    sys.exit(main())
