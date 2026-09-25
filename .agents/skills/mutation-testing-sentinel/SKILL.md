---
name: mutation-testing-sentinel
description: Auditoria matemática da robustez da suíte de testes via injeção controlada de mutações no código de produção.
---

# Mutation Testing Sentinel Skill

Esta skill governa a aplicação de **Testes de Mutação (Mutation Testing)** como a prova matemática definitiva contra testes tautológicos, asserts cegos e falsos positivos no XP Multi-Agent Kit.

---

## 1. Fundamento Teórico & Racional
Passar 100% dos testes não garante que o código está protegido. Se um teste passar mesmo quando mutações deliberadas forem introduzidas na lógica (ex: inverter `>` para `<=`, trocar `true` por `false`, remover chamadas de função), o teste é **fraco ou inútil**.

- **Mutante Sobrevivente (Surviving Mutant):** Falha grave na suíte de testes. Significa que o código pode quebrar sem que nenhum teste acuse o erro.
- **Mutante Morto (Killed Mutant):** O teste falhou imediatamente após a mutação ser injetada. O teste é robusto e eficaz.
- **Score Mínimo Exigido:** No mínimo **80% de Mutation Score** em módulos de risco L2/L3.

---

## 2. Ferramentas por Ecossistema
- **JavaScript / TypeScript:** [Stryker Mutator](https://stryker-mutator.io/) (`npx stryker run`)
- **Python:** [mutmut](https://github.com/boxed/mutmut) (`mutmut run --paths-to-mutate <path>`)
- **Rust:** [cargo-mutants](https://github.com/sourcefrog/cargo-mutants) (`cargo mutants`)
- **Go:** [go-mutesting](https://github.com/zimmski/go-mutesting)

---

## 3. Protocolo de Auditoria do Test-Guardian & Release-Gatekeeper
1. **Identificação de Módulos Críticos:** Módulos de autorização, cálculo financeiro, validação de tokens e regras fiscais.
2. **Execução de Amostragem de Mutação:**
   ```bash
   # Exemplo Python:
   mutmut run --paths-to-mutate src/billing.py
   mutmut results
   ```
3. **Análise de Mutantes Sobreviventes:** Para cada mutante que não foi morto:
   - Identifique a asserção ausente.
   - Escreva o teste específico que captura a mutação.
4. **Veredito:** O `release-gatekeeper` bloqueia releases se mutantes sobreviventes forem detectados na fronteira de segurança ou pagamentos.
