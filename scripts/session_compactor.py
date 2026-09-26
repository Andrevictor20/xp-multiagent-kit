#!/usr/bin/env python3
"""
scripts/session_compactor.py
Utilitário de Checkpoint Rápido e Fast Bootstrap.
Grava o estado atômico da sessão no PROJECT_MEMORY.md e prepara a transição para um chat limpo.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import argparse
import datetime
import subprocess
import sys
from pathlib import Path


def get_git_summary() -> tuple[str, str]:
    """Obtém status compacto e estatísticas de diff do git."""
    try:
        status_proc = subprocess.run(
            ["git", "status", "-s"],
            capture_output=True,
            text=True,
            check=False,
        )
        status_out = status_proc.stdout.strip()
    except Exception:
        status_out = ""

    try:
        diff_proc = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True,
            text=True,
            check=False,
        )
        diff_out = diff_proc.stdout.strip()
    except Exception:
        diff_out = ""

    return status_out, diff_out


def update_project_memory(summary_msg: str, memory_path: Path) -> bool:
    """Atualiza o PROJECT_MEMORY.md com o checkpoint da sessão."""
    if not memory_path.exists():
        return False

    content = memory_path.read_text(encoding="utf-8")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    checkpoint_entry = (
        f"\n### Checkpoint de Sessão [{now_str}]\n"
        f"- **Resumo:** {summary_msg}\n"
    )

    status_out, diff_out = get_git_summary()
    if status_out:
        first_files = status_out.splitlines()[:8]
        checkpoint_entry += f"- **Arquivos Ativos:** {len(status_out.splitlines())} alterados ({', '.join([l.strip() for l in first_files[:4]])}...)\n"

    # Inserir após a seção de Working Memory ou Episodic Memory
    marker = "## 2. Working Memory (Sessão Atual)"
    if marker in content:
        parts = content.split(marker, 1)
        new_content = parts[0] + marker + checkpoint_entry + parts[1]
    else:
        new_content = content + "\n" + checkpoint_entry

    memory_path.write_text(new_content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Grava checkpoint atômico no PROJECT_MEMORY.md para possibilitar chat limpo."
    )
    parser.add_argument(
        "-m",
        "--message",
        type=str,
        default="Checkpoint atômico de sessão.",
        help="Descrição do estado alcançado",
    )
    parser.add_argument(
        "--memory-file",
        type=Path,
        default=Path(".agents/memory/PROJECT_MEMORY.md"),
        help="Caminho do PROJECT_MEMORY.md",
    )
    args = parser.parse_args()

    memory_file: Path = args.memory_file
    updated = update_project_memory(args.message, memory_file)

    print("====================================================================")
    if updated:
        print(f"✅ Checkpoint gravado com sucesso em: {memory_file}")
    else:
        print(f"⚠️ Aviso: Arquivo de memória não encontrado em {memory_file}")

    print("====================================================================")
    print("🧹 RECOMENDAÇÃO DE ECONOMIA DE TOKENS (FAST BOOTSTRAP):")
    print("   Seu progresso está salvo fisicamente em disco.")
    print("   Para poupar de 30.000 a 60.000 tokens acumulados de histórico,")
    print("   reinicie agora a conversa digitando: /clear")
    print("====================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
