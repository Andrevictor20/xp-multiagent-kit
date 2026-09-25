# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 01:21:06  
> **Sessão:** `a1ea7869-fc7c-44a8-af4b-ddee47837e49` | **Modelo:** `gemini-3.8-flash`

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `71.0k` tokens | `1.05M` | **6.77%** | `977.6k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `530.2k` tokens | `500.0k` | **106.05%** | `0` livres | 11 sessões (~106.0k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `4.98M` tokens | `10.00M` | **49.78%** | `5.02M` livres | 27 sessões (~711.1k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `32.6k` | 107,703 B | 46.0% |
| **Execuções de Ferramentas** | `33.9k` | 108,480 B | 47.7% |
| **Respostas & Thinking** | `3.9k` | 13,555 B | 5.5% |
| **Mensagens do Usuário** | `593` | 2,372 B | 0.8% |

---

## 3. Top Ferramentas Consumidoras
| `VIEW_FILE` | 24 | 17.9k | 57,182 B |
| `RUN_COMMAND` | 36 | 11.3k | 36,122 B |
| `CODE_ACTION` | 9 | 4.0k | 12,855 B |
| `LIST_DIRECTORY` | 3 | 408 | 1,307 B |
| `GREP_SEARCH` | 2 | 316 | 1,014 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **106.0%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **49.8%** da cota semanal (5.02M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
