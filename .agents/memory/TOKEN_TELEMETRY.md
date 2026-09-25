# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-24 22:27:28  
> **Sessão:** `3ba5fdc1-d966-4ee3-a986-867f21e3df2a` | **Modelo:** `gemini-3.8-flash`

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `58.8k` tokens | `1.05M` | **5.61%** | `989.8k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `680.5k` tokens | `500.0k` | **136.11%** | `0` livres | 8 sessões (~136.1k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `4.66M` tokens | `10.00M` | **46.63%** | `5.34M` livres | 20 sessões (~666.2k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `32.3k` | 106,543 B | 54.9% |
| **Execuções de Ferramentas** | `19.6k` | 62,822 B | 33.4% |
| **Respostas & Thinking** | `5.5k` | 19,286 B | 9.4% |
| **Mensagens do Usuário** | `1.4k` | 5,556 B | 2.4% |

---

## 3. Top Ferramentas Consumidoras
| `VIEW_FILE` | 8 | 7.8k | 25,069 B |
| `RUN_COMMAND` | 31 | 7.6k | 24,265 B |
| `CODE_ACTION` | 4 | 3.4k | 10,809 B |
| `GREP_SEARCH` | 1 | 653 | 2,091 B |
| `SYSTEM_MESSAGE` | 1 | 183 | 588 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **136.1%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **46.6%** da cota semanal (5.34M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
