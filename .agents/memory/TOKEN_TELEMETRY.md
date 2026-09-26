# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🟢 Saudável | **Última Leitura:** 2026-09-25 23:59:33  
> **Sessão:** `cf212f86-5577-4981-b41b-fc76e45cdd24` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `Medium`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `75.5k` tokens | `1.05M` | **7.20%** | `973.0k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `346.7k` tokens | `800.0k` | **43.34%** | `453.3k` livres | 8 sessões (~69.3k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `3.71M` tokens | `10.00M` | **37.09%** | `6.29M` livres | 45 sessões (~529.9k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `34.1k` | 112,528 B | 45.1% |
| **Execuções de Ferramentas** | `38.2k` | 122,112 B | 50.5% |
| **Respostas & Thinking** | `2.9k` | 10,282 B | 3.9% |
| **Mensagens do Usuário** | `348` | 1,395 B | 0.5% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 75 | 32.4k | 103,552 B |
| `EPHEMERAL_MESSAGE` | 78 | 5.6k | 18,010 B |
| `SYSTEM_MESSAGE` | 1 | 171 | 550 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **43.3%** do teto (453.3k disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **37.1%** da cota semanal (6.29M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
