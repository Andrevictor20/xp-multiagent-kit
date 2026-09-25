# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 02:14:47  
> **Sessão:** `bbef55d5-96e4-4170-9bda-ab872c43b48f` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `High`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `221.1k` tokens | `1.05M` | **21.09%** | `827.4k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `620.5k` tokens | `500.0k` | **124.09%** | `0` livres | 11 sessões (~124.1k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `5.22M` tokens | `10.00M` | **52.22%** | `4.78M` livres | 28 sessões (~746.0k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `32.8k` | 108,292 B | 14.8% |
| **Execuções de Ferramentas** | `164.3k` | 525,791 B | 74.3% |
| **Respostas & Thinking** | `22.4k` | 78,368 B | 10.1% |
| **Mensagens do Usuário** | `1.6k` | 6,499 B | 0.7% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 292 | 164.3k | 525,791 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **124.1%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **52.2%** da cota semanal (4.78M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
