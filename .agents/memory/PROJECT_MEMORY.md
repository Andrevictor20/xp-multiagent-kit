# 🧠 Project Memory & Context Snapshot

> **Última Atualização:** 2026-10-16 (Local)  
> **Status Geral do Projeto:** STABLE  
> **Versão / Marco Atual:** v3.1.3 (Universal One-Liner Installer, Multi-Platform Deployment & 5-Host Parity)

---

## 1. Quick Project Summary (Semantic)

- **Propósito:** Kit modular e agnóstico de governança, agentes, skills, workflows e políticas para pair programming com IA em **Antigravity, OpenCode, Cursor, Codex e Qoder (IDE & CLI)**, orquestrando Task Routing L0-L3, Pirâmide ATDD/BDD, TDD estrito, Anti-Test-Bypass, SSDLC, Autocorreção Reflexiva, Otimização de Tokens e Memória Contínua em 4 Tiers.
- **Tech Stack:** Multi-Host Agent Framework (`AGENTS.md`, `opencode.json`, `.cursor/rules/*.mdc`, `.codex/rules/`, `.qoder/rules/`), Python 3.8+, Bash, PowerShell 5.1+, Windows CMD, Git, GitHub Actions CLI (`gh`). Agnóstico de SO (Linux, macOS, Windows).
- **Arquitetura Chave:** `.agents/` (11 agentes, 77 skills, 11 workflows, 12 policies, 2 templates em Token-Dense English com regra mandatória de saída em Português ao usuário; memória viva em 4 tiers). Suíte modular em `scripts/telemetry/`, `scripts/host_adapters.py`, `scripts/mcp_installers.py`, `scripts/spec_tool.py`, `scripts/update_manager.py`, `scripts/windows_support.py` e binários globais `xp-*` / `agy-*` em `~/.local/bin/` (Unix) ou `%USERPROFILE%\.local\bin\` (Windows `.cmd` shims).
- **Comandos Essenciais:** (Catálogo completo em [details/commands.md](details/commands.md))
  - Instalação Linux/macOS: `./install.sh [--global|--project <dir>|--both <dir>] [--target all|...] [--lang pt|en]`
  - Instalação Windows (PowerShell/CMD): `powershell -ExecutionPolicy Bypass -File .\install.ps1` ou `install.cmd`
  - Gestão e Auto-Update do Kit: `xp-kit [doctor|init <dir>|sync|update|version]` / `agy-kit`
  - Ferramenta ATDD de Specs: `xp-spec [new <slug>|validate <file>]` / `agy-spec`
  - Telemetria Compacta (4 linhas + ANSI Colors): `xp-tokens --turn [--color] [--host <host>]` / `agy-tokens --turn`
  - Auditoria de Orçamento & Índice de Skills: `python3 scripts/skill_index.py [generate|audit]`
  - Conformidade ATDD & Débitos: `xp-conformance` / `agy-debt --scan`

---

## 2. Current Health & System Status

- **Agent Suite Status:** OPERATIONAL (11 Agentes, 77 Skills `< 4KB` em Inglês, 11 Workflows, 12 Policies, 5 Hosts, Instaladores Nativos, Toolchain RTK/OD/CRG, Auto-Update e Telemetria).
- **Quality Gate / Rules:** 100% compliant com `AGENTS.md` (348/348 testes unitários e de integração `PASS`, 0 caminhos pessoais, arquivos `< 500` linhas, `PROJECT_MEMORY.md` `< 8KB`).
- **Última Execução / Evidência:** `EV-KIT-V3.1.3-ONE-LINER-20261016-01` (Validação e deploy do comando único de instalação remota, auto-healing de dependências e diagnóstico dos 5 hosts).
- **Ambiente Ativo:** Local & Global / Linux, macOS e Windows nativo (PowerShell / CMD).

---

## 3. Recent Changes & Activity Log (Episodic - Sliding Window: 5 Entregas)

| 2026-10-16 | `FIX` | Adaptação Multi-Shell (Fish, Zsh, Bash, Ksh) & One-Liner Universal via Pipe — (1) `PathConfigurator` atualizado com sintaxe nativa do Fish (`set -gx PATH`), Zsh (`$ZDOTDIR/.zshrc`), Bash, Ksh e `.profile` + auto-criação do RC do `$SHELL` ativo, (2) `install-shell-aliases.sh` com auto-loader em `~/.config/fish/conf.d/xp-kit.fish` e `.zshrc`, (3) `install.sh` adaptado para pipe direto (`curl -fsSL ... | bash`) compatível com Fish/Zsh/Bash sem `$(...)` e sem quebra de linha | `install.sh`, `scripts/kit_installer.py`, `scripts/global-token-optimizer/install-shell-aliases.sh`, `tests/test_kit_installer.py`, `README.md` | `PASS (EV-KIT-V3.1.4-MULTI-SHELL-20261016-01)` |
| 2026-10-16 | `FEAT` | Publicação & Validação do Instalador Universal One-Liner — (1) Comando único curl/bash testado e validado em ambiente limpo, (2) Auto-healing de dependências do sistema operacional (Python 3, Git), (3) Injeção não-interativa e feedback legível na saída do terminal, (4) Suporte universal a Linux, macOS e Windows (PowerShell/CMD), (5) Sincronização e deploy completo no branch main do GitHub | `install.sh`, `install.ps1`, `install.cmd`, `scripts/kit_installer.py`, `scripts/host_adapters.py`, `scripts/mcp_installers.py` | `PASS (EV-KIT-V3.1.3-ONE-LINER-20261016-01)` |
| 2026-10-16 | `FIX` | Auditoria Multiplataforma & Portabilidade Universal — (1) Sincronização de `.agents/skills` e `.agents/agents` em projetos locais (eliminando File Not Found de SKILLS_INDEX.md), (2) Cursor customInstructions compatível com macOS e Windows, (3) Shims Windows com detecção e fallback `py -3`, (4) `agy-run` no Windows com `cmd.exe`/`bash` em vez de `/bin/sh`, (5) `KitDoctor` com auditoria dos 5 hosts e alertas de auto-update, (6) Roteamento de telemetria por marcadores de projeto (`.cursor`, `.codex`, etc.), (7) `xp-kit init [path]` posicional | `scripts/host_adapters.py`, `scripts/kit_installer.py`, `scripts/agy-run`, `scripts/windows_support.py`, `scripts/telemetry/*`, `tests/*` | `PASS (EV-KIT-V3.1.2-CROSS-PLATFORM-AUDIT-20261016-01)` |
| 2026-10-16 | `FIX` | SPEC-006: Instalação Global Cursor & Auto-Discovery — (1) Correção do bug de diretório aninhado `.cursor/.cursor/`, (2) Geração de regras globais em `~/.cursor/rules/*.mdc` e injeção de instruções em `settings.json`, (3) Auto-descoberta e sync automático de `AGENTS.md` v3 em projetos de trabalho (`vito`, `Saturn`, `Essenza`), (4) Leitor SQLite OpenCode e telemetria adaptativa multi-host | `scripts/host_adapters.py`, `scripts/kit_installer.py`, `scripts/telemetry/*`, `tests/test_multi_host_telemetry.py` | `PASS (EV-KIT-V3.1-CURSOR-GLOBAL-20261016-02)` |
| 2026-10-16 | `FEAT` | SPEC-005: Suporte Nativo ao Windows — (1) Scripts `install.ps1` e `install.cmd`, (2) Shims `.cmd` em `%USERPROFILE%\.local\bin`, (3) PATH via `winreg`, (4) Fallback NTFS para cópia, (5) Documentação no `README.md` | `install.ps1`, `install.cmd`, `scripts/windows_support.py`, `scripts/kit_installer.py`, `tests/test_windows_installer.py`, `README.md` | `PASS (EV-KIT-V3.1-WINDOWS-20261016-01)` |

*(Entregas anteriores arquivadas em [archive/HISTORY.md](archive/HISTORY.md))*

---

## 4. Active Backlog & Immediate Handoff (Working / Episodic)

- [x] **[DONE] Instalador nativo para Windows (PowerShell/CMD/Batch) com shims .cmd e configuração de PATH via winreg.**
- [x] **[DONE] Suporte ao Codex CLI e matriz de 5 hosts (Antigravity, OpenCode, Cursor, Codex, Qoder).**
- [x] **[DONE] Toolchain embutida no instalador: RTK (compilação cargo/download), OpenDesign e CodeReviewGraph.**
- [x] **[DONE] Reforço ATDD/BDD com CLI `xp-spec`/`agy-spec` e hook de disciplina ATDD.**
- [x] **[DONE] Eliminação total de caminhos e referências pessoais do desenvolvedor em arquivos rastreados.**
- [x] **[DONE] Catálogo de modelos multi-ferramenta e telemetria adaptativa por host (`--host`).**
- [x] **[DONE] Motor de Auto-Update `xp-kit update` com cache de 24h e notificações discretas.**
- [x] **[DONE] Matriz de instalação flexível: global, projetos específicos (`--project`), ou ambos (`--both`).**
- [x] **[DONE] Documentação técnica completa em inglês no `README.md`.**
- [ ] **[P1] Validar execução de projeto piloto multi-IDE (OpenCode + Cursor + Codex + Qoder) em repositório externo.**

---

## 5. Architectural Decisions & Domain Models (Semantic Memory)

> Conteúdo em [details/5-architectural-decisions-domain-models-semantic-memory.md](details/5-architectural-decisions-domain-models-semantic-memory.md) (sob demanda).

## 6. Gotchas, Hurdles & Learned Playbooks (Procedural Memory)

> Conteúdo em [details/6-gotchas-hurdles-learned-playbooks-procedural-memory.md](details/6-gotchas-hurdles-learned-playbooks-procedural-memory.md) (sob demanda).

## 7. Technical Debts & Known Blockers

- **Nenhum bloqueio ativo.** Orçamento de contexto base (`AGENTS.md`, `PROJECT_MEMORY.md`, 77 `SKILL.md` e `SKILLS_INDEX.md`) 100% dentro dos tetos de `kit_constants.py`.

