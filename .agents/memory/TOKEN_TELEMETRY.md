# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🟢 Saudável | **Última Leitura:** 2026-09-24 18:39:16  
> **Sessão:** `c0c53556-726c-45fb-b66f-1c770d55f167` | **Modelo:** `gemini-3.8-flash`

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `138.4k` tokens | `1.05M` | **13.19%** | `910.2k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `188.8k` tokens | `500.0k` | **37.76%** | `311.2k` livres | 2 sessões (~37.8k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `4.17M` tokens | `10.00M` | **41.72%** | `5.83M` livres | 14 sessões (~595.9k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `32.2k` | 106,232 B | 23.3% |
| **Execuções de Ferramentas** | `90.7k` | 290,347 B | 65.6% |
| **Respostas & Thinking** | `13.2k` | 46,356 B | 9.6% |
| **Mensagens do Usuário** | `2.2k` | 8,736 B | 1.6% |

---

## 3. Top Ferramentas Consumidoras
| `RUN_COMMAND` | 114 | 47.2k | 151,132 B |
| `VIEW_FILE` | 39 | 35.8k | 114,524 B |
| `CODE_ACTION` | 11 | 5.3k | 17,067 B |
| `GREP_SEARCH` | 3 | 2.2k | 7,033 B |
| `SYSTEM_MESSAGE` | 1 | 184 | 591 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **37.8%** do teto (311.2k disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **41.7%** da cota semanal (5.83M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
