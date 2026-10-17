#!/usr/bin/env python3
"""
scripts/telemetry/reports.py
Detailed Markdown reporting, JSON dumps, dashboards, and budget audits for Token Telemetry.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional, Tuple

from scripts.telemetry.models import (
    TokenStats,
    TurnStats,
    get_model_display_name,
    human_tokens,
)
from scripts.telemetry.quota_rpc import clean_refresh_text


def _extract_quota_metrics(stats: TokenStats) -> Tuple[bool, float, float, str, float, float, str]:
    """Returns (is_live, pct_5h_used, pct_5h_rem, desc_5h, pct_7d_used, pct_7d_rem, desc_7d)."""
    if stats.live_quota and stats.live_quota.is_live:
        model_lower = (stats.model_name or "").lower()
        is_argon = "argon" in model_lower
        is_claude = "claude" in model_lower or "gpt" in model_lower

        if is_argon and getattr(stats.live_quota, "gemini_argon_weekly", None):
            b_5h = stats.live_quota.gemini_5h
            b_7d = stats.live_quota.gemini_argon_weekly
        elif is_claude:
            b_5h = stats.live_quota.claude_5h
            b_7d = stats.live_quota.claude_weekly
        else:
            b_5h = stats.live_quota.gemini_5h
            b_7d = stats.live_quota.gemini_weekly

        pct_5h_rem = (b_5h.remaining_fraction * 100.0) if b_5h else 100.0
        pct_7d_rem = (b_7d.remaining_fraction * 100.0) if b_7d else 100.0
        pct_5h_used = max(0.0, 100.0 - pct_5h_rem)
        pct_7d_used = max(0.0, 100.0 - pct_7d_rem)

        desc_5h = clean_refresh_text(b_5h.description) if b_5h else ""
        desc_7d = clean_refresh_text(b_7d.description) if b_7d else ""
        return True, pct_5h_used, pct_5h_rem, desc_5h, pct_7d_used, pct_7d_rem, desc_7d
    return False, 0.0, 0.0, "", 0.0, 0.0, ""


def format_json_stats(stats: TokenStats) -> str:
    """Exports structured TokenStats into machine-readable JSON."""
    display_model = get_model_display_name(stats.model_name)
    payload: Dict[str, Any] = {
        "conversation_id": stats.conversation_id,
        "model": stats.model_name,
        "model_display_name": display_model,
        "effort": stats.effort,
        "model_limits": {
            "context_window": stats.context_window,
            "max_output": stats.max_output,
            "context_window_human": human_tokens(stats.context_window),
            "max_output_human": human_tokens(stats.max_output),
        },
        "total_tokens": stats.total_tokens,
        "context_window": stats.context_window,
        "max_output": stats.max_output,
        "remaining_tokens": stats.remaining_tokens,
        "percent_used": round(stats.percent_used, 2),
        "steps_count": stats.steps_count,
        "rolling_limits": {
            "tokens_5h": stats.rolling.tokens_5h,
            "limit_5h": stats.rolling.limit_5h,
            "percent_5h": round(stats.rolling.percent_5h, 2),
            "remaining_5h": stats.rolling.remaining_5h,
            "conversations_5h": stats.rolling.conversations_5h,
            "tokens_7d": stats.rolling.tokens_7d,
            "limit_7d": stats.rolling.limit_7d,
            "percent_7d": round(stats.rolling.percent_7d, 2),
            "remaining_7d": stats.rolling.remaining_7d,
            "conversations_7d": stats.rolling.conversations_7d,
        },
        "breakdown": {
            "system_prompt": {"tokens": stats.system_prompt_tokens, "bytes": stats.system_prompt_bytes},
            "user_input": {"tokens": stats.user_input_tokens, "bytes": stats.user_input_bytes},
            "tools": {"tokens": stats.tool_tokens, "bytes": stats.tool_bytes, "top_tools": stats.top_tools},
            "model_output": {"tokens": stats.model_output_tokens, "bytes": stats.model_output_bytes},
        },
    }
    if stats.rtk_savings:
        payload["rtk_savings"] = stats.rtk_savings
    return json.dumps(payload, indent=2)


def format_markdown_report(stats: TokenStats) -> str:
    """Generates Markdown telemetry report for TOKEN_TELEMETRY.md."""
    status_emoji = "🟢 Saudável"
    if stats.percent_used >= 80 or stats.rolling.percent_5h >= 80 or stats.rolling.percent_7d >= 80:
        status_emoji = "🔴 Crítico (>80%)"
    elif stats.percent_used >= 50 or stats.rolling.percent_5h >= 50 or stats.rolling.percent_7d >= 50:
        status_emoji = "🟡 Atenção (>50%)"

    tools_rows = [
        f"| `{tool_name}` | {data['calls']} | {human_tokens(data['tokens'])} | {data['bytes']:,} B |"
        for tool_name, data in stats.top_tools.items()
    ]
    tools_table = "\n".join(tools_rows) if tools_rows else "| Nenhuma ferramenta executada | - | - | - |"

    is_live, p5_used, p5_rem, d5, p7_used, p7_rem, d7 = _extract_quota_metrics(stats)
    if is_live:
        row_5h = f"| **2. Janela Móvel de 5 Horas (Rate)** | - | - | **{p5_used:.1f}%** | {p5_rem:.1f}% restante | {d5} |"
        row_7d = f"| **3. Janela Semanal (7 Dias Quota)** | - | - | **{p7_used:.1f}%** | {p7_rem:.1f}% restante | {d7} |"
        gov_5h = f"Consumo atual em **{p5_used:.1f}%** ({p5_rem:.1f}% restante). Mantenha comandos concisos."
        gov_7d = f"Consumo atual em **{p7_used:.1f}%** ({p7_rem:.1f}% restante). Utilize `PROJECT_MEMORY.md` para resetar sessões longas."
    else:
        row_5h = "| **2. Janela Móvel de 5 Horas (Rate)** | Não está sendo possível aferir no momento | - | - | - | - |"
        row_7d = "| **3. Janela Semanal (7 Dias Quota)** | Não está sendo possível aferir no momento | - | - | - | - |"
        gov_5h = "Não está sendo possível aferir no momento. Mantenha comandos e leituras concisas."
        gov_7d = "Não está sendo possível aferir no momento. Utilize `PROJECT_MEMORY.md` para resetar sessões longas."

    display_model = get_model_display_name(stats.model_name)
    effort_str = f" | **Effort:** `{stats.effort}`" if stats.effort else ""
    report = f"""# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** {status_emoji} | **Última Leitura:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
