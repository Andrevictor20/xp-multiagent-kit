# Evidence Policy

- Afirmações puramente verbais ("Testes passaram") NÃO SÃO ACEITAS em fases de TDD ou CI/CD.
- **Runtime Enforcement:** Toda evidência de execução válida deve vir do `bin/xp-runtime` e possuir um `execution_id`. O agente é PROIBIDO de declarar `GREEN`, `RED` ou um `exit_code` real sem fornecer o respectivo `execution_id` gerado pelo runtime.
- **Claim vs Verified:** Há uma separação estrita entre CLAIM (o que o agente declara que aconteceu) e VERIFIED EVIDENCE (o que o runtime provou). O release gate confia EXCLUSIVAMENTE na Verified Evidence.
- **Fake Evidence:** Qualquer tentativa de apresentar `Fake GREEN`, `Fake RED`, `Fake exit_code` ou `Fake execution_id` resulta imediatamente em BLOCK.
- É exigido um nível de evidência L0 a L4 proporcional ao risco da mudança.
- A saída do test runner (evidence walkthrough) deve ser apresentada claramente no processo de release, através do runtime store.
