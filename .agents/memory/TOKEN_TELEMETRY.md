# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🟢 Saudável | **Última Leitura:** 2026-09-26 10:23:32  
> **Sessão:** `536a2722-e99c-4a23-a943-3059ad7498f2` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `High`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `154.3k` tokens | `1.05M` | **14.71%** | `894.3k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `286.9k` tokens | `800.0k` | **35.87%** | `513.1k` livres | 4 sessões (~57.4k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `3.78M` tokens | `10.00M` | **37.84%** | `6.22M` livres | 50 sessões (~540.6k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `35.0k` | 115,564 B | 22.7% |
| **Execuções de Ferramentas** | `107.7k` | 344,717 B | 69.8% |
| **Respostas & Thinking** | `9.6k` | 33,695 B | 6.2% |
| **Mensagens do Usuário** | `1.9k` | 7,699 B | 1.2% |

---

## 3. Top Ferramentas Consumidoras
| `VIEW_FILE` | 59 | 43.7k | 139,752 B |
| `EPHEMERAL_MESSAGE` | 136 | 37.7k | 120,767 B |
| `RUN_COMMAND` | 40 | 12.0k | 38,289 B |
| `CODE_ACTION` | 15 | 10.7k | 34,236 B |
| `GREP_SEARCH` | 10 | 2.6k | 8,395 B |
| `LIST_DIRECTORY` | 2 | 479 | 1,534 B |
| `ERROR_MESSAGE` | 1 | 232 | 744 B |
| `SYSTEM_MESSAGE` | 1 | 178 | 571 B |
| `GENERIC` | 2 | 134 | 429 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **35.9%** do teto (513.1k disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **37.8%** da cota semanal (6.22M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
