# Política de Economia de Tokens & Enforcement Mecânico

> Carregada sob demanda. O `AGENTS.md` contém apenas o núcleo inegociável;
> este arquivo detalha o *como* e os valores exatos, que vivem em
> `scripts/kit_constants.py` (fonte única de verdade).

## 1. Modelo de custo (por que estas regras existem)

O custo dominante de uma sessão de agente **não** é o tamanho de cada saída de
ferramenta, e sim o produto:

```
custo_total ≈ Σ_turnos ( contexto_base + histórico ) + Σ saídas_de_ferramentas
```

Cada turno reenvia system prompt + regras + memória + histórico. Portanto:

1. **Reduzir turnos** vale mais do que reduzir o tamanho de uma saída.
2. **Reduzir o contexto base** multiplica a economia por todos os turnos.
3. Sanitizar output é a terceira alavanca, não a primeira.

Ferramentas de medição: `agy-turn --report` (reenvio acumulado, share, ranking)
e `agy-skill-index audit` (orçamento do contexto base).

## 2. Orçamento de turnos por risco (B2)

| Risco | Chamadas de ferramenta | Regra |
|-------|------------------------|-------|
| L0 | 3 | Zero-tool para consultas conceituais |
| L1 | 8 | Testes só do módulo afetado |
| L2 | 20 | Spec + testes + implementação |
| L3 | sem teto | Checkpoint atômico obrigatório |

**Batching obrigatório (B3):** chamadas independentes vão no mesmo turno.
Declarar o plano de chamadas antes de executar quando o orçamento for apertado.
No **Turno 1**, agrupar a leitura do `PROJECT_MEMORY.md` (Passo 0) com a inspeção dos arquivos-alvo e testes.

## 3. Leituras de arquivo (B1)

- Arquivo até `WHOLE_FILE_READ_MAX_LINES` (800): ler **inteiro em uma chamada**.
- Acima disso: localizar o símbolo via busca e pedir o intervalo exato
  (`SECTION_READ_MAX_LINES` = 400 por janela).
- Proibido fatiar em janelas pequenas: leitura contígua repetida é sinal de
  abordagem errada, e o hook avisa.
- **No-Reread pós-edição:** Proibido chamar `view_file` imediatamente após
  `replace_file_content` bem-sucedido no mesmo arquivo (`POST_EDIT_REREAD_TTL_SECONDS = 30s`).
  Confiar na aplicação da edição e prosseguir diretamente para a execução dos testes.

## 4. Saídas de comando e tarefas (B4/B5)

- `agy-run "<comando>"` é o executor padrão onde não há hooks: aplica
  compatibilidade de shell, remove banner/MOTD, trunca e registra telemetria.
- **Anti-Polling de tarefas:** Ao disparar testes ou builds que possam demorar,
  ajuste `WaitMsBeforeAsync: 8000`. Se o comando for para background, NUNCA faça
  polling em loop com `manage_task(Action='status')`. O `smart-tool-optimizer`
  bloqueia chamadas consecutivas (`MAX_TASK_STATUS_POLLS = 1`). Encerre o turno e aguarde
  a notificação reativa automática.
- `agy-sanitize` remove ruído decorativo **antes** de medir tamanho: banners de
  fastfetch/neofetch custam centenas de tokens por chamada e ficam abaixo do
  limiar de flood.
- Git e CI/CD continuam ultra-econômicos: `git status -s`, `git diff --stat`,
  `git log -n 5 --oneline`, `git push --quiet`, `agy-git-ops ci-status`,
  `gh run view --log-failed | agy-compact --ci`. Nunca `gh run view --log`.
- Erro de sintaxe de shell custa um turno inteiro sem produzir nada: em shell
  não-POSIX (fish/csh), comandos POSIX rodam via `bash -c`.

## 5. Hooks e enforcement portátil (C1/C2)

`.agents/hooks.json` usa `${KIT_ROOT}` e é renderizado por `install-global.sh`
em `hooks.rendered.json` (arquivo derivado, fora do versionamento).

