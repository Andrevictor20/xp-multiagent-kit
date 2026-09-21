---
name: dependency-governance
description: "Avaliação de risco, segurança e necessidade de novas dependências."
---

# Dependency Governance

Antes de adicionar uma dependência, avalie o seguinte checklist:
1. Já existe solução no projeto para este problema?
2. A dependência é realmente necessária (evite bibliotecas gigantes para resolver coisas simples)?
3. A biblioteca é madura e ativamente mantida?
4. Possui histórico limpo de vulnerabilidades?
5. Qual a licença e peso no tamanho final (bundle/container)?
6. Possui risco na cadeia de suprimentos (dependency confusion, scripts maliciosos de instalação)?
