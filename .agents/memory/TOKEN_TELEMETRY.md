# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 18:42:40  
> **Sessão:** `f349289d-bc5a-4336-aa95-7cf4a0899a63` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `Medium`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `101.3k` tokens | `1.05M` | **9.66%** | `947.2k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `626.3k` tokens | `500.0k` | **125.27%** | `0` livres | 10 sessões (~125.3k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `4.79M` tokens | `10.00M` | **47.88%** | `5.21M` livres | 38 sessões (~684.0k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `33.7k` | 111,114 B | 33.2% |
| **Execuções de Ferramentas** | `60.4k` | 193,382 B | 59.6% |
| **Respostas & Thinking** | `6.8k` | 23,714 B | 6.7% |
| **Mensagens do Usuário** | `467` | 1,870 B | 0.5% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 75 | 54.2k | 173,303 B |
| `EPHEMERAL_MESSAGE` | 79 | 6.3k | 20,079 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **125.3%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **47.9%** da cota semanal (5.21M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