| Hook | Fase | Efeito |
|------|------|--------|
| `smart-tool-optimizer` | PreToolUse | loop detection (deny), proteção de `list_dir` na raiz, filtros de ruído em busca, janela de leitura, bloqueio de `write_to_file` em arquivo > 60 linhas, sanitização de comandos verbosos |
| `tool-size-guard` | PostToolUse | remove banner e trunca saída acima do orçamento |
| `token-badge` | PostInvocation | registra o turno na telemetria local e atualiza o relatório |
| `dynamic-effort-router` | PreInvocation | modula o reasoning effort por risco |

**Em IDEs sem sistema de hooks** (Qoder, Cursor), o enforcement mecânico é feito
por `agy-run`, `agy-sanitize`, `agy-turn`, `agy-evidence` e `agy-conformance`.
Regra em prosa é sugestão; regra dentro do binário é enforcement.

Estado volátil vive em `.agents/runtime/` (loop detection com TTL, log de
turnos, evidências), nunca em `/tmp` global.

## 6. Contexto base (A1/A2/A3)

| Artefato | Orçamento | Como manter |
|----------|-----------|-------------|
| `AGENTS.md` | 6 KB | núcleo + ponteiros para políticas |
| `.agents/skills/SKILLS_INDEX.md` | 1 linha por skill | `agy-skill-index generate` |
| `PROJECT_MEMORY.md` | 8 KB | `agy-memory-archive` (poda Seção 3 e derrama seções para `memory/details/`) |
| `SKILL.md` individual | 6 KB | `agy-skill-index split` (fatiar em `sections/`) |

`agy-skill-index audit` retorna exit code 1 quando qualquer teto é violado e
deve rodar no gate de release.

## 7. Telemetria (D)

Três camadas, com fonte oficial quando disponível e estimativa local como
fallback portável:

1. **Turno** — entrada, ferramentas, resposta.
2. **Reenvio acumulado** — Σ(contexto base + histórico) por turno. É a métrica
   que explica o consumo real e a que faltava.
3. **Cota 5h / semanal** — Language Server RPC no Antigravity; estimativa local
   em outras IDEs, sempre marcada como `[Estimado]`.

O rodapé canônico continua obrigatório em toda resposta:

```text
Consumo:  16.2k tokens (Entrada: 113 | Ferramentas: 15.1k | Resposta: 959)
Contexto: [▰▱▱▱▱▱▱▱▱▱] 6.0% usado (63.2k) • 94.0% livre de 1.05M
5h:       [▱▱▱▱▱▱▱▱▱▱] 1.0% usado (8.1k) • 99.0% restante (~791.9k) de 800.0k (renova em 4 h, 46 m)
Semana:   [▰▰▰▰▰▱▱▱▱▱] 50.9% usado (5.09M) • 49.1% restante (4.91M) de 10.00M (renova em 5 d, 19 h)
Modelo:   Gemini 3.8 Flash (Effort: Medium) | Janela: 1.05M | Saída: 65.5k
```

Quando não houver fonte oficial de cota, o agente exibe as camadas 1 e 2 com
dados locais (`agy-turn --report`) e marca as camadas 3 como `[Estimado]`.
Omitir ou inventar números é proibido.

**Pre-Flight Gate:** alerta acima de 70% de contexto ou 80% de cota, ou quando o
orçamento de turnos do nível de risco é excedido. Se o usuário insistir, operar
em Modo Cirúrgico Atômico: entregar um checkpoint completo, testado e estável.

## 8. Evidência e conformidade baratas (E1/E2)

- `agy-evidence run "<comando de teste>"` grava o log completo em
  `.agents/runtime/evidence/` e indexa um resumo estruturado. O
  `walkthrough.md` recebe apenas a tabela (`agy-evidence render`), nunca o log.
- `agy-conformance --spec SPEC-NNN-ATDD.md --tests tests/ --results r.json`
  deriva a matriz AC → teste → status dos artefatos reais. AC sem teste ou com
  teste em falha = `NON-COMPLIANT` = gate `BLOCKED` (exit code 1).
- Regra Anti-Self-Test permanece: a IA não define Acceptance Criteria e testes
  sem aprovação humana intermediária.

