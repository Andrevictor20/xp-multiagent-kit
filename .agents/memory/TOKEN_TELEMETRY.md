# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 18:18:57  
> **Sessão:** `126d0b47-8767-4886-b008-31a285cf6b93` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `Medium`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `56.5k` tokens | `1.05M` | **5.39%** | `992.1k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `551.5k` tokens | `500.0k` | **110.30%** | `0` livres | 9 sessões (~110.3k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `4.71M` tokens | `10.00M` | **47.13%** | `5.29M` livres | 37 sessões (~673.3k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `33.0k` | 108,849 B | 58.4% |
| **Execuções de Ferramentas** | `22.4k` | 71,817 B | 39.7% |
| **Respostas & Thinking** | `964` | 3,377 B | 1.7% |
| **Mensagens do Usuário** | `132` | 528 B | 0.2% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 27 | 19.9k | 63,825 B |
| `EPHEMERAL_MESSAGE` | 27 | 2.5k | 7,992 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **110.3%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **47.1%** da cota semanal (5.29M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
