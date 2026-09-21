#!/usr/bin/env python3
"""
scripts/token_tracker.py - Telemetria de Tokens para Antigravity IDE & CLI
XP Multi-Agent Kit v2

Diferencia 3 camadas essenciais de limites com exibição de <usado> / <total>:
1. Janela de Contexto por Mensagem/Sessão (Context Window)
2. Limite Móvel de 5 Horas (Rolling 5-Hour Rate Limit)
3. Limite Semanal / Ciclo de Quota (7-Day Weekly Quota)
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sqlite3
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

MODEL_LIMITS: Dict[str, Dict[str, int]] = {
    "gemini-3.8-flash": {"context_window": 1_048_576, "max_output": 65_536},
    "gemini-3.7-flash": {"context_window": 1_048_576, "max_output": 65_536},
    "gemini-3.6-flash": {"context_window": 1_048_576, "max_output": 65_536},
    "gemini-2.0-flash": {"context_window": 1_048_576, "max_output": 65_536},
    "gemini-1.5-flash": {"context_window": 1_048_576, "max_output": 65_536},
    "gemini-3.1-pro": {"context_window": 2_097_152, "max_output": 65_536},
    "gemini-1.5-pro": {"context_window": 2_097_152, "max_output": 65_536},
    "claude-sonnet-4-6": {"context_window": 200_000, "max_output": 8_192},
    "claude-opus-4-6": {"context_window": 200_000, "max_output": 8_192},
    "claude-3-5-sonnet": {"context_window": 200_000, "max_output": 8_192},
    "default": {"context_window": 1_000_000, "max_output": 8_192},
}

DEFAULT_SYSTEM_PROMPT_BYTES = 85_000
DEFAULT_LIMIT_5H = 500_000        # Teto padrão de rate limit para janela de 5 horas
DEFAULT_LIMIT_WEEKLY = 10_000_000  # Teto padrão de cota semanal da conta


def parse_token_limit(val: Any, default: int = 500_000) -> int:
    """Converte valores com sufixos k, M para inteiros (ex: '500k' -> 500000, '10M' -> 10000000)."""
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return int(val)

    s = str(val).strip().upper()
    if not s:
        return default

    multiplier = 1
    if s.endswith("K"):
        multiplier = 1_000
        s = s[:-1]
    elif s.endswith("M"):
        multiplier = 1_000_000
        s = s[:-1]
    elif s.endswith("B"):
        multiplier = 1_000_000_000
        s = s[:-1]

    try:
        return int(float(s) * multiplier)
    except ValueError:
        return default


@dataclass
class RollingWindowStats:
    tokens_5h: int = 0
    conversations_5h: int = 0
    limit_5h: int = DEFAULT_LIMIT_5H
    tokens_7d: int = 0
    conversations_7d: int = 0
    limit_7d: int = DEFAULT_LIMIT_WEEKLY

    @property
    def percent_5h(self) -> float:
        return (self.tokens_5h / self.limit_5h * 100.0) if self.limit_5h else 0.0

    @property
    def remaining_5h(self) -> int:
        return max(0, self.limit_5h - self.tokens_5h)

    @property
    def percent_7d(self) -> float:
        return (self.tokens_7d / self.limit_7d * 100.0) if self.limit_7d else 0.0

    @property
    def remaining_7d(self) -> int:
        return max(0, self.limit_7d - self.tokens_7d)


@dataclass
class TokenStats:
    conversation_id: str
    model_name: str
    context_window: int
    max_output: int
    system_prompt_tokens: int
    system_prompt_bytes: int
    user_input_tokens: int
    user_input_bytes: int
    tool_tokens: int
    tool_bytes: int
    model_output_tokens: int
    model_output_bytes: int
    total_tokens: int
    remaining_tokens: int
    percent_used: float
    rolling: RollingWindowStats = field(default_factory=RollingWindowStats)
    top_tools: Dict[str, Dict[str, int]] = field(default_factory=dict)
    steps_count: int = 0


def estimate_tokens(text: Optional[str]) -> int:
    """Estima a quantidade de tokens para um texto arbitrário (BPE/SentencePiece)."""
    if not text:
        return 0

    char_len = len(text)
    if char_len == 0:
        return 0

    code_chars = len(re.findall(r'[{}\[\]()<>=;:\'"`_\\\/\-\+\*&\|\$@#]', text))
    code_ratio = code_chars / char_len

    chars_per_token = 3.2 if code_ratio > 0.15 else 3.8
    return max(1, int(char_len / chars_per_token))


def get_model_limits(model_name: Optional[str]) -> Dict[str, int]:
    """Retorna a janela de contexto e limite de output para o modelo informado."""
    if not model_name:
        return MODEL_LIMITS["default"]

    clean_name = model_name.lower().strip()
    for key, limits in MODEL_LIMITS.items():
        if key in clean_name:
            return limits

    return MODEL_LIMITS["default"]


def human_tokens(count: int) -> str:
    """Converte contagem de tokens para formato legível (ex: 45.4k, 1.05M)."""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.2f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}k"
    return str(count)


def calculate_rolling_windows(
    search_dirs: Optional[List[Path]] = None,
    limit_5h: Optional[int] = None,
    limit_7d: Optional[int] = None,
) -> RollingWindowStats:
    """Calcula o volume agregado de tokens consumidos nas últimas 5h e nos últimos 7 dias."""
    home = Path.home()
    if search_dirs is None:
        search_dirs = [home / ".gemini" / "antigravity-ide", home / ".gemini" / "antigravity-cli"]

    eff_limit_5h = limit_5h or parse_token_limit(os.environ.get("XP_LIMIT_5H"), DEFAULT_LIMIT_5H)
    eff_limit_7d = limit_7d or parse_token_limit(os.environ.get("XP_LIMIT_WEEKLY"), DEFAULT_LIMIT_WEEKLY)

    now = time.time()
    five_hours_ago = now - (5 * 3600)
    seven_days_ago = now - (7 * 86400)

    tokens_5h = 0
    convs_5h = 0
    tokens_7d = 0
    convs_7d = 0

    for base_dir in search_dirs:
        brain_dir = base_dir / "brain"
        if not brain_dir.is_dir():
            continue

        for conv_dir in brain_dir.iterdir():
            t_file = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
            if not t_file.is_file():
                continue

            mtime = t_file.stat().st_mtime
            if mtime < seven_days_ago:
                continue

            file_tokens = 0
            try:
                with open(t_file, "r", encoding="utf-8", errors="ignore") as fp:
                    for line in fp:
                        file_tokens += estimate_tokens(line)
            except Exception:
                pass

            tokens_7d += file_tokens
            convs_7d += 1

            if mtime >= five_hours_ago:
                tokens_5h += file_tokens
                convs_5h += 1

    return RollingWindowStats(
        tokens_5h=tokens_5h,
        conversations_5h=convs_5h,
        limit_5h=eff_limit_5h,
        tokens_7d=tokens_7d,
        conversations_7d=convs_7d,
        limit_7d=eff_limit_7d,
    )


def parse_transcript_data(
    conversation_id: str,
    model_name: str,
    steps: List[Dict[str, Any]],
    system_prompt_bytes: int = DEFAULT_SYSTEM_PROMPT_BYTES,
    rolling: Optional[RollingWindowStats] = None,
) -> TokenStats:
    """Processa a lista de passos do transcript e consolida a telemetria em 3 camadas."""
    limits = get_model_limits(model_name)
    sys_tokens = estimate_tokens(" " * system_prompt_bytes)

    user_bytes = 0
    tool_bytes = 0
    model_bytes = 0
    tool_breakdown: Dict[str, Dict[str, int]] = {}

    for step in steps:
        stype = step.get("type", "UNKNOWN")
        content = step.get("content", "")
        if not isinstance(content, str):
            content = json.dumps(content) if content else ""

        step_len = len(content)

        if stype == "USER_INPUT":
            user_bytes += step_len
        elif stype == "PLANNER_RESPONSE":
            thinking = step.get("thinking", "")
            if isinstance(thinking, str):
                step_len += len(thinking)
            model_bytes += step_len
        elif stype in ("CHECKPOINT", "CONVERSATION_HISTORY", "KNOWLEDGE_ARTIFACTS"):
            user_bytes += step_len
        else:
            tool_bytes += step_len
            if stype not in tool_breakdown:
                tool_breakdown[stype] = {"bytes": 0, "tokens": 0, "calls": 0}
            tool_breakdown[stype]["bytes"] += step_len
            tool_breakdown[stype]["calls"] += 1

    user_tokens = estimate_tokens(" " * user_bytes)
    tool_tokens = estimate_tokens(" " * tool_bytes)
    model_tokens = estimate_tokens(" " * model_bytes)

    for t_name, t_data in tool_breakdown.items():
        t_data["tokens"] = estimate_tokens(" " * t_data["bytes"])

    sorted_tools = dict(
        sorted(tool_breakdown.items(), key=lambda item: item[1]["bytes"], reverse=True)
    )

    total_tokens = sys_tokens + user_tokens + tool_tokens + model_tokens
    remaining = max(0, limits["context_window"] - total_tokens)
    pct = (total_tokens / limits["context_window"]) * 100.0 if limits["context_window"] else 0.0

    return TokenStats(
        conversation_id=conversation_id,
        model_name=model_name,
        context_window=limits["context_window"],
        max_output=limits["max_output"],
        system_prompt_tokens=sys_tokens,
        system_prompt_bytes=system_prompt_bytes,
        user_input_tokens=user_tokens,
        user_input_bytes=user_bytes,
        tool_tokens=tool_tokens,
        tool_bytes=tool_bytes,
        model_output_tokens=model_tokens,
        model_output_bytes=model_bytes,
        total_tokens=total_tokens,
        remaining_tokens=remaining,
        percent_used=pct,
        rolling=rolling or RollingWindowStats(),
        top_tools=sorted_tools,
        steps_count=len(steps),
    )


def format_badge(stats: TokenStats) -> str:
    """Gera um badge markdown exibindo <usado> / <total> (<%>) para Janela, 5h e Semanal."""
    tot_str = human_tokens(stats.total_tokens)
    win_str = human_tokens(stats.context_window)
    r5h_used = human_tokens(stats.rolling.tokens_5h)
    r5h_tot = human_tokens(stats.rolling.limit_5h)
    r7d_used = human_tokens(stats.rolling.tokens_7d)
    r7d_tot = human_tokens(stats.rolling.limit_7d)
    return (
        f"📊 **Token Telemetry ({stats.model_name}):** `{tot_str}/{win_str}` ({stats.percent_used:.1f}%) "
        f"| **5h:** `{r5h_used}/{r5h_tot}` ({stats.rolling.percent_5h:.1f}%) "
        f"| **Semana:** `{r7d_used}/{r7d_tot}` ({stats.rolling.percent_7d:.1f}%)"
    )


def format_json_stats(stats: TokenStats) -> str:
    """Exporta as métricas de telemetria em formato JSON estruturado com os tetos <usado>/<total>."""
    payload = {
        "conversation_id": stats.conversation_id,
        "model": stats.model_name,
        "context_window": stats.context_window,
        "max_output": stats.max_output,
        "total_tokens": stats.total_tokens,
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
            "system_prompt": {
                "tokens": stats.system_prompt_tokens,
                "bytes": stats.system_prompt_bytes,
            },
            "user_input": {
                "tokens": stats.user_input_tokens,
                "bytes": stats.user_input_bytes,
            },
            "tools": {
                "tokens": stats.tool_tokens,
                "bytes": stats.tool_bytes,
                "top_tools": stats.top_tools,
            },
            "model_output": {
                "tokens": stats.model_output_tokens,
                "bytes": stats.model_output_bytes,
            },
        },
    }
    return json.dumps(payload, indent=2)


def format_markdown_report(stats: TokenStats) -> str:
    """Gera o relatório visual em Markdown para TOKEN_TELEMETRY.md cobrindo <usado>/<total>."""
    status_emoji = "🟢 Saudável"
    if stats.percent_used >= 80 or stats.rolling.percent_5h >= 80 or stats.rolling.percent_7d >= 80:
        status_emoji = "🔴 Crítico (>80%)"
    elif stats.percent_used >= 50 or stats.rolling.percent_5h >= 50 or stats.rolling.percent_7d >= 50:
        status_emoji = "🟡 Atenção (>50%)"

    tools_rows = []
    for tool_name, data in stats.top_tools.items():
        tools_rows.append(
            f"| `{tool_name}` | {data['calls']} | {human_tokens(data['tokens'])} | {data['bytes']:,} B |"
        )
    tools_table = "\n".join(tools_rows) if tools_rows else "| Nenhuma ferramenta executada | - | - | - |"

    report = f"""# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** {status_emoji} | **Última Leitura:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
