# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 19:35:59  
> **Sessão:** `09972d4b-d3ba-4651-b7e2-566595836818` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `Medium`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `133.2k` tokens | `1.05M` | **12.71%** | `915.3k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `804.9k` tokens | `800.0k` | **100.61%** | `0` livres | 12 sessões (~161.0k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `4.97M` tokens | `10.00M` | **49.67%** | `5.03M` livres | 40 sessões (~709.5k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `33.7k` | 111,182 B | 25.3% |
| **Execuções de Ferramentas** | `89.9k` | 287,770 B | 67.5% |
| **Respostas & Thinking** | `8.9k` | 31,119 B | 6.7% |
| **Mensagens do Usuário** | `734` | 2,938 B | 0.6% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 120 | 78.2k | 250,080 B |
| `EPHEMERAL_MESSAGE` | 127 | 11.8k | 37,690 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **100.6%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **49.7%** da cota semanal (5.03M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
