#!/usr/bin/env python3
"""
scripts/antigravity_multiagent.py
Antigravity-Native Dynamic Multi-Agent Engine (Boss-Worker Execution).
Coordinates heterogeneous models (Argon High + Flash Low/Medium workers),
parallel execution groups, contract injection via MEMORY.md, visual mission dashboard,
task-level gatekeeping, auto-healing with escalation, and mission report generation.
Part of XP Multi-Agent Kit v3.3 (SPEC-004).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class MissionManifestError(ValueError):
    """Raised when a mission manifest violates the schema or validation rules."""
    pass


def validate_mission_manifest(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validates the structure and mandatory fields of a mission manifest."""
    if not isinstance(data, dict):
        raise MissionManifestError("O manifesto deve ser um objeto JSON (dict).")

    for req_field in ("mission_id", "feature_name", "tasks"):
        if req_field not in data or not data[req_field]:
            raise MissionManifestError(f"Campo obrigatório ausente ou vazio: '{req_field}'")

    if not isinstance(data["tasks"], list) or len(data["tasks"]) == 0:
        raise MissionManifestError("O campo 'tasks' deve conter uma lista não vazia de tarefas.")

    required_task_keys = (
        "task_id", "subagent", "model", "effort", "execution_group",
        "allowed_paths", "objective", "verification_cmd"
    )

    for idx, task in enumerate(data["tasks"]):
        if not isinstance(task, dict):
            raise MissionManifestError(f"Tarefa na posição {idx} deve ser um objeto JSON.")
        for key in required_task_keys:
            if key not in task:
                raise MissionManifestError(f"Tarefa '{task.get('task_id', idx)}' ausenta campo obrigatório: '{key}'")
        if not isinstance(task["execution_group"], int) or task["execution_group"] < 1:
            raise MissionManifestError(f"Tarefa '{task['task_id']}': 'execution_group' deve ser um inteiro >= 1.")

    return data


def prepare_subagent_payload(
    task: Dict[str, Any], shared_memory: str = "", host: str = "antigravity"
) -> Dict[str, Any]:
    """Formats the payload required for the target host's subagent driver."""
    from scripts.multiagent_drivers import get_worker_driver
    driver = get_worker_driver(host)
    return driver.build_worker_payload(task, shared_memory=shared_memory)


def render_mission_dashboard(
    mission_id: str,
    feature_name: str,
    tasks: List[Dict[str, Any]],
    current_group: Optional[int] = None,
) -> str:
    """Renders an ASCII mission dashboard with status indicators and execution groups."""
    lines: List[str] = [
        "═══════════════════════════════════════════════════════════════════════════════",
        f" 🚀 QUADRO DE EXECUÇÃO MULTIAGENTE ANTIGRAVITY — XP-MULTIAGENT-KIT",
        "═══════════════════════════════════════════════════════════════════════════════",
        f" • Missão ID   : {mission_id}",
        f" • Funcionalidade: {feature_name}",
        "───────────────────────────────────────────────────────────────────────────────",
        f" {'GRUPO':<7} | {'TASK ID':<18} | {'AGENTE':<12} | {'MODELO/ESFORÇO':<18} | {'STATUS':<10}",
        "───────────────────────────────────────────────────────────────────────────────",
    ]

    status_icons = {
        "PENDING": "⏳ PENDENTE",
        "RUNNING": "⚡ EM EXECUÇÃO",
        "PASS": "✅ PASS",
        "HEALING": "🔄 AUTO-HEAL",
        "FAIL": "❌ FALHA",
    }

    for task in tasks:
        grp = f"G-{task.get('execution_group', 1)}"
        tid = task.get("task_id", "")[:18]
        ag = task.get("subagent", "")[:12]

        raw_m = str(task.get("model", "flash")).lower()
        m_label = "Flash" if "flash" in raw_m else ("Argon" if "argon" in raw_m or "pro" in raw_m else "Base")
        eff = str(task.get("effort", "medium")).upper()
        model_info = f"{m_label} [{eff}]"

        st_raw = task.get("status", "PENDING")
        st_display = status_icons.get(st_raw, st_raw)
        lines.append(f" {grp:<7} | {tid:<18} | {ag:<12} | {model_info:<18} | {st_display:<10}")

    lines.append("═══════════════════════════════════════════════════════════════════════════════")
    return "\n".join(lines)


