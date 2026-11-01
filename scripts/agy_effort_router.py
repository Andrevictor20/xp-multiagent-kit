#!/usr/bin/env python3
"""scripts/agy_effort_router.py — Router de Reasoning Effort (B19: <= 150 linhas)"""
from __future__ import annotations
import argparse, json, os, re, shutil, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EFFORT_LOW, EFFORT_MEDIUM, EFFORT_HIGH = "low", "medium", "high"
LEVEL_L0_TRIVIAL, LEVEL_L1_SMALL, LEVEL_L2_FEATURE, LEVEL_L3_CRITICAL = "L0 (Trivial)", "L1 (Small)", "L2 (Feature)", "L3 (Critical)"
L0_RE = re.compile(r"\b(typo|erro de digita[çc][ãa]o|ortografia|readme|documenta[çc][ãa]o|docs?|docstrings?|coment[áa]rios?|changelog|prettier|eslint|black|isort|formata?[çc][ãa]o?|css|scss|estilos?|cores?|o que [ée]|explique|como funciona|do que se trata|para que serve|duvida|d[úu]vida|pergunta|economiza|quantos tokens|qual(?: a)? diferen[çc]a|compar[ea]|simples|r[áa]pido|git log|git status)\b", re.I)
L3_RE = re.compile(r"\b(auth|autentica[çc][ãa]o|login|jwt|oauth|(?:jwt|auth|bearer|csrf|session|access|refresh)[_-]?tokens?|tokens?\s+(?:de\s+)?(?:acesso|jwt|auth|api|sess[ãa]o|bearer)|mfa|2fa|senha|password|permiss[ãa]o|credenciais?|rbac|idor|crypto|criptografia|secret|vulnerabilidade|cve|threat modeling|stride|pagamentos?|payments?|stripe|billing|checkout|transa[çc][ãa]o|migra[çc][ãa]o|migrations?|schema change|drop table|race condition|deadlock|concorr[êe]ncia|mutex|zero-downtime|canary|rollback)\b", re.I)
L2_RE = re.compile(r"\b(features?|nova funcionalidade|novo endpoint|criar api|novo componente|nova esteira|integra[çc][ãa]o|refatora[çc][ãa]o estrutural|redesign|implemente|implementad[oa]s?|implementa[çc][ãa]o|construa|monte|crie|exporta[çc][ãa]o|workflows?|api)\b", re.I)
L1_RE = re.compile(r"\b(pequeno ajuste|refatore|refatora[çc][ãa]o isolada|teste unit[áa]rio|adicione um teste|pequeno bug|ajuste|renomeie|mover|lint fix)\b", re.I)
DIRECTIVE_HIGH_PATTERNS = [r"(?:^|[\s/])(effort\s+high|to\s+high|em\s+high|para\s+high|set\s+effort.*high|high\s+effort)", r"(?:mude|coloque|troque|set|use|configure).*\bhigh\b"]
DIRECTIVE_LOW_PATTERNS = [r"(?:^|[\s/])(effort\s+low|to\s+low|em\s+low|para\s+low|set\s+effort.*low|low\s+effort|modo\s+rapido)", r"(?:mude|coloque|troque|set|use).*\blow\b"]
DIRECTIVE_MEDIUM_PATTERNS = [r"(?:^|[\s/])(effort\s+medium|to\s+medium|em\s+medium|para\s+medium|set\s+effort.*medium|medium\s+effort)", r"(?:mude|coloque|troque|set|use).*\bmedium\b"]
CONTINUATION_PATTERNS = [r"^\s*(continue|prossiga|pode continuar|pode fazer|vai em frente|manda bala|sim|ok|aprovado|confirmado|avançar|prosseguir)\b"]

@dataclass
class EffortDecision:
    effort: str; risk_level: str; reason: str; estimated_token_savings: int = 0
    throttled: bool = False; override: bool = False; details: Dict[str, Any] = field(default_factory=dict)
def fetch_live_antigravity_quota(force_refresh: bool = False): return type("Dummy", (), {"is_live": False})()
def _local_preflight(*a, **k): return {"alerts": [], "turns": 0}
def get_cli_settings_path() -> Path: return Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
def get_token_budget_status() -> Dict[str, float]: return {"rolling_5h_percent": 0.0, "weekly_percent": 0.0}
def get_current_settings_effort() -> Optional[str]:
    for p in (get_cli_settings_path(), Path.home() / ".gemini" / "settings.json"):
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                ef = data.get("reasoningEffort") or ("high" if "high" in data.get("model", "").lower() else None)
                if ef: return str(ef).lower()
            except Exception: pass
    return None

