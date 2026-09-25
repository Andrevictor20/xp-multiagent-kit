---
name: diff-simplifier-review
description: Revisão cirúrgica de diff orientada a minimalismo, removendo código morto, complexidade acidental e over-engineering antes do commit.
---

# Diff Simplifier Review Skill

Esta skill governa o passo sistemático de **auto-revisão e simplificação de diff** antes da submissão para o `release-gatekeeper`, assegurando que apenas a quantidade estritamente necessária de código seja adicionada ao repositório.

---

## 1. Princípios de Minimalismo & Deslop
1. **Regra do Menos é Mais:** Cada linha de código adicionada é uma linha a ser mantida, testada e depurada no futuro. Se algo puder ser resolvido sem adicionar novas abstrações, elimine-as.
2. **Eliminação de Código Acidental:** Remova logs temporários (`console.log`, `print`, `dbg!`), comentários comentados, arquivos de teste temporários ou importações não utilizadas.
3. **No God Files (<500 Linhas):** Nenhum arquivo tocado pela PR deve ultrapassar o limite estrito de 500 linhas. Se ultrapassar, execute o desmembramento modular imediato.

---

## 2. Checklist Cirúrgico de 5 Passadas no `git diff`
- [ ] **Passada 1 (Necessidade):** Todas as alterações no `git diff` pertencem estritamente ao escopo da tarefa atual?
- [ ] **Passada 2 (Abstrações Prematuras):** Há interfaces ou classes genéricas demais criadas para um único caso de uso? Simplifique.
- [ ] **Passada 3 (Comentários Óbvios):** Remova comentários que apenas repetem o que o código faz (ex: `// incrementa o contador`). Preserve apenas comentários explicando *porquês* não óbvios.
- [ ] **Passada 4 (Tratamento de Erros Limpo):** Erros são tratados na fonte sem mascarar exceções (`except Exception: pass`, `try { ... } catch {}`).
- [ ] **Passada 5 (Estilo e Nomenclatura):** Variáveis e funções têm nomes auto-explicativos, eliminando siglas crípticas.

---

## 3. Protocolo de Ação do Refactor-Warden
```bash
# Inspecione o diff compacto
git diff --stat
git diff

# Remova arquivos e alterações não intencionais
git checkout -- <arquivo-acidental>
```
Após o simplificador validar o diff, o Handoff Packet é emitido para o `release-gatekeeper`.
