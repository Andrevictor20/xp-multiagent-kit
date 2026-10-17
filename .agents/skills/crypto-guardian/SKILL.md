---
name: crypto-guardian
description: Cryptographic primitive auditing, key management, and ban on weak ciphers.
---

# Crypto Guardian

Block custom, deprecated, or misconfigured cryptography across the codebase:
- **Strictly Forbidden:** Custom crypto/hashing schemes, `MD5` or `SHA-1` for security, `AES-ECB` mode, hardcoded keys/IVs, static nonces, and non-cryptographic RNG (`Math.random()`, `random.randint()`).
- **Mandatory Standards:** Use vetted libraries (`libsodium`, Google `Tink`, WebCrypto, `cryptography.io`), authenticated encryption (`AES-256-GCM`, `ChaCha20-Poly1305`), `Argon2id` for passwords, and OS CSPRNG (`crypto.randomBytes`, `secrets`).
