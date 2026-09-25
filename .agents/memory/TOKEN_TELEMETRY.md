# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-24 22:29:00  
> **Sessão:** `3ba5fdc1-d966-4ee3-a986-867f21e3df2a` | **Modelo:** `gemini-3.8-flash`

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `66.1k` tokens | `1.05M` | **6.30%** | `982.5k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `687.8k` tokens | `500.0k` | **137.56%** | `0` livres | 8 sessões (~137.6k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `4.67M` tokens | `10.00M` | **46.71%** | `5.33M` livres | 20 sessões (~667.2k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `32.3k` | 106,543 B | 48.9% |
| **Execuções de Ferramentas** | `26.0k` | 83,143 B | 39.3% |
| **Respostas & Thinking** | `6.2k` | 21,705 B | 9.4% |
| **Mensagens do Usuário** | `1.6k` | 6,378 B | 2.4% |

---

## 3. Top Ferramentas Consumidoras
| `VIEW_FILE` | 11 | 11.0k | 35,264 B |
| `RUN_COMMAND` | 36 | 9.9k | 31,666 B |
| `CODE_ACTION` | 6 | 4.2k | 13,534 B |
| `GREP_SEARCH` | 1 | 653 | 2,091 B |
| `SYSTEM_MESSAGE` | 1 | 183 | 588 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **137.6%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **46.7%** da cota semanal (5.33M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
