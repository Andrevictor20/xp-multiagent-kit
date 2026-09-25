# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 18:38:29  
> **Sessão:** `f349289d-bc5a-4336-aa95-7cf4a0899a63` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `Medium`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `77.5k` tokens | `1.05M` | **7.39%** | `971.0k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `602.7k` tokens | `500.0k` | **120.55%** | `0` livres | 10 sessões (~120.5k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `4.76M` tokens | `10.00M` | **47.65%** | `5.24M` livres | 38 sessões (~680.7k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `33.5k` | 110,441 B | 43.2% |
| **Execuções de Ferramentas** | `38.7k` | 123,950 B | 50.0% |
| **Respostas & Thinking** | `5.0k` | 17,418 B | 6.4% |
| **Mensagens do Usuário** | `362` | 1,448 B | 0.5% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 49 | 35.0k | 111,857 B |
| `EPHEMERAL_MESSAGE` | 52 | 3.8k | 12,093 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **120.5%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **47.6%** da cota semanal (5.24M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
