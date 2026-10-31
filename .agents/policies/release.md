# Release Gate & Zero-Downtime Deployment Policy

Require green CI, `COMPLIANT` Conformance Report, zero High/Critical vulnerabilities, atomic commits, and Canary/Blue-Green rollout with automated rollback on RED metric degradation. When CodeRabbit CLI is authenticated and active, zero unaddressed `critical`/`major` findings are required; if unavailable or unauthenticated, release proceeds seamlessly via native local gates without blocking.