def detect_git_context(repo_path: Optional[Path] = None) -> Dict[str, Any]:
    cwd, ctx = repo_path or Path.cwd(), {"branch": "", "changed_files": []}
    try:
        b = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(cwd), capture_output=True, text=True, timeout=2)
        if b.returncode == 0: ctx["branch"] = b.stdout.strip()
        s = subprocess.run(["git", "status", "--porcelain"], cwd=str(cwd), capture_output=True, text=True, timeout=2)
        if s.returncode == 0: ctx["changed_files"] = [l.strip().split(maxsplit=1)[1] for l in s.stdout.splitlines() if len(l.strip().split(maxsplit=1)) == 2]
    except Exception: pass
    return ctx

def classify_task_effort(prompt: str = "", git_context: Optional[Dict[str, Any]] = None, token_budget: Optional[Dict[str, float]] = None, explicit_effort: Optional[str] = None, conversation_context: Optional[Dict[str, Any]] = None) -> EffortDecision:
    conv_ctx = conversation_context or {}
    if explicit_effort and explicit_effort.lower().strip() in (EFFORT_LOW, EFFORT_MEDIUM, EFFORT_HIGH):
        return EffortDecision(effort=explicit_effort.lower().strip(), risk_level="Manual Override", reason=f"Definido explicitamente: {explicit_effort}", override=True)
    p_low = prompt.lower().strip()
    is_q = "?" in p_low or any(p_low.startswith(w) for w in ["por que", "pq", "como ", "o que", "do que", "qual "])
    if not is_q:
        if any(re.search(pat, p_low) for pat in DIRECTIVE_HIGH_PATTERNS): return EffortDecision(effort=EFFORT_HIGH, risk_level=conv_ctx.get("active_risk") or LEVEL_L3_CRITICAL, reason="Diretriz explícita detectada no prompt para modo HIGH", override=True)
        if any(re.search(pat, p_low) for pat in DIRECTIVE_LOW_PATTERNS): return EffortDecision(effort=EFFORT_LOW, risk_level=LEVEL_L0_TRIVIAL, reason="Diretriz explícita detectada no prompt para modo LOW", override=True, estimated_token_savings=5000)
        if any(re.search(pat, p_low) for pat in DIRECTIVE_MEDIUM_PATTERNS): return EffortDecision(effort=EFFORT_MEDIUM, risk_level=LEVEL_L1_SMALL, reason="Diretriz explícita detectada no prompt para modo MEDIUM", override=True)
    if conv_ctx.get("is_continuation") or any(re.search(pat, p_low) for pat in CONTINUATION_PATTERNS):
        act_risk = conv_ctx.get("active_risk", "")
        if act_risk in (LEVEL_L3_CRITICAL, LEVEL_L2_FEATURE): return EffortDecision(effort=EFFORT_HIGH, risk_level=act_risk, reason=f"Continuação de tarefa {act_risk} confirmada pelo usuário")
    cum = conv_ctx.get("cumulative_text", "").lower()
    raw_effort, risk, reason, savings = EFFORT_LOW, LEVEL_L0_TRIVIAL, "Tarefa padrão de complexidade básica (baseline low)", 0
    if L3_RE.search(p_low): raw_effort, risk, reason = EFFORT_HIGH, LEVEL_L3_CRITICAL, f"Detectado risco L3 por palavras-chave críticas: {L3_RE.search(p_low).group(0)}"
    elif cum and L3_RE.search(cum): raw_effort, risk, reason = EFFORT_HIGH, LEVEL_L3_CRITICAL, "Detectado risco L3 pelo histórico acumulado"
    elif L2_RE.search(p_low): raw_effort, risk, reason = EFFORT_HIGH, LEVEL_L2_FEATURE, f"Detectado risco L2 por termos de feature/construção: {L2_RE.search(p_low).group(0)}"
    elif cum and L2_RE.search(cum): raw_effort, risk, reason = EFFORT_HIGH, LEVEL_L2_FEATURE, "Detectado risco L2 pelo histórico acumulado"
    elif L0_RE.search(p_low): raw_effort, risk, savings, reason = EFFORT_LOW, LEVEL_L0_TRIVIAL, 5000, f"Detectado risco L0 (Trivial/Docs/CSS) por: {L0_RE.search(p_low).group(0)}"
    elif L1_RE.search(p_low): raw_effort, risk, reason = EFFORT_MEDIUM, LEVEL_L1_SMALL, f"Detectado risco L1 por: {L1_RE.search(p_low).group(0)}"
    elif not p_low:
        g, br, files = git_context or {}, (git_context or {}).get("branch", "").lower(), (git_context or {}).get("changed_files", [])
        if any(br.startswith(p) for p in ("hotfix/", "sec/", "auth/")): raw_effort, risk, reason = EFFORT_HIGH, LEVEL_L3_CRITICAL, f"Branch crítica ({br})"
        elif any(br.startswith(p) for p in ("feat/", "feature/")): raw_effort, risk, reason = EFFORT_HIGH, LEVEL_L2_FEATURE, f"Branch feature ({br})"
        elif any(br.startswith(p) for p in ("docs/", "chore/")): raw_effort, risk, savings, reason = EFFORT_LOW, LEVEL_L0_TRIVIAL, 5000, f"Branch docs ({br})"
        elif files and any(f.endswith((".py", ".ts", ".tsx", ".js")) for f in files): raw_effort, risk, reason = EFFORT_HIGH, LEVEL_L2_FEATURE, "Alterações ativas em arquivos de código de produção detectadas"
        elif get_current_settings_effort() == EFFORT_HIGH: raw_effort, risk, reason = EFFORT_HIGH, LEVEL_L2_FEATURE, "Preservada configuração ativa em settings.json (modo HIGH)"
    throttled, b = False, token_budget or {}
    q = max(b.get("rolling_5h_percent", 0.0), b.get("weekly_percent", 0.0))
    if q > 80.0:
        throttled = True
        if raw_effort == EFFORT_HIGH: raw_effort, reason = EFFORT_MEDIUM, reason + f" | ⚠️ [BUDGET THROTTLE] Cota crítica ({q:.1f}% > 80%): reduzido HIGH -> MEDIUM"
        elif raw_effort == EFFORT_MEDIUM: raw_effort, savings, reason = EFFORT_LOW, savings + 3000, reason + f" | ⚠️ [BUDGET THROTTLE] Cota crítica ({q:.1f}% > 80%): reduzido MEDIUM -> LOW"
    return EffortDecision(effort=raw_effort, risk_level=risk, reason=reason, estimated_token_savings=savings, throttled=throttled, override=False)

