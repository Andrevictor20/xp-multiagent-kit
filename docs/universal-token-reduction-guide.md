# 📘 Guia Universal de Redução de Tokens — Antigravity (IDE & CLI)

Este guia apresenta as **melhores práticas operacionais e ferramentas** para manter o consumo de tokens sob controle estrito no **Antigravity (IDE e CLI)**, em **qualquer projeto ou situação**, garantindo respostas mais rápidas, menor latência e preservação da cota de 5 horas e semanal.

---

## 🎯 As 5 Regras de Ouro de Economia de Tokens

### 1. A Regra dos 25 Turnos / 50k Tokens (Reset Preventivo)
- **O Problema:** O Antigravity retransmite todo o histórico da conversa em cada novo turno. Em chats com mais de 25 turnos, uma pergunta simples de 2 linhas pode custar 80.000 tokens de histórico reenviado.
- **A Solução:** Ao atingir 25 turnos ou quando `agy-tokens` indicar > 50k tokens na janela, gere o pacote de transição e abra um chat novo:
  ```bash
  agy-handoff --write-file
  ```
- **Resultado:** O novo chat começa limpo lendo apenas as ~25 linhas do `SESSION_HANDOFF.md` (~300 tokens), poupando **mais de 90% dos tokens por mensagem**.

---

### 2. Modulação de Raciocínio (Thinking Tokens Adaptativos)
- **O Problema:** Modelos de raciocínio avançado geram entre 3.000 e 8.000 tokens internos de pensamento mesmo para tarefas mecânicas banais (corrigir CSS, renomear variáveis, criar commits).
- **A Solução:** No CLI, selecione o perfil de esforço correspondente:
  - `agy-fast "ajuste a margem do botão"`: Ativa `--effort low` (economiza ~80% de tokens de pensamento).
  - `agy "implemente o endpoint X"`: Modo padrão balanceado (`--effort medium`).
  - `agy-deep "analise essa condição de corrida"`: Reserva `--effort high` para raciocínio profundo.

---

### 3. Protocolo Anti-Flood de Ferramentas (`agy-sanitize`)
- **O Problema:** Rodar comandos como `npm test`, `pytest`, `docker build` ou `cargo build` despeja centenas de linhas de logs no chat. Uma vez no histórico, essas linhas são cobradas em todos os turnos seguintes.
- **A Solução:** Execute comandos via `agy-sanitize` ou utilize pipes:
  ```bash
  # Como wrapper direto:
  agy-sanitize pytest -v

  # Ou via pipe:
  npm test | agy-sanitize
  cargo build | agy-sanitize
  ```
- **Resultado:** Preserva as primeiras 10 linhas, as últimas 20 linhas (erros e diagnósticos) e oculta as linhas intermediárias com indicação clara, preservando 100% o exit code do comando original.

---

### 4. Inspeção Cirúrgica de Código vs Fatiamento Cego ($O(N^2)$)
- **O Problema:** Ler arquivos inteiros consome milhares de tokens, mas fatiar cegamente em múltiplos blocos contíguos sequenciais (ex: 1-40, depois 41-80, depois 81-120) gera acúmulo quadrático de histórico em sub-etapas intermediárias ($O(N^2)$), retransmitindo as saídas anteriores a cada round-trip.
- **A Solução:**
  - Pratique **Symbol-First Navigation**: consulte o `REPO_MAP.md` e localize a linha exata do símbolo via `grep_search`.
  - Ao inspecionar o código, solicite uma janela cirúrgica de até 60 linhas contendo o símbolo completo, evitando round-trips repetidos.
  - O hook nativo `smart-tool-optimizer` calibra janelas em 60 linhas e detecta automaticamente leituras contíguas para evitar a armadilha do fatiamento excessivo.

---

### 5. Dieta Global e Modelos de Exclusão (`.geminiignore`)
- **O Problema:** Deixar regras gigantes em `~/.gemini/config/rules/` ou esquecer de ignorar `node_modules` / `.venv` faz com que o agente indexe gigabytes de código desnecessário.
- **A Solução:**
  - Audite periodicamente as configurações globais:
    ```bash
    agy-audit
    ```
  - Copie o template universal para novos projetos:
    ```bash
    cp /caminho/do/kit/templates/universal.geminiignore .geminiignore
    ```

---

## 🛠️ Tabela de Ferramentas Globais Disponíveis

| Utilitário | Finalidade | Como Usar |
| :--- | :--- | :--- |
| `agy-tokens` / `xp-tokens` | Telemetria de tokens em 3 camadas (Janela, 5h, Semanal) | `agy-tokens --check` ou `agy-tokens --badge` |
| `agy-fast` | Executa CLI com esforço reduzido (economia de thinking) | `agy-fast "sua instrução"` |
| `agy-deep` | Executa CLI com esforço máximo para problemas críticos | `agy-deep "sua instrução complexa"` |
| `agy-sanitize` | Trunca saídas de terminal e previne inundações de log | `agy-sanitize <comando>` ou `<cmd> \| agy-sanitize` |
| `agy-handoff` | Gera resumo ultra-compacto (<30 linhas) para resetar chats | `agy-handoff --write-file` |
| `agy-audit` | Audita inchaço de rules, MCPs e skills globais | `agy-audit` |

---

## 🚨 Modo Cirúrgico Atômico (Quando a Cota Estiver < 20%)

Se `agy-tokens --check` emitir o alerta crítico:
1. **Evite tarefas exploratórias amplas:** Peça apenas a modificação estritamente necessária.
2. **Execute um único ciclo RED -> GREEN:** Não inicie novos épicos ou refatorações periféricas.
3. **Gere o checkpoint imediatamente:** Salve o estado atual com `agy-handoff --write-file` para não deixar trabalho pela metade.
