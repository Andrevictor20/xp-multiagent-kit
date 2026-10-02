---
name: backend-performance-testing
description: Testes de carga, estresse, benchmark de backend, profiling e detecção de gargalos.
---

# Backend Performance & Load Testing Engineering

> **Propósito:** Validar empiricamente a escalabilidade de endpoints e serviços, descobrir limites de saturação sob carga concorrente e garantir conformidade com Service Level Objectives (SLOs) de latência e throughput.

---

## 1. Tipos Canônicos de Testes de Carga

| Tipo de Teste | Objetivo | Padrão de Carga | O que Procurar |
| :--- | :--- | :--- | :--- |
| **Smoke Test** | Validação mínima de sanidade | 1 a 5 Virtual Users (VUs) por 1 minuto | Erros funcionais básicos, HTTP 500 em endpoints |
| **Load Test** | Simulação de tráfego esperado em pico | VUs normais de pico mantidos por 10 a 30 min | Violações de SLO de P95/P99 sob carga contínua |
| **Stress Test** | Descoberta do ponto de ruptura | Aumento contínuo de VUs até falha do sistema | Limite máximo de RPS, degradação graciosa vs colapso |
| **Spike Test** | Resposta a explosões repentinas | Degrau abrupto (0 → 1000 VUs em segundos) | Recuperação automática, filas de conexão, auto-scaling |
| **Soak Test (Endurance)** | Detecção de vazamentos lentos | Carga moderada mantida por horas (2h a 24h) | Heap memory leaks, connection pool exhaustion |

---

## 2. Métricas Críticas & Gargalos de Backend

1. **Connection Pool Exhaustion:**
   - Esgotamento de conexões disponíveis no pool de banco de dados (ex: HikariCP, SQLAlchemy, pgpool). Sintoma: timeouts de aquisição de conexão sob carga moderada.
2. **Consultas N+1 & Queries Mal Indexadas:**
   - Múltiplas consultas SQL disparadas em loop para hidratar coleções. Sintoma: latência cresce linearmente com a quantidade de itens retornados.
3. **Event Loop Lag & Thread Starvation:**
   - Em runtimes assíncronos (Node.js, Python Asyncio), operações de CPU síncronas bloqueiam o event loop. Sintoma: todas as requisições, mesmo simples, sofrem atraso simultâneo.
4. **Garbage Collection (GC) Pauses:**
   - Coleta de lixo frequente ou demorada em runtimes gerenciados (JVM, V8, Go). Sintoma: picos periódicos e repentinos no percentil P99.

---

## 3. Critérios de Aceite de Confiabilidade (SLO Gates)

Todo relatório de teste de carga deve validar três portas numéricas inegociáveis:
1. **Gate de Taxa de Erro:** `http_req_failed < 0.1%` (menos de 1 erro a cada 1000 requisições).
2. **Gate de Percentil P95:** `p(95) < limiar_contratual` (ex: < 200ms para APIs transacionais).
3. **Gate de Percentil P99:** `p(99) < 2x limiar_p95` (evitar cauda longa imprevisível).

---

## 4. Ferramental Padrão (k6 Exemplo Declarativo)

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 }, // Rampa de subida
    { duration: '5m', target: 100 }, // Carga constante
    { duration: '1m', target: 0 },   // Rampa de descida
  ],
  thresholds: {
    'http_req_duration': ['p(95)<250', 'p(99)<500'],
    'http_req_failed': ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('http://api-service.local/v1/health');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```
