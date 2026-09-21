---
name: supply-chain-security
description: "Auditoria de segurança de dependências e integridade da cadeia (SCA)."
---

# Supply Chain Security

Antes de incorporar componentes externos:
- Instalações (NPM, Pip) devem ter lockfiles para prevenir poisoning.
- Avalie licenças e procedência de pacotes novos.
- Avalie o risco de dependency confusion e typosquatting.
- Prefira soluções nativas ou bibliotecas já presentes e auditadas no projeto.
