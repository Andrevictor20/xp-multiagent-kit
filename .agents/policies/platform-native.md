# Catálogo de Soluções Nativas da Plataforma (Platform-Native Solutions)

> **Regra de Ouro:** Antes de instalar ou sugerir uma biblioteca externa ou componente artesanal, consulte este catálogo. A plataforma já traz a solução gratuitamente, sem custo de bundle, sem falhas em atualizações e mantida pelos autores do próprio runtime.

---

## 1. Elementos Nativos HTML5

Substitua componentes pesados de interface por controles nativos do browser:

| Você acha que precisa de biblioteca para | O que a plataforma já oferece nativamente | Vantagens |
|---|---|---|
| Date picker (`flatpickr`, `react-datepicker`) | `<input type="date">` | Teclado móvel nativo, acessível, 0 KB de bundle |
| Time picker (`timepicker`) | `<input type="time">` | Validação integrada, formato regional automático |
| Color picker (`react-color`) | `<input type="color">` | Paleta do sistema operacional |
| Range slider (`rc-slider`) | `<input type="range" min="0" max="100">` | Sem scripts, estilizado via CSS accent-color |
| Barra de progresso | `<progress value="70" max="100">` | Semântico para leitores de tela |
| Medidor / Gauge de capacidade | `<meter value="0.7" min="0" max="1">` | Exibe faixas de aviso/alerta nativas |
| Modal / Dialog (`react-modal`, `radix-dialog`) | `<dialog>` + `dialog.showModal()` | Foco isolado (*focus trap*), backdrop nativo, tecla Esc |
| Accordion / FAQ (`react-accordion`) | `<details><summary>Título</summary>...</details>` | Estado toggle sem JavaScript, zero estado React |
| Dropdown pesquisável / autocomplete | `<input list="items"><datalist id="items"><option value="X">` | Busca nativa integrada pelo browser |
| Textarea auto-expansível | CSS: `field-sizing: content` no `<textarea>` | Elimina observadores de DOM e scripts de redimensionamento |

---

## 2. Capacidades Modernas de CSS (Zero JavaScript para Layout e Responsividade)

Substitua cálculos em JavaScript por recursos nativos de CSS:

| Você acha que precisa de JavaScript para | O que o CSS moderno já resolve nativamente |
|---|---|
| Tipografia responsiva | `font-size: clamp(1rem, 2.5vw, 2rem)` |
| Espaçamentos fluidos | `padding: clamp(1rem, 5vw, 3rem)` |
| Detecção de Dark Mode | `@media (prefers-color-scheme: dark)` |
| Redução de Movimento | `@media (prefers-reduced-motion: reduce)` |
| Grid responsivo sem media queries | `grid-template-columns: repeat(auto-fill, minmax(250px, 1fr))` |
| Responsividade no nível do componente | Container queries: `@container (min-width: 400px)` |
| Seleção de pai baseada em filho | `:has(input:checked)`, `:has(.erro)` |
| Scroll suave | `html { scroll-behavior: smooth; }` |
| Carrossel com encaixe | `scroll-snap-type: x mandatory` + `scroll-snap-align: start` |
| Encaixe e proporção de imagem/vídeo | `aspect-ratio: 16 / 9; object-fit: cover;` |
| Truncamento de texto com reticências | `overflow: hidden; text-overflow: ellipsis; white-space: nowrap;` |
| Truncamento multi-linhas | `display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;` |
| Isolamento e ordenação de regras CSS | `@layer base, components, utilities;` |
| Aninhamento de seletores | CSS Nesting nativo (`& .filho { ... }`) sem Sass ou PostCSS |

---

## 3. Web APIs / JavaScript Browser Runtimes

Substitua pacotes NPM por APIs globais padrão do navegador:

