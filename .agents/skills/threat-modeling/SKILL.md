---
name: threat-modeling
description: STRIDE threat modeling, trust boundaries, and security test derivation for L3.
---

# Threat Modeling (STRIDE)

Before implementing L3/high-risk features (auth, payments, PII, multi-tenant boundaries, IaC, external webhooks), perform a structured Threat Model:
1. **Decompose System:** Identify critical **Assets**, **Actors/Principals**, **Trust Boundaries**, **Data Flows**, and **Entry Points / Attack Surface**.
2. **Apply STRIDE Per Boundary:**
   - **S**poofing (identity forgery)
   - **T**ampering (unauthorized payload/state modification)
   - **R**epudiation (missing audit trail)
   - **I**nformation Disclosure (PII/secret leak, IDOR)
   - **D**enial of Service (rate/resource exhaustion)
   - **E**levation of Privilege (RBAC/BOLA bypass)
3. **Derive Security Tests (RED):** Every mitigated threat must map to an automated security test implemented by `test-guardian` before `builder` writes production code.