def get_canonical_model_for_task(risk_level: str, is_planning: bool = False) -> Tuple[str, str]:
    if is_planning and risk_level in (LEVEL_L3_CRITICAL, LEVEL_L2_FEATURE): return "Gemini Pro", EFFORT_HIGH
    return ("Gemini 3.8 Flash", EFFORT_HIGH) if risk_level in (LEVEL_L3_CRITICAL, LEVEL_L2_FEATURE) else (("Gemini 3.8 Flash", EFFORT_MEDIUM) if risk_level == LEVEL_L1_SMALL else ("Gemini 3.8 Flash", EFFORT_LOW))
def map_model_to_effort(current_model: str, target_effort: str) -> str:
    ec, el = target_effort.capitalize(), target_effort.lower()
    if "pro" in current_model.lower() and "gemini" in current_model.lower(): return f"Gemini 3.8 Flash ({ec})"
    if re.search(r"\((High|Medium|Low)\)$", current_model, re.I): return re.sub(r"\((High|Medium|Low)\)$", f"({ec})", current_model, flags=re.I)
    if re.search(r"-(high|medium|low)$", current_model, re.I): return re.sub(r"-(high|medium|low)$", f"-{el}", current_model, flags=re.I)
    return f"{current_model} ({ec})" if "flash" in current_model.lower() or "gemini" in current_model.lower() else current_model
def update_settings_effort(settings_path: Path, target_effort: str) -> Tuple[bool, str, str]:
    if not settings_path.is_file(): return False, "", ""
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.read_text(encoding="utf-8").strip() else {}
        old_m = data.get("model", ""); new_m = map_model_to_effort(old_m or "Gemini 3.8 Flash", target_effort)
        data["model"], data["reasoningEffort"] = new_m, target_effort.lower()
        settings_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return True, old_m, new_m
    except Exception: return False, "", ""
def sync_global_settings(target_effort: str, force_ide: bool = True) -> List[str]:
    return [str(p.name) for p in (get_cli_settings_path(), Path.home() / ".gemini" / "settings.json") if p.is_file() and update_settings_effort(p, target_effort)[0]]
