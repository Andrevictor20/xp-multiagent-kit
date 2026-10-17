---
name: infrastructure-as-code-governance
description: IaC governance and security for Terraform, OpenTofu, Kubernetes, and Docker.
---

# Infrastructure as Code (IaC) Governance & Security

Ensure all provisioned infrastructure (Terraform, OpenTofu, Kubernetes, Helm, Docker Compose) is declarative, immutable, least-privilege, and statically scanned before `apply`.

## 1. Core IaC Principles
1. **Immutable & Declarative (No ClickOps):** All infrastructure state lives in version-controlled code; forbid manual console mutations.
2. **IAM Least Privilege:** Ban wildcard policies (`AdministratorAccess`, `Action: "*"`, `Resource: "*"`). Scope every workload role to exact actions and ARNs.
3. **Network Isolation:** Place databases, caches, and queues in **private subnets with no public IPs**; enforce default-deny Kubernetes `NetworkPolicies`.

## 2. Technology Guardrails

### 2.A Terraform / OpenTofu
- **Remote State & Locking:** Store state in encrypted remote backends (e.g., S3 with SSE-KMS + DynamoDB lock) and never commit `.tfstate` files.
- **Zero Plaintext Secrets:** Never hardcode credentials in `.tf` or `.tfvars`; inject via Vault, AWS Secrets Manager, or ephemeral OIDC env vars.
- **Pinned Immutable Modules:** Pin module sources to explicit Git tags or commit SHAs (`?ref=v1.2.0`).

### 2.B Kubernetes (Manifests, Helm, Kustomize)
- **Restricted Pod SecurityContext:**
  ```yaml
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    allowPrivilegeEscalation: false
    readOnlyRootFilesystem: true
    capabilities:
      drop: ["ALL"]
  ```
- **Mandatory Resource Quotas:** Define `resources.requests` and `resources.limits` (CPU & memory) on every container.
- **Default-Deny NetworkPolicy:** Enforce ingress/egress `default-deny-all` per namespace and open only required service ports.

## 3. Pre-Apply Static Validation Gate
1. **Format & Syntax:** Run `terraform fmt -check`, `terraform validate`, and `helm lint`.
2. **IaC Security Scan:** Run **Checkov**, **tfsec**, or **Trivy Config** to block `0.0.0.0/0` admin ports, unencrypted storage, and wildcard IAM roles.
3. **Auditable Plan:** Generate and review `terraform plan` resource counts (`to add`, `to change`, `to destroy`) before applying.
