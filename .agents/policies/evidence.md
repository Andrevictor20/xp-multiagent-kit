# Evidence Policy

- Afirmações puramente verbais ("Testes passaram") NÃO SÃO ACEITAS para declarar aprovação em testes ou release.
- **Native Execution Evidence:** Uma execução somente pode ser considerada realizada quando o agente efetivamente executou o comando apropriado do projeto (ex: `npm test`, `pytest`, `cargo test`). O agente deve descobrir dinamicamente a toolchain. O comando real utilizado deve ser registrado na evidência.
- **Fake Evidence:** O agente NUNCA deve fabricar evidências, forjar `exit_code: 0`, ou declarar GREEN sem a execução real correspondente. Qualquer tentativa resulta imediatamente em BLOCK.
- É exigido um nível de evidência L0 a L4 proporcional ao risco da mudança:
  - **Level 0 (CLAIM)**: Apenas afirmação textual. NÃO é suficiente para declarar teste PASS.
  - **Level 1 (OBSERVED OUTPUT)**: Comando real executado + saída observada. Pode ser usado para feedback local.
  - **Level 2 (REPRODUCIBLE TEST)**: Comando real + resultado + contexto suficiente para reprodução.
  - **Level 3 (CI VERIFIED)**: Resultado confirmado por CI externo.
  - **Level 4 (RELEASE AUTHORIZED)**: Resultado confirmado por CI + controles de branch/review/release apropriados.
- **Local vs Release Authority:** Execução local != autoridade de release. A execução local nunca deve ser tratada como prova de autorização de release, a menos que o projeto se classifique como Trivial/Small sem CI.
- Se o projeto não possuir testes, o agente DEVE declarar explicitamente "No automated test command discovered" e NUNCA fingir que passaram testes inexistentes.

---

## Evidência de Conformidade (ATDD/BDD)

Para entregas L2 (Feature) e L3 (Critical), além da evidência de execução de testes, é obrigatório incluir o **Conformance Report** gerado pelo `conformance-tracker`:

- **Conteúdo obrigatório:** Matriz de rastreabilidade Acceptance Criteria → teste correspondente → status (GREEN/RED).
- **Formato:** Tabela com colunas `#`, `Acceptance Criteria`, `Test File`, `Test Name`, `Status`.
- **Resumo:** Total de critérios, total cobertos, total aprovados (ex: "4/4 critérios cobertos e aprovados").
- **Bloqueio:** Entregas com critérios sem teste correspondente ou com teste RED são bloqueadas independentemente de outros testes passarem.
- **Evidência real:** O status GREEN no Conformance Report deve ser comprovado por execução nativa (evidence level ≥ L1). Conformance baseado em afirmação verbal é rejeitado.

Referência: skill `conformance-tracker`, policy `atdd-bdd-tdd.md`.

---

## Ferramentas CLI de Evidência

- **`agy-evidence run <cmd>`:** Executa o comando, grava o log completo em `.agents/runtime/evidence/` e emite resumo estruturado (comando, exit code, N passed/failed, hash) no `walkthrough.md` — sem colar output bruto.
- **`agy-evidence render <evidence-dir>`:** Gera a tabela de evidência formatada a partir dos logs gravados.
- **`agy-conformance --spec <SPEC.md> --tests <dir>`:** Deriva a matriz Acceptance Criteria → teste → status. Exit 1 se NON-COMPLIANT.