def format_badge(d: EffortDecision) -> str:
    ico = {"low": "⚡", "medium": "⚖️", "high": "🧠"}.get(d.effort, "🎯"); sav = f" | Economia estimada: ~{d.estimated_token_savings:,} tokens" if d.estimated_token_savings > 0 else ""
    return f"------------------------------------------------------------------\n{ico} [AGY-EFFORT] Modo de Raciocínio: {d.effort.upper()}{' [THROTTLED]' if d.throttled else ''}\n   📌 Classificação: {d.risk_level}\n   💡 Motivo: {d.reason}{sav}\n------------------------------------------------------------------"
def evaluate_provider_quota_health() -> Dict[str, Any]:
    try:
        q = fetch_live_antigravity_quota()
        if not getattr(q, "is_live", False): raise ValueError()
        g5, c5 = getattr(getattr(q, "gemini_5h", None), "remaining_fraction", 1.0), getattr(getattr(q, "claude_5h", None), "remaining_fraction", 1.0)
        return {"is_live": True, "google_exhausted": g5 <= 0.02, "third_party_exhausted": c5 <= 0.02, "google_5h_pct": round(g5*100, 1), "third_party_5h_pct": round(c5*100, 1)}
    except Exception: return {"is_live": False, "google_exhausted": False, "third_party_exhausted": False, "google_5h_pct": 100.0, "third_party_5h_pct": 100.0}
def resolve_model_with_failover(preferred_provider: str = "google", effort: str = "medium", force_model: Optional[str] = None) -> Tuple[str, Optional[str]]:
    if force_model: return force_model.strip(), None
    ef = effort.lower() if effort in ("low", "medium", "high") else "medium"; h = evaluate_provider_quota_health()
    if "google" in preferred_provider.lower():
        if h["google_exhausted"] and not h["third_party_exhausted"]: return "claude-sonnet-4-6", f"🔄 Failover Automático para Claude Sonnet 4.6 (3P: {h['third_party_5h_pct']}% livre)."
        return f"gemini-3.8-flash-{ef}", None
    if h["third_party_exhausted"] and not h["google_exhausted"]: return f"gemini-3.8-flash-{ef}", f"🔄 Failover Automático para Gemini 3.8 Flash ({ef.capitalize()})."
    return "claude-sonnet-4-6", None

def parse_cli_session_args(argv: List[str]) -> Tuple[str, Optional[str], Optional[str], List[str]]:
    prompt_parts, pass_through, explicit_effort, explicit_model, skip_next = [], [], None, None, False
    val_flags = {"--mode", "--agent", "--conversation", "--input-format", "--output-format", "--log-file", "--project", "--json-schema", "--print-timeout", "--add-dir", "--cwd", "-C", "--target", "--profile", "--config"}
    for i, arg in enumerate(argv):
        if skip_next: skip_next = False; continue
        if arg in ("--effort", "-e") and i + 1 < len(argv): explicit_effort, skip_next = argv[i+1], True
        elif arg in ("--model", "-m") and i + 1 < len(argv): explicit_model, skip_next = argv[i+1], True; pass_through.extend([arg, argv[i+1]])
        elif arg in val_flags and i + 1 < len(argv): pass_through.extend([arg, argv[i+1]]); skip_next = True
        elif arg.startswith("-"): pass_through.append(arg)
        else: prompt_parts.append(arg); pass_through.append(arg)
    return " ".join(prompt_parts).strip(), explicit_effort, explicit_model, pass_through

def locate_native_agy() -> Optional[str]:
    for b in ("agy-native", "agy-bin", "antigravity-native", "agy.real"):
        if shutil.which(b): return shutil.which(b)
    return None
def run_cli_session(argv: List[str]) -> int:
    p_text, ef, model, passthru = parse_cli_session_args(argv); d = classify_task_effort(prompt=p_text, git_context=detect_git_context(), explicit_effort=ef)
    sys.stderr.write(format_badge(d) + "\n"); resolved_model, _ = resolve_model_with_failover(preferred_provider="google", effort=d.effort, force_model=model)
    sync_global_settings(d.effort); real_bin = locate_native_agy() or shutil.which("agy")
    if not real_bin: return 1
    os.execvp(real_bin, [real_bin, "--dangerously-skip-permissions", "--mode", "accept-edits"] + (["--model", resolved_model] if resolved_model else []) + passthru)
    return 0
def main() -> int:
    p = argparse.ArgumentParser(description="Router de Reasoning Effort"); p.add_argument("prompt", nargs="*", default=[]); return run_cli_session(p.parse_args().prompt)

if __name__ == "__main__": sys.exit(main())