> **Sessão:** `{stats.conversation_id}` | **Modelo Utilizado:** `{display_model}` (`{stats.model_name}`){effort_str}  
> **Limites do Modelo:** Janela de Contexto: `{human_tokens(stats.context_window)}` (`{stats.context_window:,}` tokens) | Saída Máxima: `{human_tokens(stats.max_output)}` (`{stats.max_output:,}` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `{human_tokens(stats.total_tokens)}` tokens | `{human_tokens(stats.context_window)}` | **{stats.percent_used:.2f}%** | `{human_tokens(stats.remaining_tokens)}` livres | Ativa na sessão |
{row_5h}
{row_7d}

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `{human_tokens(stats.system_prompt_tokens)}` | {stats.system_prompt_bytes:,} B | {stats.system_prompt_tokens * 100 / max(1, stats.total_tokens):.1f}% |
| **Execuções de Ferramentas** | `{human_tokens(stats.tool_tokens)}` | {stats.tool_bytes:,} B | {stats.tool_tokens * 100 / max(1, stats.total_tokens):.1f}% |
| **Respostas & Thinking** | `{human_tokens(stats.model_output_tokens)}` | {stats.model_output_bytes:,} B | {stats.model_output_tokens * 100 / max(1, stats.total_tokens):.1f}% |
| **Mensagens do Usuário** | `{human_tokens(stats.user_input_tokens)}` | {stats.user_input_bytes:,} B | {stats.user_input_tokens * 100 / max(1, stats.total_tokens):.1f}% |

---

## 3. Top Ferramentas Consumidoras
{tools_table}
"""
    if stats.rtk_savings and stats.rtk_savings.get("saved_tokens", 0) > 0:
        s = stats.rtk_savings
        report += f"""
---

## ⚡ Economia de Tokens via RTK (Rust Token Killer)
- **Comandos interceptados:** {s.get('total_commands', 0)}
- **Tokens economizados:** `{human_tokens(s.get('saved_tokens', 0))}` ({s.get('saved_tokens', 0):,} tokens)
- **Taxa média de redução:** **{s.get('avg_savings_pct', 0.0):.1f}%**
"""
    report += f"""
---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** {gov_5h}
- **Janela Semanal:** {gov_7d}
"""
    return report


def check_budget_status(stats: TokenStats) -> Tuple[str, bool, str]:
    """Evaluates budget health across the 3 token layers."""
    warnings = []
    is_critical = False

    if stats.percent_used >= 80:
        is_critical = True
        warnings.append(f"• Contexto da Mensagem em {stats.percent_used:.1f}% ({human_tokens(stats.remaining_tokens)} livres de {human_tokens(stats.context_window)})")
    elif stats.percent_used >= 65:
        warnings.append(f"• Contexto da Mensagem em {stats.percent_used:.1f}% ({human_tokens(stats.remaining_tokens)} livres de {human_tokens(stats.context_window)})")

    if stats.live_quota and stats.live_quota.is_live:
        is_gemini = "gemini" in stats.model_name.lower()
        b_5h = stats.live_quota.gemini_5h if is_gemini else stats.live_quota.claude_5h
        b_7d = stats.live_quota.gemini_weekly if is_gemini else stats.live_quota.claude_weekly

        rem_5h = b_5h.remaining_fraction if b_5h else 1.0
        rem_7d = b_7d.remaining_fraction if b_7d else 1.0

        if rem_5h <= 0.10:
            is_critical = True
            warnings.append(f"• Limite Móvel 5 Horas (Google): apenas {rem_5h * 100.0:.1f}% restante ({clean_refresh_text(b_5h.description if b_5h else '')})")
        elif rem_5h <= 0.25:
            warnings.append(f"• Limite Móvel 5 Horas (Google): {rem_5h * 100.0:.1f}% restante ({clean_refresh_text(b_5h.description if b_5h else '')})")

        if rem_7d <= 0.05:
            is_critical = True
            warnings.append(f"• Cota Semanal (Google): apenas {rem_7d * 100.0:.1f}% restante ({clean_refresh_text(b_7d.description if b_7d else '')})")
        elif rem_7d <= 0.20:
            warnings.append(f"• Cota Semanal (Google): {rem_7d * 100.0:.1f}% restante ({clean_refresh_text(b_7d.description if b_7d else '')})")
    elif stats.rolling and (stats.rolling.tokens_5h > 0 or stats.rolling.tokens_7d > 0):
        if stats.rolling.percent_5h >= 80:
            is_critical = True
            warnings.append(f"• Janela Móvel de 5 Horas em {stats.rolling.percent_5h:.1f}% ({human_tokens(stats.rolling.remaining_5h)} livres de {human_tokens(stats.rolling.limit_5h)})")
        elif stats.rolling.percent_5h >= 65:
            warnings.append(f"• Janela Móvel de 5 Horas em {stats.rolling.percent_5h:.1f}% ({human_tokens(stats.rolling.remaining_5h)} livres de {human_tokens(stats.rolling.limit_5h)})")

        if stats.rolling.percent_7d >= 85:
            is_critical = True
            warnings.append(f"• Cota Semanal em {stats.rolling.percent_7d:.1f}% ({human_tokens(stats.rolling.remaining_7d)} livres de {human_tokens(stats.rolling.limit_7d)})")
        elif stats.rolling.percent_7d >= 70:
            warnings.append(f"• Cota Semanal em {stats.rolling.percent_7d:.1f}% ({human_tokens(stats.rolling.remaining_7d)} livres de {human_tokens(stats.rolling.limit_7d)})")

    if is_critical:
        msg = (
            "⚠️ **ALERTA DE LIMITE CRÍTICO DE TOKENS DETECTADO:**\n"
            + "\n".join(warnings) + "\n\n"
            + "**Recomendações Operacionais:**\n"
            + "1. O agente alertará o usuário antes de iniciar tarefas substantivas.\n"
            + "2. Se o usuário insistir em prosseguir, a execução adotará **Modo Cirúrgico Atômico**.\n"
            + "3. Para poupar tokens, utilize `PROJECT_MEMORY.md` para resetar a sessão e abrir um chat limpo."
        )
        return "CRITICAL", True, msg
    if warnings:
        msg = (
            "🟡 **AVISO DE ATENÇÃO AO CONSUMO DE TOKENS:**\n"
            + "\n".join(warnings) + "\n"
            + "Recomenda-se evitar comandos verbosos ou leituras de arquivos inteiros."
        )
        return "WARNING", False, msg
    return "HEALTHY", False, "Orçamento de tokens saudável em todas as 3 camadas."


def audit_token_bottlenecks(stats: TokenStats) -> Dict[str, Any]:
    """Identifies high-consumption tools and context bloat bottlenecks."""
    bottlenecks = []
    total = max(1, stats.total_tokens)

    for tool_name, data in stats.top_tools.items():
        tool_pct = (data["tokens"] / total) * 100.0
        if tool_pct >= 35.0:
            if tool_name == "RUN_COMMAND":
                rec = "Saídas extensas de terminal detectadas. Utilize flags silenciosas (--silent, -q), supressão via head ou o utilitário scripts/sanitize-tool-output.sh."
            elif tool_name == "VIEW_FILE":
                rec = "Leituras extensas de arquivo. Restrinja o fatiamento utilizando StartLine e EndLine."
            else:
                rec = f"A ferramenta {tool_name} consumiu mais de 35% do contexto. Avalie truncamento de output."
            bottlenecks.append({
                "tool": tool_name,
                "tokens": data["tokens"],
                "percent": round(tool_pct, 1),
                "calls": data["calls"],
                "recommendation": rec,
            })

    session_rec = None
    if stats.steps_count >= 25 or stats.total_tokens >= 65_000:
        session_rec = (
            f"Sessão longa detectada ({stats.steps_count} passos, {human_tokens(stats.total_tokens)} tokens). "
            "Recomenda-se realizar Session Reset: salvar o progresso no PROJECT_MEMORY.md e iniciar um chat limpo."
        )

    sys_rec = None
    if stats.system_prompt_bytes > 90_000:
        sys_rec = "System Prompt elevado (>90KB). Verifique duplicações de regras em ~/.gemini/config/rules/."

    return {
        "conversation_id": stats.conversation_id,
        "total_tokens": stats.total_tokens,
        "bottlenecks": bottlenecks,
        "session_longevity_warning": session_rec,
        "system_prompt_warning": sys_rec,
    }


def render_plain_dashboard(stats: TokenStats) -> None:
    """Plain text dashboard (preserved for unit test compatibility)."""
    display_model = get_model_display_name(stats.model_name)
    print("=" * 70)
    print(" ANTIGRAVITY TOKEN & QUOTA TELEMETRY TRACKER")
    print("=" * 70)
    print(f"Sessão:          {stats.conversation_id}")
    effort_str = f" | Effort: {stats.effort}" if stats.effort else ""
    print(f"Modelo Utilizado: {display_model} ({stats.model_name}){effort_str}")
    print(f"Limites Modelo:   Janela Contexto: {stats.context_window:,} ({human_tokens(stats.context_window)}) | Saída Máx: {stats.max_output:,} ({human_tokens(stats.max_output)})")
    print("-" * 70)
    print(f"1. Contexto Msg: {stats.total_tokens:,} / {stats.context_window:,} ({stats.percent_used:.2f}%)")
    print(f"   Margem Livre: {stats.remaining_tokens:,} tokens disponíveis")
    is_live, p5_used, p5_rem, d5, p7_used, p7_rem, d7 = _extract_quota_metrics(stats)
    if is_live:
        d_5h = f" ({d5})" if d5 else ""
        d_7d = f" ({d7})" if d7 else ""
        print(f"2. Janela 5h:    {p5_used:.1f}% usado • {p5_rem:.1f}% restante{d_5h}")
        print(f"3. Cota Semanal: {p7_used:.1f}% usado • {p7_rem:.1f}% restante{d_7d}")
    else:
        print("2. Janela 5h:    Não está sendo possível aferir no momento")
        print("3. Cota Semanal: Não está sendo possível aferir no momento")
    print("-" * 70)
    print(f" - System Prompt & Schemas: {stats.system_prompt_tokens:,} tokens ({stats.system_prompt_bytes:,} B)")
    print(f" - Execuções de Ferramentas: {stats.tool_tokens:,} tokens ({stats.tool_bytes:,} B)")
    print(f" - Respostas & Thinking:    {stats.model_output_tokens:,} tokens ({stats.model_output_bytes:,} B)")
    print(f" - Mensagens do Usuário:    {stats.user_input_tokens:,} tokens ({stats.user_input_bytes:,} B)")
    if stats.rtk_savings and stats.rtk_savings.get("saved_tokens", 0) > 0:
        s = stats.rtk_savings
        print("-" * 70)
        print(f"⚡ ECONOMIA RTK (Rust Token Killer): {s['saved_tokens']:,} tokens poupados ({s['avg_savings_pct']:.1f}% em {s['total_commands']} comandos)")
    print("=" * 70)