## 9. Colapso de agentes (E3)

| Risco | Agentes |
|-------|---------|
| L0 | `builder` → `archivist` |
| L1 | `navigator` → `builder` → `archivist` → `release-gatekeeper` |
| L2 | pirâmide completa com Stop Gate humano |
| L3 | pirâmide + Threat Modeling + Zero-Downtime Plan |

Cada agente adicional é um contexto novo relendo specs e memória. Só ativar o
papel quando ele agrega decisão, não cerimônia.

## 10. Saídas efêmeras & auto-compact

Ao atingir 15 turnos ou 40k tokens na sessão, gravar checkpoint no
`PROJECT_MEMORY.md` e abrir chat limpo via Fast Bootstrap (Passo 0).

## 11. Escada de Simplificação & Governança de Débitos Técnicos

O melhor código é o código nunca escrito. Menos código = menos tokens de leitura, menos tokens de teste e menor superfície de bugs.

1. **Escada de 7 Degraus de Simplificação:**
   - 1. *Precisa existir? (YAGNI)* → Se especulativo, descarte e avise em 1 linha.
   - 2. *Já existe no repositório?* → Reutilize utilitários e tipos antes de criar novos.
   - 3. *A Standard Library resolve?* → Use os módulos embutidos da linguagem.
   - 4. *A plataforma nativa cobre?* → Consulte `.agents/policies/platform-native.md` (HTML5, CSS moderno, Web APIs) antes de adicionar bibliotecas de interface ou utilitários pesados.
   - 5. *Dependência instalada resolve?* → Proibido adicionar novas dependências se algo no manifesto já resolve.
   - 6. *Pode ser uma linha?* → Faça em 1 linha idiomática.
   - 7. *Apenas se nenhum anterior servir:* O código mínimo que resolve o problema.

2. **Regra de Concisão de Resposta:**
   - Em alterações de código de produção: **Código primeiro**, seguido de no máximo 2-3 linhas de justificativa (*o que foi pulado e quando adicionar*).
   - Se a explicação for mais longa do que o diff gerado, corte a explicação. Toda explicação desnecessária é complexidade reintroduzida como prosa.

3. **Governança de Débitos Técnicos Auditáveis (`agy-debt`):**
   - Ao introduzir simplificações ou atalhos deliberados com limites conhecidos (ex: lock global, scan O(N)), marque-os no código com:
     `// debt: <teto da simplificação>, <gatilho para refatorar>`
     (ou `# debt: <teto>, <gatilho>` em Python/Shell).
   - Débitos sem gatilho de upgrade são marcados como `[NO-TRIGGER]` pelo `agy-debt` e representam risco de apodrecimento (*rot risk*).

## 12. Binários do kit

| Comando | Papel |
|---------|-------|
| `agy-run` | executor com enforcement portátil (shell compat, strip de banner, truncamento, telemetria) |
| `agy-sanitize` | sanitizador de saída verbosa em pipe ou como wrapper |
| `agy-turn` | telemetria local de turnos (`--record`, `--report`, `--preflight`, `--top`) |
| `agy-tokens` / `xp-tokens` | cota oficial ao vivo + relatório em 3 camadas |
| `agy-evidence` | evidência estruturada (`run`, `record`, `render`) |
| `agy-conformance` | Conformance Report derivado de spec + testes |
| `agy-skill-index` | índice de skills, auditoria de orçamento e fatiamento (`generate`, `audit`, `split`) |
| `agy-memory-archive` | rotação por teto de bytes e spill para `memory/details/` |
| `agy-repo-map` | AST Repo Map anti-exploração cega |
| `agy-ci-heal` | auto-healer de CI/CD (máx. 3 iterações) |
| `agy-handoff` | Handoff Packet estruturado |
| `agy-git-ops` | operações Git compactas (`status`, `ci-status`) |
| `agy-smart` / `agy-effort` | roteamento de reasoning effort |
| `agy-health` / `agy-audit-config` | integridade do kit e auditoria de bloat global |
| `agy-debt` | auditoria in-code de débitos técnicos e detecção de rot (`no-trigger`) |

