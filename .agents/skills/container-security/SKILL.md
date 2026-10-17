---
name: container-security
description: Dockerfile hardening, non-root execution, minimal base images, and SBOMs.
---

# Container Security

Harden all Dockerfiles and container workloads before deployment:
- **Non-Root Execution:** Always create and switch to an unprivileged user (`USER 10001:10001`).
- **Minimal Base Images:** Use multi-stage builds with `distroless` or `alpine` runtime images.
- **Pinned Versions:** Pin exact image tags and SHA256 digests; never use `:latest`.
- **Zero Embedded Secrets:** Never copy `.env`, SSH keys, or credentials into image layers or build args.
- **Least-Privilege Runtime:** Ban `--privileged`, host network/PID namespaces, and drop all Linux capabilities (`cap_drop: [ALL]`) with `readOnlyRootFilesystem: true`.
- **Vulnerability Scanning:** Scan built images with Trivy/Grype and attach an SBOM in CI.
