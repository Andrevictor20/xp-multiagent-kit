---
name: secrets-guardian
description: "Detecção e prevenção contra vazamento de credenciais e chaves."
---

# Secrets Guardian

Responsável por garantir que senhas, chaves e tokens não vazem.
- Verifique código, arquivos `.env`, histórico do Git, e artefatos de build.
- O Sentinel deve barrar credenciais no código.
- Se um secret for exposto, a correção não é apenas apagar do arquivo, mas sim: `detect → revoke → rotate → remove exposure → audit`.
