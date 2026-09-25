---
name: token-budget-tracker
description: "Telemetria de tokens em 3 camadas, Pre-Flight Budget Gate e Modo Cirúrgico Atômico."
---

# Token & Quota Budget Tracker

Mecanismo para auditoria, controle, governança preventiva e degradação graciosa de tokens no Antigravity IDE e CLI.

## As 3 Camadas de Limites

1. **Janela de Mensagem/Sessão (Context Window):**
   - Mede a memória de trabalho acumulada nesta conversa (ex: 1.05M tokens para Gemini Flash, 200k para Claude).
   - Alerta preventivo se ultrapassar 70% ou restar menos de 100k tokens.
2. **Limite Móvel de 5 Horas (Rolling 5-Hour Rate Limit):**
   - Janela de taxa que se recicla continuamente nas últimas 5 horas entre todas as sessões ativas.
   - Alerta preventivo se ultrapassar 80% ou restar menos de 50k tokens.
3. **Limite Semanal (Weekly Quota):**
   - Teto da assinatura/conta com renovação semanal a cada 7 dias.
   - Alerta preventivo se ultrapassar 85% ou restar menos de 1M tokens.

---

## Governança de Consumo em Ferramentas (Tool Budget)
- **Smart Tool Optimizer Ativo (PreToolUse Hook):** O hook `smart-tool-optimizer` intercepta e reescreve automaticamente argumentos via `overwrite`: aplica clamping transparente em `view_file` (máx 40 linhas) e injeta `agy-sanitize` em comandos verbosos não filtrados (`run_command`).
- **Teto por Chamada de Ferramenta:** Máximo 1.500 caracteres / 400 tokens por retorno.
- **Sanitização Mandatória:** Todo comando com potencial de log extenso deve rodar via `agy-sanitize` ou pipes limitadores (`| head -n 25`, `| tail -n 20`).
- **Fatiamento Cirúrgico:** `view_file` restrito a blocos de no máximo **40 linhas** (`EndLine - StartLine <= 40`), proibindo leitura cega.
- **Session Reset Agressivo:** Recomendado reiniciar a sessão a cada **15 turnos ou 40k tokens** para impedir que históricos de ferramentas pesadas continuem faturando nos turnos posteriores.

---

## Pre-Flight Budget Gate & Modo Cirúrgico Atômico

### 1. Alerta Prévio Obrigatório
Quando o usuário solicitar uma tarefa substantiva e qualquer uma das 3 camadas estiver com limite baixo/crítico:
- O agente **DEVE avisar o usuário antes** de iniciar a execução pesada:
  - Informa qual camada está sob pressão e a margem restante.
  - Oferece alternativas (ex: reset de sessão via `PROJECT_MEMORY.md` para abrir um chat limpo de ~2k tokens).

### 2. Execução Sob Insistência do Usuário (Modo Cirúrgico Atômico)
Se o usuário insistir em prosseguir mesmo com o limite baixo:
- **Proibido Deixar Trabalho Pela Metade:** Dimensione o escopo estritamente para o que for viável dentro da margem disponível.
- **Entregas Fechadas e Atômicas:** Execute apenas uma sub-etapa completa (ex: 1 teste passando, 1 refatoração pontual), rode os testes para garantir estabilidade e registre o checkpoint no `PROJECT_MEMORY.md`.
- **Encerramento Controlado:** Pause com uma mensagem clara de progresso alcançado, evitando que a resposta seja cortada por estouro de token no meio de um arquivo.

---

## Consultas de Consumo no Chat (IDE & CLI)
Quando o usuário perguntar no chat sobre dados de consumo, cotas ou tokens:
O agente **DEVE apresentar o máximo de informações possíveis**, incluindo:
1. **Modelo Ativo & Limites:** Nome amigável, chave técnica, Janela de Contexto e Saída Máxima.
2. **Janela de Mensagem (Sessão Atual):** Tokens acumulados, teto, margem livre restante e percentual de ocupação.
3. **Cota Oficial ao Vivo (Google Language Server):** Percentual restante e tempo exato de refresh para a Janela Móvel de 5 Horas e para o Ciclo Semanal de 7 Dias.
4. **Decomposição do Consumo:** Tokens e bytes gastos em System Prompt/Schemas, Chamadas de Ferramentas, Respostas/Thinking e Mensagens do Usuário.
5. **Heurística Acumulada da Conta:** Total de tokens e sessões registradas nas últimas 5h e 7 dias com taxa horária/diária.
6. **Diagnóstico & Status:** Avaliação de integridade (🟢 Saudável, 🟡 Atenção ou 🔴 Crítico) e recomendações práticas de preservação de cota.

---

## Comandos Disponíveis

```bash
# Visualizar dashboard interativo no terminal (com rich e <usado>/<total>)
xp-tokens

# Forçar modelo específico e visualizar seus limites dedicados
xp-tokens -m claude-sonnet-4-6
xp-tokens -m gemini-3.8-pro --plain

# Verificar integridade do orçamento e emitir alertas se necessário
xp-tokens --check

# Monitoramento contínuo em tempo real (para painel split/tmux)
xp-tokens --watch

# Imprimir rodapé de telemetria da mensagem/turno atual e acumulado (IDE e CLI)
xp-tokens --turn

# Imprimir badge markdown compacto para chat
xp-tokens --badge

# Exportar métricas completas em JSON estruturado
xp-tokens --json

# Gerar relatório detalhado .agents/memory/TOKEN_TELEMETRY.md
xp-tokens --report
```
