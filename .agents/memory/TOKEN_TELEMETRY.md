# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 03:18:57  
> **Sessão:** `c815a518-8e14-440b-8956-4c3ea21313be` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `Medium`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `92.1k` tokens | `1.05M` | **8.78%** | `956.5k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `656.8k` tokens | `500.0k` | **131.37%** | `0` livres | 10 sessões (~131.4k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `5.29M` tokens | `10.00M` | **52.93%** | `4.71M` livres | 29 sessões (~756.2k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `32.9k` | 108,552 B | 35.7% |
| **Execuções de Ferramentas** | `48.9k` | 156,483 B | 53.1% |
| **Respostas & Thinking** | `9.7k` | 33,936 B | 10.5% |
| **Mensagens do Usuário** | `589` | 2,358 B | 0.6% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 107 | 48.9k | 156,483 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **131.4%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **52.9%** da cota semanal (4.71M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
