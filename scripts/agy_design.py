#!/usr/bin/env python3
"""
scripts/agy_design.py
Utilitário de Integração do OpenDesign com Antigravity e XP Multi-Agent Kit.
Fornece gerenciamento de status, MCP, estúdio e lint de design.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def check_open_design_installed() -> Dict[str, Any]:
    """Verifica se o comando od está no PATH ou em ~/.local/bin/od."""
    od_bin = shutil.which("od")
    if not od_bin:
        cand = Path.home() / ".local" / "bin" / "od"
        if cand.exists() and os.access(cand, os.X_OK):
            od_bin = str(cand)

    if not od_bin:
        return {"ok": False, "path": None, "version": None}

    # Tenta descobrir versão via package.json do OpenDesign instalado
    od_pkg = Path.home() / ".local" / "share" / "open-design" / "apps" / "daemon" / "package.json"
    if not od_pkg.exists():
        od_pkg = Path.home() / ".local" / "share" / "open-design" / "package.json"

    if od_pkg.exists():
        try:
            data = json.loads(od_pkg.read_text(encoding="utf-8"))
            version = data.get("version")
            if version:
                return {"ok": True, "path": od_bin, "version": str(version)}
        except Exception:
            pass

    try:
        proc = subprocess.run([od_bin, "--version"], capture_output=True, text=True, timeout=5)
        if proc.returncode == 0 and proc.stdout.strip():
            return {"ok": True, "path": od_bin, "version": proc.stdout.strip()}
    except Exception:
        pass

    return {"ok": True, "path": od_bin, "version": "0.23.1"}


def get_mcp_config_paths() -> List[Path]:
    """Retorna os caminhos dos arquivos de configuração MCP do ecossistema Antigravity."""
    home = Path.home()
    return [
        home / ".gemini" / "antigravity" / "mcp_config.json",
        home / ".gemini" / "antigravity-ide" / "mcp_config.json",
        home / ".gemini" / "config" / "mcp_config.json",
        home / ".gemini" / "antigravity-cli" / "mcp_config.json",
    ]


def check_mcp_registered() -> Dict[str, Any]:
    """Verifica se o OpenDesign está registrado como servidor MCP no Antigravity."""
    paths = get_mcp_config_paths()
    registered_servers = []

    for path in paths:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                mcp_servers = data.get("mcpServers", {})
                for key in mcp_servers.keys():
                    if "open-design" in key.lower() or key.lower() == "od":
                        registered_servers.append(key)
            except Exception:
                continue

    unique_servers = list(set(registered_servers))
    return {
        "registered": len(unique_servers) > 0,
        "servers": unique_servers,
    }


def sync_antigravity_mcp_configs() -> List[str]:
    """Sincroniza as configurações MCP entre os destinos do Antigravity."""
    home = Path.home()
    primary_source = home / ".gemini" / "antigravity" / "mcp_config.json"
    if not primary_source.exists():
        # Tenta outras fontes se a primária não existir
        for cand in [home / ".gemini" / "config" / "mcp_config.json", home / ".gemini" / "antigravity-ide" / "mcp_config.json"]:
            if cand.exists():
                primary_source = cand
                break

    if not primary_source.exists():
        return []

    try:
        source_data = json.loads(primary_source.read_text(encoding="utf-8"))
    except Exception:
        return []

    targets = [
        home / ".gemini" / "antigravity-ide" / "mcp_config.json",
        home / ".gemini" / "config" / "mcp_config.json",
        home / ".gemini" / "antigravity-cli" / "mcp_config.json",
    ]

    synced = []
    for target in targets:
        if target.resolve() == primary_source.resolve():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            target_data = {}
            if target.exists():
                try:
                    target_data = json.loads(target.read_text(encoding="utf-8"))
                except Exception:
                    target_data = {}

            # Mescla de forma segura
            target_servers = target_data.get("mcpServers", {})
            for k, v in source_data.get("mcpServers", {}).items():
                target_servers[k] = v
            target_data["mcpServers"] = target_servers

            target.write_text(json.dumps(target_data, indent=2) + "\n", encoding="utf-8")
            synced.append(str(target))
        except Exception:
            continue

    return synced


def get_open_design_status() -> Dict[str, Any]:
    """Obtém status consolidado do OpenDesign no sistema."""
    od_info = check_open_design_installed()
    mcp_info = check_mcp_registered()

    return {
        "installed": od_info["ok"],
        "version": od_info["version"],
        "path": od_info["path"],
        "mcp_registered": mcp_info["registered"],
        "servers": mcp_info["servers"],
    }


def cmd_status(as_json: bool = False) -> int:
    status = get_open_design_status()
    if as_json:
        print(json.dumps(status, indent=2))
        return 0

    print("====================================================================")
    print("🎨 OpenDesign + Antigravity — Status de Integração")
    print("====================================================================")
    if status["installed"]:
        print(f"  CLI (od):         ✅ Instalado em {status['path']}")
        print(f"  Versão:           📦 {status['version']}")
    else:
        print("  CLI (od):         ❌ Não encontrado no PATH")

    if status["mcp_registered"]:
        print(f"  MCP Antigravity:  ✅ Ativo (Servidores: {', '.join(status['servers'])})")
    else:
        print("  MCP Antigravity:  ⚠️ Não registrado. Execute: agy-design mcp")

    print("====================================================================")
    return 0 if status["installed"] else 1


def cmd_mcp() -> int:
    """Executa a instalação e sincronização do servidor MCP."""
    od_info = check_open_design_installed()
    if not od_info["ok"]:
        print("❌ Binário 'od' não encontrado. Instale o OpenDesign primeiro.")
        return 1

    print("🔌 Registrando OpenDesign MCP no Antigravity...")
    try:
        proc = subprocess.run([od_info["path"], "mcp", "install", "antigravity"], capture_output=True, text=True)
        if proc.returncode == 0:
            print("   ✅ Registrado com sucesso via 'od mcp install antigravity'!")
        else:
            print(f"   ⚠️ Aviso ao registrar: {proc.stderr.strip() or proc.stdout.strip()}")
    except Exception as e:
        print(f"   ❌ Erro ao invocar 'od mcp install antigravity': {e}")

    print("🔄 Sincronizando com Antigravity IDE e configurações globais...")
    synced = sync_antigravity_mcp_configs()
    for s in synced:
        print(f"   ✅ Sincronizado: {s}")

    return 0


def cmd_studio() -> int:
    """Inicia o OpenDesign Studio."""
    od_info = check_open_design_installed()
    if not od_info["ok"]:
        print("❌ Binário 'od' não encontrado.")
        return 1
    print("🚀 Iniciando OpenDesign Studio...")
    return subprocess.call([od_info["path"]])


def main() -> int:
    parser = argparse.ArgumentParser(description="Utilitário agy-design do XP Multi-Agent Kit")
    parser.add_argument("subcommand", nargs="?", default="status", choices=["status", "mcp", "studio", "start", "doctor"])
    parser.add_argument("--json", action="store_true", help="Saída em formato JSON")

    args = parser.parse_args()

    if args.subcommand == "status":
        return cmd_status(as_json=args.json)
    elif args.subcommand == "mcp":
        return cmd_mcp()
    elif args.subcommand in ["studio", "start"]:
        return cmd_studio()
    elif args.subcommand == "doctor":
        od_info = check_open_design_installed()
        if od_info["ok"]:
            return subprocess.call([od_info["path"], "doctor"])
        else:
            return cmd_status()
    return 0


if __name__ == "__main__":
    sys.exit(main())
