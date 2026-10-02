---
name: caching-architecture
description: Arquitetura de cache, Redis/Memcached, Cache-Aside e mitigação de stampede/avalanche.
---

# Caching Architecture & Invalidation Strategies

> **Propósito:** Acelerar leituras e proteger recursos caros de I/O e banco de dados, mantendo coerência estrita de dados e eliminando riscos clássicos de saturação de cache.

---

## 1. Padrões de Acesso ao Cache

### 1.A Cache-Aside (Lazy Loading) — Padrão Recomendado
- **Leitura:**
  1. A aplicação consulta o cache pela chave (ex: `user:1001`).
  2. *Cache Hit:* Retorna o dado imediatamente.
  3. *Cache Miss:* Consulta a fonte da verdade (banco de dados/API externa), grava o resultado no cache com TTL e retorna o dado.
- **Escrita:**
  - A aplicação grava na fonte da verdade primeiro.
  - **Invalide (delete)** a chave no cache em vez de sobrescrever, para evitar condições de corrida (*race conditions*) em escritas concorrentes.

### 1.B Write-Through vs Write-Behind
- **Write-Through:** Escreve no cache e no banco sincronicamente. Garante consistência imediata, mas aumenta a latência de escrita.
- **Write-Behind (Write-Back):** Escreve no cache imediatamente e enfileira a gravação no banco de forma assíncrona. Alta velocidade de escrita, com risco de perda se o nó de cache falhar antes da persistência.

---

## 2. Mitigação das 3 Anomalias Críticas de Cache

### 2.A Cache Stampede (Dog-piling / Thundering Herd)
- **Cenário:** Uma chave muito quente (*hot key*) expira e centenas de requisições simultâneas sofrem *cache miss*, bombardeando o banco de dados ao mesmo tempo.
- **Soluções:**
  1. **Mutex / Distributed Lock:** A primeira requisição adquire um lock temporário para consultar o banco e repovoar o cache; as demais aguardam alguns milissegundos ou retornam valor anterior.
  2. **Probabilistic Early Expiration (Algoritmo XFetch):** A chave é recomputada em segundo plano antes de expirar se `compute_time * beta * ln(random()) > (expiry - now)`.

### 2.B Cache Avalanche
- **Cenário:** Centenas de milhares de chaves expiram exatamente no mesmo segundo (ex: job noturno ou TTLs idênticos configurados).
- **Solução:** **Jitter Obrigatório no TTL.** Nunca use TTLs fixos. Adicione variação pseudoaleatória:
  ```text
  effective_ttl = base_ttl + random(-delta, +delta)
  # Exemplo: base de 3600s com delta de 300s (expira entre 3300s e 3900s)
  ```

### 2.C Cache Penetration
- **Cenário:** Requisições buscam IDs inexistentes (ex: `id = -999` ou varredura de ataque), o cache nunca tem o dado e todas as consultas atingem o banco de dados.
- **Soluções:**
  1. **Cache de Valores Nulos:** Armazene `null`/`nil` no cache com TTL muito curto (ex: 30 a 60 segundos).
  2. **Bloom Filter:** Filtro probabilístico na borda para rejeitar requisições de chaves comprovadamente inexistentes antes de consultar o cache ou banco.

---

## 3. Estratégias de Invalidação & Nomenclatura

- **Nomenclatura Semântica de Chaves:**
  - Formato: `<ambiente>:<serviço>:<entidade>:<id>:<versão>`
  - Exemplo: `prod:billing:invoice:98712:v1`
- **Invalidação Orientada a Eventos:**
  - Prefira disparar invalidação por eventos de domínio (ex: evento `InvoiceUpdated` dispara `DEL prod:billing:invoice:98712:v1`).
- **Versionamento de Chaves:** Para mudanças estruturais de schema de cache, altere o prefixo de versão na chave em vez de executar `FLUSHALL` ou `KEYS *` (comandos bloqueantes proibidos em produção).
