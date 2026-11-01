#!/usr/bin/env python3
"""
scripts/agy_effort_router.py
Router Inteligente de Reasoning Effort para o Antigravity CLI (XP Multi-Agent Kit v3.9).
Prioriza Completude Exaustiva (COMPLETENESS_OVER_SPEED = True) e Revisão Multi-Pass EGM.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def fetch_live_antigravity_quota(force_refresh: bool = False):
    class Dummy:
        is_live = False
    return Dummy()


try:
    from scripts.turn_telemetry import preflight as _local_preflight
except ImportError:
    try:
        from turn_telemetry import preflight as _local_preflight  # type: ignore
    except ImportError:
        _local_preflight = None  # type: ignore

EFFORT_LOW = "low"
EFFORT_MEDIUM = "medium"
EFFORT_HIGH = "high"

LEVEL_L0_TRIVIAL = "L0 (Trivial)"
LEVEL_L1_SMALL = "L1 (Small)"
LEVEL_L2_FEATURE = "L2 (Feature)"
LEVEL_L3_CRITICAL = "L3 (Critical)"

L0_KEYWORDS = [
    r"\btypo\b", r"\berro de digita[çc][ãa]o\b", r"\bortografia\b", r"\bescrita\b", r"\breadme\b", r"\bdocumenta[çc][ãa]o\b", r"\bdocs?\b", r"\bdocstrings?\b", r"\bcoment[áa]rios?\b", r"\bchangelog\b",
    r"\bprettier\b", r"\beslint\b", r"\bblack\b", r"\bisort\b", r"\bformate?\b", r"\bformata[çc][ãa]o\b", r"\bidenta[çc][ãa]o\b", r"\bindenta[çc][ãa]o\b", r"\bcss\b", r"\bscss\b", r"\bestilos?\b",
    r"\bpadding\b", r"\bmargin\b", r"\bcores?\b", r"\bfont-size\b", r"\bo que [ée]\b", r"\bexplique\b", r"\bcomo funciona\b", r"\bquais s[ãa]o\b", r"\bdo que se trata\b", r"\bo que faz\b", r"\bpara que serve\b",
    r"\bcomo uso\b", r"\bcomo usar\b", r"\bduvida\b", r"\bd[úu]vida\b", r"\bpergunta\b", r"\bquest[ãa]o\b", r"\beconomiza\b", r"\beconomizar\b", r"\beconomia de tokens?\b", r"\bquantos tokens\b",
    r"\bqual(?: a)? diferen[çc]a\b", r"\bcompar[ea]\b", r"\bcomparativo\b", r"\bde forma simples\b", r"\bsimples\b", r"\br[áa]pido\b", r"\bb[áa]sico\b", r"\bresumo\b", r"\bstatus\b", r"\bgit log\b", r"\bgit status\b", r"\bquais arquivos\b", r"\bclean code\b",
]

L3_KEYWORDS = [
    r"\bauth\b", r"\bautentica[çc][ãa]o\b", r"\blogin\b", r"\bjwt\b", r"\boauth\b",
    r"\b(?:jwt|auth|bearer|csrf|session|access|refresh)[_-]?tokens?\b",
    r"\btokens?\s+(?:de\s+)?(?:acesso|jwt|auth|api|sess[ãa]o|bearer)\b",
    r"\bmfa\b", r"\b2fa\b", r"\bdois fatores\b", r"\bmulti-factor\b", r"\bsenha\b", r"\bpassword\b",
    r"\bpermiss[ãa]o\b", r"\bcredenciais?\b", r"\brbac\b", r"\bidor\b", r"\bcrypto\b", r"\bcriptografia\b",
    r"\bsecret\b", r"\bvulnerabilidade\b", r"\bcve\b", r"\bthreat modeling\b", r"\bstride\b",
    r"\bpagamento\b", r"\bpayment\b", r"\bstripe\b", r"\bbilling\b", r"\bcheckout\b", r"\btransa[çc][ãa]o\b",
    r"\bfatura\b", r"\bmigra[çc][ãa]o\b", r"\bmigrations?\b", r"\bschema change\b", r"\bdrop table\b",
    r"\balter table\b", r"\b[íi]ndice concorrente\b", r"\brace condition\b", r"\bdeadlock\b",
    r"\bconcorr[êe]ncia\b", r"\bmutex\b", r"\bgoroutine\b", r"\bthread safety\b", r"\bzero-downtime\b",
    r"\bblue-green\b", r"\bcanary\b", r"\brollback\b", r"\bkernel panic\b", r"\bcrash\b",
    r"\bmemory leak\b", r"\bcausa raiz\b", r"\broot cause\b", r"\bflaky test\b", r"\bstop gate\b", r"\brisco l3\b",
]

L2_KEYWORDS = [
    r"\bfeatures?\b", r"\bnova funcionalidade\b", r"\bnovo endpoint\b", r"\bcriar api\b",
    r"\bnovo componente\b", r"\bnova esteira\b", r"\bintegra[çc][ãa]o\b", r"\brefatora[çc][ãa]o estrutural\b",
    r"\bredesign\b", r"\bimplemente\b", r"\bimplementad[oa]s?\b", r"\bimplementa[çc][ãa]o\b",
    r"\bconstrua\b", r"\bmonte\b", r"\bcrie\b", r"\bexporta[çc][ãa]o\b", r"\bworkflows?\b", r"\bapi\b",
    r"\bplanej(?:ar|amento|amentos)\b", r"\bplanos?\b", r"\barquitetura\b", r"\bespecifica[çc][ãa]o\b",
    r"\bspecs?\b", r"\begm\b", r"\bgoldfish\b", r"\brevis(?:ar|[ãa]o|[õo]es)\b", r"\baudit(?:ar|oria|orias)\b",
    r"\bmelhor(?:ar|ia|ias)\b", r"\bcomplet(?:o|a|os|as|ude)\b", r"\bexaustiv[oa]s?\b",
    r"\baprofund(?:ar|ado|ada)\b", r"\bmultiagent\b", r"\bmultiagente\b", r"\bsistema\b",
    r"\bdispositivos m[óo]veis\b", r"\bmobile\b", r"\bresponsiv(?:o|a|idade)\b", r"\bvisualiza[çc][ãa]o\b",
    r"\binterface\b", r"\btelas?\b", r"\bcontainers?\b", r"\bmonitoramento\b",
    r"\bdetec[çc][ãa]o autom[áa]tica\b", r"\bcorrija esse comportamento\b", r"\bcomportamento incorreto\b", r"\brisco l2\b",
]

L1_KEYWORDS = [
    r"\bpequeno ajuste\b", r"\brefatore\b", r"\brefatora[çc][ãa]o isolada\b", r"\bteste unit[áa]rio\b",
    r"\badicione um teste\b", r"\bpequeno bug\b", r"\bajuste\b", r"\brenomeie\b", r"\bmover\b", r"\blint fix\b",
]

DIRECTIVE_HIGH_PATTERNS = [
    r"\b(?:mude|mudar|coloque|colocar|altere|alterar|troque|trocar|set|setar|muda|use|usar|coloquem?|troquem?)\s+(?:para\s+|em\s+|no\s+|pro\s+|o\s+|o\s+modelo\s+em\s+|o\s+modo\s+)?(?:effort\s+)?(?:to\s+)?high\b",
    r"\b(?:effort|racioc[íi]nio|reasoning|modo)\s+(?:em\s+|para\s+|no\s+|to\s+)?high\b",
    r"\bset\s+effort\s+(?:to\s+)?high\b", r"\bhigh\s+(?:effort|reasoning|mode)\b",
    r"\b/effort\s+high\b", r"\b(?:deep|m[áa]ximo)\s+effort\b", r"\b(?:modo|effort)\s+profundo\b",
]

DIRECTIVE_LOW_PATTERNS = [
    r"\b(?:mude|mudar|coloque|colocar|altere|alterar|troque|trocar|set|setar|muda|use|usar)\s+(?:para\s+|em\s+|no\s+|pro\s+|o\s+|o\s+modelo\s+em\s+|o\s+modo\s+)?(?:effort\s+)?(?:to\s+)?low\b",
    r"\b(?:effort|racioc[íi]nio|reasoning|modo)\s+(?:em\s+|para\s+|no\s+|to\s+)?low\b",
    r"\bset\s+effort\s+(?:to\s+)?low\b", r"\blow\s+(?:effort|reasoning|mode)\b",
    r"\b/effort\s+low\b", r"\bfast\s+effort\b", r"\b(?:modo|effort)\s+r[áa]pido\b",
]

DIRECTIVE_MEDIUM_PATTERNS = [
    r"\b(?:mude|mudar|coloque|colocar|altere|alterar|troque|trocar|set|setar|muda|use|usar)\s+(?:para\s+|em\s+|no\s+|pro\s+|o\s+|o\s+modelo\s+em\s+|o\s+modo\s+)?(?:effort\s+)?(?:to\s+)?medium\b",
    r"\b(?:effort|racioc[íi]nio|reasoning|modo)\s+(?:em\s+|para\s+|no\s+|to\s+)?medium\b",
    r"\bset\s+effort\s+(?:to\s+)?medium\b", r"\bmedium\s+(?:effort|reasoning|mode)\b",
    r"\b/effort\s+medium\b", r"\b(?:modo|effort)\s+equilibrado\b",
]

CONTINUATION_PATTERNS = [
    r"^\s*(?:continue|prossiga|pode continuar|pode fazer|vai|vai em frente|manda bala|sim|ok|aprovado|confirmado|executar|implementar|avançar|prosseguir|go ahead|proceed|yes|done)\b",
    r"\b(?:continue|prossiga|avançar|vai em frente|pode fazer)\b",
]


@dataclass
class EffortDecision:
    effort: str
    risk_level: str
    reason: str
    estimated_token_savings: int = 0
    throttled: bool = False
    override: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


def get_cli_settings_path() -> Path:
    return Path.home() / ".gemini" / "antigravity-cli" / "settings.json"


def get_current_settings_effort() -> Optional[str]:
    for p in (get_cli_settings_path(), Path.home() / ".gemini" / "antigravity-ide" / "settings.json", Path.home() / ".gemini" / "settings.json"):
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                effort = data.get("reasoningEffort")
                if effort and str(effort).lower() in (EFFORT_LOW, EFFORT_MEDIUM, EFFORT_HIGH):
                    return str(effort).lower()
                model = data.get("model", "").lower()
                for lvl in (EFFORT_HIGH, EFFORT_LOW, EFFORT_MEDIUM):
                    if lvl in model:
                        return lvl
            except Exception:
                continue
    return None


def detect_git_context(repo_path: Optional[Path] = None) -> Dict[str, Any]:
    cwd = repo_path or Path.cwd()
    context: Dict[str, Any] = {"branch": "", "changed_files": []}
    try:
        b_proc = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(cwd), capture_output=True, text=True, timeout=2)
        if b_proc.returncode == 0:
            context["branch"] = b_proc.stdout.strip()
        s_proc = subprocess.run(["git", "status", "--porcelain"], cwd=str(cwd), capture_output=True, text=True, timeout=2)
        if s_proc.returncode == 0:
            context["changed_files"] = [line.strip().split(maxsplit=1)[1] for line in s_proc.stdout.splitlines() if len(line.strip().split(maxsplit=1)) == 2]
    except Exception:
        pass
    return context


def get_token_budget_status() -> Dict[str, float]:
    return {"rolling_5h_percent": 0.0, "weekly_percent": 0.0}


def classify_task_effort(
    prompt: str = "", git_context: Optional[Dict[str, Any]] = None,
    token_budget: Optional[Dict[str, float]] = None, explicit_effort: Optional[str] = None,
    conversation_context: Optional[Dict[str, Any]] = None,
) -> EffortDecision:
    conv_ctx = conversation_context or {}
    if explicit_effort and explicit_effort.lower().strip() in (EFFORT_LOW, EFFORT_MEDIUM, EFFORT_HIGH):
        norm = explicit_effort.lower().strip()
        return EffortDecision(effort=norm, risk_level="Manual Override", reason=f"Definido explicitamente via flag --effort {norm}", override=True)

    p_lower = prompt.lower().strip()
    git_ctx, budget = git_context or {}, token_budget or {}
    is_report_or_question = (
        "?" in p_lower
        or any(p_lower.startswith(w) for w in ["por que", "pq", "porque", "ele ", "continua ", "abre ", "quando ", "como ", "ta ", "tá ", "não ", "nao "])
        or any(w in p_lower for w in ["continua", "abre em", "ja muda", "já muda", "ta mudando", "tá mudando", "do que", "o que"])
    )

    if not is_report_or_question:
        for pat in DIRECTIVE_HIGH_PATTERNS:
            if re.search(pat, p_lower):
                return EffortDecision(effort=EFFORT_HIGH, risk_level=conv_ctx.get("active_risk") or LEVEL_L3_CRITICAL, reason="Diretriz explícita detectada no prompt para modo HIGH", override=True)
        for pat in DIRECTIVE_LOW_PATTERNS:
            if re.search(pat, p_lower):
                return EffortDecision(effort=EFFORT_LOW, risk_level=LEVEL_L0_TRIVIAL, reason="Diretriz explícita detectada no prompt para modo LOW", override=True, estimated_token_savings=5000)
        for pat in DIRECTIVE_MEDIUM_PATTERNS:
            if re.search(pat, p_lower):
                return EffortDecision(effort=EFFORT_MEDIUM, risk_level=LEVEL_L1_SMALL, reason="Diretriz explícita detectada no prompt para modo MEDIUM", override=True)

    is_cont = conv_ctx.get("is_continuation", False) or any(re.search(pat, p_lower) for pat in CONTINUATION_PATTERNS)
    active_risk = conv_ctx.get("active_risk", "")
    cumulative_text = conv_ctx.get("cumulative_text", "").lower()

    if is_cont:
        if active_risk in (LEVEL_L3_CRITICAL, LEVEL_L2_FEATURE):
            return EffortDecision(effort=EFFORT_HIGH, risk_level=active_risk, reason=f"Continuação de tarefa {active_risk} confirmada pelo usuário")
        if cumulative_text and any(re.search(kw, cumulative_text) for kw in L3_KEYWORDS):
            matched_l3_cum = [kw for kw in L3_KEYWORDS if re.search(kw, cumulative_text)]
            return EffortDecision(effort=EFFORT_HIGH, risk_level=LEVEL_L3_CRITICAL, reason=f"Continuação com contexto acumulado L3 (Critical): {', '.join(matched_l3_cum[:2])}")
        if cumulative_text and any(re.search(kw, cumulative_text) for kw in L2_KEYWORDS):
            matched_l2_cum = [kw for kw in L2_KEYWORDS if re.search(kw, cumulative_text)]
            return EffortDecision(effort=EFFORT_HIGH, risk_level=LEVEL_L2_FEATURE, reason=f"Continuação com contexto acumulado L2 (Feature): {', '.join(matched_l2_cum[:2])}")

    raw_effort, risk_level, reason, savings = EFFORT_LOW, LEVEL_L0_TRIVIAL, "Tarefa padrão de complexidade básica (baseline low)", 0

    matched_l3 = [kw for kw in L3_KEYWORDS if re.search(kw, p_lower)]
    if matched_l3:
        raw_effort, risk_level, reason = EFFORT_HIGH, LEVEL_L3_CRITICAL, f"Detectado risco L3 por palavras-chave críticas: {', '.join(matched_l3[:3])}"
    elif cumulative_text and any(re.search(kw, cumulative_text) for kw in L3_KEYWORDS):
        matched_l3_cum = [kw for kw in L3_KEYWORDS if re.search(kw, cumulative_text)]
        raw_effort, risk_level, reason = EFFORT_HIGH, LEVEL_L3_CRITICAL, f"Detectado risco L3 pelo histórico acumulado: {', '.join(matched_l3_cum[:3])}"
    elif any(re.search(kw, p_lower) for kw in L2_KEYWORDS):
        matched_l2 = [kw for kw in L2_KEYWORDS if re.search(kw, p_lower)]
        raw_effort, risk_level, reason = EFFORT_HIGH, LEVEL_L2_FEATURE, f"Detectado risco L2 por termos de feature/construção: {', '.join(matched_l2[:3])}"
    elif cumulative_text and any(re.search(kw, cumulative_text) for kw in L2_KEYWORDS):
        matched_l2_cum = [kw for kw in L2_KEYWORDS if re.search(kw, cumulative_text)]
        raw_effort, risk_level, reason = EFFORT_HIGH, LEVEL_L2_FEATURE, f"Detectado risco L2 pelo histórico acumulado: {', '.join(matched_l2_cum[:3])}"
    elif any(re.search(kw, p_lower) for kw in L0_KEYWORDS):
        matched_l0 = [kw for kw in L0_KEYWORDS if re.search(kw, p_lower)]
        raw_effort, risk_level, savings, reason = EFFORT_LOW, LEVEL_L0_TRIVIAL, 5000, f"Detectado risco L0 (Trivial/Docs/CSS) por: {', '.join(matched_l0[:3])}"
    elif any(re.search(kw, p_lower) for kw in L1_KEYWORDS):
        matched_l1 = [kw for kw in L1_KEYWORDS if re.search(kw, p_lower)]
        raw_effort, risk_level, reason = EFFORT_MEDIUM, LEVEL_L1_SMALL, f"Detectado risco L1 por: {', '.join(matched_l1[:3])}"
    elif not p_lower:
        branch, files = git_ctx.get("branch", "").lower(), git_ctx.get("changed_files", [])
        if any(branch.startswith(p) for p in ("hotfix/", "sec/", "auth/", "critical/")):
            raw_effort, risk_level, reason = EFFORT_HIGH, LEVEL_L3_CRITICAL, f"Branch de segurança/hotfix detectada ({branch})"
        elif any(branch.startswith(p) for p in ("feat/", "feature/")):
            raw_effort, risk_level, reason = EFFORT_HIGH, LEVEL_L2_FEATURE, f"Branch de feature detectada ({branch})"
        elif any(branch.startswith(p) for p in ("docs/", "chore/", "style/")):
            raw_effort, risk_level, savings, reason = EFFORT_LOW, LEVEL_L0_TRIVIAL, 5000, f"Branch de documentação/estilo detectada ({branch})"
        elif files and all(f.endswith((".md", ".txt", ".css", ".scss")) for f in files):
            raw_effort, risk_level, savings, reason = EFFORT_LOW, LEVEL_L0_TRIVIAL, 5000, "Todos os arquivos modificados são documentação ou estilos cosméticos"
        elif any("migration" in f or "auth" in f for f in files):
            raw_effort, risk_level, reason = EFFORT_HIGH, LEVEL_L3_CRITICAL, "Arquivos modificados envolvem migrações ou autenticação"
        elif files and any(f.endswith((".py", ".ts", ".tsx", ".js", ".go", ".rs", ".java")) for f in files):
            raw_effort, risk_level, reason = EFFORT_HIGH, LEVEL_L2_FEATURE, "Alterações ativas em arquivos de código de produção detectadas"
        elif get_current_settings_effort() == EFFORT_HIGH:
            raw_effort, risk_level, reason = EFFORT_HIGH, LEVEL_L2_FEATURE, "Preservada configuração ativa em settings.json (modo HIGH)"
        else:
            raw_effort, risk_level, savings, reason = EFFORT_LOW, LEVEL_L0_TRIVIAL, 5000, "Sessão interativa sem prompt inicial (baseline low)"

    # 9a. Preserva modo HIGH/MEDIUM em tarefas longas (COMPLETENESS_OVER_SPEED = True): nunca faz downgrade por turnos
    throttled = False
    rolling_5h, weekly = budget.get("rolling_5h_percent", 0.0), budget.get("weekly_percent", 0.0)

    # 9b. Budget do Language Server (cota crítica explícita >80%)
    if rolling_5h > 80.0 or weekly > 80.0:
        critical_quota = rolling_5h if rolling_5h > 80.0 else weekly
        quota_type = "5h" if rolling_5h > 80.0 else "semanal"
        if raw_effort == EFFORT_HIGH:
            raw_effort, throttled = EFFORT_MEDIUM, True
            reason += f" | ⚠️ [BUDGET THROTTLE] Cota crítica {quota_type} ({critical_quota:.1f}% > 80%): reduzido HIGH -> MEDIUM"
        elif raw_effort == EFFORT_MEDIUM:
            raw_effort, throttled, savings = EFFORT_LOW, True, savings + 3000
            reason += f" | ⚠️ [BUDGET THROTTLE] Cota crítica {quota_type} ({critical_quota:.1f}% > 80%): reduzido MEDIUM -> LOW"

    return EffortDecision(
        effort=raw_effort, risk_level=risk_level, reason=reason,
        estimated_token_savings=savings, throttled=throttled, override=False,
        details={"prompt_length": len(prompt), "branch": git_ctx.get("branch", ""), "budget": budget},
    )


def get_canonical_model_for_task(risk_level: str, is_planning: bool = False) -> Tuple[str, str]:
    if is_planning:
        if risk_level in (LEVEL_L3_CRITICAL, LEVEL_L2_FEATURE):
            return "Gemini Pro", EFFORT_HIGH
        return ("Gemini 3.8 Flash", EFFORT_MEDIUM) if risk_level == LEVEL_L1_SMALL else ("Gemini 3.8 Flash", EFFORT_LOW)
    if risk_level in (LEVEL_L3_CRITICAL, LEVEL_L2_FEATURE):
        return "Gemini 3.8 Flash", EFFORT_HIGH
    return ("Gemini 3.8 Flash", EFFORT_MEDIUM) if risk_level == LEVEL_L1_SMALL else ("Gemini 3.8 Flash", EFFORT_LOW)


def map_model_to_effort(current_model: str, target_effort: str) -> str:
    effort_cap, effort_lower = target_effort.capitalize(), target_effort.lower()
    if "pro" in current_model.lower() and "gemini" in current_model.lower():
        return f"Gemini 3.8 Flash ({effort_cap})"
    if re.search(r"\((High|Medium|Low)\)$", current_model, re.IGNORECASE):
        return re.sub(r"\((High|Medium|Low)\)$", f"({effort_cap})", current_model, flags=re.IGNORECASE)
    if re.search(r"-(high|medium|low)$", current_model, re.IGNORECASE):
        return re.sub(r"-(high|medium|low)$", f"-{effort_lower}", current_model, flags=re.IGNORECASE)
    if "flash" in current_model.lower() or "gemini" in current_model.lower():
        return f"{current_model} ({effort_cap})"
    return current_model


def update_settings_effort(settings_path: Path, target_effort: str) -> Tuple[bool, str, str]:
    if not settings_path.is_file():
        return False, "", ""
    try:
        content = settings_path.read_text(encoding="utf-8")
        data = json.loads(content) if content.strip() else {}
        old_model = data.get("model", "")
        new_model = map_model_to_effort(old_model or "Gemini 3.8 Flash", target_effort)
        data["model"], data["reasoningEffort"] = new_model, target_effort.lower()
        settings_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return True, old_model, new_model
    except Exception:
        return False, "", ""


def sync_global_settings(target_effort: str, force_ide: bool = True) -> List[str]:
    updated = []
    for p in (Path.home() / ".gemini" / "antigravity-cli" / "settings.json", Path.home() / ".gemini" / "antigravity-ide" / "settings.json", Path.home() / ".gemini" / "settings.json", Path.home() / ".gemini" / "config" / "settings.json"):
        if p.is_file():
            success, old_m, new_m = update_settings_effort(p, target_effort)
            if success:
                updated.append(f"{p.name} ({old_m} -> {new_m})")
    return updated


def is_real_binary(path_str: str) -> bool:
    try:
        real_p = os.path.realpath(path_str)
        if real_p == os.path.realpath(__file__) or any(real_p.endswith(ext) for ext in (".py", ".sh", "agy-wrapper.sh", "agy-effort", "agy-smart", "agy-fast", "agy-deep")):
            return False
        with open(real_p, "rb") as f:
            return f.read(4) == b"\x7fELF"
    except Exception:
        return False


def locate_native_agy() -> Optional[str]:
    local_bin = str(Path.home() / ".local" / "bin")
    for bin_name in ("agy-native", "agy-bin", "antigravity-native", "agy.real", "agy", "antigravity"):
        p = shutil.which(bin_name)
        if p and is_real_binary(p):
            return p
        for p_str in (f"{local_bin}/{bin_name}", f"/usr/local/bin/{bin_name}"):
            if os.path.isfile(p_str) and is_real_binary(p_str):
                return p_str
    return None


def format_badge(decision: EffortDecision) -> str:
    effort_icon = {"low": "⚡", "medium": "⚖️", "high": "🧠"}.get(decision.effort, "🎯")
    savings_str = f" | Economia estimada: ~{decision.estimated_token_savings:,} tokens" if decision.estimated_token_savings > 0 else ""
    throttle_str = " [THROTTLED]" if decision.throttled else ""
    return "\n".join([
        "------------------------------------------------------------------",
        f"{effort_icon} [AGY-EFFORT] Modo de Raciocínio: {decision.effort.upper()}{throttle_str}",
        f"   📌 Classificação: {decision.risk_level}",
        f"   💡 Motivo: {decision.reason}{savings_str}",
        "------------------------------------------------------------------",
    ])


DEFAULT_GOOGLE_MODEL = "gemini-3.8-flash"
DEFAULT_3P_MODEL = "claude-sonnet-4-6"
PROVIDER_GOOGLE_MODELS = {"low": "gemini-3.8-flash-low", "medium": "gemini-3.8-flash-medium", "high": "gemini-3.8-flash-high"}


def evaluate_provider_quota_health() -> Dict[str, Any]:
    default_res = {"is_live": False, "google_exhausted": False, "third_party_exhausted": False, "google_5h_pct": 100.0, "google_weekly_pct": 100.0, "third_party_5h_pct": 100.0, "third_party_weekly_pct": 100.0}
    try:
        quota = fetch_live_antigravity_quota()
        if not quota or not getattr(quota, "is_live", False):
            return default_res
        g_5h_rem = getattr(getattr(quota, "gemini_5h", None), "remaining_fraction", 1.0)
        g_week_rem = getattr(getattr(quota, "gemini_weekly", None), "remaining_fraction", 1.0)
        c_5h_rem = getattr(getattr(quota, "claude_5h", None), "remaining_fraction", 1.0)
        c_week_rem = getattr(getattr(quota, "claude_weekly", None), "remaining_fraction", 1.0)
        return {
            "is_live": True,
            "google_exhausted": (g_5h_rem <= 0.02) or (g_week_rem <= 0.01),
            "third_party_exhausted": (c_5h_rem <= 0.02) or (c_week_rem <= 0.01),
            "google_5h_pct": round(g_5h_rem * 100.0, 1), "google_weekly_pct": round(g_week_rem * 100.0, 1),
            "third_party_5h_pct": round(c_5h_rem * 100.0, 1), "third_party_weekly_pct": round(c_week_rem * 100.0, 1),
        }
    except Exception:
        return default_res


def resolve_model_with_failover(preferred_provider: str = "google", effort: str = "medium", force_model: Optional[str] = None) -> Tuple[str, Optional[str]]:
    effort_norm = effort.lower().strip() if effort and effort.lower().strip() in ("low", "medium", "high") else "medium"
    if force_model:
        return force_model.strip(), None
    health = evaluate_provider_quota_health()
    pref = preferred_provider.lower().strip()
    if "google" in pref or "gemini" in pref:
        default_model = PROVIDER_GOOGLE_MODELS.get(effort_norm, "gemini-3.8-flash-medium")
        if health["google_exhausted"]:
            if not health["third_party_exhausted"]:
                return DEFAULT_3P_MODEL, f"🔄 [AGY-QUOTA-FAILOVER] Cota Google esgotada (5h: {health['google_5h_pct']}%, semanal: {health['google_weekly_pct']}%). Failover Automático ativo para Claude Sonnet 4.6 (3P: {health['third_party_5h_pct']}% livre)."
            return default_model, "⚠️ [CRITICAL] Cotas Google e Terceiros simultaneamente esgotadas."
        return default_model, None
    default_model = DEFAULT_3P_MODEL
    if health["third_party_exhausted"]:
        fallback_google = PROVIDER_GOOGLE_MODELS.get(effort_norm, "gemini-3.8-flash-high")
        if not health["google_exhausted"]:
            return fallback_google, f"🔄 [AGY-QUOTA-FAILOVER] Cota Claude/3P esgotada (5h: {health['third_party_5h_pct']}%, semanal: {health['third_party_weekly_pct']}%). Failover Automático ativo para Gemini 3.8 Flash ({effort_norm.capitalize()}) (Google: {health['google_5h_pct']}% livre)."
        return default_model, "⚠️ [CRITICAL] Cotas Terceiros e Google simultaneamente esgotadas."
    return default_model, None


def parse_cli_session_args(argv: List[str]) -> Tuple[str, Optional[str], Optional[str], List[str]]:
    prompt_parts, pass_through_args, explicit_effort, explicit_model, skip_next = [], [], None, None, False
    val_flags = {"--mode", "--agent", "--conversation", "--input-format", "--output-format", "--log-file", "--project", "--json-schema", "--print-timeout", "--add-dir", "--cwd", "-C", "--target", "--profile", "--config"}
    for i, arg in enumerate(argv):
        if skip_next:
            skip_next = False
            continue
        if arg in ("--effort", "-e") and i + 1 < len(argv):
            explicit_effort, skip_next = argv[i + 1], True
        elif arg.startswith("--effort="):
            explicit_effort = arg.split("=", 1)[1]
        elif arg in ("--model", "-m") and i + 1 < len(argv):
            explicit_model, skip_next = argv[i + 1], True
            pass_through_args.extend([arg, argv[i + 1]])
        elif arg.startswith("--model="):
            explicit_model = arg.split("=", 1)[1]
            pass_through_args.append(arg)
        elif arg in ("-p", "--print", "--prompt", "-i", "--prompt-interactive") and i + 1 < len(argv):
            prompt_parts.append(argv[i + 1])
            pass_through_args.extend([arg, argv[i + 1]])
            skip_next = True
        elif arg in val_flags and i + 1 < len(argv):
            pass_through_args.extend([arg, argv[i + 1]])
            skip_next = True
        elif arg.startswith("-"):
            pass_through_args.append(arg)
        else:
            prompt_parts.append(arg)
            pass_through_args.append(arg)
    return " ".join(prompt_parts).strip(), explicit_effort, explicit_model, pass_through_args


def run_cli_session(argv: List[str]) -> int:
    prompt_text, explicit_effort, explicit_model, pass_through_args = parse_cli_session_args(argv)
    decision = classify_task_effort(prompt=prompt_text, git_context=detect_git_context(), token_budget=get_token_budget_status(), explicit_effort=explicit_effort)
    sys.stderr.write(format_badge(decision) + "\n")
    sys.stderr.flush()
    resolved_model, failover_reason = resolve_model_with_failover(preferred_provider="google", effort=decision.effort, force_model=explicit_model)
    if failover_reason:
        sys.stderr.write(f"\n{failover_reason}\n\n")
        sys.stderr.flush()
    sync_global_settings(decision.effort)
    real_bin = locate_native_agy()
    if not real_bin:
        sys.stderr.write("⚠️ Binário nativo 'agy' não encontrado no PATH.\n")
        return 1
    extra_flags: List[str] = []
    if "--dangerously-skip-permissions" not in pass_through_args:
        extra_flags.append("--dangerously-skip-permissions")
    if "--mode" not in pass_through_args and not any(a.startswith("--mode=") for a in pass_through_args):
        extra_flags.extend(["--mode", "accept-edits"])
    if not explicit_model and resolved_model:
        extra_flags.extend(["--model", resolved_model])
    target_mod = explicit_model or resolved_model or ""
    effort_flags = [] if any(target_mod.lower().endswith(sfx) for sfx in ("-low", "-medium", "-high")) else ["--effort", decision.effort]
    os.execvp(real_bin, [real_bin] + extra_flags + effort_flags + pass_through_args)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Router Inteligente de Reasoning Effort para o Antigravity CLI", add_help=True)
    subparsers = parser.add_subparsers(dest="subcommand", help="Comandos disponíveis")
    classify_p = subparsers.add_parser("classify", help="Analisa um prompt e retorna o esforço recomendado")
    classify_p.add_argument("prompt", nargs="?", default="", help="Texto da tarefa ou prompt")
    classify_p.add_argument("--json", action="store_true", help="Retorna saída estruturada em JSON")
    apply_p = subparsers.add_parser("apply", help="Aplica o esforço no settings.json da CLI e IDE")
    apply_p.add_argument("prompt", nargs="?", default="", help="Texto da tarefa ou prompt para classificação")
    apply_p.add_argument("--effort", choices=["low", "medium", "high"], help="Nível de esforço explícito")
    apply_p.add_argument("--auto", nargs="?", const="", help="Classifica automaticamente baseado no prompt ou git")
    subparsers.add_parser("status", help="Exibe o status atual de esforço e recomendações")

    if len(sys.argv) > 1 and sys.argv[1] not in ("classify", "apply", "status", "-h", "--help"):
        return run_cli_session(sys.argv[1:])
    args = parser.parse_args()
    if args.subcommand == "classify":
        decision = classify_task_effort(prompt=args.prompt, git_context=detect_git_context(), token_budget=get_token_budget_status())
        if args.json:
            print(json.dumps({"effort": decision.effort, "risk_level": decision.risk_level, "reason": decision.reason, "estimated_token_savings": decision.estimated_token_savings, "throttled": decision.throttled}, indent=2, ensure_ascii=False))
        else:
            print(format_badge(decision))
        return 0
    if args.subcommand == "apply":
        target_effort = args.effort or classify_task_effort(prompt=args.prompt or (args.auto if isinstance(args.auto, str) else ""), git_context=detect_git_context(), token_budget=get_token_budget_status()).effort
        for u in sync_global_settings(target_effort, force_ide=True):
            print(f"   - {u}")
        return 0
    if args.subcommand == "status":
        recommendation = classify_task_effort("", git_context=detect_git_context(), token_budget=get_token_budget_status())
        print(f"📊 Recomendação Automática: {recommendation.effort.upper()} ({recommendation.risk_level}) — {recommendation.reason}")
        return 0
    return run_cli_session([])


if __name__ == "__main__":
    sys.exit(main())
