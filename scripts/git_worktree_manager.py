#!/usr/bin/env python3
"""
git_worktree_manager.py — Gerenciador de Git Worktrees para Subagentes e Tarefas Paralelas.

Permite isolar completamente execuções de subagentes em worktrees temporários,
prevenindo contaminação do workspace principal e possibilitando rollback imediato.
"""

import os
import re
import sys
import subprocess
import argparse
from typing import Dict, List, Optional, Tuple


def sanitize_branch_name(name: str) -> str:
    """Higieniza o nome da tarefa para criar uma branch git segura."""
    clean = re.sub(r"[^a-zA-Z0-9_\-\.]+", "-", name)
    clean = re.sub(r"-+", "-", clean).strip("-.")
    return clean


def get_repo_root(base_dir: Optional[str] = None) -> str:
    """Obtém a raiz do repositório git."""
    if base_dir:
        return base_dir
    res = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode == 0:
        return res.stdout.strip()
    return os.getcwd()


def create_worktree(
    task_name: str,
    base_branch: str = "main",
    base_dir: Optional[str] = None,
    worktrees_subpath: str = os.path.join(".agents", "worktrees"),
) -> Tuple[str, str]:
    """Cria um novo git worktree e branch dedicada para a tarefa."""
    repo_root = get_repo_root(base_dir)
    clean_task = sanitize_branch_name(task_name)
    branch_name = f"task/{clean_task}"
    worktree_path = os.path.join(repo_root, worktrees_subpath, clean_task)

    os.makedirs(os.path.dirname(worktree_path), exist_ok=True)

    cmd = [
        "git",
        "worktree",
        "add",
        "-b",
        branch_name,
        worktree_path,
        base_branch,
    ]
    res = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(
            f"Failed to create git worktree '{worktree_path}': {res.stderr.strip()}"
        )

    return worktree_path, branch_name


def remove_worktree(
    task_name: str,
    force: bool = True,
    delete_branch: bool = True,
    base_dir: Optional[str] = None,
    worktrees_subpath: str = os.path.join(".agents", "worktrees"),
) -> bool:
    """Remove um git worktree existente e opcionalmente deleta a branch da tarefa."""
    repo_root = get_repo_root(base_dir)
    clean_task = sanitize_branch_name(task_name)
    branch_name = f"task/{clean_task}"
    worktree_path = os.path.join(repo_root, worktrees_subpath, clean_task)

    cmd = ["git", "worktree", "remove"]
    if force:
        cmd.append("--force")
    cmd.append(worktree_path)

    res = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)

    if delete_branch:
        del_cmd = ["git", "branch", "-D" if force else "-d", branch_name]
        subprocess.run(del_cmd, cwd=repo_root, capture_output=True, text=True)

    return res.returncode == 0


def list_worktrees(
    base_dir: Optional[str] = None,
    worktrees_subpath: str = os.path.join(".agents", "worktrees"),
) -> List[Dict[str, str]]:
    """Lista todos os git worktrees ativos gerenciados sob .agents/worktrees/."""
    repo_root = get_repo_root(base_dir)
    res = subprocess.run(
        ["git", "worktree", "list"], cwd=repo_root, capture_output=True, text=True
    )
    if res.returncode != 0:
        return []

    worktrees = []
    marker = os.path.normpath(os.path.join(repo_root, worktrees_subpath))
    for line in res.stdout.strip().splitlines():
        parts = line.split()
        if not parts:
            continue
        path = parts[0]
        if marker in os.path.normpath(path):
            task_name = os.path.basename(path)
            branch = parts[-1].strip("[]") if len(parts) >= 3 else ""
            commit = parts[1] if len(parts) >= 2 else ""
            worktrees.append({
                "task": task_name,
                "path": path,
                "commit": commit,
                "branch": branch,
            })
    return worktrees


def main() -> None:
    parser = argparse.ArgumentParser(
        description="XP Git Worktree Manager for Antigravity Subagents"
    )
    parser.add_argument(
        "--create",
        metavar="TASK",
        help="Cria um worktree isolado para a tarefa especificada",
    )
    parser.add_argument(
        "--remove", metavar="TASK", help="Remove o worktree da tarefa"
    )
    parser.add_argument(
        "--base",
        default="main",
        help="Branch base para criação (default: main)",
    )
    parser.add_argument(
        "--list", action="store_true", help="Lista todos os worktrees ativos"
    )
    parser.add_argument(
        "--clean-all",
        action="store_true",
        help="Remove e limpa todos os worktrees sob .agents/worktrees/",
    )

    args = parser.parse_args()

    if args.create:
        try:
            path, branch = create_worktree(args.create, base_branch=args.base)
            print(f"✅ Worktree criado com sucesso!")
            print(f"   📁 Caminho: {path}")
            print(f"   🌿 Branch: {branch}")
        except Exception as e:
            print(f"❌ Erro ao criar worktree: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.remove:
        ok = remove_worktree(args.remove)
        if ok:
            print(f"✅ Worktree '{args.remove}' removido com sucesso.")
        else:
            print(f"⚠️ Não foi possível remover o worktree '{args.remove}'.")
            sys.exit(1)
    elif args.list:
        wts = list_worktrees()
        if not wts:
            print("ℹ️ Nenhum worktree ativo em .agents/worktrees/.")
        else:
            print(f"🌿 {len(wts)} Worktree(s) ativo(s):")
            for w in wts:
                print(f"   - Tarefa: {w['task']} | Branch: {w['branch']} | Path: {w['path']}")
    elif args.clean_all:
        wts = list_worktrees()
        for w in wts:
            remove_worktree(w["task"], force=True)
            print(f"   🧹 Limpo: {w['task']}")
        print("✅ Todos os worktrees foram limpos.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
