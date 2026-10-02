---
name: diff-simplifier-review
description: Revisão minimalista de diff e remoção de over-engineering.
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

## 3. Gramática Cirúrgica de Findings (1 Linha por Item)

Ao emitir o parecer de simplificação, reporte cada apontamento estritamente em uma única linha:
`L<linha>: <tag> <o que cortar>. <o que substitui>.`  
*(ou `<arquivo>:L<linha>: <tag> ...` para diffs multi-arquivos).*

### Tags Padronizadas:
- `delete:` código morto, flexibilidade não utilizada ou feature especulativa. Substituto: nada.
- `stdlib:` reimplementação artesanal que a Standard Library já fornece. Nomeie a função nativa.
- `native:` dependência externa fazendo o que a plataforma/HTML5/CSS3 já cobre. Consulte `platform-native.md`.
- `yagni:` abstração com implementação única, config que ninguém altera, camada com um único chamador.
- `shrink:` mesma lógica, menos linhas. Mostre a forma reduzida.

### Saldo Final de Revisão:
Toda revisão de simplificação deve terminar com o saldo líquido de corte:
`net: -<N> lines, -<M> deps possible.`  
Se o diff já estiver ótimo e minimalista: `Lean already. Ship.`

---

## 4. Protocolo de Ação do Refactor-Warden
```bash
# Inspecione o diff compacto
git diff --stat
git diff

# Remova arquivos e alterações não intencionais
git checkout -- <arquivo-acidental>
```
Após o simplificador validar o diff e aplicar o corte, o Handoff Packet é emitido para o `release-gatekeeper`.

