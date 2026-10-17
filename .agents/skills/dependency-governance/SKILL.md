---
name: dependency-governance
description: Third-party dependency risk evaluation, license audit, and bloat prevention.
---

# Dependency Governance

Evaluate every proposed third-party dependency against this 6-point gate before adding it:
1. **Existing Capability:** Does the standard library or an already-installed package solve this?
2. **Proportionality:** Avoid pulling massive libraries for trivial utilities (prefer native platform APIs).
3. **Maintenance Health:** Verify active maintenance, recent releases, and issue responsiveness.
4. **Vulnerability Track Record:** Check CVE history via `npm audit`, `pip-audit`, or OSV database.
5. **License & Footprint:** Confirm permissive/compatible license (MIT, Apache-2.0, BSD) and acceptable bundle/image size impact.
6. **Supply Chain Safety:** Verify exact package name (anti-typosquatting), pin lockfile hashes, and inspect install scripts.
