---
name: async-messaging-and-resilience
description: Mensageria assíncrona, EDA, Outbox Pattern, DLQ, idempotência e Circuit Breaker.
---

# Async Messaging & System Resilience

> **Propósito:** Garantir confiabilidade absoluta, consistência eventual sem perdas e resiliência a falhas transitórias em arquiteturas distribuídas e orientadas a eventos (EDA).

---

## 1. Padrões de Mensageria Confiável

### 1.A Transactional Outbox Pattern
- **Problema:** Atualizar o banco de dados e publicar uma mensagem em um broker (Kafka, RabbitMQ, SQS) na mesma requisição não é transacional (risco de commit no banco com falha no broker ou vice-versa).
- **Regra:** Nunca publique diretamente em um broker durante uma transação de banco.
- **Implementação:**
  1. Grave o evento de domínio em uma tabela `outbox` na **mesma transação local** que altera os dados do negócio.
  2. Um processo background dedicado (ou worker CDC como Debezium) lê a tabela `outbox` e publica as mensagens no broker com confirmação (*at-least-once delivery*).
  3. Marque a mensagem como enviada ou remova-a após confirmação (ACK).

### 1.B Idempotência no Consumidor (Deduplicação)
- **Problema:** Brokers distribuídos garantem entrega *at-least-once*. Mensagens duplicadas acontecerão inevitavelmente devido a re-entregas de rede ou retentativas.
- **Regra:** Todo consumidor deve ser estritamente idempotente.
- **Implementação:**
  - Extraia uma chave de unicidade da mensagem (`message_id` ou `idempotency_key` de negócio).
  - Antes de processar, verifique se a chave já foi registrada na tabela de `processed_messages`.
  - Execute a lógica de processamento e a inserção da chave na mesma transação.
  - Se a chave já existir, descarte a mensagem e emita ACK imediatamente.

### 1.C Dead Letter Queue (DLQ) & Poison Pill Isolation
- Se o processamento de uma mensagem falhar:
  1. Realize até **N retentativas com backoff exponencial** (ex: 3 a 5 tentativas).
  2. Se a falha persistir (erro irrecuperável / *poison pill*), envie a mensagem para uma **Dead Letter Queue (DLQ)** com o payload original, stack trace do erro e metadados de tentativa.
  3. Emita ACK no canal principal para não travar a fila.
  4. Alerte a equipe de operações sobre mensagens acumuladas na DLQ.

---

## 2. Padrões de Resiliência de Comunicação

### 2.A Circuit Breaker (Disjuntor)
Protege chamadas remotas contra falhas em cascata quando o serviço dependente estiver degradado:
- **Fechado (Closed):** Fluxo normal. Todas as chamadas são executadas. Contabiliza falhas.
- **Aberto (Open):** Quando a taxa de falha (ex: HTTP 5xx ou timeouts) atinge o limiar (ex: 50% em 10s), o disjuntor abre. Chamadas subsequentes falham imediatamente (*fail-fast*) sem tocar a rede.
- **Meio-Aberto (Half-Open):** Após uma janela de espera (*sleep window*, ex: 30s), permite um número controlado de requisições de teste. Se tiverem sucesso, fecha o disjuntor; se falharem, volta para Aberto.

### 2.B Exponential Backoff com Full Jitter
Ao retentar operações de I/O transitórias, **sempre adicione jitter** para evitar o problema da *manada enfurecida* (*thundering herd*):
```text
sleep = random(0, min(max_backoff, base_backoff * (2 ^ attempt)))
```
- Nunca faça retentativas imediatas ou com intervalos fixos em sistemas com concorrência.

### 2.C Bulkhead & Backpressure
- **Bulkhead:** Isole pools de threads e conexões para cada dependência externa. A falha de um serviço de terceiros não pode exaurir as threads da aplicação principal.
- **Backpressure:** Consumidores devem buscar mensagens de acordo com sua capacidade de processamento (*pull-based* com prefetch limitado), nunca aceitar sobrecarga irrestrita.
