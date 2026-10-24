#!/usr/bin/env python3
"""
scripts/multiagent_drivers.py
Host-Agnostic Worker Drivers for Dynamic Multi-Agent Engine (SPEC-004).
Provides execution abstraction across Antigravity, OpenCode, Claude, Codex, Cursor, and Qoder.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseWorkerDriver(ABC):
    """Abstract base driver for formatting worker commands and subagent payloads."""

    @abstractmethod
    def build_worker_payload(
        self, task: Dict[str, Any], shared_memory: str = ""
    ) -> Dict[str, Any]:
        """Builds a dictionary payload representing the task for this host."""
        pass

    @abstractmethod
    def build_worker_command(
        self, task: Dict[str, Any], shared_memory: str = ""
    ) -> List[str]:
        """Builds a CLI command list to execute this worker headlessly, if supported."""
        pass


class AntigravityWorkerDriver(BaseWorkerDriver):
    """Worker driver for native Antigravity invoke_subagent orchestration."""

    def build_worker_payload(
        self, task: Dict[str, Any], shared_memory: str = ""
    ) -> Dict[str, Any]:
        subagent_type = str(task.get("subagent", "builder")).strip().lower()

        raw_model = str(task.get("model", "gemini-3.8-flash")).lower()
        if "flash" in raw_model:
            model_arg = "flash"
            model_display = "Flash"
        elif "pro" in raw_model or "argon" in raw_model:
            model_arg = "pro"
            model_display = "Argon"
        else:
            model_arg = "inherit"
            model_display = "Inherit"

        effort = str(task.get("effort", "medium")).lower()
        role_desc = f"[{model_display.upper()} {effort.upper()}] {task.get('task_id', '')}"

        paths_str = ", ".join(task.get("allowed_paths", ["src/"]))
        prompt_sections = [
            f"Missão: {task.get('objective', '')}",
            f"Modelo Alocado: {model_display} | Esforço de Raciocínio: {effort.upper()}",
            f"Escopo Permitido de Arquivos (allowed_paths): {paths_str}",
            f"Comando de Verificação Obrigatório (TDD/Gate): {task.get('verification_cmd', '')}",
            "Diretrizes Estritas de Engenharia:",
            "- Respeite estritamente o isolamento de pastas. Nunca altere arquivos fora do seu escopo.",
            "- Siga o ciclo estrito de TDD (RED -> GREEN -> REFACTOR).",
            "- Valide seu código rodando o comando de verificação antes de finalizar.",
        ]

        if shared_memory:
            prompt_sections.append(
                f"\n--- CONTRATOS COMPARTILHADOS (.agents/MEMORY.md) ---\n{shared_memory}"
            )

        return {
            "TypeName": subagent_type,
            "Role": role_desc,
            "Model": model_arg,
            "Workspace": "branch",
            "Prompt": "\n".join(prompt_sections),
        }

    def build_worker_command(
        self, task: Dict[str, Any], shared_memory: str = ""
    ) -> List[str]:
        # Antigravity workers are dispatched via native IDE/CLI tool calls rather than a subprocess CLI
        return ["agy-orchestrate", "run", "--task", str(task.get("task_id", ""))]


class OpenCodeWorkerDriver(BaseWorkerDriver):
    """Worker driver for OpenCode headless CLI execution (opencode run)."""

    def _resolve_model(self, raw_model: str) -> str:
        low = raw_model.strip().lower()
        if "/" in low:
            return raw_model
        if "flash" in low:
            return "google/gemini-3.8-flash"
        if "argon" in low or "pro" in low:
            return "google/gemini-4-argon"
        if "haiku" in low:
            return "openrouter/anthropic/claude-haiku-4.5"
        if "sonnet" in low:
            return "openrouter/anthropic/claude-sonnet-4.6"
        return "google/gemini-3.8-flash"

    def _build_prompt(self, task: Dict[str, Any], shared_memory: str = "") -> str:
        paths_str = ", ".join(task.get("allowed_paths", ["src/"]))
        prompt_sections = [
            f"Missão: {task.get('objective', '')}",
            f"Agente Designado: {task.get('subagent', 'builder')}",
            f"Escopo Permitido de Arquivos (allowed_paths): {paths_str}",
            f"Comando de Verificação Obrigatório (TDD/Gate): {task.get('verification_cmd', '')}",
            "Diretrizes Estritas de Engenharia:",
            "- Respeite estritamente o isolamento de pastas. Nunca altere arquivos fora do seu escopo.",
            "- Siga o ciclo estrito de TDD (RED -> GREEN -> REFACTOR).",
            "- Valide seu código rodando o comando de verificação antes de finalizar.",
            "- Responda exclusivamente em Português (PT-BR).",
        ]

        if shared_memory:
            prompt_sections.append(
                f"\n--- CONTRATOS COMPARTILHADOS (.agents/MEMORY.md) ---\n{shared_memory}"
            )

        return "\n".join(prompt_sections)

    def build_worker_command(
        self, task: Dict[str, Any], shared_memory: str = ""
    ) -> List[str]:
        subagent = str(task.get("subagent", "builder")).strip().lower()
        model = self._resolve_model(str(task.get("model", "gemini-3.8-flash")))
        prompt = self._build_prompt(task, shared_memory)

        return [
            "opencode",
            "run",
            "--agent",
            subagent,
            "--model",
            model,
            "--auto",
            "--format",
            "json",
            prompt,
        ]

    def build_worker_payload(
        self, task: Dict[str, Any], shared_memory: str = ""
    ) -> Dict[str, Any]:
        subagent = str(task.get("subagent", "builder")).strip().lower()
        cmd = self.build_worker_command(task, shared_memory)
        return {
            "host": "opencode",
            "agent": subagent,
            "model": self._resolve_model(str(task.get("model", "gemini-3.8-flash"))),
            "command": cmd,
            "prompt": cmd[-1],
        }


class ClaudeWorkerDriver(BaseWorkerDriver):
    """Worker driver for Claude Code CLI headless execution (claude -p)."""

    def _resolve_model(self, raw_model: str) -> str:
        low = raw_model.strip().lower()
        if "haiku" in low or "flash" in low:
            return "haiku"
        if "opus" in low:
            return "opus"
        if "sonnet" in low or "argon" in low or "pro" in low:
            return "sonnet"
        return "haiku"

    def _build_prompt(self, task: Dict[str, Any], shared_memory: str = "") -> str:
        paths_str = ", ".join(task.get("allowed_paths", ["src/"]))
        prompt_sections = [
            f"Missão: {task.get('objective', '')}",
            f"Subagente Designado: {task.get('subagent', 'builder')}",
            f"Escopo Permitido de Arquivos (allowed_paths): {paths_str}",
            f"Comando de Verificação Obrigatório (TDD/Gate): {task.get('verification_cmd', '')}",
            "Diretrizes Estritas de Engenharia:",
            "- Respeite estritamente o isolamento de pastas. Nunca altere arquivos fora do seu escopo.",
            "- Siga o ciclo estrito de TDD (RED -> GREEN -> REFACTOR).",
            "- Valide seu código rodando o comando de verificação antes de finalizar.",
            "- Responda exclusivamente em Português (PT-BR).",
        ]

        if shared_memory:
            prompt_sections.append(
                f"\n--- CONTRATOS COMPARTILHADOS (.agents/MEMORY.md) ---\n{shared_memory}"
            )

        return "\n".join(prompt_sections)

    def build_worker_command(
        self, task: Dict[str, Any], shared_memory: str = ""
    ) -> List[str]:
        subagent = str(task.get("subagent", "builder")).strip().lower()
        model = self._resolve_model(str(task.get("model", "flash")))
        effort = str(task.get("effort", "low")).lower()
        prompt = self._build_prompt(task, shared_memory)
        task_id = str(task.get("task_id", "default")).strip()

        return [
            "claude",
            "-p",
            prompt,
            "--model",
            model,
            "--effort",
            effort,
            "--permission-mode",
            "bypassPermissions",
            "--worktree",
            f"worker-{task_id}",
            "--output-format",
            "json",
        ]

    def build_worker_payload(
        self, task: Dict[str, Any], shared_memory: str = ""
    ) -> Dict[str, Any]:
        subagent = str(task.get("subagent", "builder")).strip().lower()
        model = self._resolve_model(str(task.get("model", "flash")))
        effort = str(task.get("effort", "low")).lower()
        cmd = self.build_worker_command(task, shared_memory)
        return {
            "host": "claude",
            "agent": subagent,
            "model": model,
            "effort": effort,
            "command": cmd,
            "prompt": cmd[2],
        }


class CodexWorkerDriver(BaseWorkerDriver):
    """Worker driver for OpenAI Codex CLI headless execution (codex exec)."""

    def _resolve_model(self, raw_model: str) -> str:
        low = raw_model.strip().lower()
        if "terra" in low or "argon" in low or "pro" in low or "o1" in low or "o3" in low:
            return "gpt-5.6-terra"
        if "luna" in low or "flash" in low or "mini" in low:
            return "gpt-5.6-luna"
        return "gpt-5.6-luna"

    def _build_prompt(self, task: Dict[str, Any], shared_memory: str = "") -> str:
        paths_str = ", ".join(task.get("allowed_paths", ["src/"]))
        prompt_sections = [
            f"Missão: {task.get('objective', '')}",
            f"Subagente Designado: {task.get('subagent', 'builder')}",
            f"Escopo Permitido de Arquivos (allowed_paths): {paths_str}",
            f"Comando de Verificação Obrigatório (TDD/Gate): {task.get('verification_cmd', '')}",
            "Diretrizes Estritas de Engenharia:",
            "- Respeite estritamente o isolamento de pastas. Nunca altere arquivos fora do seu escopo.",
            "- Siga o ciclo estrito de TDD (RED -> GREEN -> REFACTOR).",
            "- Valide seu código rodando o comando de verificação antes de finalizar.",
            "- Responda exclusivamente em Português (PT-BR).",
        ]

        if shared_memory:
            prompt_sections.append(
                f"\n--- CONTRATOS COMPARTILHADOS (.agents/MEMORY.md) ---\n{shared_memory}"
            )

        return "\n".join(prompt_sections)

    def build_worker_command(
        self, task: Dict[str, Any], shared_memory: str = ""
    ) -> List[str]:
        subagent = str(task.get("subagent", "builder")).strip().lower()
        model = self._resolve_model(str(task.get("model", "flash")))
        effort = str(task.get("effort", "low")).lower()
        prompt = self._build_prompt(task, shared_memory)
        task_id = str(task.get("task_id", "default")).strip()

        return [
            "codex",
            "exec",
            prompt,
            "-m",
            model,
            "-c",
            f'model_reasoning_effort="{effort}"',
            "--sandbox",
            "workspace-write",
            "--approve-for-me",
            "--worktree",
            "--ephemeral",
            "-o",
            f".agents/runtime/worker_{task_id}.md",
        ]

    def build_worker_payload(
        self, task: Dict[str, Any], shared_memory: str = ""
    ) -> Dict[str, Any]:
        subagent = str(task.get("subagent", "builder")).strip().lower()
        model = self._resolve_model(str(task.get("model", "flash")))
        effort = str(task.get("effort", "low")).lower()
        cmd = self.build_worker_command(task, shared_memory)
        return {
            "host": "codex",
            "agent": subagent,
            "model": model,
            "effort": effort,
            "command": cmd,
            "prompt": cmd[2],
        }


def get_worker_driver(host: Optional[str] = None) -> BaseWorkerDriver:
    """Factory function returning the specialized worker driver for a target host."""
    resolved = str(host or "antigravity").strip().lower()
    if resolved == "opencode":
        return OpenCodeWorkerDriver()
    if resolved == "claude":
        return ClaudeWorkerDriver()
    if resolved == "codex":
        return CodexWorkerDriver()
    return AntigravityWorkerDriver()
