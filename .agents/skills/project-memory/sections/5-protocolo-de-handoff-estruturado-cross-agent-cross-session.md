## 5. Protocolo de Handoff Estruturado (Cross-Agent & Cross-Session)

Ao encerrar um chat ou alternar entre agentes especializados, o agente `archivist` compila um pacote de handoff estruturado:

```markdown
### 🔄 Handoff Packet
- **From Agent / Session:** `[ex: designer / chat-123]`
- **To Agent / Next Session:** `[ex: builder / próximo chat]`
- **Summary:** Resumo conciso de 1-2 frases do que foi alcançado.
- **Files Touched:** Lista exata de arquivos modificados (`path/to/file.ts`).
- **Open Questions & Blockers:** Dúvidas de produto ou dependências não resolvidas.
- **Next Steps:** Próximos passos imediatos e ordenados para quem assumir.
- **Verification Evidence:** Comando de teste nativo e status comprovado (`PASS (exit_code: 0)`).
```

---
