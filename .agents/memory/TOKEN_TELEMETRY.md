# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** 🔴 Crítico (>80%) | **Última Leitura:** 2026-09-25 21:18:23  
> **Sessão:** `33b26b88-340f-419d-a872-b1296e9c0d85` | **Modelo Utilizado:** `Claude Sonnet 4.6` (`claude-sonnet-4-6`) | **Effort:** `Thinking`  
> **Limites do Modelo:** Janela de Contexto: `200.0k` (`200,000` tokens) | Saída Máxima: `8.2k` (`8,192` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `36.4k` tokens | `200.0k` | **18.21%** | `163.6k` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `870.5k` tokens | `800.0k` | **108.81%** | `0` livres | 17 sessões (~174.1k/h) |
| **3. Janela Semanal (7 Dias Quota)** | `5.03M` tokens | `10.00M` | **50.32%** | `4.97M` livres | 45 sessões (~718.9k/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `33.9k` | 111,744 B | 93.0% |
| **Execuções de Ferramentas** | `1.9k` | 6,187 B | 5.3% |
| **Respostas & Thinking** | `428` | 1,501 B | 1.2% |
| **Mensagens do Usuário** | `194` | 776 B | 0.5% |

---

## 3. Top Ferramentas Consumidoras
| `GENERIC` | 4 | 1.6k | 5,267 B |
| `EPHEMERAL_MESSAGE` | 4 | 287 | 920 B |

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **108.8%** do teto (0 disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **50.3%** da cota semanal (4.97M disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
