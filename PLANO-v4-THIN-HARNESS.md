# Plano de Implementação — XP Multi-Agent Kit v4 "Thin Harness"

**Fonte única:** `.agents/specs/SPEC-006-THIN-HARNESS.md`. Este arquivo é só um índice; em caso de divergência, vale o SPEC-006.

- **Risco:** L2. **Branch:** `refactor/thin-harness` (de `v3.9.2-baseline`).
- **Execução:** Regra 0 do SPEC (sem subagentes, uma fase por vez, parar na 2ª falha idêntica).

| Fase | Entrega | ACs |
|---|---|---|
| 0 | Baseline, SPEC-006 (concluída) | — |
| 1 | `xp_contract`, `policy.yaml`, `xp_gate`, `kit_events`, esqueleto `xp`, `components.yaml` | AC-1 a AC-4 |
| 2 | Contexto base ≤8 KB, fonte única (`kit_lint`), CLI `xp` completa | AC-5, AC-6 |
| 3 | `workflow.yaml` + `xp_flow`, congelamento SHA-256, stubs de host | AC-7 |
| 4 | 6 agentes, 24 skills no núcleo, packs | AC-8 |
| 5 | EGM em 3 passes, esforço, hook ≤400 B | AC-9 |
| 6 | `xp evolve` | AC-10 |
| 7 | Poda, README, benchmark, invariantes | AC-11 a AC-13 |

Regra 9: nenhuma prosa sai antes do mecanismo passar nos testes (Seção 12 do SPEC).
