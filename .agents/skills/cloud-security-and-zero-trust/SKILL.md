---
name: cloud-security-and-zero-trust
description: Zero Trust cloud security, federated OIDC CI/CD, Cosign signing, and mTLS.
---

# Cloud Security, Zero Trust & OIDC CD Pipelines

Eliminate long-lived static cloud credentials, enforce cryptographic container provenance, and apply **Zero Trust** across cloud perimeters.

## 1. Keyless CI/CD via Federated OIDC
> **Golden Rule:** NEVER store static cloud keys (`AWS_SECRET_ACCESS_KEY`, GCP service account JSONs) in CI/CD secrets.

1. CI runner requests a short-lived signed OIDC JWT.
2. Cloud provider (AWS/GCP/Azure) validates the OIDC token and issues temporary role credentials scoped to the repository and branch.
3. Credentials expire automatically when the job finishes.

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - name: Configure AWS Credentials via OIDC
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-actions-deploy-role
      aws-region: us-east-1
```

## 2. Supply Chain Integrity (Cosign & SBOM)
1. **Keyless Image Signing (Sigstore Cosign):**
   ```bash
   cosign sign --yes $IMAGE_URI
   ```
2. **SBOM Generation & Attestation (Syft):**
   ```bash
   syft $IMAGE_URI -o spdx-json > sbom.json
   cosign attach sbom --sbom sbom.json $IMAGE_URI
   ```
3. **Cluster Admission Control (Kyverno / OPA Gatekeeper):** Reject any pod whose image lacks a valid CI-issued Cosign signature.

## 3. Zero Trust Defense in Depth
1. **Mutual TLS (mTLS):** Encrypt and mutually authenticate all service-to-service traffic (Istio, Linkerd, or native mTLS).
2. **WAF & Rate Limiting:** Enforce OWASP Top 10 filtering and per-IP/per-JWT rate limits on sensitive endpoints.
3. **SSRF & Metadata Protection:** Block container access to cloud metadata (`169.254.169.254`) via NetworkPolicies/iptables and validate all outbound URLs.
4. **Egress Isolation:** Deny arbitrary outbound internet traffic from workloads by default; allowlist required external hosts only.
