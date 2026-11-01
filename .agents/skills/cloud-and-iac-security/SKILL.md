---
name: cloud-and-iac-security
description: Zero Trust cloud architecture, Infrastructure as Code (IaC) governance, and Model Context Protocol (MCP) server security.
---

# Cloud & IaC Security (`cloud-and-iac-security`)

Consolida as diretrizes de **Segurança em Nuvem**, **Governança de IaC** (Terraform, Kubernetes, Docker) e **Governança de Servidores MCP**.

## 1. Zero Trust & Arquitetura de Nuvem
- **Princípio do Menor Privilégio:** Permissões IAM granulares; nunca conceder `*` ou papéis de Admin irrestritos.
- **Autenticação Federada:** Uso de OIDC em pipelines de CI/CD para deploy em nuvem (GCP Workload Identity, AWS IAM Roles). Proibido exportar JSON service accounts fixas.
- **Isolamento de Redes:** Redes privadas (VPC), sem IPs públicos diretos em bancos ou serviços internos; tráfego encriptado via mTLS.

## 2. Governança de Infraestrutura como Código (IaC)
- **Terraform / OpenTofu:** State remoto criptografado com bloqueio de estado (locking via DynamoDB/GCS).
- **Sem Segredos em Plaintext:** Uso de referências dinâmicas para segredos em arquivos de infraestrutura.
- **Validação de Sintaxe & Políticas:** Checagens estáticas com ferramentas locais determinísticas antes de aplicar mudanças.

## 3. Governança de Servidores MCP (Model Context Protocol)
- **Zero Trust Local:** Servidores MCP locais operam com menor privilégio e timeouts estritos.
- **Higienização de Payloads:** Argumentos passados a ferramentas MCP devem ser sanitizados para prevenir injeção de comandos no shell do host.
- **Proteção de Dados Sensíveis:** Mascaramento de credenciais e logs de ferramentas MCP contendo PII.
