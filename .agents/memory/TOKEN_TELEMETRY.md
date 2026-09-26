# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 22:46:33  
> **Sessão:** `33b26b88-340f-419d-a872-b1296e9c0d85` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `Medium`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `96.1k` tokens | `1.05M` | **9.16%** | `952.5k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `923.6k` tokens | `800.0k` | **115.45%** | `0` livres | 13 sessões (~184.7k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `3.66M` tokens | `10.00M` | **36.62%** | `6.34M` livres | 44 sessões (~523.1k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `33.9k` | 111,830 B | 35.3% |
| **Execuções de Ferramentas** | `54.5k` | 174,412 B | 56.7% |
| **Respostas & Thinking** | `6.8k` | 23,963 B | 7.1% |
| **Mensagens do Usuário** | `855` | 3,420 B | 0.9% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 83 | 47.0k | 150,482 B |
| `EPHEMERAL_MESSAGE` | 92 | 6.6k | 21,160 B |
| `SYSTEM_MESSAGE` | 1 | 865 | 2,770 B |
| `ERROR_MESSAGE` | 8 | 0 | 0 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **115.5%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **36.6%** da cota semanal (6.34M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
