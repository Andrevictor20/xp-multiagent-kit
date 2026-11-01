# Guia Completo de Publicação & Monetização no Agensi.io

Este guia fornece o passo a passo prático para comercializar as skills e pacotes do **XP Multi-Agent Kit** no marketplace **Agensi.io**, faturando via Stripe Connect ou USDC Solana.

---

## 📦 1. Pacotes Prontos para Publicação (Gerados em `dist/`)

Todos os pacotes foram validados e estruturados seguindo o padrão Agensi Certified:

| Pacote / Slug | Preço Sugerido | Arquivo Gerado | Objetivo |
| :--- | :---: | :--- | :--- |
| **`free-lead-magnets`** | **FREE ($0)** | `dist/agensi-free-lead-magnets-v1.0.0.zip` | Aquisição de usuários, reviews 5 estrelas e autoridade |
| **`clean-code-tdd`** | **$29 USD** | `dist/agensi-clean-code-tdd-v1.0.0.zip` | Anti-test-bypass e eliminação de alucinações de IA |
| **`anti-slop-ui`** | **$35 USD** | `dist/agensi-anti-slop-ui-v1.0.0.zip` | Design systems, WCAG AA e estética Awwwards |
| **`devsecops-stride`** | **$39 USD** | `dist/agensi-devsecops-stride-v1.0.0.zip` | Modelagem STRIDE, segredos e OWASP API Security |
| **`resilient-backend`** | **$49 USD** | `dist/agensi-resilient-backend-v1.0.0.zip` | Alta escala, Outbox pattern, Redis e migrações zero-downtime |

---

## 🛠️ 2. Como Recompilar ou Gerar Novos Pacotes

Para regerar ou empacotar novos bundles via terminal:

```bash
# Listar o catálogo de pacotes comerciais
xp-pack --list

# Validar uma skill individual
xp-pack --validate .agents/skills/sua-skill

# Gerar todos os arquivos .zip comerciais na pasta dist/
xp-pack --bundle free-lead-magnets --out dist
xp-pack --bundle clean-code-tdd --out dist
xp-pack --bundle anti-slop-ui --out dist
xp-pack --bundle devsecops-stride --out dist
xp-pack --bundle resilient-backend --out dist
```

---

## 🌐 3. Passo a Passo de Upload no Agensi.io

1. **Acesso à Conta de Criador:**
   - Acesse [agensi.io](https://agensi.io) e faça login com sua conta (GitHub / Google / Wallet).
   - Navegue até o **Creator Dashboard** / **Submit a Skill**.

2. **Configuração Financeira (Payouts):**
   - Conecte sua conta **Stripe Connect** (para depósitos bancários automáticos em BRL/USD) ou insira seu endereço de carteira **USDC (Solana)** para liquidações instantâneas com taxas mínimas.
   - O repasse padrão é de 70% a 80% do valor de venda líquido.

3. **Submissão do Pacote Gratuito (Primeiro Passo Estratégico):**
   - **Título:** `Clean Code Essentials (Community Edition)`
   - **Preço:** `$0.00`
   - **Upload:** Selecione `dist/agensi-free-lead-magnets-v1.0.0.zip`.
   - **Tags:** `clean-code`, `code-review`, `anti-slop`, `cursor`, `claude-code`, `free`.
   - **Descrição:** Use o conteúdo do arquivo `README.md` gerado automaticamente dentro do zip.
   - *Por que começar pelo gratuito?* Isso acelera a aprovação pela moderação do Agensi e acumula as primeiras avaliações positivas na plataforma.

4. **Submissão dos Pacotes Premium:**
   - Para cada um dos 4 pacotes pagos (`clean-code-tdd`, `anti-slop-ui`, `devsecops-stride`, `resilient-backend`):
     * Faça o upload do respectivo `.zip` da pasta `dist/`.
     * Preencha os valores recomendados ($29, $35, $39, $49).
     * Cole o texto do `README.md` incluído no pacote como descrição do produto.
     * Na seção de suporte, adicione o link para o repositório público do kit no GitHub como referência.

---

## 📈 4. Estratégia de Tração & Conversão (Funil Open-Core)

```
       [ Repositório Aberto no GitHub (SEO & Stars) ]
                         │
                         ▼
          [ Pack Gratuito no Agensi.io (Lead Magnet) ]
         (Usuários instalam `diff-simplifier` e `code-deslop`)
                         │
                         ▼
        [ Oferta no README: "Precisa de TDD & DevSecOps?" ]
                         │
                         ▼
     [ Pacotes Premium: $29 (TDD) / $35 (UI) / $49 (Backend) ]
```

- Cada usuário do seu pacote gratuito recebe instruções no terminal apontando para as extensões de segurança e TDD.
- No seu repositório no GitHub, o banner com os links do Agensi direciona visitantes corporativos e desenvolvedores individuais para compras diretas.
