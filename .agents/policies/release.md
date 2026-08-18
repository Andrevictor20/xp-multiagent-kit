# Release Policy

- O `release-gatekeeper` é o gate final. Valida CI completo, regras estáticas, secrets, e as evidências reais de execução via runtime.
- Apenas commits aprovados prosseguem para o deploy (shipper).
- **Hard Enforcement (Release Gate Independence):** O Release Gatekeeper é PROIBIDO de aprovar baseando-se apenas em claims verbais ou em JSONs gerados localmente. Ele DEVE executar `bin/xp-verify-evidence` e este script consultará obrigatoriamente o status da Pipeline de CI (GitHub Actions) do commit HEAD atual.
- Qualquer claim de PASS em desenvolvimento local sem push para o repositório resultará em BLOCK obrigatório, pois a autoridade verdadeira é a do CI.
- O Agente Local não possui as chaves de permissão da Pipeline externa, logo não consegue forjar o PASS.
- Deploys críticos exigem estratégias como Feature Flags ou Gradual Rollouts.
- O Rollback deve ser rápido, não apenas uma nota na documentação.
