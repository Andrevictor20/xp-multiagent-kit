---
name: api-contracts
description: OpenAPI contract design, versioning, DTO schemas, and error modeling.
---

# API Contracts

Enforce explicit, versioned, and predictable API contracts:
- **Request/Response Schemas:** Define strict DTOs and runtime validation (Zod, Joi, Pydantic, JSON Schema).
- **HTTP Semantics:** Return accurate status codes (`200`, `201`, `204`, `400`, `401`, `403`, `404`, `409`, `422`, `429`, `500`).
- **Standard Error Envelope:** Use consistent error payloads (`code`, `message`, `details`, `correlation_id`).
- **Collection Endpoints:** Support bounded pagination, filtering, sorting, and idempotency keys on mutating requests.
- **Boundary Separation:** Keep domain logic in services/use-cases; controllers only parse, validate, and serialize.