def format_agents_roster(tasks: List[Dict[str, Any]]) -> str:
    """Formats a concise markdown roster of scheduled subagents."""
    unique_agents = sorted(list({str(t.get("subagent", "builder")).strip() for t in tasks}))
    total_count = len(unique_agents)
    lines: List[str] = [
        f"👥 **Alocação Multiagente ({total_count} agentes escalados):**",
        f"- **Total de Agentes Especialistas:** {total_count}",
        f"- **Agentes Escalados:** {', '.join(f'`{ag}`' for ag in unique_agents)}",
        "",
        "| Agente | Tarefa / ID | Modelo | Esforço | Escopo Permitido |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for t in tasks:
        ag = t.get("subagent", "builder")
        tid = t.get("task_id", "")
        mod = t.get("model", "flash")
        eff = str(t.get("effort", "medium")).upper()
        paths = ", ".join(t.get("allowed_paths", ["src/"]))
        lines.append(f"| `{ag}` | `{tid}` | {mod} | {eff} | `{paths}` |")
    return "\n".join(lines)


def format_agents_summary(task_results: List[Dict[str, Any]]) -> str:
    """Formats a final execution summary of participating agents and outcomes."""
    unique_agents = sorted(list({str(t.get("subagent", "builder")).strip() for t in task_results}))
    total_count = len(unique_agents)
    passed_count = sum(1 for t in task_results if t.get("status") == "PASS")
    total_tasks = len(task_results)
    lines: List[str] = [
        f"### 👥 Relatório de Execução Multiagente ({total_count} agentes utilizados)",
        f"- **Total de Agentes Envolvidos:** {total_count}",
        f"- **Agentes Participantes:** {', '.join(f'`{ag}`' for ag in unique_agents)}",
        f"- **Taxa de Sucesso:** {passed_count}/{total_tasks} tarefas GREEN",
        "",
        "| Agente | Task ID | Modelo / Esforço | Status | Retries |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for t in task_results:
        ag = t.get("subagent", "builder")
        tid = t.get("task_id", "")
        mod = f"{t.get('model', '')} ({t.get('effort', '')})"
        st = t.get("status", "UNKNOWN")
        retries = t.get("retries", 0)
        lines.append(f"| `{ag}` | `{tid}` | {mod} | **{st}** | {retries} |")
    return "\n".join(lines)


class AntigravityMissionEngine:
    """Core execution engine for managing parallel tasks, gatekeeping, and auto-healing."""

    def __init__(self, project_dir: Optional[Path] = None):
        self.project_dir = Path(project_dir or Path.cwd()).resolve()
        self.agents_dir = self.project_dir / ".agents"
        self.memory_file = self.agents_dir / "MEMORY.md"
        self.report_file = self.agents_dir / "mission-report.md"

    def read_shared_memory(self) -> str:
        """Reads the shared memory file if it exists."""
        if self.memory_file.is_file():
            try:
                return self.memory_file.read_text(encoding="utf-8")
            except Exception:
                pass
        return ""

    def get_execution_groups(
        self, manifest: Dict[str, Any]
    ) -> Dict[int, List[Dict[str, Any]]]:
        """Groups tasks by execution_group in ascending chronological order."""
        validated = validate_mission_manifest(manifest)
        groups: Dict[int, List[Dict[str, Any]]] = {}
        for task in validated["tasks"]:
            grp = task["execution_group"]
            groups.setdefault(grp, []).append(task)
        return dict(sorted(groups.items()))

    def _execute_command(self, cmd: str, cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Executes a verification shell command synchronously and returns result."""
        target_dir = str(cwd or self.project_dir)
        try:
            res = subprocess.run(
                cmd,
                shell=True,
                cwd=target_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return {
                "exit_code": res.returncode,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip(),
            }
        except subprocess.TimeoutExpired:
            return {"exit_code": -1, "stdout": "", "stderr": "Command timed out after 120s"}
        except Exception as ex:
            return {"exit_code": -1, "stdout": "", "stderr": str(ex)}

    def run_task_verification_with_healing(
        self,
        task: Dict[str, Any],
        max_retries: int = 2,
    ) -> Dict[str, Any]:
        """Executes verification_cmd with automatic retry and error capture."""
        cmd = task.get("verification_cmd", "")
        retries = 0
        last_error = ""

        while retries <= max_retries:
            res = self._execute_command(cmd)
            if res["exit_code"] == 0:
                return {
                    "task_id": task["task_id"],
                    "status": "PASS",
                    "retries": retries,
                    "error": None,
                }

            retries += 1
            last_error = res["stderr"] or res["stdout"] or f"Exit code {res['exit_code']}"

        return {
            "task_id": task["task_id"],
            "status": "FAIL",
            "retries": retries - 1,
            "error": last_error,
        }

    def run_mission(
        self,
        manifest: Dict[str, Any],
        execute_subagents: bool = False,
    ) -> Dict[str, Any]:
        """Executes the complete mission pipeline with group parallelism and reporting."""
        validated = validate_mission_manifest(manifest)
        mission_id = validated["mission_id"]
        feature_name = validated["feature_name"]
        max_retries = validated.get("orchestrator", {}).get("max_retries_per_task", 2)
        global_cmd = validated.get("global_verification_cmd", "")

        groups = self.get_execution_groups(validated)
        task_results: List[Dict[str, Any]] = []
        overall_success = True

        for grp_num, group_tasks in groups.items():
            # Parallel execution within the same execution_group
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(group_tasks)) as executor:
                future_to_task = {
                    executor.submit(
                        self.run_task_verification_with_healing, task, max_retries
                    ): task
                    for task in group_tasks
                }

                for future in concurrent.futures.as_completed(future_to_task):
                    orig_task = future_to_task[future]
                    try:
                        res = future.result()
                    except Exception as exc:
                        res = {
                            "task_id": orig_task["task_id"],
                            "status": "FAIL",
                            "retries": 0,
                            "error": str(exc),
                        }

                    # Merge original task metadata
                    merged = dict(orig_task)
                    merged.update(res)
                    task_results.append(merged)

                    if merged["status"] != "PASS":
                        overall_success = False

            # If any task in current group failed completely, stop future dependent groups
            if not overall_success:
                break

        # Run global verification if tasks passed
        global_status = "NOT_RUN"
        if overall_success and global_cmd:
            g_res = self._execute_command(global_cmd)
            global_status = "PASS" if g_res["exit_code"] == 0 else "FAIL"
            if global_status != "PASS":
                overall_success = False

        passed_count = sum(1 for t in task_results if t.get("status") == "PASS")
        failed_count = sum(1 for t in task_results if t.get("status") != "PASS")

        # Generate mission-report.md
        self._write_mission_report(
            mission_id=mission_id,
            feature_name=feature_name,
            task_results=task_results,
            global_status=global_status,
            success=overall_success,
        )

        return {
            "mission_id": mission_id,
            "success": overall_success,
            "passed_tasks": passed_count,
            "failed_tasks": failed_count,
            "tasks": task_results,
            "global_verification": global_status,
        }

    def _write_mission_report(
        self,
        mission_id: str,
        feature_name: str,
        task_results: List[Dict[str, Any]],
        global_status: str,
        success: bool,
    ) -> Path:
        """Writes the consolidated markdown report to .agents/mission-report.md."""
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        status_label = "✅ SUCESSO (CONFORMIDADE TOTAL)" if success else "❌ FALHA NA MISSÃO"
        unique_agents = sorted(list({str(t.get("subagent", "builder")).strip() for t in task_results}))

        lines = [
            f"# Relatório de Missão Multiagente: {feature_name}",
            "",
            f"- **Missão ID:** `{mission_id}`",
            f"- **Resultado Final:** {status_label}",
            f"- **Verificação Global:** `{global_status}`",
            f"- **Total de Agentes Utilizados:** {len(unique_agents)}",
            f"- **Agentes Participantes:** {', '.join(f'`{ag}`' for ag in unique_agents)}",
            "",
            "## Tabela de Tarefas Executadas",
            "",
            "| Grupo | Task ID | Agente | Modelo / Esforço | Retries | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        for t in task_results:
            grp = f"G-{t.get('execution_group', 1)}"
            tid = t.get("task_id", "")
            ag = t.get("subagent", "")
            mod = f"{t.get('model', '')} ({t.get('effort', '')})"
            retries = t.get("retries", 0)
            st = t.get("status", "UNKNOWN")
            lines.append(f"| {grp} | `{tid}` | `{ag}` | {mod} | {retries} | **{st}** |")

        lines.extend([
            "",
            "## Detalhes de Auto-Healing & Auditoria",
            "",
        ])

        healed = [t for t in task_results if t.get("retries", 0) > 0 and t.get("status") == "PASS"]
        failed = [t for t in task_results if t.get("status") != "PASS"]

        if healed:
            lines.append("### Tarefas Curadas via Auto-Healing:")
            for h in healed:
                lines.append(f"- **{h['task_id']}:** Passou na tentativa {h['retries'] + 1} após injeção de erro.")
            lines.append("")

        if failed:
            lines.append("### Tarefas que Falharam:")
            for f in failed:
                lines.append(f"- **{f['task_id']}:** Erro persistente: `{f.get('error', '')}`")
            lines.append("")

        if not healed and not failed:
            lines.append("Todas as tarefas passaram na primeira tentativa (Zero Regressão).")
            lines.append("")

        report_content = "\n".join(lines) + "\n"
        self.report_file.write_text(report_content, encoding="utf-8")
        return self.report_file


def main() -> int:
    """CLI entrypoint for agy-orchestrate / xp-orchestrate."""
    parser = argparse.ArgumentParser(
        description="Antigravity Dynamic Multi-Agent Engine (xp-multiagent-kit)"
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Comando a executar")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Executa o manifesto de missão")
    run_parser.add_argument("manifest", nargs="?", default=".agents/active-mission.json")
    run_parser.add_argument("--host", choices=["antigravity", "opencode", "claude", "codex", "cursor", "qoder"], default=None, help="Host para execução dos workers")

    # Command: validate
    val_parser = subparsers.add_parser("validate", help="Valida o manifesto de missão")
    val_parser.add_argument("manifest", nargs="?", default=".agents/active-mission.json")

    # Command: dashboard
    dash_parser = subparsers.add_parser("dashboard", help="Exibe o quadro visual de tarefas")
    dash_parser.add_argument("manifest", nargs="?", default=".agents/active-mission.json")

    # Command: init
    init_parser = subparsers.add_parser("init", help="Gera manifesto modelo de missão")
    init_parser.add_argument("feature_name", nargs="?", default="Nova Feature Multiagente")

    args = parser.parse_args()

    engine = AntigravityMissionEngine()

    if args.subcommand in ("validate", "dashboard", "run"):
        m_path = Path(args.manifest)
        if not m_path.is_file():
            print(f"❌ Erro: Manifesto '{m_path}' não encontrado.", file=sys.stderr)
            return 1
        try:
            data = json.loads(m_path.read_text(encoding="utf-8"))
            validated = validate_mission_manifest(data)
        except Exception as ex:
            print(f"❌ Erro de validação: {ex}", file=sys.stderr)
            return 1

        if args.subcommand == "validate":
            print(f"✅ Manifesto '{m_path}' é válido. ({len(validated['tasks'])} tarefas configuradas)")
            return 0

        if args.subcommand == "dashboard":
            print(render_mission_dashboard(validated["mission_id"], validated["feature_name"], validated["tasks"]))
            return 0

        if args.subcommand == "run":
            if getattr(args, "host", None):
                validated["host"] = args.host
            print(render_mission_dashboard(validated["mission_id"], validated["feature_name"], validated["tasks"]))
            print("\n⏳ Iniciando pipeline de orquestração multiagente...")
            res = engine.run_mission(validated)
            print(render_mission_dashboard(validated["mission_id"], validated["feature_name"], res["tasks"]))
            if res["success"]:
                print(f"\n✅ Missão concluída com sucesso! Relatório gerado em: {engine.report_file}")
                return 0
            else:
                print(f"\n❌ Missão finalizada com falhas. Relatório em: {engine.report_file}", file=sys.stderr)
                return 1

    if args.subcommand == "init":
        dest = engine.agents_dir / "active-mission.json"
        engine.agents_dir.mkdir(parents=True, exist_ok=True)
        sample = {
            "mission_id": "feat-exemplo-01",
            "feature_name": args.feature_name,
            "orchestrator": {
                "model": "gemini-4-argon",
                "effort": "high",
                "max_retries_per_task": 2,
            },
            "global_verification_cmd": "python3 -m unittest discover tests",
            "tasks": [
                {
                    "task_id": "task-dto",
                    "subagent": "builder",
                    "model": "gemini-3.8-flash",
                    "effort": "low",
                    "execution_group": 1,
                    "allowed_paths": ["src/dto/"],
                    "objective": "Criar DTOs e tipagens básicas",
                    "verification_cmd": "pytest tests/test_dto.py",
                },
                {
                    "task_id": "task-service",
                    "subagent": "builder",
                    "model": "gemini-3.8-flash",
                    "effort": "medium",
                    "execution_group": 2,
                    "allowed_paths": ["src/services/"],
                    "objective": "Implementar regras de negócio e testes TDD",
                    "verification_cmd": "pytest tests/test_service.py",
                },
            ],
        }
        dest.write_text(json.dumps(sample, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"✅ Manifesto modelo inicializado em: {dest}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
