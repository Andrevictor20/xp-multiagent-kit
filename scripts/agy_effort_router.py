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
    r"\bresumo\b", r"\bstatus\b", r"\bgit log\b", r"\bgit status\b",
    r"\bquais arquivos\b", r"\bclean code\b",
]

L3_KEYWORDS = [
    r"\bauth\b", r"\bautentica[çc][ãa]o\b", r"\blogin\b", r"\bjwt\b", r"\boauth\b",
    r"\btoken\b", r"\bmfa\b", r"\bsenha\b", r"\bpassword\b", r"\bpermiss[ãa]o\b",
    r"\brbac\b", r"\bidor\b", r"\bcrypto\b", r"\bcriptografia\b", r"\bsecret\b",
    r"\bvulnerabilidade\b", r"\bcve\b", r"\bthreat modeling\b", r"\bstride\b",
    r"\bpagamento\b", r"\bpayment\b", r"\bstripe\b", r"\bbilling\b", r"\bcheckout\b",
    r"\btransa[çc][ãa]o\b", r"\bfatura\b",
    r"\bmigra[çc][ãa]o\b", r"\bmigrations?\b", r"\bschema change\b", r"\bdrop table\b",
    r"\balter table\b", r"\b[íi]ndice concorrente\b", r"\brace condition\b",
    r"\bdeadlock\b", r"\bconcorr[êe]ncia\b", r"\bmutex\b", r"\bgoroutine\b",
    r"\bthread safety\b", r"\bzero-downtime\b", r"\bblue-green\b", r"\bcanary\b",
    r"\brollback\b", r"\bkernel panic\b", r"\bcrash\b", r"\bmemory leak\b",
    r"\bcausa raiz\b", r"\broot cause\b", r"\bflaky test\b",
]

L2_KEYWORDS = [
    r"\bfeature\b", r"\bnova funcionalidade\b", r"\bnovo endpoint\b", r"\bcriar api\b",
    r"\bnovo componente\b", r"\bnova esteira\b", r"\bintegra[çc][ãa]o\b",
    r"\brefatora[çc][ãa]o estrutural\b", r"\bredesign\b", r"\bimplemente\b",
    r"\bconstrua\b", r"\bmonte\b", r"\bcrie\b", r"\bexporta[çc][ãa]o\b",
    r"\bworkflows?\b", r"\bapi\b",
]

L1_KEYWORDS = [
    r"\bpequeno ajuste\b", r"\brefatore\b", r"\brefatora[çc][ãa]o isolada\b",
    r"\bteste unit[áa]rio\b", r"\badicione um teste\b", r"\bpequeno bug\b",
    r"\bajuste\b", r"\brenomeie\b", r"\bmover\b", r"\blint fix\b",
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
) -> EffortDecision:
    """Classifica o esforço ideal de raciocínio de forma inteligente."""
    # 1. Override explícito do usuário
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

    raw_effort = EFFORT_MEDIUM
    risk_level = LEVEL_L1_SMALL
    reason = "Tarefa padrão de complexidade moderada"
    savings = 0

    # 2. Avaliação de L3 (Crítico / Segurança / DB / Auth / Pagamentos)
    matched_l3 = [kw for kw in L3_KEYWORDS if re.search(kw, p_lower)]
    if matched_l3:
        raw_effort = EFFORT_HIGH
        risk_level = LEVEL_L3_CRITICAL
        reason = f"Detectado risco L3 por palavras-chave críticas: {', '.join(matched_l3[:3])}"

    # 3. Avaliação de L2 (Feature / Novas APIs / Componentes)
    elif any(re.search(kw, p_lower) for kw in L2_KEYWORDS):
        matched_l2 = [kw for kw in L2_KEYWORDS if re.search(kw, p_lower)]
        raw_effort = EFFORT_HIGH
        risk_level = LEVEL_L2_FEATURE
        reason = f"Detectado risco L2 por termos de feature/construção: {', '.join(matched_l2[:3])}"

    # 4. Avaliação de L0 (Trivial / Docs / CSS / Typo)
    elif any(re.search(kw, p_lower) for kw in L0_KEYWORDS):
        matched_l0 = [kw for kw in L0_KEYWORDS if re.search(kw, p_lower)]
        raw_effort = EFFORT_LOW
        risk_level = LEVEL_L0_TRIVIAL
        savings = 5000
        reason = f"Detectado risco L0 (Trivial/Docs/CSS) por: {', '.join(matched_l0[:3])}"

    # 5. Avaliação de L1 (Pequeno ajuste / Refatoração isolada)
    elif any(re.search(kw, p_lower) for kw in L1_KEYWORDS):
        matched_l1 = [kw for kw in L1_KEYWORDS if re.search(kw, p_lower)]
        raw_effort = EFFORT_MEDIUM
        risk_level = LEVEL_L1_SMALL
        reason = f"Detectado risco L1 por: {', '.join(matched_l1[:3])}"

    # 6. Heurística via Git Context se o prompt for vazio
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
        else:
            raw_effort = EFFORT_MEDIUM
            risk_level = LEVEL_L1_SMALL
            reason = "Sessão interativa sem prompt inicial (baseline medium)"

    # 7. Pre-Flight Token Budget Throttle (Salvaguarda de Cota Crítica >80%)
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


