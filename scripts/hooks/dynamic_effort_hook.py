#!/usr/bin/env python3
"""
scripts/hooks/dynamic_effort_hook.py
PreInvocation Hook do Antigravity CLI para Modulação Dinâmica de Reasoning Effort.
Analisa a última mensagem do usuário (USER_INPUT) no transcript, classifica o risco
da tarefa (L0-L3), sincroniza os settings.json e injeta diretrizes de esforço via ephemeralMessage.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from scripts.agy_effort_router import (
        classify_task_effort,
        detect_git_context,
        get_token_budget_status,
        sync_global_settings,
        format_badge,
        EFFORT_LOW,
        EFFORT_MEDIUM,
        EFFORT_HIGH,
    )
except ImportError:
    # Fallback simplificado se import falhar
    def classify_task_effort(*args, **kwargs):
        class Dummy:
            effort = "medium"
            risk_level = "L1 (Small)"
            reason = "Fallback"
        return Dummy()

    def detect_git_context(): return {}
    def get_token_budget_status(): return {}
    def sync_global_settings(effort): return []
    def format_badge(d): return ""


def extract_latest_user_prompt(transcript_path: str) -> str:
    """Extrai o texto mais recente enviado pelo usuário do transcript.jsonl."""
    if not transcript_path or not os.path.isfile(transcript_path):
        return ""

    last_user_content = ""
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "USER_INPUT":
                        last_user_content = entry.get("content", "")
                except Exception:
                    continue
    except Exception:
        return ""

    if not last_user_content:
        return ""

    # Extrai conteúdo de <USER_REQUEST> se presente
    req_match = re.search(r"<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>", last_user_content, re.DOTALL)
    if req_match:
        prompt_text = req_match.group(1).strip()
    else:
        prompt_text = last_user_content.strip()

    # Remove metadados adicionais
    prompt_text = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", prompt_text, flags=re.DOTALL)
    prompt_text = re.sub(r"<USER_SETTINGS_CHANGE>.*?</USER_SETTINGS_CHANGE>", "", prompt_text, flags=re.DOTALL)

    return prompt_text.strip()


def handle_pre_invocation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Processa o evento PreInvocation do Antigravity CLI."""
    transcript_path = payload.get("transcriptPath", "")
    prompt_text = extract_latest_user_prompt(transcript_path)

    # Classifica o esforço com base no prompt real do turno
    git_ctx = detect_git_context()
    budget = get_token_budget_status()
    decision = classify_task_effort(
        prompt=prompt_text,
        git_context=git_ctx,
        token_budget=budget,
    )

    # Sincroniza silenciosamente os arquivos de settings (CLI e IDE)
    try:
        sync_global_settings(decision.effort)
    except Exception:
        pass

    # Exibe badge informativo no terminal CLI (via stderr)
    try:
        badge = format_badge(decision)
        if badge:
            sys.stderr.write(badge + "\n")
            sys.stderr.flush()
    except Exception:
        pass

    # Monta a diretriz de execução ephemeral para orientar o modelo neste turno
    effort_upper = decision.effort.upper()
    if decision.effort == "high":
        guidance = "Operar em modo HIGH: máxima profundidade analítica, matriz TDD estrita, sem workarounds e com reflexão arquitetural completa."
    elif decision.effort == "low":
        guidance = "Operar em modo LOW: resposta direta, concisa e enxuta, sem prolixidade e estritamente Zero-Tool para consultas teóricas/conceituais."
    else:
        guidance = "Operar em modo MEDIUM: equilíbrio entre eficiência de tokens e análise metódica."

    ephemeral_msg = (
        f"⚡ [AGY-EFFORT-ACTIVE] Modulação Automática Ativa: {effort_upper} "
        f"| Risco: {decision.risk_level} | Motivo: {decision.reason}\n"
        f"🎯 Diretriz de Execução: {guidance}"
    )

    return {
        "injectSteps": [
            {
                "ephemeralMessage": ephemeral_msg
            }
        ]
    }


def main() -> int:
    try:
        raw_input = sys.stdin.read() if not sys.stdin.isatty() else ""
        if raw_input.strip():
            payload = json.loads(raw_input)
            result = handle_pre_invocation(payload)
        else:
            result = {"injectSteps": []}
    except Exception:
        result = {"injectSteps": []}

    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
