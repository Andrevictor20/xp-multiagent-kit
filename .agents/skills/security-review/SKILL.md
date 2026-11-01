---
name: security-review
description: Comprehensive application security review covering AuthN/AuthZ, OWASP API, container hardening, crypto, secrets, and SAST/DAST testing.
---

# Security Review (`security-review`)

Consolida a governança de segurança aplicacional: **AuthN/AuthZ**, **OWASP API**, **Crypto**, **Secrets**, **Containers** e **Testes Negativos**.

## 1. Autenticação (AuthN) & Autorização (AuthZ)
- **Senhas & Hashing:** Argon2id ou bcrypt com custo calibrado. Ban em MD5/SHA1 para credenciais.
- **Tokens & Sessões:** JWT assimétrico (RS256/ES256) com validação de `exp`, `iss`, `aud` e rotação de chaves.
- **Autorização:** RBAC/ABAC em nível de endpoint e linha (prevenção rigorosa de IDOR/BOLA). Isolamento multi-tenant por tenant_id validado no token.

## 2. OWASP API Security & Resiliência
- **Rate Limiting:** Proteção contra força bruta em rotas sensíveis (`/login`, `/reset-password`).
- **Validação de Entrada:** Schemas estritos (Pydantic, Zod) rejeitando propriedades adicionais e injeções.
- **Timeouts & DoS:** Definição explícita de timeouts em todas as chamadas HTTP/RPC externas e queries de banco.

## 3. Criptografia & Segredos
- **Criptografia em Repouso:** AES-GCM-256 ou ChaCha20-Poly1305 com IV/Nonce exclusivo por operação.
- **Secrets Governance:** Nunca versionar segredos, tokens ou senhas em código, commits ou `.env`. Uso obrigatório de KMS ou Secret Manager.
- **Detecção de Segredos:** Scanner em pré-commit para bloquear patterns de chaves de API, AWS, Stripe, etc.

## 4. Hardening de Contêineres & Supply Chain (SCA)
- Imagens base mínimas (Distroless ou Alpine) e execução obrigatória com usuário não-root.
- Auditoria de dependências (`pip audit`, `npm audit`) e integridade de lockfiles contra typosquatting.

## 5. Testes Negativos de Segurança (SAST/DAST)
- Toda rota autenticada deve possuir testes unitários e de integração validando:
  - Token ausente -> HTTP 401.
  - Token expirado ou assinatura inválida -> HTTP 401.
  - Tentativa de acesso a recurso de outro usuário/tenant -> HTTP 403 / 404.
