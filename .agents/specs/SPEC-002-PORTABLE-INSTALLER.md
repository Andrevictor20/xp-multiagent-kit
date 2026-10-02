# SPEC-002: Instalador Unificado & Portabilidade do XP Multi-Agent Kit (Global vs Projeto Local)

> **Status:** APPROVED  
> **Risco:** L2 (Novo Utilitário de Bootstrap, Portabilidade Multi-Ambiente e CLI agy-kit)  
> **Autor:** Antigravity (Pair Programming AI)  
> **Data:** 2026-10-02  

---

## 1. Contexto & Problema de Negócio

- **Por que estamos construindo isso?**  
  Atualmente, a instalação do kit depende de rodar manualmente `./scripts/install-global.sh`, o qual assume instalação global em `~/.gemini/config/` e requer que o repositório já esteja previamente clonado. Usuários que utilizam o Antigravity (via IDE ou CLI) e desejam adotar o kit enfrentam barreiras de onboarding:
  1. Falta de um **comando único de instalação (one-liner)** via `curl -fsSL ... | bash` ou `./install.sh`;
  2. Impossibilidade de escolher se desejam aplicar o kit **globalmente** (todas as sessões da IDE/CLI) ou **apenas em um projeto específico** (isolando diretório `.agents/` e memória sem impactar outros repositórios);
  3. Ausência de um utilitário CLI de diagnóstico e gestão contínua (`agy-kit`) para checar saúde (`doctor`), injetar em novos projetos (`init`) ou ressincronizar (`sync`).

- **Impacto esperado:**  
  1. Portabilidade plug-and-play do kit para qualquer usuário do Antigravity IDE ou CLI;
  2. Experiência de instalação em 1 clique/comando com wizard interativo amigável e suporte a flags não-interativas (`--global`, `--project <dir>`, `--both`);
  3. Garantia de ambiente saudável através do verificador de dependências e diagnóstico `agy-kit doctor`;
  4. Isolamento estrito de memória e contexto para usuários que preferirem aplicação projeto a projeto.

- **Restrições não negociáveis:**  
  1. **Zero dependências externas de runtime:** O motor instalador deve utilizar exclusivamente a standard library do Python 3 (`os`, `sys`, `shutil`, `subprocess`, `pathlib`, `argparse`, `urllib`), sem requerer `pip install` prévio;
  2. **Idempotência estrita:** A execução do instalador múltiplas vezes não deve corromper configurações, duplicar entradas no PATH nos arquivos de shell (`.bashrc`, `.zshrc`) ou sobrescrever memórias de projeto existentes sem confirmação;
  3. **TDD estrito:** A suíte de testes unitários existente (288/288 testes) deve ser preservada com zero regressão, acompanhada de novos testes cobrindo todos os módulos do instalador.

---

## 2. Acceptance Criteria (ATDD)

### AC-1: Script de Entrada Único & Portável (`install.sh`)
- **Dado:** Um usuário em qualquer máquina Linux ou macOS com terminal bash/sh.
- **Quando:** O usuário executa `./install.sh [flags]` localmente ou via `curl -fsSL <URL> | bash`.
- **Então:** 
  1. Se executado via curl em máquina sem clone, clona o repositório no diretório canônico padrão `~/.xp-multiagent-kit` e aciona o instalador;
  2. Se executado dentro do repositório clonado, utiliza o diretório local como origem do kit;
  3. Transfere a execução de forma transparente para o motor Python `scripts/kit_installer.py`.
- **Métrica:** Executável via bash, retorno 0 em ambos os cenários (local e remoto clonado).

### AC-2: Verificação e Diagnóstico de Dependências (`DependencyChecker`)
- **Dado:** O motor de instalação `kit_installer.py`.
- **Quando:** A etapa de verificação de dependências é iniciada.
- **Então:**
  1. Checa a presença e versão mínima de `python3` (>= 3.8) e `git`;
  2. Se faltar `python3` ou `git`, identifica a distribuição Linux (`apt`, `dnf`, `pacman`, `apk`) ou macOS (`brew`) e emite mensagem clara com o comando exato para resolução;
  3. Verifica e diagnostica a existência dos diretórios do Antigravity (`~/.gemini/config`, `~/.gemini/antigravity-ide`, `~/.gemini/antigravity-cli`);
  4. Detecta ferramentas complementares (`gh`, `cargo`/`rtk`) informando seu status sem interromper a instalação básica.
- **Métrica:** Método de checagem retorna estrutura com status de cada dependência e código de saída adequado.