| Você acha que precisa de biblioteca | O que o navegador já disponibiliza nativamente |
|---|---|
| `query-string`, `qs` | `new URLSearchParams(window.location.search)` |
| `lodash.clonedeep` | `structuredClone(objeto)` |
| `lodash.groupby` | `Object.groupBy(array, item => item.categoria)` |
| `lodash.debounce` | Debounce nativo de 3 linhas com `setTimeout` (veja snippet abaixo) |
| `numeral`, `accounting` | `new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" })` |
| `date-fns/format`, `moment` | `new Intl.DateTimeFormat("pt-BR", { dateStyle: "long" }).format(data)` |
| `date-fns/relative` | `new Intl.RelativeTimeFormat("pt", { numeric: "auto" }).format(-2, "day")` |
| `uuid` (v4) | `crypto.randomUUID()` |
| Infinite scroll externo | `new IntersectionObserver(callback).observe(sentinelElement)` |
| Listener de resize de elemento | `new ResizeObserver(callback).observe(element)` |
| Timeout para requisições `fetch` | `fetch(url, { signal: AbortSignal.timeout(5000) })` |
| Event bus customizado | `const bus = new EventTarget(); bus.dispatchEvent(new CustomEvent('x', { detail }));` |
| Cópia para área de transferência | `navigator.clipboard.writeText(texto)` |

### Snippet Canônico: Debounce em 3 Linhas
```javascript
// debt: debounce simples em memória, migrar para streaming/RxJS se houver cancelamento complexo
const debounce = (fn, ms) => {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); };
};
```

---

## 4. Node.js Standard Library

Substitua micro-pacotes npm por módulos nativos de Node.js:

| Pacote npm obsoleto | Alternativa nativa Node.js |
|---|---|
| `mkdirp`, `make-dir` | `fs.mkdirSync(path, { recursive: true })` |
| `rimraf` | `fs.rmSync(path, { recursive: true, force: true })` |
| `uuid` | `crypto.randomUUID()` (módulo nativo `crypto`) |
| `path-exists` | `fs.existsSync(path)` |
| `array-uniq` | `[...new Set(array)]` |
| `array-flatten` | `array.flat(Infinity)` |
| `object-assign` | `Object.assign({}, a, b)` ou object spread `{ ...a, ...b }` |
| `is-stream` | `val instanceof stream.Readable` |
| `load-json-file` | `JSON.parse(fs.readFileSync(path, 'utf8'))` |
| `write-json-file` | `fs.writeFileSync(path, JSON.stringify(data, null, 2))` |

---

## 5. Python Standard Library

Substitua bibliotecas externas por utilitários nativos em Python:

| Pacote / Prática Externa | Equivalente Python Stdlib |
|---|---|
| Cache artesanal ou redis local | `@functools.lru_cache(maxsize=1024)` ou `@functools.cache` |
| Dicionários de contagem manuais | `collections.Counter(lista)` |
| Agrupamento manual com `if key in d:` | `collections.defaultdict(list)` |
| Manipulação de caminhos com strings | `pathlib.Path` |
| Geração de UUIDs | `uuid.uuid4()` |
| Números aleatórios seguros / tokens | `secrets.token_hex(16)` ou `secrets.token_urlsafe(32)` |
| Classes de dados com boilerplate `__init__` | `@dataclasses.dataclass` |
| Envio de requisições simples sem dependência | `urllib.request.urlopen` (quando `requests` ou `httpx` não forem estritamente necessários) |
| Merge de dicionários | `d1 | d2` (Python 3.9+) |

---

## 6. Checklist de Avaliação Pré-Código (Gatekeeper)
- [ ] Esta feature pode ser resolvida com tags semânticas do HTML5?
- [ ] Este layout/comportamento pode ser feito com CSS puro sem tocar em JS?
- [ ] A linguagem de programação já possui isso na biblioteca padrão (`stdlib`)?
- [ ] O projeto já tem uma biblioteca instalada que faz exatamente isso?
- [ ] Se a resposta for **SIM** para qualquer uma das perguntas anteriores, **É PROIBIDO** adicionar novas bibliotecas ou escrever mais de 10 linhas artesanais.
