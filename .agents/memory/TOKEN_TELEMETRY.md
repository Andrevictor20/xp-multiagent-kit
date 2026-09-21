# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-21 14:27:21  
> **Sessão:** `c8a98482-56e3-43ae-8554-0f75e1ca453e` | **Modelo:** `gemini-3.8-flash`

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `90.1k` tokens | `1.05M` | **8.60%** | `958.4k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `133.1k` tokens | `500.0k` | **26.61%** | `366.9k` livres | 2 sessões (~26.6k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `8.14M` tokens | `10.00M` | **81.44%** | `1.86M` livres | 10 sessões (~1.16M/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `22.4k` | 85,000 B | 24.8% |
| **Execuções de Ferramentas** | `55.6k` | 211,112 B | 61.6% |
| **Respostas & Thinking** | `10.9k` | 41,456 B | 12.1% |
| **Mensagens do Usuário** | `1.3k` | 4,921 B | 1.4% |

---

## 3. Top Ferramentas Consumidoras
| `RUN_COMMAND` | 78 | 20.8k | 79,066 B |
| `VIEW_FILE` | 25 | 20.1k | 76,554 B |
| `CODE_ACTION` | 34 | 11.0k | 41,798 B |
| `SYSTEM_MESSAGE` | 5 | 2.2k | 8,484 B |
| `GENERIC` | 3 | 1.0k | 3,952 B |
| `ERROR_MESSAGE` | 2 | 331 | 1,258 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **26.6%** do teto (366.9k disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **81.4%** da cota semanal (1.86M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
