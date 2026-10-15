# AGENTS.md — Avery Acupuncture website

Project context for anyone working in this repository (human or agent). Read
[`README.md`](README.md) first for the full history, recovery record, and
verification results; this file is the short operational reference.

## What this is

A **static marketing site** for **Avery Acupuncture & Natural Medicine, Inc.**
(Veronica Avery, Licensed Acupuncturist and Herbalist), Paso Robles, CA.
Production domain: `https://averyacupuncture.com`. Plain HTML + CSS + vanilla
JS — **no frameworks, no package manager, no build-time dependencies beyond
Python 3's standard library** (`verify.py` additionally needs
`beautifulsoup4`).

It is a rebuild of the practice's former WordPress site, reconstructed from
content recovered off the live site, so the client owns the whole codebase.
Business claims on the pages (services, hours, policies) are the practice's
own words — do not invent or "improve" clinical content.

## Commands

| Task | Command |
|---|---|
| View locally | `python3 -m http.server 8099` → http://localhost:8099 (or just open `index.html`) |
| Rebuild HTML + minified CSS | `python3 build.py` |
| Regenerate responsive image variants | `python3 build_images.py` |
| Re-download self-hosted font faces | `python3 build_fonts.py` (rarely needed) |
| Run the acceptance suite | `python3 verify.py` |
| Build the container image | `docker build -t avery-acupuncture .` (see `Dockerfile`) |

`build.py` writes **9 HTML files** (8 content pages + the branded `404.html`)
and regenerates `css/style.min.css` plus `css/pages/*.min.css`. It takes no
flags — any argument is ignored and the build simply runs.

Deployment is documented in §4 of the README. The live container runs in the
host's `templetonbak` compose stack (`127.0.0.1:8100` → container `:8080`,
reached through the Cloudflare tunnel); the stack runbook lives outside this
repo at `/opt/templetonBak/avery-acupuncture/README.md`.

## Layout

```
index.html  about-veronica.html  conditions-treated.html  about-treatment.html
contact.html  office-policy.html  privacy-policy.html  news.html   # 8 content pages
404.html                                                          # branded error page
assets/img/   responsive originals + AVIF/WebP/width derivatives
assets/fonts/ self-hosted OFL woff2 faces
css/style.css        shared chrome source (edit this)
css/style.min.css    build output — never edit
css/pages/<page>.css per-page rules, auto-linked by build.py (edit the .css, not .min.css)
js/main.js           all site JS (nav, carousel, FAQ, embed facades, parallax)
recovered/           ground truth recovered from the live site — DO NOT EDIT
build.py             page generator + templates + SEO/JSON-LD head
build_images.py      responsive image derivative policy
build_fonts.py       font download + css/fonts.css generation
verify.py            acceptance/regression suite (fail loudly on any gap)
Dockerfile  nginx.conf  .dockerignore  _redirects  sitemap.xml  robots.txt
```

## Conventions

- **Content lives in `build.py`** (page functions) with `recovered/content-inventory.json`
  as the recovery record. Shared chrome (nav, footer, booking links, SEO head)
  is generated from the single `page()`/`header()`/`footer()` templates — change
  it once, all pages follow.
- **Edit source CSS, never the minified copy.** `build.py` regenerates the
  `.min.css` files, which is what the pages load.
- **Per-page rules go in `css/pages/<page>.css`.** `build.py` auto-links it
  after `style.min.css`, so page rules cannot leak into other pages.
- **Cache busting is by mtime query** (`?v=<mtime>`, `asset_ver()`), which is
  why `nginx.conf` can serve CSS/JS/fonts/images for a year while HTML stays
  `no-cache`. Never rename asset files to force a refresh — just rebuild.
- **No new external requests or libraries.** Embeds (YouTube, Maps, Facebook,
  Wellness.com, UserWay) are click-to-load facades or deferred on purpose.
- **Accessibility and mobile rules are hard requirements**, not nice-to-haves:
  see [`ACCESSIBILITY.md`](ACCESSIBILITY.md) (WCAG 2.1/2.2 AA conformance) and
  [`MOBILE-RULES.md`](MOBILE-RULES.md) (M1–M9: zero horizontal overflow at any
  width, ≥24px touch targets, desktop parity). `verify.py` enforces the
  regression subset.
- **Third-party accounts are the client's**: the GA4 measurement ID and the
  UserWay `data-account` value in `build.py` belong to the practice — keep them,
  don't add new tracking, and never commit credentials to this repo.

## Constraints

- **Do not commit or push** unless the user explicitly asks.
- `recovered/` is the evidence record of what the live site contained — read it,
  never rewrite it.
- Keep diffs surgical: match existing formatting/tone, and don't reformat or
  "modernise" unrelated code. Visual changes to a client site need client
  approval (see the colour/aspect-ratio decisions recorded in README §6e–6f).
- Business-facing copy is reviewed content. Flag suspected errors (e.g. the
  hours conflict in README §5) rather than silently fixing them.
