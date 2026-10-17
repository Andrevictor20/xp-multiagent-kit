---
name: seo-content-engine
description: Technical On-Page SEO, Schema.org JSON-LD, and AI Search optimization (GEO/AEO).
---

# SEO Content Engine: On-Page SEO & AI Search Optimization (GEO/AEO)

Optimize web pages for both traditional search engines (Google, Bing) and AI citation engines (ChatGPT Search, Perplexity, Claude, Google AI Overviews).

## 1. Technical & Semantic On-Page SEO
- **Title Tag (50-60 chars):** `[Primary Keyword] - [Value Proposition] | [Brand]`.
- **Meta Description (150-160 chars):** Include primary keyword, concrete benefit, and active CTA.
- **Heading & HTML5 Hierarchy:** Exactly **one `<h1>`** per page; sequential `<h1> -> <h2> -> <h3>` without skipped levels; semantic `<main>`, `<article>`, `<section>`, `<nav>`, `<header>`, `<footer>`.
- **Media Optimization:** Descriptive `alt` attributes on all informative images, `.webp`/`.avif` formats, `fetchpriority="high"` on Hero image, and `loading="lazy"` below the fold.

## 2. AI Search Optimization (GEO / AEO)
AI answer engines extract self-contained passages and structured facts:
- **Direct Answer Blocks (40-60 words):** Open FAQ answers and concept definitions with a concise, self-contained summary paragraph.
- **Structured HTML Comparison Tables:** Use semantic `<table>` elements for *"X vs. Y"* and pricing/feature matrices (3x higher LLM extraction accuracy).
- **Quantified Citations:** Include specific metrics, dates, and author credentials (+37% LLM citation lift).

## 3. Schema.org Structured Data (`application/ld+json`)
Inject valid JSON-LD (`SoftwareApplication`, `Organization`, `FAQPage`, `Product`):

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "FinanceX",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "offers": { "@type": "Offer", "price": "49.00", "priceCurrency": "USD" },
  "aggregateRating": { "@type": "AggregateRating", "ratingValue": "4.9", "reviewCount": "340" }
}
```

## 4. Machine-Readable Agent Discovery Files
Provide `/llms.txt` (product summary, architecture, canonical docs links) and `/pricing.md` (clean Markdown plan/limit matrix) at the site root.
