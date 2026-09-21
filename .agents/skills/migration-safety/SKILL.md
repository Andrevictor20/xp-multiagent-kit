---
name: migration-safety
description: "Migrações de banco de dados expand-and-contract seguras e sem downtime."
---

# Migration Safety

Não considere "migration executou" como sinônimo de "migration é segura". Toda migration relevante deve considerar:
- O novo schema deve ser compatível com a aplicação antiga (durante o deploy contínuo).
- **Nunca faça:** `NOT NULL` em tabela populada sem default, rename destrutivo, drop de coluna direto, lock prolongado de tabela, ou backfills pesados na mesma migration.
- Se for uma mudança de alto risco (ex: dividir tabela), use um padrão *expand and contract*.
- Toda migration deve possuir um plano de rollback ou verificação prévia de que é irreversível (e o que fazer a respeito).
