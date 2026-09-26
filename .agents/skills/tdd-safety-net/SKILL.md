---
name: tdd-safety-net
description: "Ciclo RED-GREEN-REFACTOR, matriz multi-camadas e Anti-Test-Bypass estrito."
---

# TDD Safety Net & Anti-Test-Bypass

> **Princípio:** O desenvolvimento é estritamente orientado a testes (Red → Green → Refactor). Um teste só tem valor se tiver a capacidade real de **falhar quando a implementação estiver incorreta** e **comprovar o comportamento esperado**.

---

## 1. Diretrizes Fundamentais do Ciclo TDD

1. **Nunca implemente antes do RED:** Exceto para spikes descartáveis explícitos, nenhuma lógica de negócio é escrita antes do teste que comprova sua necessidade.
2. **Cobertura de Comportamento Real:** Avalie a qualidade dos testes por *behavior coverage*, *critical path coverage* e validação de contratos/limites, nunca por quantidade bruta de linhas de código.
3. **Matriz de Testes Adaptativa:**
   - *Unitário:* Para algoritmos, regras de negócio e funções puras.
   - *Integração:* Para transações de banco, queries SQL, adapters e endpoints HTTP.
   - *Contrato:* Para compatibilidade de schemas e APIs.
   - *Regressão:* Para provar bugs e blindar o sistema contra reincidência.
   - *E2E:* Para fluxos de jornada crítica do usuário.
   - *Propriedade/Fuzzing:* Para testar invariantes matemáticas e limites de entrada.

---

## 2. Protocolo Anti-Test-Bypass (Proibição de Burlar Testes)

Antes de considerar um teste como válido, verifique se ele não comete nenhuma das infrações abaixo:

- [ ] **O teste executa o código real?** (Proibido mocar o próprio código em teste ou mocar em excesso).
- [ ] **O teste contém asserções de valor precisas?** (Proibido testes sem asserções, com `assert(true)` ou que apenas checam tipos em vez de dados).
- [ ] **Nenhum teste foi silenciado com `.skip` ou `xit`?** (Proibido pular testes falhando).
- [ ] **Nenhum teste existente quebrado foi deletado ou comentado?** (Erros devem ser corrigidos na causa raiz do código de produção).
- [ ] **A evidência foi capturada via terminal nativo?** (Proibido forçar aprovação sem execução real da toolchain).

---

## 3. Execução Cirúrgica e Eficiência de Tokens (Targeted & On-Demand)

Para economizar de 5.000 a 20.000 tokens de payload de ferramentas por ciclo, aplique o princípio de execução cirúrgica:

1. **Gatilho Estrito por Necessidade:** Se a alteração for puramente documental (`.md`), configs declarativas, comentários ou estilos cosméticos (Fast-Path L0), a execução de testes de código de produção é **formalmente dispensada**.
2. **Escopo Cirúrgico por Arquivo/Módulo:** Ao modificar um módulo específico, execute **exclusivamente** o arquivo de teste correspondente àquele módulo (ex: `python3 -m unittest tests/test_<modulo>.py` ou `pytest tests/test_<modulo>.py -k test_especifico`). É expressamente proibido rodar a suíte inteira (`discover`, `pytest`, `npm test` geral) para validar refatorações ou correções locais.
3. **Reserva da Suíte Completa:** A execução da suíte abrangente fica restrita ao gate final de release (`L3` / `release-gatekeeper`), alterações transversais no núcleo do framework ou quando expressamente requisitado pelo usuário.
