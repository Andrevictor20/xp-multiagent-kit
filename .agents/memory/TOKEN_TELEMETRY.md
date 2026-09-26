# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 22:24:28  
> **Sessão:** `33b26b88-340f-419d-a872-b1296e9c0d85` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `Medium`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `78.6k` tokens | `1.05M` | **7.50%** | `970.0k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `906.6k` tokens | `800.0k` | **113.33%** | `0` livres | 14 sessões (~181.3k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `5.07M` tokens | `10.00M` | **50.74%** | `4.93M` livres | 45 sessões (~724.9k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `33.9k` | 111,830 B | 43.1% |
| **Execuções de Ferramentas** | `39.2k` | 125,396 B | 49.8% |
| **Respostas & Thinking** | `4.8k` | 16,830 B | 6.1% |
| **Mensagens do Usuário** | `741` | 2,964 B | 0.9% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 61 | 34.4k | 110,216 B |
| `EPHEMERAL_MESSAGE` | 66 | 4.7k | 15,180 B |
| `ERROR_MESSAGE` | 8 | 0 | 0 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **113.3%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **50.7%** da cota semanal (4.93M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
