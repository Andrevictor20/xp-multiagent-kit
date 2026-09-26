# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 21:54:05  
> **Sessão:** `33b26b88-340f-419d-a872-b1296e9c0d85` | **Modelo Utilizado:** `Gemini 3.8 Flash` (`gemini-3.8-flash`) | **Effort:** `Medium`  
> **Limites do Modelo:** Janela de Contexto: `1.05M` (`1,048,576` tokens) | Saída Máxima: `65.5k` (`65,536` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `62.9k` tokens | `1.05M` | **6.00%** | `985.6k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `891.7k` tokens | `800.0k` | **111.47%** | `0` livres | 15 sessões (~178.3k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `5.06M` tokens | `10.00M` | **50.59%** | `4.94M` livres | 45 sessões (~722.7k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `33.9k` | 111,830 B | 53.8% |
| **Execuções de Ferramentas** | `25.8k` | 82,545 B | 41.0% |
| **Respostas & Thinking** | `2.8k` | 9,805 B | 4.5% |
| **Mensagens do Usuário** | `450` | 1,803 B | 0.7% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 39 | 22.8k | 72,885 B |
| `EPHEMERAL_MESSAGE` | 42 | 3.0k | 9,660 B |
| `ERROR_MESSAGE` | 8 | 0 | 0 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **111.5%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **50.6%** da cota semanal (4.94M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
