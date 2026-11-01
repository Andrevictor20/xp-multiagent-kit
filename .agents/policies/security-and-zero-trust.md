# Security & Zero Trust Policy (SSDLC)

## 1. Threat Modeling & Risk Scope
1. **STRIDE Threat Modeling:** Mandatory on all L3 (auth, crypto, billing, migrations, multi-tenant) surfaces before writing implementation code.
2. **Trust Boundaries:** Identify explicit trust boundaries, authenticate all crossing requests, and enforce strict input/payload schema validation.

## 2. Access Control & Authorization
1. **BOLA / IDOR Defense:** Enforce object-level authorization on all resource lookups. Never trust client-supplied tenant/user IDs without server-side verification.
2. **Least Privilege & Tenant Isolation:** Isolate multi-tenant data at query and database level. Ensure default-deny access controls.

## 3. Secrets & Hardening
1. **Zero Hardcoded Secrets:** Ban credentials, API tokens, and private keys in code, git commits, or client-accessible assets. Use environment variables or secret vaults.
2. **Container & Environment Hardening:** Execute container workloads as non-root users. Minimize base images and track dependencies for known vulnerabilities.
