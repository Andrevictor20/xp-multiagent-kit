#!/usr/bin/env python3
"""
scripts/hooks/dynamic_effort_hook.py
PreInvocation Hook do Antigravity CLI para Modulação Dinâmica de Reasoning Effort.
Analisa a última mensagem do usuário (USER_INPUT) no transcript, classifica o risco
da tarefa (L0-L3), sincroniza os settings.json e injeta diretrizes de esforço via ephemeralMessage.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

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
        LEVEL_L0_TRIVIAL,
        LEVEL_L1_SMALL,
        LEVEL_L2_FEATURE,
        LEVEL_L3_CRITICAL,
        CONTINUATION_PATTERNS,
        DIRECTIVE_HIGH_PATTERNS,
        DIRECTIVE_LOW_PATTERNS,
        DIRECTIVE_MEDIUM_PATTERNS,
    )
except ImportError:
    # Fallback simplificado se import falhar
    def classify_task_effort(*args, **kwargs):
        class Dummy:
            effort = "medium"
            risk_level = "L1 (Small)"
            reason = "Fallback"
            override = False
        return Dummy()

    def detect_git_context(): return {}
    def get_token_budget_status(): return {}
    def sync_global_settings(effort): return []
    def format_badge(d): return ""
    EFFORT_LOW = "low"
    EFFORT_MEDIUM = "medium"
    EFFORT_HIGH = "high"
    LEVEL_L0_TRIVIAL = "L0 (Trivial)"
    LEVEL_L1_SMALL = "L1 (Small)"
    LEVEL_L2_FEATURE = "L2 (Feature)"
    LEVEL_L3_CRITICAL = "L3 (Critical)"
    CONTINUATION_PATTERNS = []
    DIRECTIVE_HIGH_PATTERNS = []
    DIRECTIVE_LOW_PATTERNS = []
    DIRECTIVE_MEDIUM_PATTERNS = []


def clean_user_prompt(raw_content: str) -> str:
    """Limpa tags de envelope do prompt do usuário."""
    if not raw_content:
        return ""
    req_match = re.search(r"<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>", raw_content, re.DOTALL)
    if req_match:
        text = req_match.group(1).strip()
    else:
        text = raw_content.strip()

    text = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", text, flags=re.DOTALL)
    text = re.sub(r"<USER_SETTINGS_CHANGE>.*?</USER_SETTINGS_CHANGE>", "", text, flags=re.DOTALL)
    return text.strip()


def extract_conversation_context(transcript_path: str) -> Dict[str, Any]:
    """Extrai contexto multi-turn da conversa a partir do transcript.jsonl."""
    context: Dict[str, Any] = {
        "latest_user_prompt": "",
        "all_user_prompts": [],
        "cumulative_text": "",
        "is_continuation": False,
        "active_risk": "",
    }

    if not transcript_path or not os.path.isfile(transcript_path):
        return context

    all_prompts: List[str] = []
    last_planner_content = ""

    try:
        with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    etype = entry.get("type")
                    if etype == "USER_INPUT":
                        cleaned = clean_user_prompt(entry.get("content", ""))
                        if cleaned:
                            all_prompts.append(cleaned)
                    elif etype == "PLANNER_RESPONSE":
                        last_planner_content = entry.get("content", "")
                except Exception:
                    continue
    except Exception:
        return context

    if not all_prompts:
        return context

    latest_prompt = all_prompts[-1]
    context["latest_user_prompt"] = latest_prompt
    context["all_user_prompts"] = all_prompts
    # Texto cumulativo sem o prompt atual
    prior_prompts = all_prompts[:-1]
    context["cumulative_text"] = "\n".join(prior_prompts)

    # Detecção de continuação / confirmação
    p_lower = latest_prompt.lower()
    is_cont = any(re.search(pat, p_lower) for pat in CONTINUATION_PATTERNS)
    if len(p_lower) < 60 and ("continue" in p_lower or "prossiga" in p_lower or "mude" in p_lower or "coloque" in p_lower or "sim" in p_lower or "ok" in p_lower):
        is_cont = True
    context["is_continuation"] = is_cont

    # Detecção de risco no último output do planner (ex: Stop Gate / Risco L3 / Risco L2)
    if last_planner_content:
        lp_lower = last_planner_content.lower()
        if "l3" in lp_lower or "critical" in lp_lower or "stop gate" in lp_lower:
            context["active_risk"] = LEVEL_L3_CRITICAL
        elif "l2" in lp_lower or "feature" in lp_lower:
            context["active_risk"] = LEVEL_L2_FEATURE
        elif "l1" in lp_lower or "small" in lp_lower:
            context["active_risk"] = LEVEL_L1_SMALL
        elif "l0" in lp_lower or "trivial" in lp_lower:
            context["active_risk"] = LEVEL_L0_TRIVIAL

    return context


def extract_latest_user_prompt(transcript_path: str) -> str:
    """Extrai o texto mais recente enviado pelo usuário do transcript.jsonl (compatibilidade)."""
    ctx = extract_conversation_context(transcript_path)
    return ctx.get("latest_user_prompt", "")


def should_emit_badge(conv_id: str, effort: str) -> bool:
    """Evita duplicar badges no stderr no mesmo turno/segundo entre processos."""
    now = time.time()
    safe_conv = re.sub(r"[^a-zA-Z0-9_-]", "_", conv_id or "default")
    lock_file = Path(tempfile.gettempdir()) / f".agy_effort_badge_{safe_conv}.json"
    key = f"{conv_id}_{effort}"
    try:
        if lock_file.is_file():
            data = json.loads(lock_file.read_text(encoding="utf-8"))
            last_key = data.get("key", "")
            last_ts = float(data.get("ts", 0.0))
            if last_key == key and (now - last_ts) < 5.0:
                return False
        lock_file.write_text(json.dumps({"key": key, "ts": now}), encoding="utf-8")
        return True
    except Exception:
        return True


def handle_pre_invocation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Processa o evento PreInvocation do Antigravity CLI."""
    transcript_path = payload.get("transcriptPath", "")
    conv_ctx = extract_conversation_context(transcript_path)
    prompt_text = conv_ctx["latest_user_prompt"]

    # Classifica o esforço com base no contexto completo
    git_ctx = detect_git_context()
    budget = get_token_budget_status()
    decision = classify_task_effort(
        prompt=prompt_text,
        git_context=git_ctx,
        token_budget=budget,
        conversation_context=conv_ctx,
    )

    # Sincroniza silenciosamente os arquivos de settings (CLI e IDE)
    try:
        sync_global_settings(decision.effort)
    except Exception:
        pass

    # Exibe badge informativo no terminal CLI (via stderr), deduplicado
    conv_id = payload.get("conversationId", "default")
    inv_num = payload.get("invocationNum", 0)

    # Evita dupla injeção se o hook for executado por múltiplos hooks.json (global e workspace)
    # ou em sub-etapas consecutivas (invocations) dentro do mesmo turno/prompt
    tpath = payload.get("transcriptPath", "")
    tpath_hash = hashlib.md5(tpath.encode("utf-8")).hexdigest()[:8] if tpath else "notrans"
    prompt_hash = hashlib.md5(prompt_text.encode("utf-8")).hexdigest()[:8] if prompt_text else "noprompt"
    safe_conv = re.sub(r"[^a-zA-Z0-9_-]", "_", conv_id or "default")
    dedup_file = Path(tempfile.gettempdir()) / f".agy_effort_injected_{safe_conv}_{tpath_hash}_{prompt_hash}.lock"
    already_injected = False
    now = time.time()
    if dedup_file.is_file():
        try:
            mtime = dedup_file.stat().st_mtime
            if (now - mtime) < 600.0:
                already_injected = True
        except Exception:
            pass

    if already_injected:
        return {"injectSteps": []}

    try:
        dedup_file.write_text(str(now), encoding="utf-8")
    except Exception:
        pass

    if should_emit_badge(conv_id, decision.effort):
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

    # Obtém o bloco oficial de telemetria ao vivo via Language Server RPC
    live_footer = ""
    try:
        from scripts.token_tracker import (
            find_active_session, load_transcript, calculate_turn_stats,
            detect_model_name, parse_transcript_data, format_message_footer
        )
        t_path = Path(transcript_path) if transcript_path and os.path.isfile(transcript_path) else None
        if not t_path:
            _, t_path, _ = find_active_session()
        steps = load_transcript(t_path) if t_path else []
        turn = calculate_turn_stats(steps)
        model_name = detect_model_name(conv_id, steps)
        stats = parse_transcript_data(conv_id, model_name, steps, fetch_live=True, effort=decision.effort)
        live_footer = format_message_footer(stats, turn)
    except Exception:
        live_footer = ""

    ephemeral_msg = (
        f"⚡ [AGY-EFFORT-ACTIVE] Modulação Automática Ativa: {effort_upper} "
        f"| Risco: {decision.risk_level} | Motivo: {decision.reason}\n"
        f"🎯 Diretriz de Execução: {guidance}"
    )
    if live_footer:
        ephemeral_msg += (
            f"\n\n📋 TELEMETRIA AO VIVO OFICIAL DESTE TURNO (Language Server RPC):\n"
            f"OBRIGATÓRIO: Copie e cole com exatidão matemática o bloco abaixo como rodapé final da sua resposta:\n"
            f"{live_footer}"
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
