---
name: container-security
description: "Hardening de Dockerfiles, imagens seguras, non-root e multi-stage builds."
---

# Container Security

Quando lidar com Dockerfiles e orchestradores, certifique-se de:
- Executar como usuário não-root.
- Imagem base mínima (distroless/alpine).
- Tags/versões pinnadas (não usar `latest`).
- Secrets NUNCA dentro da imagem.
- Sem flags `privileged` desnecessárias ou `host networking` desprotegido.
- Suporte a verificação de vulnerabilidades da imagem e SBOM.
