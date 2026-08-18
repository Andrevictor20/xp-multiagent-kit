# Phase 11.2 Audit Report - CORE DECOUPLING & NATIVE TOOLCHAIN ENFORCEMENT

## 1. Changes Made
- Transição completa de evidências rígidas (`execution_id` gerado por scripts locais do runtime) para o modelo de **Native Execution Evidence**.
- Definição de níveis de evidência de teste locais (L0 a L2) e de autoridade remota (L3, L4).
- Substituição da obrigatoriedade do `bin/xp-verify-evidence` pela separação em **LOCAL RELEASE CHECK** e **EXTERNAL RELEASE CHECK**.
- Instrução explícita aos agentes (Builder, Test Guardian e Release Gatekeeper) para descobrir e invocar a toolchain nativa (npm, pytest, cargo, etc).
- Limpeza dos históricos JSON legados da pasta de runtime, isolando a engine das antigas interações com a TaskBoard.
- Separação entre execução de CI (GitHub/GitLab/etc) como autoridade externa, tornando a implementação em GitHub Actions opcional e tratável via skills em vez de ser hardcoded no CORE.

## 2. Files Modified
- `.agents/policies/evidence.md`
- `.agents/policies/release.md`
- `.agents/agents/builder/agent.md`
- `.agents/agents/test-guardian/agent.md`
- `.agents/agents/release-gatekeeper/agent.md`
- Deletado: Todos os arquivos `.json` de execuções legadas em `.agents/runtime/evidence/`

## 3. Legacy Dependencies Removed
- `xp-runtime`
- `xp-verify-evidence`
- `TaskBoard`
- `Trusted Release Validation`

## 4. Evidence Model
O modelo agora está classificado em:
- **Level 0 (CLAIM):** Apenas afirmação textual. Inválido para PASS.
- **Level 1 (OBSERVED OUTPUT):** Execução local com saída real. Válido para feedback de desenvolvimento.
- **Level 2 (REPRODUCIBLE TEST):** Comando real, resultado gravado e reprodutível.
- **Level 3 (CI VERIFIED):** Execução remota autorizada via CI pipeline.
- **Level 4 (RELEASE AUTHORIZED):** CI + Regras de Release/Deploy aplicadas.
  
## 5. Command Discovery Model
A ferramenta `bin/xp-runtime` não precisa mais existir. O agente agora realiza **Command Discovery**, buscando em arquivos padrão de stack (ex: `package.json`, `pyproject.toml`) as definições para linting, typechecking, testes e build.

## 6. TDD Model
Testes ainda são estritamente obrigatórios. Em vez de rodar um script externo que obrigatoriamente acusa `exit 1` com `execution_id`, o Test Guardian constrói/encontra o teste na própria tecnologia do projeto, executa através do CLI natural da linguagem (produzindo o RED) e envia a requisição ao Builder.

## 7. Release Model
A separação agora abrange:
- **LOCAL**: Permite commits normais avaliando a toolchain do projeto sem barrar por inexistência do script legacy do Gate.
- **EXTERNAL**: Garante que o release final e deploys exijam o carimbo externo da pipeline do CI (Hard Enforcement).

## 8. CI Abstraction
Foram removidas as menções restritivas diretas que bloqueavam a execução caso `GitHub Actions` não fosse encontrada, estabelecendo que o framework lida com **External CI Authority**, independente da engine rodando no backend.

## 9. Security Preservation
A segurança e a impossibilidade de forjar "Fake Evidence" foram preservadas por policy explícita nos agentes. Mentir sobre sucesso ou forjar um `exit_code: 0` localmente ainda é motivo para BLOCK. A autoridade máxima sobre a validade do commit migrou para a auditoria de output e, no cenário de release, ao próprio CI rodando o ambiente sem a interferência do agente.

## 10. Portability Tests
Validado teoricamente e processualmente:
- Um novo projeto (React/Vite ou Python/FastAPI) ao copiar apenas o diretório `.agents/` descobre a estrutura por si só, utiliza seus scripts nativos (como `npm run test` e `pytest`), sem gerar bloqueios artificiais por "missing xp-runtime file".

## 11. Negative Tests
- **Test 1 & 2:** Projetos sem `bin/` ou `.github/` continuam progredindo normalmente via toolchain nativa ou recebendo warnings dependendo do estado do TDD.
- **Test 3 & 4:** Ausência de npm força a busca em pyproject.toml ou Cargo.toml. Sem testes, levanta WARNING/BLOCKED, nunca assumindo um FAKE PASS.
- **Test 5:** Exit code != 0 corretamente falha as evidências nativas.
- **Test 6:** O Agente Gatekeeper continua programado para analisar a prova real e barrar "Testes rodaram ok" sem output nativo.
- **Test 7:** A política de release proíbe claims de aprovação externa se não há comunicação com um CI vivo.

## 12. Before/After SHA
- **Before:** `f45709247aa0c0746f77be28bf7d8bd004becfa40d704172930e174f91789328`
- **After:** `696e5472af35cea28b39050e0749033217bd31545a9de48d82e7be64329bc9d7`

## 13. Remaining Risks
Como as execuções agora exigem menos acoplamento e são baseadas no sistema nativo, há maior suscetibilidade de o agente enganar a si próprio caso o log não seja processado inteiramente. A abstração de external CI requer que o agente saiba usar GH CLI ou Gitlab API, portanto ele pode falhar em descobrir o status dependendo da disponibilidade da API.

## 14. Final Architecture
O CORE (`.agents/`) não possui dependências estritas externas ao seu próprio repositório e prompts. Ele atua como orquestrador abstrato que demanda que o projeto hospedeiro garanta a execução. O projeto hospedeiro, não o runtime injetado, cuida da ferramenta local. E a entidade CI externa garante a liberação de deploy.

## 15. Final Verdict
🟢 SELF-CONTAINED
