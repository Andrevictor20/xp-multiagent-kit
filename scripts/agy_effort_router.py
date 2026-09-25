#!/usr/bin/env python3
"""
scripts/agy_effort_router.py
Router Inteligente de Reasoning Effort para o Antigravity CLI.
XP Multi-Agent Kit v2

Analisa o prompt do usuário, contexto do git e cota de tokens (5h/semanal)
para modular dinamicamente o esforço do modelo (low | medium | high),
economizando de 3.000 a 8.000 tokens de raciocínio em tarefas L0/L1
e garantindo profundidade máxima (high) em L2/L3.
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

# Constantes de esforço
EFFORT_LOW = "low"
EFFORT_MEDIUM = "medium"
EFFORT_HIGH = "high"

# Constantes de nível de risco
LEVEL_L0_TRIVIAL = "L0 (Trivial)"
LEVEL_L1_SMALL = "L1 (Small)"
LEVEL_L2_FEATURE = "L2 (Feature)"
LEVEL_L3_CRITICAL = "L3 (Critical)"

# Padrões e palavras-chave de classificação
L0_KEYWORDS = [
    r"\btypo\b", r"\berro de digita[çc][ãa]o\b", r"\bortografia\b", r"\bescrita\b",
    r"\breadme\b", r"\bdocumenta[çc][ãa]o\b", r"\bdocs?\b", r"\bdocstrings?\b",
    r"\bcoment[áa]rios?\b", r"\bchangelog\b",
    r"\bprettier\b", r"\beslint\b", r"\bblack\b", r"\bisort\b", r"\bformate?\b",
    r"\bformata[çc][ãa]o\b", r"\bidenta[çc][ãa]o\b", r"\bindenta[çc][ãa]o\b",
    r"\bcss\b", r"\bscss\b", r"\bestilos?\b", r"\bpadding\b", r"\bmargin\b",
    r"\bcores?\b", r"\bfont-size\b",
    r"\bo que [ée]\b", r"\bexplique\b", r"\bcomo funciona\b", r"\bquais s[ãa]o\b",
    r"\bdo que se trata\b", r"\bo que faz\b", r"\bpara que serve\b", r"\bcomo uso\b", r"\bcomo usar\b",
    r"\bduvida\b", r"\bd[úu]vida\b", r"\bpergunta\b", r"\bquest[ãa]o\b",
    r"\beconomiza\b", r"\beconomizar\b", r"\beconomia de tokens?\b", r"\bquantos tokens\b",
    r"\bqual(?: a)? diferen[çc]a\b", r"\bcompar[ea]\b", r"\bcomparativo\b",
    r"\bde forma simples\b", r"\bsimples\b", r"\br[áa]pido\b", r"\bb[áa]sico\b",
    r"\bresumo\b", r"\bstatus\b", r"\bgit log\b", r"\bgit status\b",
    r"\bquais arquivos\b", r"\bclean code\b",
]

L3_KEYWORDS = [
    r"\bauth\b", r"\bautentica[çc][ãa]o\b", r"\blogin\b", r"\bjwt\b", r"\boauth\b",
    r"\b(?:jwt|auth|bearer|csrf|session|access|refresh)[_-]?tokens?\b",
    r"\btokens?\s+(?:de\s+)?(?:acesso|jwt|auth|api|sess[ãa]o|bearer)\b",
    r"\bmfa\b", r"\b2fa\b", r"\bdois fatores\b", r"\bmulti-factor\b",
    r"\bsenha\b", r"\bpassword\b", r"\bpermiss[ãa]o\b", r"\bcredenciais?\b",
    r"\brbac\b", r"\bidor\b", r"\bcrypto\b", r"\bcriptografia\b", r"\bsecret\b",
    r"\bvulnerabilidade\b", r"\bcve\b", r"\bthreat modeling\b", r"\bstride\b",
    r"\bpagamento\b", r"\bpayment\b", r"\bstripe\b", r"\bbilling\b", r"\bcheckout\b",
    r"\btransa[çc][ãa]o\b", r"\bfatura\b",
    r"\bmigra[çc][ãa]o\b", r"\bmigrations?\b", r"\bschema change\b", r"\bdrop table\b",
    r"\balter table\b", r"\b[íi]ndice concorrente\b", r"\brace condition\b",
    r"\bdeadlock\b", r"\bconcorr[êe]ncia\b", r"\bmutex\b", r"\bgoroutine\b",
    r"\bthread safety\b", r"\bzero-downtime\b", r"\bblue-green\b", r"\bcanary\b",
    r"\brollback\b", r"\bkernel panic\b", r"\bcrash\b", r"\bmemory leak\b",
    r"\bcausa raiz\b", r"\broot cause\b", r"\bflaky test\b", r"\bstop gate\b",
    r"\brisco l3\b",
]

L2_KEYWORDS = [
    r"\bfeature\b", r"\bnova funcionalidade\b", r"\bnovo endpoint\b", r"\bcriar api\b",
    r"\bnovo componente\b", r"\bnova esteira\b", r"\bintegra[çc][ãa]o\b",
    r"\brefatora[çc][ãa]o estrutural\b", r"\bredesign\b", r"\bimplemente\b",
    r"\bconstrua\b", r"\bmonte\b", r"\bcrie\b", r"\bexporta[çc][ãa]o\b",
    r"\bworkflows?\b", r"\bapi\b",
    r"\bdispositivos m[óo]veis\b", r"\bmobile\b", r"\bresponsiv(?:o|a|idade)\b",
    r"\bvisualiza[çc][ãa]o\b", r"\binterface\b", r"\btelas?\b", r"\bcontainers?\b",
    r"\bmonitoramento\b", r"\bdetec[çc][ãa]o autom[áa]tica\b",
    r"\bcorrija esse comportamento\b", r"\bcomportamento incorreto\b",
    r"\brisco l2\b",
]

L1_KEYWORDS = [
    r"\bpequeno ajuste\b", r"\brefatore\b", r"\brefatora[çc][ãa]o isolada\b",
    r"\bteste unit[áa]rio\b", r"\badicione um teste\b", r"\bpequeno bug\b",
    r"\bajuste\b", r"\brenomeie\b", r"\bmover\b", r"\blint fix\b",
]

# Diretrizes explícitas de esforço em linguagem natural ou comandos
DIRECTIVE_HIGH_PATTERNS = [
    r"\b(?:mude|mudar|coloque|colocar|altere|alterar|troque|trocar|set|setar|muda|use|usar|coloquem?|troquem?)\s+(?:para\s+|em\s+|no\s+|pro\s+|o\s+|o\s+modelo\s+em\s+|o\s+modo\s+)?(?:effort\s+)?(?:to\s+)?high\b",
    r"\b(?:effort|racioc[íi]nio|reasoning|modo)\s+(?:em\s+|para\s+|no\s+|to\s+)?high\b",
    r"\bset\s+effort\s+(?:to\s+)?high\b",
    r"\bhigh\s+(?:effort|reasoning|mode)\b",
    r"\b/effort\s+high\b",
    r"\b(?:deep|m[áa]ximo)\s+effort\b",
    r"\b(?:modo|effort)\s+profundo\b",
]

DIRECTIVE_LOW_PATTERNS = [
    r"\b(?:mude|mudar|coloque|colocar|altere|alterar|troque|trocar|set|setar|muda|use|usar)\s+(?:para\s+|em\s+|no\s+|pro\s+|o\s+|o\s+modelo\s+em\s+|o\s+modo\s+)?(?:effort\s+)?(?:to\s+)?low\b",
    r"\b(?:effort|racioc[íi]nio|reasoning|modo)\s+(?:em\s+|para\s+|no\s+|to\s+)?low\b",
    r"\bset\s+effort\s+(?:to\s+)?low\b",
    r"\blow\s+(?:effort|reasoning|mode)\b",
    r"\b/effort\s+low\b",
    r"\bfast\s+effort\b",
    r"\b(?:modo|effort)\s+r[áa]pido\b",
]

DIRECTIVE_MEDIUM_PATTERNS = [
    r"\b(?:mude|mudar|coloque|colocar|altere|alterar|troque|trocar|set|setar|muda|use|usar)\s+(?:para\s+|em\s+|no\s+|pro\s+|o\s+|o\s+modelo\s+em\s+|o\s+modo\s+)?(?:effort\s+)?(?:to\s+)?medium\b",
    r"\b(?:effort|racioc[íi]nio|reasoning|modo)\s+(?:em\s+|para\s+|no\s+|to\s+)?medium\b",
    r"\bset\s+effort\s+(?:to\s+)?medium\b",
    r"\bmedium\s+(?:effort|reasoning|mode)\b",
    r"\b/effort\s+medium\b",
    r"\b(?:modo|effort)\s+equilibrado\b",
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
    """Retorna o caminho do settings.json do CLI."""
    return Path.home() / ".gemini" / "antigravity-cli" / "settings.json"


def get_current_settings_effort() -> Optional[str]:
    """Lê o effort atualmente configurado nos settings da CLI ou IDE."""
    for p in (
        get_cli_settings_path(),
        Path.home() / ".gemini" / "antigravity-ide" / "settings.json",
        Path.home() / ".gemini" / "settings.json",
    ):
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                effort = data.get("reasoningEffort")
                if effort and str(effort).lower() in (EFFORT_LOW, EFFORT_MEDIUM, EFFORT_HIGH):
                    return str(effort).lower()
                model = data.get("model", "")
                if "high" in model.lower():
                    return EFFORT_HIGH
                if "low" in model.lower():
                    return EFFORT_LOW
                if "medium" in model.lower():
                    return EFFORT_MEDIUM
            except Exception:
                continue
    return None


def detect_git_context(repo_path: Optional[Path] = None) -> Dict[str, Any]:
    """Detecta informações do repositório Git atual."""
    cwd = repo_path or Path.cwd()
    context = {"branch": "", "changed_files": []}
    try:
        branch_proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=2,
        )
        if branch_proc.returncode == 0:
            context["branch"] = branch_proc.stdout.strip()

        status_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=2,
        )
        if status_proc.returncode == 0:
            files = []
            for line in status_proc.stdout.splitlines():
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    files.append(parts[1])
            context["changed_files"] = files
    except Exception:
        pass
    return context


def get_token_budget_status() -> Dict[str, float]:
    """Consulta estimativas de cota de tokens via token_tracker."""
    status = {"rolling_5h_percent": 0.0, "weekly_percent": 0.0}
    try:
        tracker_script = Path(__file__).resolve().parent / "token_tracker.py"
        if tracker_script.is_file():
            proc = subprocess.run(
                [sys.executable, str(tracker_script), "--json"],
                cwd=str(tracker_script.parent.parent),
                capture_output=True,
                text=True,
                timeout=3,
            )
            if proc.returncode == 0:
                data = json.loads(proc.stdout)
                # Extrair limites
                rolling = data.get("rolling_windows", {})
                status["rolling_5h_percent"] = float(rolling.get("window_5h", {}).get("percent_used", 0.0))
                status["weekly_percent"] = float(rolling.get("window_weekly", {}).get("percent_used", 0.0))
    except Exception:
        pass
    return status


def classify_task_effort(
    prompt: str = "",
    git_context: Optional[Dict[str, Any]] = None,
    token_budget: Optional[Dict[str, float]] = None,
    explicit_effort: Optional[str] = None,
    conversation_context: Optional[Dict[str, Any]] = None,
) -> EffortDecision:
    """Classifica o esforço ideal de raciocínio de forma inteligente e contextual."""
    conv_ctx = conversation_context or {}

    # 1. Override explícito do usuário via flag CLI
    if explicit_effort:
        norm_effort = explicit_effort.lower().strip()
        if norm_effort in (EFFORT_LOW, EFFORT_MEDIUM, EFFORT_HIGH):
            return EffortDecision(
                effort=norm_effort,
                risk_level="Manual Override",
                reason=f"Definido explicitamente pelo usuário via flag --effort {norm_effort}",
                override=True,
            )

    p_lower = prompt.lower().strip()
    git_ctx = git_context or {}
    budget = token_budget or {}

    # 2. Diretriz explícita em linguagem natural no prompt
    for pat in DIRECTIVE_HIGH_PATTERNS:
        if re.search(pat, p_lower):
            return EffortDecision(
                effort=EFFORT_HIGH,
                risk_level=conv_ctx.get("active_risk") or LEVEL_L3_CRITICAL,
                reason="Diretriz explícita detectada no prompt para modo HIGH",
                override=True,
            )

    for pat in DIRECTIVE_LOW_PATTERNS:
        if re.search(pat, p_lower):
            return EffortDecision(
                effort=EFFORT_LOW,
                risk_level=LEVEL_L0_TRIVIAL,
                reason="Diretriz explícita detectada no prompt para modo LOW",
                override=True,
                estimated_token_savings=5000,
            )

    for pat in DIRECTIVE_MEDIUM_PATTERNS:
        if re.search(pat, p_lower):
            return EffortDecision(
                effort=EFFORT_MEDIUM,
                risk_level=LEVEL_L1_SMALL,
                reason="Diretriz explícita detectada no prompt para modo MEDIUM",
                override=True,
            )

    # 3. Continuação de tarefa ativa (Stop Gate / confirmação de plano / avanço)
    is_cont = conv_ctx.get("is_continuation", False) or any(re.search(pat, p_lower) for pat in CONTINUATION_PATTERNS)
    active_risk = conv_ctx.get("active_risk", "")
    cumulative_text = conv_ctx.get("cumulative_text", "").lower()

    if is_cont:
        if active_risk in (LEVEL_L3_CRITICAL, LEVEL_L2_FEATURE):
            return EffortDecision(
                effort=EFFORT_HIGH,
                risk_level=active_risk,
                reason=f"Continuação de tarefa {active_risk} confirmada pelo usuário",
            )
        elif cumulative_text and any(re.search(kw, cumulative_text) for kw in L3_KEYWORDS):
            matched_l3_cum = [kw for kw in L3_KEYWORDS if re.search(kw, cumulative_text)]
            return EffortDecision(
                effort=EFFORT_HIGH,
                risk_level=LEVEL_L3_CRITICAL,
                reason=f"Continuação com contexto acumulado L3 (Critical): {', '.join(matched_l3_cum[:2])}",
            )
        elif cumulative_text and any(re.search(kw, cumulative_text) for kw in L2_KEYWORDS):
            matched_l2_cum = [kw for kw in L2_KEYWORDS if re.search(kw, cumulative_text)]
            return EffortDecision(
                effort=EFFORT_HIGH,
                risk_level=LEVEL_L2_FEATURE,
                reason=f"Continuação com contexto acumulado L2 (Feature): {', '.join(matched_l2_cum[:2])}",
            )

    raw_effort = EFFORT_MEDIUM
    risk_level = LEVEL_L1_SMALL
    reason = "Tarefa padrão de complexidade moderada"
    savings = 0

    # 4. Avaliação de L3 (Crítico / Segurança / DB / Auth / Pagamentos)
    matched_l3 = [kw for kw in L3_KEYWORDS if re.search(kw, p_lower)]
    if matched_l3:
        raw_effort = EFFORT_HIGH
        risk_level = LEVEL_L3_CRITICAL
        reason = f"Detectado risco L3 por palavras-chave críticas: {', '.join(matched_l3[:3])}"
    elif cumulative_text and any(re.search(kw, cumulative_text) for kw in L3_KEYWORDS):
        matched_l3_cum = [kw for kw in L3_KEYWORDS if re.search(kw, cumulative_text)]
        raw_effort = EFFORT_HIGH
        risk_level = LEVEL_L3_CRITICAL
        reason = f"Detectado risco L3 pelo histórico acumulado: {', '.join(matched_l3_cum[:3])}"

    # 5. Avaliação de L2 (Feature / Novas APIs / Componentes)
    elif any(re.search(kw, p_lower) for kw in L2_KEYWORDS):
        matched_l2 = [kw for kw in L2_KEYWORDS if re.search(kw, p_lower)]
        raw_effort = EFFORT_HIGH
        risk_level = LEVEL_L2_FEATURE
        reason = f"Detectado risco L2 por termos de feature/construção: {', '.join(matched_l2[:3])}"
    elif cumulative_text and any(re.search(kw, cumulative_text) for kw in L2_KEYWORDS):
        matched_l2_cum = [kw for kw in L2_KEYWORDS if re.search(kw, cumulative_text)]
        raw_effort = EFFORT_HIGH
        risk_level = LEVEL_L2_FEATURE
        reason = f"Detectado risco L2 pelo histórico acumulado: {', '.join(matched_l2_cum[:3])}"

    # 6. Avaliação de L0 (Trivial / Docs / CSS / Typo)
    elif any(re.search(kw, p_lower) for kw in L0_KEYWORDS):
        matched_l0 = [kw for kw in L0_KEYWORDS if re.search(kw, p_lower)]
        raw_effort = EFFORT_LOW
        risk_level = LEVEL_L0_TRIVIAL
        savings = 5000
        reason = f"Detectado risco L0 (Trivial/Docs/CSS) por: {', '.join(matched_l0[:3])}"

    # 7. Avaliação de L1 (Pequeno ajuste / Refatoração isolada)
    elif any(re.search(kw, p_lower) for kw in L1_KEYWORDS):
        matched_l1 = [kw for kw in L1_KEYWORDS if re.search(kw, p_lower)]
        raw_effort = EFFORT_MEDIUM
        risk_level = LEVEL_L1_SMALL
        reason = f"Detectado risco L1 por: {', '.join(matched_l1[:3])}"

    # 8. Heurística via Git Context e Settings se o prompt for vazio
    elif not p_lower:
        branch = git_ctx.get("branch", "").lower()
        files = git_ctx.get("changed_files", [])

        if any(branch.startswith(prefix) for prefix in ("hotfix/", "sec/", "auth/", "critical/")):
            raw_effort = EFFORT_HIGH
            risk_level = LEVEL_L3_CRITICAL
            reason = f"Branch de segurança/hotfix detectada ({branch})"
        elif any(branch.startswith(prefix) for prefix in ("feat/", "feature/")):
            raw_effort = EFFORT_HIGH
            risk_level = LEVEL_L2_FEATURE
            reason = f"Branch de feature detectada ({branch})"
        elif any(branch.startswith(prefix) for prefix in ("docs/", "chore/", "style/")):
            raw_effort = EFFORT_LOW
            risk_level = LEVEL_L0_TRIVIAL
            savings = 5000
            reason = f"Branch de documentação/estilo detectada ({branch})"
        elif files and all(f.endswith((".md", ".txt", ".css", ".scss")) for f in files):
            raw_effort = EFFORT_LOW
            risk_level = LEVEL_L0_TRIVIAL
            savings = 5000
            reason = "Todos os arquivos modificados são documentação ou estilos cosméticos"
        elif any("migration" in f or "auth" in f for f in files):
            raw_effort = EFFORT_HIGH
            risk_level = LEVEL_L3_CRITICAL
            reason = "Arquivos modificados envolvem migrações ou autenticação"
        elif files and any(f.endswith((".py", ".ts", ".tsx", ".js", ".go", ".rs", ".java")) for f in files):
            raw_effort = EFFORT_HIGH
            risk_level = LEVEL_L2_FEATURE
            reason = "Alterações ativas em arquivos de código de produção detectadas"
        else:
            current_saved = get_current_settings_effort()
            if current_saved == EFFORT_HIGH:
                raw_effort = EFFORT_HIGH
                risk_level = LEVEL_L2_FEATURE
                reason = "Preservada configuração ativa em settings.json (modo HIGH)"
            else:
                raw_effort = EFFORT_MEDIUM
                risk_level = LEVEL_L1_SMALL
                reason = "Sessão interativa sem prompt inicial (baseline medium)"

    # 9. Pre-Flight Token Budget Throttle (Salvaguarda de Cota Crítica >80%)
    throttled = False
    rolling_5h = budget.get("rolling_5h_percent", 0.0)
    weekly = budget.get("weekly_percent", 0.0)

    if rolling_5h > 80.0 or weekly > 80.0:
        critical_quota = rolling_5h if rolling_5h > 80.0 else weekly
        quota_type = "5h" if rolling_5h > 80.0 else "semanal"
        if raw_effort == EFFORT_HIGH:
            raw_effort = EFFORT_MEDIUM
            throttled = True
            reason += f" | ⚠️ [BUDGET THROTTLE] Cota crítica {quota_type} ({critical_quota:.1f}% > 80%): reduzido HIGH -> MEDIUM"
        elif raw_effort == EFFORT_MEDIUM:
            raw_effort = EFFORT_LOW
            throttled = True
            savings += 3000
            reason += f" | ⚠️ [BUDGET THROTTLE] Cota crítica {quota_type} ({critical_quota:.1f}% > 80%): reduzido MEDIUM -> LOW"

    return EffortDecision(
        effort=raw_effort,
        risk_level=risk_level,
        reason=reason,
        estimated_token_savings=savings,
        throttled=throttled,
        override=False,
        details={
            "prompt_length": len(prompt),
            "branch": git_ctx.get("branch", ""),
            "budget": budget,
        },
    )


def get_canonical_model_for_task(risk_level: str, is_planning: bool = False) -> Tuple[str, str]:
    """
    Retorna o modelo canônico e o reasoning effort ideal para a tarefa.
    Regra de Ouro: Escrita de código/execução SEMPRE usa Gemini 3.8 Flash (modulando effort).
    Gemini Pro é reservado exclusivamente para planejamento arquitetural / Stop Gate prévio.
    """
    if is_planning:
        if risk_level == LEVEL_L3_CRITICAL:
            return "Gemini Pro", EFFORT_HIGH
        elif risk_level == LEVEL_L2_FEATURE:
            return "Gemini Pro", EFFORT_MEDIUM
        elif risk_level == LEVEL_L1_SMALL:
            return "Gemini 3.8 Flash", EFFORT_MEDIUM
        else:
            return "Gemini 3.8 Flash", EFFORT_LOW

    # Escrita de código e implementação prática (sempre Gemini 3.8 Flash)
    if risk_level in (LEVEL_L3_CRITICAL, LEVEL_L2_FEATURE):
        return "Gemini 3.8 Flash", EFFORT_HIGH
    elif risk_level == LEVEL_L1_SMALL:
        return "Gemini 3.8 Flash", EFFORT_MEDIUM
    else:
        return "Gemini 3.8 Flash", EFFORT_LOW


def map_model_to_effort(current_model: str, target_effort: str) -> str:
    """
    Mapeia o modelo configurado para a variante correspondente de esforço.
    Se o modelo configurado for Pro, substitui por Gemini 3.8 Flash para escrita de código.
    """
    effort_cap = target_effort.capitalize()
    effort_lower = target_effort.lower()

    # Se for Pro, substitui para Gemini 3.8 Flash na execução de código
    if "pro" in current_model.lower() and "gemini" in current_model.lower():
        return f"Gemini 3.8 Flash ({effort_cap})"

    # Modelos no formato 'Gemini 3.8 Flash (High)'
    if re.search(r"\((High|Medium|Low)\)$", current_model, re.IGNORECASE):
        return re.sub(r"\((High|Medium|Low)\)$", f"({effort_cap})", current_model, flags=re.IGNORECASE)

    # Modelos no formato 'gemini-3.8-flash-high'
    if re.search(r"-(high|medium|low)$", current_model, re.IGNORECASE):
        return re.sub(r"-(high|medium|low)$", f"-{effort_lower}", current_model, flags=re.IGNORECASE)

    # Se for modelo que suporta sufixo
    if "flash" in current_model.lower() or "gemini" in current_model.lower():
        return f"{current_model} ({effort_cap})"

    # Caso padrão (ex: Claude, GPT) mantém o nome
    return current_model


def update_settings_effort(settings_path: Path, target_effort: str) -> Tuple[bool, str, str]:
    """Atualiza o arquivo settings.json com o modelo e effort corretos."""
    if not settings_path.is_file():
        return False, "", ""

    try:
        content = settings_path.read_text(encoding="utf-8")
        data = json.loads(content) if content.strip() else {}
        old_model = data.get("model", "")
        new_model = map_model_to_effort(old_model or "Gemini 3.8 Flash", target_effort)

        data["model"] = new_model
        data["reasoningEffort"] = target_effort.lower()

        settings_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return True, old_model, new_model
    except Exception:
        return False, "", ""


def sync_global_settings(target_effort: str) -> List[str]:
    """Sincroniza os arquivos de settings da CLI e da IDE."""
    updated = []
    settings_paths = (
        Path.home() / ".gemini" / "antigravity-cli" / "settings.json",
        Path.home() / ".gemini" / "antigravity-ide" / "settings.json",
        Path.home() / ".gemini" / "settings.json",
        Path.home() / ".gemini" / "config" / "settings.json",
    )

    for p in settings_paths:
        if p.is_file():
            success, old_m, new_m = update_settings_effort(p, target_effort)
            if success:
                updated.append(f"{p.name} ({old_m} -> {new_m})")
    return updated


def locate_native_agy() -> Optional[str]:
    """Encontra o binário nativo do agy ou antigravity."""
    # 1. Verifica binários nativos renomeados com prioridade
    for bin_name in ("agy-native", "agy-bin", "antigravity-native", "agy.real"):
        p = shutil.which(bin_name)
        if p:
            return p
        for p_str in (f"/home/andrevmp/.local/bin/{bin_name}", f"/usr/local/bin/{bin_name}"):
            if os.path.isfile(p_str) and os.access(p_str, os.X_OK):
                return p_str

    # 2. Busca padrão no PATH evitando o wrapper e este script
    for bin_name in ("agy", "antigravity"):
        p = shutil.which(bin_name)
        if p:
            real_p = os.path.realpath(p)
            if real_p != os.path.realpath(__file__) and not real_p.endswith("agy-wrapper.sh") and not real_p.endswith("agy-effort"):
                return p

    for path_str in ("/home/andrevmp/.local/bin/agy", "/usr/local/bin/agy"):
        if os.path.isfile(path_str) and os.access(path_str, os.X_OK):
            real_p = os.path.realpath(path_str)
            if real_p != os.path.realpath(__file__) and not real_p.endswith("agy-wrapper.sh") and not real_p.endswith("agy-effort"):
                return path_str
    return None


def format_badge(decision: EffortDecision) -> str:
    """Gera o badge visual informativo do esforço selecionado."""
    effort_icon = {"low": "⚡", "medium": "⚖️", "high": "🧠"}.get(decision.effort, "🎯")
    effort_str = decision.effort.upper()

    savings_str = f" | Economia estimada: ~{decision.estimated_token_savings:,} tokens" if decision.estimated_token_savings > 0 else ""
    throttle_str = " [THROTTLED]" if decision.throttled else ""

    lines = [
        f"------------------------------------------------------------------",
        f"{effort_icon} [AGY-EFFORT] Modo de Raciocínio: {effort_str}{throttle_str}",
        f"   📌 Classificação: {decision.risk_level}",
        f"   💡 Motivo: {decision.reason}{savings_str}",
        f"------------------------------------------------------------------",
    ]
    return "\n".join(lines)


def parse_cli_session_args(argv: List[str]) -> Tuple[str, Optional[str], List[str]]:
    """Extrai prompt, esforço explícito e argumentos de repasse da linha de comando."""
    prompt_parts: List[str] = []
    explicit_effort: Optional[str] = None
    pass_through_args: List[str] = []
    skip_next = False
    val_flags = {
        "--mode", "--model", "-m", "--agent", "--conversation",
        "--input-format", "--output-format", "--log-file", "--project",
        "--json-schema", "--print-timeout", "--add-dir", "--cwd", "-C",
        "--target", "--profile", "--config",
    }
    for i, arg in enumerate(argv):
        if skip_next:
            skip_next = False
            continue
        if arg in ("--effort", "-e") and i + 1 < len(argv):
            explicit_effort = argv[i + 1]
            skip_next = True
        elif arg.startswith("--effort="):
            explicit_effort = arg.split("=", 1)[1]
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
    return " ".join(prompt_parts).strip(), explicit_effort, pass_through_args


def run_cli_session(argv: List[str]) -> int:
    """Executa a sessão do agy com o esforço inteligente injetado."""
    prompt_text, explicit_effort, pass_through_args = parse_cli_session_args(argv)

    # Classificação
    git_ctx = detect_git_context()
    budget = get_token_budget_status()
    decision = classify_task_effort(
        prompt=prompt_text,
        git_context=git_ctx,
        token_budget=budget,
        explicit_effort=explicit_effort,
    )

    # Exibe badge informativo
    sys.stderr.write(format_badge(decision) + "\n")
    sys.stderr.flush()

    # Sincroniza settings.json silenciosamente
    sync_global_settings(decision.effort)

    # Localiza o binário nativo
    real_bin = locate_native_agy()
    if not real_bin:
        sys.stderr.write("⚠️ Binário nativo 'agy' não encontrado no PATH.\n")
        return 1

    # Monta comando final com --effort
    final_args = [real_bin, "--effort", decision.effort] + pass_through_args
    os.execvp(real_bin, final_args)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Router Inteligente de Reasoning Effort para o Antigravity CLI",
        add_help=True,
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Comandos disponíveis")

    # Subcomando: classify
    classify_p = subparsers.add_parser("classify", help="Analisa um prompt e retorna o esforço recomendado")
    classify_p.add_argument("prompt", nargs="?", default="", help="Texto da tarefa ou prompt")
    classify_p.add_argument("--json", action="store_true", help="Retorna saída estruturada em JSON")

    # Subcomando: apply
    apply_p = subparsers.add_parser("apply", help="Aplica o esforço no settings.json da CLI e IDE")
    apply_p.add_argument("prompt", nargs="?", default="", help="Texto da tarefa ou prompt para classificação")
    apply_p.add_argument("--effort", choices=["low", "medium", "high"], help="Nível de esforço explícito")
    apply_p.add_argument("--auto", nargs="?", const="", help="Classifica automaticamente baseado no prompt ou git")

    # Subcomando: status
    subparsers.add_parser("status", help="Exibe o status atual de esforço e recomendações")

    # Se nenhum argumento ou chamado como runner de agy
    if len(sys.argv) > 1 and sys.argv[1] not in ("classify", "apply", "status", "-h", "--help"):
        return run_cli_session(sys.argv[1:])

    args = parser.parse_args()

    if args.subcommand == "classify":
        git_ctx = detect_git_context()
        budget = get_token_budget_status()
        decision = classify_task_effort(prompt=args.prompt, git_context=git_ctx, token_budget=budget)
        if args.json:
            print(json.dumps({
                "effort": decision.effort,
                "risk_level": decision.risk_level,
                "reason": decision.reason,
                "estimated_token_savings": decision.estimated_token_savings,
                "throttled": decision.throttled,
            }, indent=2, ensure_ascii=False))
        else:
            print(format_badge(decision))
        return 0

    elif args.subcommand == "apply":
        target_effort = args.effort
        if not target_effort:
            prompt_str = args.prompt or (args.auto if isinstance(args.auto, str) else "")
            decision = classify_task_effort(
                prompt=prompt_str,
                git_context=detect_git_context(),
                token_budget=get_token_budget_status(),
            )
            target_effort = decision.effort
            print(format_badge(decision))

        updated = sync_global_settings(target_effort)
        print(f"✅ Esforço '{target_effort.upper()}' aplicado nos arquivos de configuração:")
        for u in updated:
            print(f"   - {u}")
        return 0

    elif args.subcommand == "status":
        cli_settings = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
        curr_model = "Desconhecido"
        curr_effort = "medium"
        if cli_settings.is_file():
            try:
                data = json.loads(cli_settings.read_text(encoding="utf-8"))
                curr_model = data.get("model", curr_model)
                curr_effort = data.get("reasoningEffort", curr_effort)
            except Exception:
                pass

        git_ctx = detect_git_context()
        budget = get_token_budget_status()
        recommendation = classify_task_effort("", git_context=git_ctx, token_budget=budget)

        print("==================================================================")
        print("📊 Antigravity CLI Reasoning Effort Status")
        print(f"   Modelo Ativo em settings.json: {curr_model}")
        print(f"   Esforço Configurado:           {curr_effort.upper()}")
        print(f"   Git Branch Atual:             {git_ctx.get('branch', 'N/A')}")
        print(f"   Cota 5h:                      {budget.get('rolling_5h_percent', 0.0):.1f}%")
        print(f"   Cota Semanal:                 {budget.get('weekly_percent', 0.0):.1f}%")
        print("------------------------------------------------------------------")
        print(f"   💡 Recomendação Automática:    {recommendation.effort.upper()} ({recommendation.risk_level})")
        print(f"      {recommendation.reason}")
        print("==================================================================")
        return 0

    # Default: modo interativo do agy
    return run_cli_session([])


if __name__ == "__main__":
    sys.exit(main())
