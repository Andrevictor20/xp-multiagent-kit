---
name: software-evolution-and-roadmapping
description: Planejamento a longo prazo, roadmapping Now/Next/Later, Strangler Fig e ciclo de vida (EOL).
---

# Software Evolution & Strategic Technical Roadmapping

> **Propósito:** Conectar a visão de produto e arquitetura a um plano de execução de longo prazo (6 a 24 meses), eliminando reescritas traumáticas ("Big Bang"), prevenindo obsolescência técnica (EOL) e garantindo escalabilidade econômica e sustentável.

---

## 1. O Modelo de Horizontes: Now / Next / Later

Substitua cronogramas rígidos de longo prazo (diagramas de Gantt) que perdem validade na primeira mudança por um modelo dinâmico de 3 horizontes:

| Horizonte | Foco Principal | Validação Exigida |
| :--- | :--- | :--- |
| **NOW (1–4 sem)** | Escopo contratado, granularidade alta | TDD estrito e Acceptance Criteria |
| **NEXT (1–3 meses)** | Arquitetura preliminar e metas validadas | Spikes técnicos para mitigar risco |
| **LATER (3–12+ meses)** | Direção de escala e mudanças estruturais | Gatilhos objetivos (*triggers*) de transição |

- **Now (Compromisso Imediato):** Tarefas ativas decompostas em Acceptance Criteria (ATDD), com dependências resolvidas e entrega contínua.
- **Next (Planejamento Técnico Próximo):** Iniciativas com arquitetura desenhada (ADRs preliminares). Exige a execução de *Spikes técnicos* antes de entrarem em `Now` para eliminar incertezas de API ou desempenho.
- **Later (Direção Arquitetural Estratégica):** Mudanças de paradigma (ex: migração de banco, quebra de serviços, internacionalização). Não detalhe código; documente apenas os gatilhos objetivos (*triggers*) que moverão a iniciativa para `Next`.

---

## 2. Modernização de Legado: O Padrão Strangler Fig

**Regra de Ouro:** Nunca aprove reescritas totais do zero ("Second-System Syndrome"). Elas consomem meses sem gerar valor e costumam recriar os mesmos bugs do legado. Em vez disso, use o padrão *Strangler Fig*:

1. **Interceptação na Borda (Edge Interception):**
   - Coloque um proxy reverso (API Gateway, Nginx, Envoy) à frente do sistema legado.
2. **Extração por Fatia Vertical (Vertical Slice Extraction):**
   - Escolha um domínio coeso e bem delimitado (ex: Módulo de Notificações ou Faturamento).
   - Implemente o novo serviço na nova arquitetura, com testes rigorosos (TDD) e conformidade de contrato.
3. **Redirecionamento Gradual (Shadowing & Canary):**
   - Use tráfego espelhado (*dark launching/shadow traffic*) para comparar respostas do novo serviço com o legado.
   - Migre o tráfego progressivamente (1% → 10% → 50% → 100%).
4. **Desativação (*Pruning*):**
   - Remova o código morto do legado assim que o tráfego for 100% estabilizado no novo serviço.

---

## 3. Planejamento de Capacidade & Escalabilidade (*Capacity Planning*)

Não espere incidentes de indisponibilidade para readequar a infraestrutura. Monitore e projete proativamente:

- **Gargalos Estruturais de Dados:**
  - Estime o crescimento de linhas por mês em tabelas transacionais críticas.
  - Planeje partições de tabela (*table partitioning*), arquivamento de dados frios (*cold storage*) ou leitura em réplicas antes que tabelas ultrapassem dezenas de milhões de linhas.
- **Limites de IOPS e Conexões:**
  - Meça o uso médio de conexões e pool de banco sob pico. Se o uso contínuo passar de **70% do teto**, provisione réplicas de leitura ou arquitetura de cache (*Cache-Aside*).
- **FinOps & Economia de Nuvem:**
  - Audite recursos superdimensionados trimestralmente. Troque instâncias sob demanda por reservas/savings plans para serviços estáveis de longo prazo.

---

## 4. Governança de Ciclo de Vida, EOL & Sunset de APIs

### 4.A Upgrades de Dependências Maiores (Major Versions)
- Estabeleça um ciclo fixo (semestral ou anual) para atualização de versões de linguagens e frameworks (ex: LTS para LTS).
- Softwares em versões sem suporte de segurança (End of Life) tornam-se automaticamente débito técnico de gravidade P1.

### 4.B Protocolo de Desativação de APIs (*Sunset Policy*)
Ao substituir endpoints ou contratos legados, cumpra o padrão **RFC 8594**:
1. **Cabeçalhos de Deprecação:**
   - Adicione cabeçalhos na resposta: `Deprecation: @<timestamp>` e `Sunset: <data_utc>`.
2. **Janela de Transição:** Forneça no mínimo 90 a 180 dias entre a marcação de deprecação e o desligamento final.
3. **Telemetria de Consumo Residual:** Monitore requisições com o cabeçalho antigo via logs JSON (`observability-and-slo-engineering`). Desligue o endpoint legado somente quando o tráfego atingir 0%.