> **Sessão:** `{stats.conversation_id}` | **Modelo:** `{stats.model_name}`

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `{human_tokens(stats.total_tokens)}` tokens | `{human_tokens(stats.context_window)}` | **{stats.percent_used:.2f}%** | `{human_tokens(stats.remaining_tokens)}` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `{human_tokens(stats.rolling.tokens_5h)}` tokens | `{human_tokens(stats.rolling.limit_5h)}` | **{stats.rolling.percent_5h:.2f}%** | `{human_tokens(stats.rolling.remaining_5h)}` livres | {stats.rolling.conversations_5h} sessões (~{human_tokens(stats.rolling.tokens_5h // 5)}/h) |
| **3. Janela Semanal (7 Dias Quota)** | `{human_tokens(stats.rolling.tokens_7d)}` tokens | `{human_tokens(stats.rolling.limit_7d)}` | **{stats.rolling.percent_7d:.2f}%** | `{human_tokens(stats.rolling.remaining_7d)}` livres | {stats.rolling.conversations_7d} sessões (~{human_tokens(stats.rolling.tokens_7d // 7)}/dia) |

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

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **{stats.rolling.percent_5h:.1f}%** do teto ({human_tokens(stats.rolling.remaining_5h)} disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **{stats.rolling.percent_7d:.1f}%** da cota semanal ({human_tokens(stats.rolling.remaining_7d)} disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
"""
    return report


def check_budget_status(stats: TokenStats) -> Tuple[str, bool, str]:
    """
    Avalia a integridade do orçamento nas 3 camadas.
    Retorna (status, is_low, alert_message).
    - Status: 'HEALTHY' | 'WARNING' | 'CRITICAL'
    - is_low: True se atingir patamar crítico de exaustão (>80% em 5h/semana ou >70% em contexto)
    - alert_message: Texto de advertência detalhado com recomendações de escopo.
    """
    warnings = []
    is_critical = False

    # 1. Janela de Mensagem (Context Window)
    if stats.percent_used >= 80:
        is_critical = True
        warnings.append(f"• Contexto da Mensagem em {stats.percent_used:.1f}% ({human_tokens(stats.remaining_tokens)} livres de {human_tokens(stats.context_window)})")
    elif stats.percent_used >= 65:
        warnings.append(f"• Contexto da Mensagem em {stats.percent_used:.1f}% ({human_tokens(stats.remaining_tokens)} livres de {human_tokens(stats.context_window)})")

    # 2. Janela de 5 Horas (Rate Limit)
    if stats.rolling.percent_5h >= 80:
        is_critical = True
        warnings.append(f"• Janela Móvel de 5 Horas em {stats.rolling.percent_5h:.1f}% ({human_tokens(stats.rolling.remaining_5h)} livres de {human_tokens(stats.rolling.limit_5h)})")
    elif stats.rolling.percent_5h >= 65:
        warnings.append(f"• Janela Móvel de 5 Horas em {stats.rolling.percent_5h:.1f}% ({human_tokens(stats.rolling.remaining_5h)} livres de {human_tokens(stats.rolling.limit_5h)})")

    # 3. Janela Semanal (Quota)
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
            + "2. Se o usuário insistir em prosseguir, a execução adotará **Modo Cirúrgico Atômico**: apenas tarefas essenciais cabíveis na margem disponível, finalizando sempre em um checkpoint estável e testado para não deixar trabalho pela metade.\n"
            + "3. Para poupar tokens, utilize `PROJECT_MEMORY.md` para resetar a sessão e abrir um chat limpo."
        )
        return "CRITICAL", True, msg
    elif warnings:
        msg = (
            "🟡 **AVISO DE ATENÇÃO AO CONSUMO DE TOKENS:**\n"
            + "\n".join(warnings) + "\n"
            + "Recomenda-se evitar comandos verbosos ou leituras de arquivos inteiros."
        )
        return "WARNING", False, msg

    return "HEALTHY", False, "Orçamento de tokens saudável em todas as 3 camadas."


def audit_token_bottlenecks(stats: TokenStats) -> Dict[str, Any]:
    """
    Analisa a distribuição de tokens e identifica ferramentas ou padrões causadores de inchaço de contexto.
    Retorna recomendações acionáveis para redução imediata de consumo.
    """
    bottlenecks = []
    total = max(1, stats.total_tokens)

    # 1. Auditoria de Ferramentas Vilãs
    for tool_name, data in stats.top_tools.items():
        tool_pct = (data["tokens"] / total) * 100.0
        if tool_pct >= 35.0:
            rec = ""
            if tool_name == "RUN_COMMAND":
                rec = "Saídas extensas de terminal detectadas. Utilize flags silenciosas (--silent, -q), supressão via head ou o utilitário scripts/sanitize-tool-output.sh."
            elif tool_name == "VIEW_FILE":
                rec = "Leituras extensas de arquivo. Restrinja o fatiamento utilizando StartLine e EndLine (máximo 50-100 linhas por vez)."
            else:
                rec = f"A ferramenta {tool_name} consumiu mais de 35% do contexto. Avalie truncamento de output."
            
            bottlenecks.append({
                "tool": tool_name,
                "tokens": data["tokens"],
                "percent": round(tool_pct, 1),
                "calls": data["calls"],
                "recommendation": rec,
            })

    # 2. Auditoria de Longevidade da Sessão
    session_rec = None
    if stats.steps_count >= 25 or stats.total_tokens >= 65_000:
        session_rec = (
            f"Sessão longa detectada ({stats.steps_count} passos, {human_tokens(stats.total_tokens)} tokens). "
            "Recomenda-se realizar Session Reset: salvar o progresso no PROJECT_MEMORY.md e iniciar um chat limpo."
        )

    # 3. Auditoria do System Prompt
    sys_rec = None
    if stats.system_prompt_bytes > 90_000:
        sys_rec = "System Prompt elevado (>90KB). Verifique duplicações de regras em ~/.gemini/config/rules/ ou descrições verbosas de skills."

    return {
        "conversation_id": stats.conversation_id,
        "total_tokens": stats.total_tokens,
        "bottlenecks": bottlenecks,
        "session_longevity_warning": session_rec,
        "system_prompt_warning": sys_rec,
    }


def find_active_session() -> Tuple[Optional[str], Optional[Path], Optional[str]]:
    """Localiza a sessão mais recente no ambiente IDE ou CLI."""
    home = Path.home()
    candidates = []

    for app in ("antigravity-ide", "antigravity-cli"):
        base_dir = home / ".gemini" / app
        brain_dir = base_dir / "brain"
        if brain_dir.is_dir():
            for conv_dir in brain_dir.iterdir():
                t_file = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
                if t_file.is_file():
                    candidates.append((t_file.stat().st_mtime, conv_dir.name, t_file, app))

    if not candidates:
        return None, None, None

    candidates.sort(key=lambda x: x[0], reverse=True)
    best = candidates[0]
    return best[1], best[2], best[3]


def load_transcript(transcript_path: Path) -> List[Dict[str, Any]]:
    """Lê as linhas do transcript.jsonl em formato JSON."""
    steps = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        steps.append(json.loads(line))
                    except Exception:
                        pass
    except Exception as e:
        sys.stderr.write(f"Erro ao ler transcript {transcript_path}: {e}\n")
    return steps


def detect_model_name(conversation_id: str) -> str:
    """Tenta detectar o modelo a partir do SQLite da conversa."""
    home = Path.home()
    for app in ("antigravity-ide", "antigravity-cli"):
        db_path = home / ".gemini" / app / "conversations" / f"{conversation_id}.db"
        if db_path.is_file():
            try:
                con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
                cur = con.cursor()
                rows = cur.execute("SELECT data FROM gen_metadata ORDER BY idx DESC LIMIT 3").fetchall()
                for (data,) in rows:
                    if isinstance(data, bytes):
                        for m in ("gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.1-pro", "gemini-1.5-pro", "claude-sonnet-4-6"):
                            if m.encode() in data:
                                con.close()
                                return m
                con.close()
            except Exception:
                pass
    return "gemini-3.8-flash"


def render_rich_dashboard(stats: TokenStats):
    """Exibe um dashboard interativo no terminal utilizando rich com <usado>/<total>."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text

        console = Console()
        console.clear()

        c_msg = "green" if stats.percent_used < 50 else ("yellow" if stats.percent_used < 80 else "red")
        c_5h = "green" if stats.rolling.percent_5h < 50 else ("yellow" if stats.rolling.percent_5h < 80 else "red")
        c_7d = "green" if stats.rolling.percent_7d < 50 else ("yellow" if stats.rolling.percent_7d < 80 else "red")

        info_text = Text()
        info_text.append("Sessão Ativa: ", style="bold cyan")
        info_text.append(f"{stats.conversation_id}\n", style="white")
        info_text.append("Modelo: ", style="bold cyan")
        info_text.append(f"{stats.model_name}  ", style="bold yellow")
        info_text.append("Passos Registrados: ", style="bold cyan")
        info_text.append(f"{stats.steps_count}\n\n", style="white")

        info_text.append("1. JANELA DE MENSAGEM: ", style="bold magenta")
        info_text.append(f"{human_tokens(stats.total_tokens)} / {human_tokens(stats.context_window)} tokens ", style="bold white")
        info_text.append(f"({stats.percent_used:.2f}%)\n", style=f"bold {c_msg}")
        info_text.append(f"   Margem Livre: {human_tokens(stats.remaining_tokens)} tokens | Saída Max: {human_tokens(stats.max_output)}\n\n", style="dim")

        info_text.append("2. LIMITE MÓVEL 5 HORAS: ", style="bold magenta")
        info_text.append(f"{human_tokens(stats.rolling.tokens_5h)} / {human_tokens(stats.rolling.limit_5h)} tokens ", style="bold white")
        info_text.append(f"({stats.rolling.percent_5h:.2f}%)\n", style=f"bold {c_5h}")
        info_text.append(f"   Margem Livre: {human_tokens(stats.rolling.remaining_5h)} tokens | {stats.rolling.conversations_5h} sessões (~{human_tokens(stats.rolling.tokens_5h // 5)}/h)\n\n", style="dim")

        info_text.append("3. LIMITE SEMANAL (7 DIAS): ", style="bold magenta")
        info_text.append(f"{human_tokens(stats.rolling.tokens_7d)} / {human_tokens(stats.rolling.limit_7d)} tokens ", style="bold white")
        info_text.append(f"({stats.rolling.percent_7d:.2f}%)\n", style=f"bold {c_7d}")
        info_text.append(f"   Margem Livre: {human_tokens(stats.rolling.remaining_7d)} tokens | {stats.rolling.conversations_7d} sessões (~{human_tokens(stats.rolling.tokens_7d // 7)}/dia)\n", style="dim")

        console.print(Panel(info_text, title="🧠 [bold magenta]Antigravity Token & Quota Tracker[/bold magenta]", border_style="bright_blue"))

        table = Table(title="📦 Distribuição de Consumo da Sessão Atual", border_style="blue", header_style="bold cyan")
        table.add_column("Categoria", style="white")
        table.add_column("Tokens Est.", justify="right", style="green")
        table.add_column("Bytes", justify="right", style="dim")
        table.add_column("% Janela", justify="right", style="bold")

        categories = [
            ("System Prompt & Tools Schemas", stats.system_prompt_tokens, stats.system_prompt_bytes),
            ("Execuções de Ferramentas", stats.tool_tokens, stats.tool_bytes),
            ("Respostas & Thinking", stats.model_output_tokens, stats.model_output_bytes),
            ("Mensagens do Usuário", stats.user_input_tokens, stats.user_input_bytes),
        ]
        for name, tok, byt in categories:
            pct_total = (tok / max(1, stats.total_tokens)) * 100.0
            table.add_row(name, f"{tok:,} ({human_tokens(tok)})", f"{byt:,} B", f"{pct_total:.1f}%")

        console.print(table)

        if stats.top_tools:
            t_table = Table(title="⚡ Top Ferramentas Consumidoras", border_style="yellow", header_style="bold yellow")
            t_table.add_column("Ferramenta", style="white")
            t_table.add_column("Chamadas", justify="right", style="cyan")
            t_table.add_column("Tokens Est.", justify="right", style="bold red")
            t_table.add_column("Bytes", justify="right", style="dim")

            for t_name, data in list(stats.top_tools.items())[:5]:
                t_table.add_row(t_name, str(data["calls"]), f"{data['tokens']:,} ({human_tokens(data['tokens'])})", f"{data['bytes']:,} B")
            console.print(t_table)

    except ImportError:
        render_plain_dashboard(stats)


def render_plain_dashboard(stats: TokenStats):
    """Fallback simples caso rich não esteja instalado."""
    print("=" * 70)
    print(" ANTIGRAVITY TOKEN & QUOTA TELEMETRY TRACKER")
    print("=" * 70)
    print(f"Sessão:        {stats.conversation_id}")
    print(f"Modelo:        {stats.model_name}")
    print("-" * 70)
    print(f"1. Contexto Msg: {stats.total_tokens:,} / {stats.context_window:,} ({stats.percent_used:.2f}%)")
    print(f"   Margem Livre: {stats.remaining_tokens:,} tokens disponíveis")
    print(f"2. Janela 5h:    {stats.rolling.tokens_5h:,} / {stats.rolling.limit_5h:,} ({stats.rolling.percent_5h:.2f}%)")
    print(f"   Margem Livre: {stats.rolling.remaining_5h:,} tokens disponíveis ({stats.rolling.conversations_5h} conversas)")
    print(f"3. Janela 7d:    {stats.rolling.tokens_7d:,} / {stats.rolling.limit_7d:,} ({stats.rolling.percent_7d:.2f}%)")
    print(f"   Margem Livre: {stats.rolling.remaining_7d:,} tokens disponíveis ({stats.rolling.conversations_7d} conversas)")
    print("-" * 70)
    print(f" - System Prompt & Schemas: {stats.system_prompt_tokens:,} tokens ({stats.system_prompt_bytes:,} B)")
    print(f" - Execuções de Ferramentas: {stats.tool_tokens:,} tokens ({stats.tool_bytes:,} B)")
    print(f" - Respostas & Thinking:    {stats.model_output_tokens:,} tokens ({stats.model_output_bytes:,} B)")
    print(f" - Mensagens do Usuário:    {stats.user_input_tokens:,} tokens ({stats.user_input_bytes:,} B)")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Antigravity Token & Quota Telemetry Tracker")
    parser.add_argument("-c", "--conversation-id", help="ID da conversa específica para monitorar")
    parser.add_argument("-w", "--watch", action="store_true", help="Atualiza em loop contínuo (tempo real)")
    parser.add_argument("-i", "--interval", type=int, default=2, help="Intervalo de atualização em segundos para --watch")
    parser.add_argument("--limit-5h", help="Teto da janela de 5h (ex: 500k, 300000)")
    parser.add_argument("--limit-weekly", help="Teto da cota semanal (ex: 10M, 15M, 10000000)")
    parser.add_argument("--badge", action="store_true", help="Imprime apenas o badge markdown de telemetria")
    parser.add_argument("--json", action="store_true", help="Imprime as estatísticas em formato JSON")
    parser.add_argument("--report", action="store_true", help="Gera e grava o arquivo .agents/memory/TOKEN_TELEMETRY.md")
    parser.add_argument("--check", action="store_true", help="Avalia se os limites estão baixos e emite alerta se necessário")
    parser.add_argument("--audit", action="store_true", help="Audita gargalos de consumo e emite recomendações de otimização")
    parser.add_argument("--plain", action="store_true", help="Força saída em texto simples (sem rich)")

    args = parser.parse_args()

    limit_5h = parse_token_limit(args.limit_5h, DEFAULT_LIMIT_5H) if args.limit_5h else None
    limit_7d = parse_token_limit(args.limit_weekly, DEFAULT_LIMIT_WEEKLY) if args.limit_weekly else None

    while True:
        conv_id = args.conversation_id
        transcript_path = None

        if not conv_id:
            conv_id, transcript_path, _ = find_active_session()
        else:
            home = Path.home()
            for app in ("antigravity-ide", "antigravity-cli"):
                candidate = home / ".gemini" / app / "brain" / conv_id / ".system_generated" / "logs" / "transcript.jsonl"
                if candidate.is_file():
                    transcript_path = candidate
                    break

        if not conv_id or not transcript_path or not transcript_path.is_file():
            sys.stderr.write("Nenhuma conversa ativa encontrada no Antigravity IDE/CLI.\n")
            if not args.watch:
                sys.exit(1)
            time.sleep(args.interval)
            continue

        steps = load_transcript(transcript_path)
        model_name = detect_model_name(conv_id)
        rolling = calculate_rolling_windows(limit_5h=limit_5h, limit_7d=limit_7d)
        stats = parse_transcript_data(conv_id, model_name, steps, rolling=rolling)

        if args.check:
            status, is_low, msg = check_budget_status(stats)
            print(f"[{status}] {msg}")
            sys.exit(2 if is_low else 0)

        if args.audit:
            audit = audit_token_bottlenecks(stats)
            print("=" * 70)
            print(" 🔍 AUDITORIA DE GARGALOS DE CONSUMO DE TOKENS")
            print("=" * 70)
            print(f"Sessão: {audit['conversation_id']} | Total: {audit['total_tokens']:,} tokens")
            print("-" * 70)
            if audit["bottlenecks"]:
                print("⚠️  FERRAMENTAS VILÃS IDENTIFICADAS (>35% do contexto):")
                for b in audit["bottlenecks"]:
                    print(f"  • {b['tool']}: {b['tokens']:,} tokens ({b['percent']}%, {b['calls']} chamadas)")
                    print(f"    👉 Ação: {b['recommendation']}\n")
            else:
                print("✅ Nenhuma ferramenta isolada ultrapassou 35% do contexto.")

            if audit["session_longevity_warning"]:
                print(f"⚠️  LONGEVIDADE: {audit['session_longevity_warning']}")
            if audit["system_prompt_warning"]:
                print(f"⚠️  SYSTEM PROMPT: {audit['system_prompt_warning']}")
            print("=" * 70)
            return

        if args.badge:
            print(format_badge(stats))
            return

        if args.json:
            print(format_json_stats(stats))
            return

        if args.report:
            report_text = format_markdown_report(stats)
            report_path = Path(".agents/memory/TOKEN_TELEMETRY.md")
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report_text, encoding="utf-8")
            print(f"Relatório gravado com sucesso em: {report_path.resolve()}")
            return

        if args.plain:
            render_plain_dashboard(stats)
        else:
            render_rich_dashboard(stats)

        if not args.watch:
            break

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
