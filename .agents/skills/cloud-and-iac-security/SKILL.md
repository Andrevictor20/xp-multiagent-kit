---
name: cloud-and-iac-security
description: Zero Trust cloud architecture, Infrastructure as Code (IaC) governance, and Model Context Protocol (MCP) server security.
---

# Cloud & IaC Security (`cloud-and-iac-security`)

Consolidates guidelines for **Cloud Security**, **IaC Governance** (Terraform, Kubernetes, Docker), and **MCP Server Governance**.

## 1. Zero Trust & Cloud Architecture
- **Principle of Least Privilege:** Granular IAM permissions; never grant `*` or unrestricted admin roles.
- **Federated Authentication:** Use OIDC in CI/CD pipelines for cloud deployments (GCP Workload Identity, AWS IAM Roles). Exporting fixed JSON service account keys is prohibited.
- **Network Isolation:** Private networks (VPC), no direct public IPs on databases or internal services; traffic encrypted via mTLS.

## 2. Infrastructure as Code (IaC) Governance
- **Terraform / OpenTofu:** Remote encrypted state with state locking (via DynamoDB/GCS).
- **No Plaintext Secrets:** Use dynamic secret references in infrastructure manifests.
- **Syntax & Policy Validation:** Static checks using deterministic local tooling before applying changes.

## 3. MCP (Model Context Protocol) Server Governance
- **Local Zero Trust:** Local MCP servers operate with least privilege and strict timeouts.
- **Payload Sanitization:** Arguments passed to MCP tools must be sanitized to prevent command injection on host shell.
- **Sensitive Data Protection:** Mask credentials and logs from MCP tools containing PII.
