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


def should_skip_duplicate_injection(
    conv_id: str,
    prompt_hash: str,
    cache_dir: Optional[Path] = None,
    ttl_seconds: float = 300.0,
) -> bool:
    """
    AC-6: Prevents re-injecting ephemeralMessage on subsequent tool steps within the same user prompt.
    Keyed strictly by (conv_id, prompt_hash) so multi-step tool calls in the same turn skip re-injection.
    """
    now = time.time()
    base_dir = cache_dir or Path(tempfile.gettempdir())
    safe_conv = re.sub(r"[^a-zA-Z0-9_-]", "_", conv_id or "default")
    dedup_file = base_dir / f".agy_effort_prompt_{safe_conv}_{prompt_hash}.lock"
    if dedup_file.is_file():
        try:
            data = json.loads(dedup_file.read_text(encoding="utf-8").strip())
            last_time = float(data.get("time", 0.0))
            if (now - last_time) < ttl_seconds:
                return True
        except Exception:
            pass
    try:
        dedup_file.write_text(json.dumps({"prompt_hash": prompt_hash, "time": now}), encoding="utf-8")
    except Exception:
        pass
    return False


def sync_dynamic_skill_profile(risk_level: str, prompt_text: str) -> Optional[str]:
    """Removido conforme AC-8 e AC-9 do SPEC-006 (perfil estático por stack)."""
    return None


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

    conv_id = payload.get("conversationId", "default")
    tpath = payload.get("transcriptPath", "")
    tpath_hash = hashlib.md5(tpath.encode("utf-8")).hexdigest()[:8] if tpath else "notrans"
    prompt_hash = hashlib.md5(f"{tpath_hash}:{prompt_text}".encode("utf-8")).hexdigest()[:12] if prompt_text else f"{tpath_hash}_noprompt"

    if should_skip_duplicate_injection(conv_id, prompt_hash):
        return {"injectSteps": []}

    if should_emit_badge(conv_id, decision.effort):
        try:
            badge = format_badge(decision)
            if badge:
                sys.stderr.write(badge + "\n")
                sys.stderr.flush()
        except Exception:
            pass

    effort_upper = decision.effort.upper()
    risk_code = decision.risk_level.split()[0] if decision.risk_level else "L1"
    
    # Recupera contexto JIT automaticamente se for tarefa L1, L2 ou L3 (teto de 80 tokens, AC-9)
    jit_summary = ""
    if decision.risk_level != "L0 (Trivial)" and prompt_text:
        try:
            from scripts.context_retriever import get_jit_context, format_jit_prompt
            jit_items = get_jit_context(
                workspace=PROJECT_ROOT,
                query=prompt_text,
                max_items=1,
                token_budget=80,
            )
            if jit_items:
                jit_summary = f" | jit: JIT Memory ({jit_items[0].get('title', '')})"
        except Exception:
            pass

    # Mensagem efêmera compacta <= 400 bytes (AC-9, B09)
    eff_tier = "n/a"
    try:
        from scripts.xp_contract import load_contract
        from scripts.hooks.pre_tool_guard import calculate_effective_tier
        c = load_contract()
        if c and c.get("risk"):
            from scripts.xp_gate import get_git_diff_files
            eff_tier = calculate_effective_tier(c.get("risk", "L1"), get_git_diff_files(), [])
    except Exception:
        eff_tier = "n/a"

    ephemeral_msg = f"[xp] risk={risk_code} effort={effort_upper} tier={eff_tier} | {decision.reason[:100]}{jit_summary}"
    encoded = ephemeral_msg.encode("utf-8")
    if len(encoded) > 400:
        ephemeral_msg = encoded[:397].decode("utf-8", errors="ignore") + "..."

    return {
        "injectSteps": [
            {
                "ephemeralMessage": ephemeral_msg
            }
        ]
    }


def auto_heal_plugin_directories() -> None:
    """Garante que diretórios exigidos por plugins internos do Antigravity existam para evitar falhas em hooks."""
    try:
        target = Path.home() / ".gemini" / "config" / "plugins" / "googlecloudtools.datacloud_telemetry"
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def main() -> int:
    auto_heal_plugin_directories()
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
