# REMOVED.md — Registro Formal de Testes e Funcionalidades Descontinuadas

Documento exigido pelo AC-13 do SPEC-006 ("Thin Harness"). Toda remoção de funcionalidade obsoleta ou teste substituído por mecanismo determinístico DEVE constar aqui com justificativa técnica.

| Data | Item Removido | Tipo | Motivo Técnico e Substituto |
|---|---|---|---|
| 2026-11-01 | `scripts/kit_constants.COMPLETENESS_OVER_SPEED` | Constante | Removido mandato textual de completude em favor do critério determinístico em código: pronto = ACs rastreados + gate PASS (AC-5). |
| 2026-11-01 | Asserção `self.assertTrue(COMPLETENESS_OVER_SPEED)` em `tests/test_egm_completeness_engine.py` | Teste | Substituído por validação de orçamento base <= 8.000 B e veredito do `xp gate` (AC-5, AC-13). |
| 2026-11-01 | `.agents/memory/REPO_MAP.md` | Arquivo | Removido mapa commitado desatualizado em favor de geração dinâmica em runtime sob demanda (AC-5). |
| 2026-11-01 | 11 Workflows em Prosa (`.agents/workflows/*.md`) | Arquivos | Substituídos pelo grafo determinístico `.agents/workflow.yaml` (≤150 linhas) e executor `scripts/xp_flow.py` (AC-7). |
| 2026-11-01 | Asserção de `feature.md` em `tests/test_spec_003_v3.py` | Teste | Atualizado para validar `.agents/workflow.yaml` diretamente após migração para YAML (AC-7, AC-13). |
| 2026-11-01 | 5 Agentes Absorvidos (`archivist`, `genesis`, `navigator`, `test-guardian`, `refactor-warden`/`release-gatekeeper`) | Agentes | Reduzidos para 6 nucleares (`orchestrator`, `builder`, `reviewer`, `sentinel`, `designer`, `shipper`) conforme AC-8. |
| 2026-11-01 | 9 Personas EGM legadas em `goldfish-spec-review/personas/` | Personas | Substituídas por 2 personas especializadas (`spec_reviewer` e `code_reviewer` <= 2 KB) conforme AC-9. |