def map_model_to_effort(current_model: str, target_effort: str) -> str:
    """Mapeia o modelo configurado para a variante correspondente de esforço."""
    effort_cap = target_effort.capitalize()
    effort_lower = target_effort.lower()

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
        data = json.loads(content)
        old_model = data.get("model", "")
        new_model = map_model_to_effort(old_model, target_effort)

        data["model"] = new_model
        data["reasoningEffort"] = target_effort.lower()

        settings_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return True, old_model, new_model
    except Exception:
        return False, "", ""


def sync_global_settings(target_effort: str) -> List[str]:
    """Sincroniza os arquivos de settings da CLI e da IDE."""
    updated = []
    cli_settings = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
    ide_settings = Path.home() / ".gemini" / "antigravity-ide" / "settings.json"

    for p in (cli_settings, ide_settings):
        if p.is_file():
            success, old_m, new_m = update_settings_effort(p, target_effort)
            if success:
                updated.append(f"{p.name} ({old_m} -> {new_m})")
    return updated


def locate_native_agy() -> Optional[str]:
    """Encontra o binário nativo do agy ou antigravity."""
    for bin_name in ("agy", "antigravity"):
        p = shutil.which(bin_name)
        if p:
            real_p = os.path.realpath(p)
            # Evita loop infinito chamando o próprio script
            if real_p != os.path.realpath(__file__) and not real_p.endswith("agy-wrapper.sh"):
                return p
    # Fallback para locais padrão
    for path_str in ("/home/andrevmp/.local/bin/agy", "/usr/local/bin/agy"):
        if os.path.isfile(path_str) and os.access(path_str, os.X_OK):
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


def run_cli_session(argv: List[str]) -> int:
    """Executa a sessão do agy com o esforço inteligente injetado."""
    # Extrai flags e prompt
    prompt_text = ""
    explicit_effort = None
    pass_through_args = []
    skip_next = False

    for i, arg in enumerate(argv):
        if skip_next:
            skip_next = False
            continue

        if arg in ("--effort", "-e") and i + 1 < len(argv):
            explicit_effort = argv[i + 1]
            skip_next = True
            continue
        elif arg.startswith("--effort="):
            explicit_effort = arg.split("=", 1)[1]
            continue
        elif arg in ("-p", "--print", "-i", "--prompt-interactive") and i + 1 < len(argv):
            prompt_text = argv[i + 1]
            pass_through_args.extend([arg, argv[i + 1]])
            skip_next = True
            continue
        elif not arg.startswith("-") and not prompt_text:
            prompt_text = arg
            pass_through_args.append(arg)
        else:
            pass_through_args.append(arg)

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
            prompt_str = args.auto if isinstance(args.auto, str) else ""
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
