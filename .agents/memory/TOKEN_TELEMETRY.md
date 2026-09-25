# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 18:12:03  
> **Sessão:** `87ee93fc-47aa-4003-af72-ca9bacfcc847` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `Medium`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `88.1k` tokens | `1.05M` | **8.41%** | `960.4k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `522.7k` tokens | `500.0k` | **104.54%** | `0` livres | 8 sessões (~104.5k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `4.68M` tokens | `10.00M` | **46.85%** | `5.32M` livres | 36 sessões (~669.2k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `33.0k` | 108,849 B | 37.4% |
| **Execuções de Ferramentas** | `48.0k` | 153,671 B | 54.5% |
| **Respostas & Thinking** | `6.1k` | 21,301 B | 6.9% |
| **Mensagens do Usuário** | `1.1k` | 4,212 B | 1.2% |

---

## 3. Top Ferramentas Consumidoras
| `VIEW_FILE` | 29 | 21.6k | 69,255 B |
| `RUN_COMMAND` | 22 | 8.3k | 26,430 B |
| `CODE_ACTION` | 14 | 8.0k | 25,727 B |
| `EPHEMERAL_MESSAGE` | 75 | 6.9k | 22,030 B |
| `SEARCH_WEB` | 2 | 2.6k | 8,232 B |
| `GREP_SEARCH` | 3 | 624 | 1,997 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **104.5%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **46.8%** da cota semanal (5.32M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
