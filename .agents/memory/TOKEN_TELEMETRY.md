# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-24 23:10:17  
> **Sessão:** `63c1cb70-c1c8-46ea-968a-819e714f430e` | **Modelo:** `gemini-3.8-flash`

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `57.4k` tokens | `1.05M` | **5.47%** | `991.2k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `714.2k` tokens | `500.0k` | **142.85%** | `0` livres | 9 sessões (~142.8k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `4.70M` tokens | `10.00M` | **46.97%** | `5.30M` livres | 21 sessões (~671.0k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `32.4k` | 106,851 B | 56.4% |
| **Execuções de Ferramentas** | `17.3k` | 55,322 B | 30.1% |
| **Respostas & Thinking** | `5.9k` | 20,613 B | 10.3% |
| **Mensagens do Usuário** | `1.8k` | 7,238 B | 3.2% |

---

## 3. Top Ferramentas Consumidoras
| `VIEW_FILE` | 8 | 8.0k | 25,522 B |
| `SEARCH_WEB` | 4 | 4.9k | 15,560 B |
| `CODE_ACTION` | 3 | 2.3k | 7,205 B |
| `RUN_COMMAND` | 4 | 2.2k | 7,035 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **142.8%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **47.0%** da cota semanal (5.30M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
