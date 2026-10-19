#!/usr/bin/env python3
"""
scripts/design_search.py
Design Intelligence: busca offline em catálogos (produtos, paletas, fontes,
regras de UX, gráficos) e geração do design-system/MASTER.md, sempre sujeita
aos locks do kit (Color/Shape Lock, 6 estados, 100dvh, 48px, WCAG AA).

Uso:
    python3 scripts/design_search.py "fintech dashboard"                 # design system (stdout)
    python3 scripts/design_search.py "fintech dashboard" --persist       # grava design-system/MASTER.md
    python3 scripts/design_search.py --domain ux "touch target mobile"   # busca num domínio
    python3 scripts/design_search.py --mobile "fitness tracker app"      # design system para app mobile
    python3 scripts/design_search.py --domain systems "react native"     # catálogo de design systems
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kit_constants import kit_root  # noqa: E402

DOMAINS = ("products", "palettes", "fonts", "ux", "charts", "systems", "mobile", "mobile-apps")
_FILES = {
    "products": "products.csv",
    "palettes": "palettes.csv",
    "fonts": "fonts.csv",
    "ux": "ux-rules.csv",
    "charts": "charts.csv",
    "systems": "design-systems.csv",
    "mobile": "mobile-ux.csv",
    "mobile-apps": "mobile-apps.csv",
}
_FALLBACK_PRODUCT = "SaaS landing page"
_FALLBACK_APP = "Productivity app"
_FALLBACK_SYSTEM = "shadcn/ui"


def assets_dir() -> Path:
    return kit_root() / ".agents" / "skills" / "design-intelligence" / "assets"


def load(domain: str) -> List[Dict[str, str]]:
    path = assets_dir() / _FILES[domain]
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def search(domain: str, query: str, limit: int = 3) -> List[Dict[str, str]]:
    """Ranks rows by query token overlap; weights the keywords column higher."""
    terms = set(_tokens(query))
    scored = []
    for row in load(domain):
        key_field = row.get("keywords", "")
        keys = set(_tokens(key_field))
        rest = set(_tokens(" ".join(v for k, v in row.items() if k != "keywords")))
        score = 3 * len(terms & keys) + len(terms & rest)
        if score:
            scored.append((score, row))
    scored.sort(key=lambda pair: -pair[0])
    return [row for _, row in scored[:limit]]


def _by_name(domain: str, name: str) -> Dict[str, str]:
    return next(r for r in load(domain) if r["name"] == name)


def _pick_system(query: str, platforms: set, hint: str = "") -> Dict[str, str]:
    pool = [s for s in load("systems") if s["platform"] in platforms and s["status"] == "active"]
    terms = set(_tokens(f"{query} {hint}"))
    scored = sorted(
        ((len(terms & set(_tokens(s["keywords"]))), s) for s in pool),
        key=lambda pair: -pair[0],
    )
    if scored and scored[0][0] > 0:
        return scored[0][1]
    return next((s for s in pool if s["name"] == _FALLBACK_SYSTEM), pool[0])


def _system_lines(system: Dict[str, str]) -> List[str]:
    return [
        f"- **Base system:** {system['name']} (`{system['package']}`, {system['license']}); {system['style']}",
        f"- Customize: {system['customize']}; never ship the default theme",
        f"- Accessibility: {system['a11y']}",
    ]


def _tokens_block(pal: Dict[str, str], font: Dict[str, str]) -> List[str]:
    return [
        "## Tokens (Color Consistency Lock)",
        f"- `color.background` {pal['bg']} | `color.text-primary` {pal['text']} | `color.surface` {pal['surface']} | `color.accent` {pal['accent']} (single accent, locked across the whole page)",
        f"- Palette: {pal['name']} ({pal['mood']})",
        "",
        "## Typography",
        f"- `font-display` {font['display']} | `font-sans` {font['body']} | `font-mono` {font['mono']}",
    ]


def _mobile_lines(app: Dict[str, str], query: str) -> List[str]:
    rules = search("mobile", query, 5)
    seen = {r["id"] for r in rules}
    rules += [r for r in load("mobile") if r["severity"] == "high" and r["id"] not in seen][: 6 - len(rules)]
    lines = [
        "## Mobile",
        f"- Navigation: {app['navigation']}",
        f"- Key screens: {app['key_screens']}",
        f"- Platform notes: {app['platform_notes']}",
        "- Units: iOS points (pt) and Android dp/sp; touch targets 44pt (iOS) / 48dp (Android), 8dp spacing",
        "- Respect the safe area on all edges; keep primary actions in the lower thumb zone",
        "- Text: support Dynamic Type (iOS) and font scale up to 200% (Android); test the largest size",
        "- Support system dark mode, Reduce Motion, VoiceOver and TalkBack labels",
        "",
        "## Mobile UX Rules for this brief",
    ]
    lines += [f"- [{r['severity']}|{r['platform']}] DO: {r['do']} | DON'T: {r['dont']}" for r in rules]
    return lines


def _compact(lines: List[str]) -> str:
    out: List[str] = []
    for line in lines:
        if line == "" and (not out or out[-1] == ""):
            continue
        out.append(line)
    return "\n".join(out) + "\n"


def generate_design_system(query: str, mobile: bool = False) -> str:
    notice = ""
    if mobile:
        hits = search("mobile-apps", query, 1)
        if hits:
            item = hits[0]
        else:
            item = next(r for r in load("mobile-apps") if r["app"] == _FALLBACK_APP)
            notice = f"> No close app match for \"{query}\"; using \"{_FALLBACK_APP}\" baseline."
        label, pattern, avoid = item["app"], item["navigation"], item["avoid"]
        system = next(s for s in load("systems") if s["name"] == item["system"])
        style = f"{system['style']}, platform-native feel"
    else:
        hits = search("products", query, 1)
        if hits:
            item = hits[0]
        else:
            item = next(r for r in load("products") if r["product"] == _FALLBACK_PRODUCT)
            notice = f"> No close product match for \"{query}\"; using \"{_FALLBACK_PRODUCT}\" baseline."
        label, pattern, style, avoid = item["product"], item["pattern"], item["style"], item["avoid"]
        system = _pick_system(query, {"web"}, item["style"])
    pal = _by_name("palettes", item["palette"])
    font = _by_name("fonts", item["fonts"])
    lines = [
        "# Design System MASTER",
        "",
        f"> Query: {query} | {'App' if mobile else 'Product'} archetype: {label}",
        "",
        notice,
        "",
        "## Direction",
        f"- **Style:** {style}",
        f"- **{'Navigation' if mobile else 'Layout pattern'}:** {pattern}",
        f"- **DESIGN_VARIANCE:** {item['variance']} | **MOTION_INTENSITY:** {item['motion']} | **VISUAL_DENSITY:** {item['density']}",
        f"- **Avoid:** {avoid}",
    ]
    lines += _system_lines(system) + [""] + _tokens_block(pal, font)
    if mobile:
        lines += ["", "## Shape Lock", "- One radius family per product; nested radius: radius_inner = max(0, radius_outer - padding)", ""]
        lines += _mobile_lines(item, query)
    else:
        ux = search("ux", query, 4) or load("ux")[:4]
        lines += [
            "- Body 16px minimum, 60-75ch line length, `tabular-nums` on metrics",
            "",
            "## Shape & Layout Locks",
            "- One radius family per product; nested radius: radius_inner = max(0, radius_outer - padding)",
            "- Use `min-h-[100dvh]` (never `100vh`); touch targets 48px minimum",
            "- All 6 states per interactive component: Default, Hover/Focus, Active, Loading, Empty, Error",
            "",
            "## UX Rules for this brief",
        ]
        lines += [f"- [{r['severity']}] DO: {r['do']} | DON'T: {r['dont']}" for r in ux]
        charts = search("charts", query, 2)
        if charts:
            lines += ["", "## Charts"]
            lines += [f"- {c['question']}: {c['chart']} (a11y: {c['a11y']}; avoid: {c['avoid']})" for c in charts]
    lines += ["", "## Pre-delivery gate", "- Run `ui-quality-gate` (WCAG AA, Anti-Slop) before shipping."]
    return _compact(lines)


def persist(query: str, base: Optional[Path] = None, mobile: bool = False) -> Path:
    target = (base or Path.cwd()) / "design-system" / "MASTER.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(generate_design_system(query, mobile=mobile), encoding="utf-8")
    return target


def _print_rows(rows: List[Dict[str, str]]) -> None:
    for row in rows:
        print(" | ".join(f"{k}={v}" for k, v in row.items()))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Design Intelligence search")
    parser.add_argument("query", help="free-text brief or keywords")
    parser.add_argument("--domain", choices=DOMAINS, help="search a single catalog")
    parser.add_argument("--mobile", action="store_true", help="generate for a native/cross-platform mobile app")
    parser.add_argument("--persist", action="store_true", help="write design-system/MASTER.md")
    args = parser.parse_args(argv)
    if args.domain:
        _print_rows(search(args.domain, args.query))
    elif args.persist:
        print(f"Wrote {persist(args.query, mobile=args.mobile)}")
    else:
        print(generate_design_system(args.query, mobile=args.mobile))
    return 0


if __name__ == "__main__":
    sys.exit(main())
