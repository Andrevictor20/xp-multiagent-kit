# The 5 Phases of the Goldfish Protocol

When auditing an architectural specification (L2/L3) or a PRD:

### Phase 1: Initial Zoom Out Review
* **Persona**: `../personas/zoom_out.md`
* **Standard**: `../resources/zoom-out-standard.md` (Heilmeier Catechism)
* **Mandatory Questions**:
  - What are we trying to do? (No jargon)
  - How is it done today and what are the limits of current practice?
  - What is new in this approach and why do we think it will succeed?
  - Who cares? If we succeed, what difference does it make?
  - What are the risks and costs (QPS, memory, tokens, latency)?
  - What are the midterm and final exams to check for success?

### Phase 2: Comprehension & Plain Language Review
* **Persona**: `../personas/comprehension.md`
* **Criterion**: Can the text be understood without ambiguity by an engineer who just joined the team? Are there promotional buzzwords (*seamless, robust, blazingly fast*)? Are technical mechanisms explained objectively?

### Phase 3: Hostile Design Critique
* **Persona**: `../personas/design_critic.md`
* **Focus**:
  - Scalability bottlenecks and single points of failure (SPOF).
  - Resource footprint: peak QPS, storage consumption, and LLM/token budgets.
  - Concurrency inconsistencies, idempotency, and transactional failure handling.

### Phase 4: Intermediate Alignment & Remediation
* The root agent consolidates findings into `[Blocker]`, `[Major]`, and `[Nit]`.
* Fixes gaps in the specification before submitting to Human Gate.

### Phase 5: Implementation Readiness
* **Persona**: `../personas/implementation_readiness.md`
* **Standard**: `../resources/implementation-readiness-standard.md`
* **Criterion**: Does the development team have everything needed to code without guessing behavior? Are acceptance criteria and edge cases 100% bounded?
