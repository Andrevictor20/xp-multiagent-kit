---
name: ci-auto-heal
description: Monitoramento autônomo de CI/CD e autocorreção de falhas (máx 3 tentativas).
---

# CI/CD Auto-Heal & Self-Correction Skill

Esta skill governa a autonomia do Antigravity para monitorar esteiras remotas (GitHub Actions) e locais, diagnosticar quebras e aplicar autocorreção na causa raiz sem exigir que o desenvolvedor aponte o erro manualmente.

---

## 1. Gatilhos de Ativação
- Após `git push` ou acionamento de release / deploy.
- Falha reportada pelo comando `agy-ci-heal --status` ou `gh run list`.
- Invocação via workflows de `/release`, `/incident` ou `/bugfix`.

---

## 2. Protocolo Operacional em 5 Etapas

### Etapa 1: Diagnóstico Cirúrgico da Falha
1. Obtenha o log isolado da falha através do utilitário:
   ```bash
   agy-ci-heal --diagnose-run <run-id>
   ```
2. Analise o bloco extraído sem carregar logs inteiros no contexto da conversa (economia de tokens).

### Etapa 2: Investigação de Causa Raiz (4 Fases)
1. **Fase 1 (Compreensão):** Identifique o arquivo, linha, dependência ou variável de ambiente responsável.
2. **Fase 2 (Isolamento):** Verifique se o erro é transiente (timeout de rede/serviço) ou determinístico (teste quebrado, tipagem, migração, lint).
3. **Fase 3 (Reprodução Local):** Execute o comando de teste ou validação localmente:
   ```bash
   npm test
   # ou pytest -v, cargo test, etc.
   ```
4. **Fase 4 (Correção na Fonte):** Aplique a correção no código de produção ou configuração.
   > [!CAUTION]
   > **Tolerância Zero para Anti-Patterns:** É estritamente proibido silenciar linters (`eslint-disable`), mascarar tipos (`as any`, `@ts-ignore`) ou pular testes (`test.skip`) para forçar o CI a passar.

### Etapa 3: Validação Local Estrita (TDD GREEN)
Execute a suíte localmente para obter evidência nativa de aprovação antes de qualquer envio remoto.

### Etapa 4: Commit Atômico & Re-Disparo
1. Crie commit semântico padronizado:
   ```bash
   git commit -m "fix(ci): <descrição concisa> [run #<run-id>] (auto-heal [iter <N>/3])"
   ```
2. Re-envie as alterações:
   ```bash
   git push origin <branch>
   ```

### Etapa 5: Salvaguarda da Regra dos 3 Fixes (`[L-003]`)
- O loop é limitado a **no máximo 3 iterações consecutivas**.
- Se na 3ª tentativa a esteira continuar falhando, o agente deve **parar imediatamente**, registrar o log do diagnóstico e solicitar intervenção humana, prevenindo loops infinitos e desperdício de minutos de runner e tokens.
