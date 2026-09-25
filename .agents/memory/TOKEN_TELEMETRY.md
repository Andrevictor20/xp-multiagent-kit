# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 03:10:46  
> **Sessão:** `c815a518-8e14-440b-8956-4c3ea21313be` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `Medium`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `74.9k` tokens | `1.05M` | **7.14%** | `973.7k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `641.5k` tokens | `500.0k` | **128.31%** | `0` livres | 11 sessões (~128.3k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `5.28M` tokens | `10.00M` | **52.76%** | `4.72M` livres | 29 sessões (~753.7k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `32.9k` | 108,552 B | 43.9% |
| **Execuções de Ferramentas** | `34.9k` | 111,712 B | 46.6% |
| **Respostas & Thinking** | `6.7k` | 23,412 B | 8.9% |
| **Mensagens do Usuário** | `397` | 1,591 B | 0.5% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 75 | 34.9k | 111,712 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **128.3%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **52.8%** da cota semanal (4.72M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
