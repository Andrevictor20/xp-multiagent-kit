---
name: mcp-server-governance
description: Zero Trust security, payload sanitization, and governance for MCP servers.
---

# MCP Server Governance

Govern the integration, security auditing, and development of **Model Context Protocol (MCP)** servers under Zero Trust rules.

## 1. MCP Threat Vectors
1. **Tool Shadowing & Prompt Injection:** Untrusted MCP servers can inject hidden instructions inside tool descriptions or returned payloads.
2. **SSRF (Server-Side Request Forgery):** MCP tools accepting unvalidated URLs can scan internal networks or cloud metadata.
3. **Credential Leakage:** Secrets passed in tool arguments leak into conversation transcripts and logs.

## 2. Zero Trust MCP Governance Checklist
- [ ] **Verified Provenance:** Run only official or locally audited MCP server source code.
- [ ] **Credential Isolation:** Inject API keys/tokens strictly via environment variables (never tool call arguments).
- [ ] **Payload Bounding:** Truncate and sanitize MCP tool outputs to prevent context-window flooding and prompt injection.
- [ ] **Least Privilege (PoLP):** Scope database/filesystem MCP servers to read-only or single-schema/directory access.

## 3. Canonical Local MCP Server Scaffold (TypeScript SDK)

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "project-local-mcp", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "query_project_schema",
      description: "Return database schema metadata without exposing production rows.",
      inputSchema: { type: "object", properties: { table_name: { type: "string" } } },
    },
  ],
}));
```
