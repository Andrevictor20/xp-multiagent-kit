# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 02:51:06  
> **Sessão:** `bbef55d5-96e4-4170-9bda-ab872c43b48f` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `High`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `232.0k` tokens | `1.05M` | **22.13%** | `816.5k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `631.3k` tokens | `500.0k` | **126.27%** | `0` livres | 11 sessões (~126.3k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `5.23M` tokens | `10.00M` | **52.33%** | `4.77M` livres | 28 sessões (~747.6k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `32.8k` | 108,292 B | 14.1% |
| **Execuções de Ferramentas** | `173.7k` | 555,823 B | 74.9% |
| **Respostas & Thinking** | `23.8k` | 83,462 B | 10.3% |
| **Mensagens do Usuário** | `1.7k` | 6,685 B | 0.7% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 309 | 173.7k | 555,823 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **126.3%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **52.3%** da cota semanal (4.77M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
