# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🟢 Saudável | **Última Leitura:** 2026-09-26 10:22:29  
> **Sessão:** `536a2722-e99c-4a23-a943-3059ad7498f2` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `High`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `150.0k` tokens | `1.05M` | **14.30%** | `898.6k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `282.6k` tokens | `800.0k` | **35.33%** | `517.4k` livres | 4 sessões (~56.5k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `3.78M` tokens | `10.00M` | **37.80%** | `6.22M` livres | 50 sessões (~540.0k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `35.0k` | 115,564 B | 23.3% |
| **Execuções de Ferramentas** | `103.4k` | 330,958 B | 69.0% |
| **Respostas & Thinking** | `9.6k` | 33,695 B | 6.4% |
| **Mensagens do Usuário** | `1.9k` | 7,699 B | 1.3% |

---

## 3. Top Ferramentas Consumidoras
| `VIEW_FILE` | 58 | 42.8k | 136,841 B |
| `EPHEMERAL_MESSAGE` | 131 | 36.4k | 116,347 B |
| `CODE_ACTION` | 14 | 10.4k | 33,243 B |
| `RUN_COMMAND` | 37 | 10.3k | 32,854 B |
| `GREP_SEARCH` | 10 | 2.6k | 8,395 B |
| `LIST_DIRECTORY` | 2 | 479 | 1,534 B |
| `ERROR_MESSAGE` | 1 | 232 | 744 B |
| `SYSTEM_MESSAGE` | 1 | 178 | 571 B |
| `GENERIC` | 2 | 134 | 429 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **35.3%** do teto (517.4k disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **37.8%** da cota semanal (6.22M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