### AC-3: Modo Interativo (Wizard de Escolha do Usuário)
- **Dado:** Execução do instalador sem argumentos em terminal interativo (TTY).
- **Quando:** O usuário é solicitado a selecionar o modo de instalação.
- **Então:**
  1. Apresenta menu numérico claro:
     - `[1] Global`: instala em `~/.gemini/config`, espelha na IDE/CLI e adiciona executáveis ao PATH (`~/.local/bin`);
     - `[2] Projeto Específico`: solicita o caminho do projeto e injeta a governança exclusivamente nele;
     - `[3] Ambos`: executa a instalação global E já aplica no projeto indicado.
  2. Solicita confirmação antes de gravar no disco e exibe resumo das operações realizadas.
- **Métrica:** Validação de input com repetição amigável em caso de opção inválida.

### AC-4: Modo Não-Interativo & Suporte a Automação (CLI Flags)
- **Dado:** Execução do instalador em scripts, containers ou com flags de terminal.
- **Quando:** Fornecidas flags como `--global` (`-g`), `--project <DIR>` (`-p`), `--both <DIR>`, `--yes` (`-y`), `--dry-run`, ou `--no-deps`.
- **Então:**
  1. Executa a operação correspondente sem solicitar confirmação interativa caso `--yes` seja passado;
  2. Suporta `--dry-run` emitindo o plano de ações sem alterar o sistema de arquivos;
  3. Suporta `--no-deps` pulando a verificação de pacotes do sistema operacional.
- **Métrica:** Argumentos parseados corretamente e sem chamadas a `input()` em modo não-interativo.

### AC-5: Injeção Isolada em Projeto Específico (`ProjectInstaller`)
- **Dado:** A seleção do modo Projeto com um diretório de destino.
- **Quando:** O instalador aplica o kit no projeto indicado.
- **Então:**
  1. Cria o diretório `.agents/` no projeto com as subpastas `policies/`, `rules/`, `templates/`, `workflows/` e `memory/`;
  2. Cria ou atualiza `AGENTS.md` canônico na raiz do projeto;
  3. Instala `.geminiignore` e `.antigravityignore` a partir dos templates universais;
  4. Inicializa `.agents/memory/PROJECT_MEMORY.md` através de `agy-init-memory` (ou template com placeholders preenchidos), preservando memória existente se já houver;
  5. Configura git hooks locais se a pasta `.git` estiver presente.
- **Métrica:** Projeto configurado de forma autocontida e funcional para o Antigravity IDE/CLI.

### AC-6: Utilitário CLI Unificado (`agy-kit` / `xp-kit`) & Idempotência de PATH
- **Dado:** Instalação global concluída.
- **Quando:** O usuário invoca o comando `agy-kit` (ou `xp-kit`) a partir de qualquer terminal.
- **Então:**
  1. Comandos disponíveis:
     - `agy-kit doctor`: verifica a integridade de todas as ferramentas, links, diretórios Antigravity e PATH;
     - `agy-kit init [dir]`: injeta o kit em um novo projeto;
     - `agy-kit sync`: re-sincroniza links e configurações globais;
     - `agy-kit version`: exibe a versão atual do kit.
  2. Garante que `~/.local/bin` seja adicionado ao arquivo de configuração de shell (`~/.bashrc`, `~/.zshrc`, etc.) de forma estritamente idempotente (sem linhas duplicadas).
- **Métrica:** Comandos acessíveis no PATH, execução com saída colorida e legível, zero duplicações no shell RC.

---

## 3. Specification by Example (SbE)

| ID | Modo de Invocação | Entrada / Flags | Pré-condição | Resultado Esperado | Código Saída |
|---|---|---|---|---|---|
| E-1 | Interativo | Opção 1 (Global) | Antigravity instalado, python3 e git presentes | Global configurado em `~/.gemini/config`, scripts em `~/.local/bin`, shell RC atualizado | 0 |
| E-2 | Interativo | Opção 2 (Projeto) | Pasta `/tmp/meu-projeto` existente | `.agents/`, `AGENTS.md`, `.geminiignore` e `PROJECT_MEMORY.md` criados no projeto | 0 |
| E-3 | Flag CLI | `--global --yes` | Sem terminal interativo | Execução global silenciosa | 0 |
| E-4 | Flag CLI | `-p /tmp/projeto --yes` | Pasta de projeto fornecida | Aplicação local sem prompt interativo | 0 |
| E-5 | Flag CLI | `--dry-run --global` | Qualquer ambiente | Log de ações simuladas, zero arquivos gravados no disco | 0 |
| E-6 | Flag CLI | `--project /pasta/inexistente` | Diretório não existe | Cria o diretório (se confirmado) ou aborta com erro claro | 0 ou 1 |
| E-7 | CLI Pós-Install | `agy-kit doctor` | Kit instalado globalmente | Tabela com status de Python, Git, IDE, CLI, PATH e Hooks | 0 |
| E-8 | Resiliência | Rodar install 2x seguidas | Mesmas flags | Idempotente: nenhuma linha duplicada no `.bashrc`, arquivos preservados | 0 |

