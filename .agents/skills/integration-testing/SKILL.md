---
name: integration-testing
description: Boundary integration tests across real databases, queues, and external APIs.
---

# Integration Testing

Respect the Testing Pyramid by verifying real component boundaries without turning every test into a slow E2E test:
- **Unit / Contract:** Pure domain logic, algorithms, and schema contracts.
- **Integration:** Database queries/transactions, cache adapters, message queues, and HTTP/gRPC boundaries.
- **E2E:** Critical user journeys only.

## Guidelines
- Write failing integration tests (**RED**) before modifying DB repositories, migrations, queue consumers, or API endpoints.
- Test against real local/ephemeral database and cache instances (or Testcontainers) rather than mocking SQL/ORM internals.
- Isolate only third-party external network APIs using contract-verified stubs.
