# Apêndice — Regras de Segurança Descartadas

Este apêndice registra regras de segurança que foram avaliadas e **descartadas** para o escopo atual da skill `security-review`, com a justificativa de cada descarte.

## R1 — Obrigatoriedade de mTLS em todos os serviços internos
**Status:** Descartada.
**Justificativa:** Impor mTLS em todo o malha interna elevaria a complexidade operacional além do orçamento de turnos L0/L1. Mantida como recomendação opcional para serviços de alto risco (pagamentos, dados sensíveis), não como regra obrigatória da skill.

## R2 — Banimento total de JWT simétrico (HS256)
**Status:** Descartada como regra rígida.
**Justificativa:** Sistemas legados de terceiros ainda utilizam HS256 por limitações de integração. A skill exige validação de `exp`/`iss`/`aud` e rotação de chaves; o banimento de HS256 fica como critério de risco elevado (L2/L3), não como regra universal.

## R3 — Exigência de HSM para todas as chaves criptográficas
**Status:** Descartada.
**Justificativa:** HSM não está disponível em ambientes de desenvolvimento e homologação do kit. A skill exige AES-GCM-256/ChaCha20-Poly1305 com IV/nonce único e gestão via KMS/Secret Manager; HSM fica como recomendação para produção crítica.

## R4 — Bloqueio automático de dependências com qualquer vulnerabilidade CVSS > 0
**Status:** Descartada.
**Justificativa:** Geraria falsos positivos excessivos e travaria builds em dependências indiretas não corrigíveis. A skill adota auditoria com `pip audit`/`npm audit`, bloqueio apenas em vulnerabilidades críticas diretas e verificação de integridade de lockfile contra typosquatting.

## R5 — Criptografia de campos PII em nível de aplicação com rotação semanal
**Status:** Descartada.
**Justificativa:** Sobrecarga de performance e complexidade de gerenciamento de chaves desproporcional ao risco. A skill adota anonimização/pseudonimização de PII, proibição de PII em logs, schedules de retenção com TTL e direito ao esquecimento.