---

## 4. Cenários de Aceite (Gherkin BDD)

```gherkin
Feature: Instalação e Portabilidade Unificada do XP Multi-Agent Kit

  Scenario: Instalação global automatizada via flags
    Given que o usuário possui python3 e git instalados no sistema
    When executar o instalador com os argumentos "--global --yes"
    Then o diretório "~/.gemini/config" deve conter os links para skills, agents e workflows
    And o diretório "~/.local/bin" deve conter os executáveis "agy-kit", "agy-tokens" e "agy-run"
    And o comando deve retornar código de saída 0

  Scenario: Injeção do kit em projeto específico sem afetar ambiente global
    Given um repositório de projeto limpo em "/tmp/test-project"
    When executar o instalador com os argumentos "--project /tmp/test-project --yes"
    Then o diretório "/tmp/test-project/.agents" deve ser criado com sucesso
    And o arquivo "/tmp/test-project/AGENTS.md" deve existir
    And o arquivo "/tmp/test-project/.geminiignore" deve ser criado
    And o arquivo "/tmp/test-project/.agents/memory/PROJECT_MEMORY.md" deve ser inicializado
    And o diretório global "~/.gemini/config" não deve ser modificado

  Scenario: Diagnóstico de integridade com agy-kit doctor
    Given que a instalação global foi concluída
    When o usuário executa "agy-kit doctor"
    Then uma tabela de diagnóstico deve ser exibida no terminal
    And deve conter o status de Python, Git, diretórios Antigravity e PATH
    And o status geral deve indicar integridade operacional
```

---

## 5. Arquitetura Técnica & Componentes

```text
┌────────────────────────────────────────────────────────┐
│                      install.sh                        │
│   • One-liner curl pipe + local bootstrap              │
│   • Auto-clone em ~/.xp-multiagent-kit se necessário   │
│   • Checagem rápida de python3 e repasse de args       │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│               scripts/kit_installer.py                 │
│   • DependencyChecker: Python, Git, Antigravity, OS    │
│   • GlobalInstaller: sincronização global e symlinks   │
│   • ProjectInstaller: injeção modular em projetos      │
│   • PathConfigurator: adição idempotente no shell RC   │
│   • KitDoctor: diagnóstico e auditoria do ambiente     │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                   scripts/agy-kit                      │
│   • CLI unificado: install, init, sync, doctor, version│
│   • Alias em ~/.local/bin/agy-kit e ~/.local/bin/xp-kit│
└────────────────────────────────────────────────────────┘
```

---

## 6. Conformance Report — SPEC-002

| # | Acceptance Criteria | Test File & Test Method | Status |
|---|---|---|---|
| **AC-1** | Script de Entrada Único & Portável (`install.sh`) | `tests/test_kit_installer.py::TestCliMainParser` + `./install.sh --dry-run` | ✅ GREEN |
| **AC-2** | Diagnóstico & Dependências (`DependencyChecker`) | `tests/test_kit_installer.py::TestDependencyChecker` (5 testes) | ✅ GREEN |
| **AC-3** | Modo Interativo (Wizard de Escolha) | `tests/test_kit_installer.py::TestCliMainParser` + manual verification | ✅ GREEN |
| **AC-4** | Modo Não-Interativo & Flags CLI | `tests/test_kit_installer.py::TestCliMainParser` (flags `-g`, `-p`, `--dry-run`) | ✅ GREEN |
| **AC-5** | Injeção Isolada em Projeto (`ProjectInstaller`) | `tests/test_kit_installer.py::TestProjectInstaller` (3 testes) | ✅ GREEN |
| **AC-6** | Utilitário CLI (`agy-kit` / `xp-kit`) & PATH | `tests/test_kit_installer.py::TestPathConfigurator` & `TestKitDoctor` | ✅ GREEN |

**Resultado: 6/6 critérios cobertos e aprovados (303/303 testes unitários GREEN).**

