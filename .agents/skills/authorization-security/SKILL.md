---
name: authorization-security
description: Access control, RBAC/ABAC permissions, tenant isolation, and BOLA/IDOR defense.
---

# Authorization Security

Enforce and test access control at every boundary:
- **Resource Ownership (BOLA / IDOR):** Every endpoint accepting an object ID must verify that the authenticated principal owns or is authorized for that exact resource.
- **RBAC & ABAC:** Evaluate roles and contextual attributes server-side on every request; never trust client-supplied role flags.
- **Function-Level Authorization:** Protect administrative and mutating routes with explicit policy middleware (deny by default).
- **Multi-Tenant Isolation:** Scope all queries and cache keys by authenticated `tenant_id`; write automated cross-tenant negative tests (User A cannot read/mutate Tenant B resources).
