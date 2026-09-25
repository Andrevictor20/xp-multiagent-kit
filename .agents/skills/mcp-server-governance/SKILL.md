---
name: mcp-server-governance
description: Governança, auditoria de segurança e integração do Model Context Protocol (MCP) para conexões externas de agentes.
---

# MCP Server Governance Skill

Esta skill governa a utilização, auditoria de segurança e desenvolvimento de integrações baseadas no **Model Context Protocol (MCP)**, garantindo que conexões entre o agente e servidores externos (bancos de dados, APIs, repositórios de documentação, sistemas de arquivos remotos) sigam a arquitetura Zero Trust.

---

## 1. Vetores de Risco & Política de Segurança MCP
Servidores MCP estendem as capacidades do agente com ferramentas adicionais, mas introduzem riscos críticos:
1. **Tool Shadowing & Prompt Injection:** Servidores MCP não confiáveis podem injetar prompts ocultos nas descrições de ferramentas para sequestrar o contexto.
2. **SSRF (Server-Side Request Forgery):** Ferramentas que aceitam URLs sem sanitização podem ser usadas para escanear redes internas.
3. **Vazamento de Credenciais:** Conexões MCP nunca devem trafegar segredos, tokens ou senhas em texto puro nos argumentos de chamadas.

---

## 2. Checklist de Governança Zero Trust para Servidores MCP
- [ ] **Origem Verificada:** O servidor MCP vem de fonte oficial ou código-fonte auditado localmente.
- [ ] **Isolamento de Credenciais:** Tokens são providos exclusivamente via variáveis de ambiente seguras (`.env` fora de versionamento).
- [ ] **Sanitização de Payloads:** Todas as saídas de ferramentas MCP passam por truncagem/resumo para evitar estourar a janela de contexto.
- [ ] **Princípio do Menor Privilégio (PoLP):** Configurar o servidor MCP com escopo de leitura restrito (ex: acesso a um único bucket ou schema específico do banco).

---

## 3. Scaffold Canônico de Servidor MCP Local (FastMCP / TypeScript)
Ao criar um servidor MCP de suporte para o projeto, utilize o padrão stdio com tipagem estrita:

```typescript
// Exemplo canônico TypeScript com SDK oficial @modelcontextprotocol/sdk
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const server = new Server({ name: "project-local-mcp", version: "1.0.0" }, { capabilities: { tools: {} } });

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "query_project_schema",
      description: "Retorna o schema de banco atualizado sem expor dados de produção.",
      inputSchema: { type: "object", properties: { table_name: { type: "string" } } }
    }
  ]
}));
```
