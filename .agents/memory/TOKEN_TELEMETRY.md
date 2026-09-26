# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🟢 Saudável | **Última Leitura:** 2026-09-25 23:35:02  
> **Sessão:** `cf212f86-5577-4981-b41b-fc76e45cdd24` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `Medium`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `54.0k` tokens | `1.05M` | **5.15%** | `994.6k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `397.3k` tokens | `800.0k` | **49.66%** | `402.7k` livres | 9 sessões (~79.5k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `3.69M` tokens | `10.00M` | **36.88%** | `6.31M` livres | 45 sessões (~526.8k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `34.1k` | 112,528 B | 63.2% |
| **Execuções de Ferramentas** | `18.0k` | 57,566 B | 33.3% |
| **Respostas & Thinking** | `1.6k` | 5,689 B | 3.0% |
| **Mensagens do Usuário** | `245` | 981 B | 0.5% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 40 | 14.9k | 47,836 B |
| `EPHEMERAL_MESSAGE` | 42 | 3.0k | 9,730 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **49.7%** do teto (402.7k disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **36.9%** da cota semanal (6.31M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
