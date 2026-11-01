# REMOVED.md — Ledger de Poda e Depreciação por Evidência (AC-12 / B18)

Este documento registra os módulos, shims e ferramentas podados do diretório `scripts/` do XP Multi-Agent Kit v4, movidos para `contrib/` ou absorvidos por novos componentes com base em auditoria de evidência.

## 1. Módulos e Shims Movidos para `contrib/`

| Componente | Destino | Justificativa | Substituição Canônica |
|---|---|---|---|
| `agy-daemon` / `agy_daemon.py` | `contrib/scripts/` | Daemon local em background de telemetria desnecessário no Thin Harness v4. Telemetria é local, direta e sob demanda. | `scripts/kit_events.py` |
| `agy-dashboard` / `agy_dashboard.py` | `contrib/scripts/` | Servidor web legilativo/dashboard obsoleto. Métricas de governança são reportadas via CLI determinístico. | `xp gate --receipt` / `xp kit doctor` |
| `skill_packer.py` | `contrib/scripts/` | Empacotador para publicação em hubs externos (doc Agensi). Código de release/contribuição isolado do core. | `contrib/scripts/skill_packer.py` |
| `sanitize-tool-output.sh` | `contrib/scripts/` | Wrapper bash redundante; substituído pelo hook nativo `tool-size-guard.py` e registro do gate. | `scripts/hooks/tool-size-guard.py` |
| `session_compactor.py` | `contrib/scripts/` | Compactação dispersa unificada no módulo canônico stdlib `xp_session.py`. | `scripts/xp_session.py` (`xp session compact`) |
| `session_resumer.py` | `contrib/scripts/` | Retomada dispersa de sessão absorvida por `xp_session.py`. | `scripts/xp_session.py` (`xp session resume`) |
| `agy-session-compact` | `contrib/scripts/` | Shim legado redundante com subcomando `xp session compact`. | `xp session compact` |
| `agy-resume` | `contrib/scripts/` | Shim legado redundante com subcomando `xp session resume`. | `xp session resume` |
| `agy-handoff` | `contrib/scripts/` | Wrapper legado de handoff unificado no `xp_session.py`. | `scripts/xp_session.py` (`create_handoff_contract`) |
| `output_noise.py` | `contrib/scripts/` | Lógica de remoção de ruído decorativo fundida diretamente no hook `tool-size-guard.py`. | `scripts/hooks/tool-size-guard.py` |

## 2. Testes Movidos para `contrib/tests/`

Os seguintes testes acompanharam os componentes podados:
- `test_agy_daemon.py`
- `test_agy_dashboard.py`
- `test_skill_packer.py`
- `test_session_compactor.py`
- `test_session_resumer.py`
- `test_agy_handoff.py`
- `test_output_noise.py`

## 3. Código Morto Removido
- `sync_dynamic_skill_profile`: removido de `scripts/hooks/dynamic_effort_hook.py` (B20). O perfil de skills no v4 é governado estaticamente por stack e packs.

## 4. Auditoria de Fusão de Skills de Segurança (P2)
As 14 skills de segurança legadas (14.234 B) foram consolidadas nas 3 skills nucleares de segurança do v4 (`security-review`, `cloud-and-iac-security`, `threat-modeling`):
- `security-review`: absorveu regras imperativas de `api-security`, `authentication-security`, `authorization-security`, `availability-security`, `container-security`, `crypto-guardian`, `privacy-review`, `secrets-guardian`, `security-observability`, `security-sentinel-review`, `security-testing` e `supply-chain-security`.
- `cloud-and-iac-security`: absorveu regras de Zero Trust cloud, infraestrutura como código e segurança MCP.
- `threat-modeling`: absorveu modelagem STRIDE, matriz de risco e derivação de testes de segurança.
- **Regras únicas retidas:** Algoritmos de hash (Argon2id/bcrypt), JWT assimétrico RS256/ES256 com validação de claims, RBAC/ABAC multi-tenant (`tenant_id`), schemas estritos (Pydantic/Zod), rate-limiting/timeouts, AES-GCM-256 com IV único, KMS/Secret Manager obrigatório, pre-commit secret scanning, containers distroless/non-root, auditoria de lockfiles (SCA), testes negativos (401/403/404), governança PII/LGPD/GDPR e logging estruturado append-only.
- **Descartes:** Explicações prolixas, tutoriais conceituais genéricos de segurança teórica, matrizes de pontuação duplicadas e payloads de exemplo estáticos que inflam o contexto sem valor de verificação automática.
