# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 00:38:11  
> **Sessão:** `f9c2f5b2-97af-4063-8d29-01b3c85d98f8` | **Modelo:** `gemini-3.8-flash`

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `71.6k` tokens | `1.05M` | **6.83%** | `976.9k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `449.1k` tokens | `500.0k` | **89.83%** | `50.9k` livres | 10 sessões (~89.8k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `4.82M` tokens | `10.00M` | **48.23%** | `5.18M` livres | 24 sessões (~688.9k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `32.6k` | 107,571 B | 45.5% |
| **Execuções de Ferramentas** | `32.9k` | 105,224 B | 45.9% |
| **Respostas & Thinking** | `5.5k` | 19,140 B | 7.6% |
| **Mensagens do Usuário** | `683` | 2,735 B | 1.0% |

---

## 3. Top Ferramentas Consumidoras
| `VIEW_FILE` | 30 | 23.3k | 74,710 B |
| `CODE_ACTION` | 10 | 5.3k | 16,906 B |
| `RUN_COMMAND` | 11 | 2.3k | 7,369 B |
| `GREP_SEARCH` | 10 | 1.5k | 4,803 B |
| `LIST_DIRECTORY` | 3 | 348 | 1,114 B |
| `SYSTEM_MESSAGE` | 1 | 100 | 322 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **89.8%** do teto (50.9k disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **48.2%** da cota semanal (5.18M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
