## 1. A Hierarquia dos 4 Tiers de Memória

A memória do projeto é governada em 4 camadas complementares:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. Working Memory (Sessão / Chat Atual - Volátil)           │
│    Arquivos abertos, steps em execução, prompts imediatos   │
├─────────────────────────────────────────────────────────────┤
│ 2. Episodic Memory (Histórico Recente & Archive)            │
│    Log de alterações recentes (Sliding Window) + HISTORY.md │
├─────────────────────────────────────────────────────────────┤
│ 3. Semantic Memory (Conhecimento Permanente / Wiki)         │
│    Arquitetura, modelos de domínio, contratos e ADRs        │
├─────────────────────────────────────────────────────────────┤
│ 4. Procedural Memory (Playbooks, Gotchas & Learned Rules)   │
│    Armadilhas de libs, comandos exatos, rotinas e fixes     │
└─────────────────────────────────────────────────────────────┘
```

1. **Working Memory:** Descartada ou consolidada ao final da tarefa/chat.
2. **Episodic Memory:** O que foi entregue, quando, por quem e com qual teste verificado (`Recent Changes` e `archive/HISTORY.md`).
3. **Semantic Memory:** Fatos técnicos perenes e decisões arquiteturais sintetizadas.
4. **Procedural Memory:** Armadilhas conhecidas (*Gotchas*), quirks de ambiente e comandos comprovados para a IA não repetir erros do passado.

---
