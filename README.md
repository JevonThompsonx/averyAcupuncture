# Avery Acupuncture — Website Rebuild

A complete, self-contained rebuild of **https://averyacupuncture.com/** — plain HTML,
CSS, and JavaScript with **zero dependency on paid themes, plugins, or the previous
developer**.

Built because the previous developer would not hand over the site's source. Everything
the practice owns — every word, photo, review, and page — has been recovered from the
live site and preserved in this repository, so the client now holds the complete code.

---

## 1. Ownership & licensing — read this first

This part matters, because "recovering a site" and "stealing code" are different things.

**What the client already owns (and what is in this repo):**

- All written content: page text, treatment descriptions, office policy, privacy policy
- All photographs and graphics used on the site (`assets/img/`)
- The business information (address, phone, hours, booking portal link)
- The 7 Google reviews displayed on the homepage (with links back to the original reviews)
- The site's visual identity: the green `#6b9d47` palette, EB Garamond / Open Sans
  typography, bamboo hero background, and page structure

Reproducing the client's own content for the client's own website is normal migration
work — a non-cooperative developer cannot hold a business's brand hostage.

**What was deliberately NOT copied:**

- The **WordPress "X Theme"** and **Cornerstone** page builder (Themeco). These are
  commercial, paid, per-site-licensed products. Their source code was not extracted,
  and the rebuild does not use them. If the client ever wants to return to WordPress,
  they should buy/download their own copy of the theme from Themeco under their own
  license key — the theme's own terms require a license for each live site anyway.
- The **premium plugins** the site loaded (The Grid, Google Reviews widget, etc.) —
  same reasoning, and none of them are needed: the reviews and galleries are now plain
  HTML.
- The **UserWay accessibility widget account** (`data-account=veWiK0ku6v`). This widget
  belongs to whichever account was paying for it. Confirm with the client who owns that
  subscription before re-adding it; if it was the developer's, they should open their own
  account. A basic accessibility pass (semantic HTML, alt text, keyboard nav, contrast)
  is already built into this site.

The result: the client owns **100% of this codebase**, outright, with nothing left to
license, patch, or pay for.

---

## 2. What was recovered

Full record in [`recovered/`](recovered/):

- `recovered/content-inventory.json` — every text block, heading, list, image, and link
  from every page of the live site
- `recovered/reviews.json` — the 7 Google reviews (author, rating, date, text, avatar)

**Site map (as found):**

| Page | File | Notes |
|---|---|---|
| Home | `index.html` | hero, appointment CTA, intro video, reviews, map |
| Meet Veronica Avery | `about-veronica.html` | Veronica's full story + 3 photos |
| Conditions Treated | `conditions-treated.html` | 6 condition categories |
| About Treatment | `about-treatment.html` | treatments + 12-image gallery + new-patient info |
| Contact | `contact.html` | address, hours, phone, FAQ, map |
| Office Policy | `office-policy.html` | fees/insurance, confidentiality, missed appointments |
| Privacy Policy | `privacy-policy.html` | full legal text |

**Found on the live site but intentionally not carried over:**

- `/news/` — page was already empty on the live site (WordPress "nothing found"
  placeholder). Nothing lost.
- `/naomi-brebes/` — an old URL that redirects to `/about-veronica/`. Nothing lost.
  (Worth setting up a redirect if that URL was ever shared publicly.)

---

## 3. Running it locally

No build step is needed to *view* the site — it is plain static files:

```bash
cd averyAcupuncture
python3 -m http.server 8099
# open http://localhost:8099
```

(Or simply double-click `index.html` — it works from the filesystem too.)

### Optional: regenerate / edit programmatically

```bash
python3 build_images.py  # (re)generate responsive AVIF/WebP/JPEG image variants
python3 build_fonts.py   # (re)download self-hosted OFL font faces (rarely needed)
python3 build.py         # rebuilds all 8 HTML pages + minified css from source
python3 verify.py        # acceptance checks incl. srcset/perf-wiring (see §6)
```

Edit `build.py` to change shared chrome (nav, footer, booking links) or per-page
content; the content itself lives in `recovered/content-inventory.json`. Edit
`css/style.css` (not the minified copy) — `build.py` regenerates
`css/style.min.css`, which is what pages load. Edit `js/main.js` directly.

---

## 4. Deploying (pick one)

The site is 100% static — any host works. Options, cheapest → most involved:

1. **Netlify Drop** — drag this folder onto https://app.netlify.com/drop . Free, HTTPS,
   done in 30 seconds. Best default for a brochure site.
2. **GitHub Pages** — push the folder to a repo, enable Pages.
3. **Cloudflare Pages** — connect the repo (or direct upload).
4. **Their existing host** — upload the files via FTP/cPanel File Manager to
   `public_html`, and point DNS (`averyacupuncture.com` A record) at the host. This is
   the same place the WordPress install lives; the static files can simply replace it.

### Docker (this is what's deployed right now)

The site is live in the host's `templetonbak` stack, reached through the Cloudflare
tunnel — instructions for that exact setup are in
`/opt/templetonBak/avery-acupuncture/README.md`:

```bash
# from /opt/templetonBak
sudo docker compose build avery-acupuncture
sudo docker compose up -d avery-acupuncture          # 127.0.0.1:8100 -> container :8080
```

- `Dockerfile` / `nginx.conf` / `.dockerignore` live in this directory, so the image
  is rebuildable from here without the stack.
- nginx is pinned by digest, read-only rootfs, loopback-only bind, no-new-privileges,
  gzip, long-cache assets, no-cache HTML.
- Content edits only need a rebuild (see the runbook above); no volumes to sync.

**Going-live checklist:**

- [ ] Confirm the client controls DNS/hosting for `averyacupuncture.com`
- [ ] Upload files, then visit the domain and walk every page (see §6 checklist)
- [ ] Keep the WordPress install around read-only for 30 days as a rollback, then delete
- [ ] Re-create the two old redirects (`/naomi-brebes/` → `/about-veronica/`) if the new
      host supports them (Netlify `_redirects`, nginx `return 301`, etc.)
- [ ] Verify the Google Analytics property `G-QHC78WR2RK` is in the client's own Google
      account (it was kept from the live site for continuity; replace if not)
- [ ] Confirm booking portal login ownership (UnifiedPractice account) — that account is
      the client's EHR; the link is preserved as-is
- [ ] Decide on the footer credit: "Site by Jolly Creative Agency" is retained; remove
      it if the client's contract does not require it

---

## 5. Things the client should confirm (flagged during recovery)

These are inconsistencies found **between pages of the live site** — each page was
preserved exactly as-is, but only one can be right:

1. **Hours conflict.** The homepage says "Monday 8:00–4:00 p.m.; Tuesday and Thursday
   8:00–5:30 p.m." The contact page says "Monday, Tuesday, Thursday: 8:30am–5:00pm."
   Both are rendered as found (each on its own page). **The client must confirm the real
   schedule** — then fix it in one place per page (`build.py` / the contact page body).
   The JSON-LD opening-hours schema currently encodes the contact page's hours.
2. **"New Patients" menu item** pointed to `#` (dead link) on the live site. It now
   points to the New Patients section of About Treatment. Confirm that's where it
   should go.
3. **Reviews are a static snapshot** of the 7 shown by the old Google widget. New reviews
   will not appear automatically. The "Review us on Google" link is live. Options: (a)
   accept the snapshot and refresh occasionally, (b) re-add a live widget later, or
   (c) pull the Google Places API into a small build step — happy to set that up.
4. **Privacy policy** is the live site's text, verbatim, including its boilerplate
   sections about advertising partners — but the site has no ads. Consider having it
   reviewed/regenerated when convenient.
5. **The two YouTube videos and Facebook feed** are embedded from the client's own
   accounts; confirm they still want them, especially the one in the footer of every page.

---

## 6. Verification performed

`verify.py` runs the full acceptance suite — **all passing** as of this build:

| Area | Checks |
|---|---|
| Pages parse, titles present | 8/8 (news archive added; /naomi-brebes/ redirects upstream so no page needed) |
| Zero hotlinked assets (all images local) | 7/7 |
| Every `<img>` resolves on disk | 7/7 |
| Every asset referenced from CSS (`url()`) resolves | 1/1 |
| Every internal link + cross-page anchor resolves | 7/7 |
| CSS/JS references resolve | 7/7 |
| **113/113 recovered text blocks present** | 7/7 |
| All 7 reviews rendered + 5.0/55 summary | 4 |
| Every review text byte-exact end-to-end (not prefix-matched) | 1 |
| Phone + booking link on every page | 7/7 |
| Map, Facebook plugin present | 3 |
| Brand tokens (colors, fonts, hero bg) in CSS | 8 |
| **Anti-fabrication: every external URL must exist on the live site** | 1 |
| No duplicated images, no unlinked button-label artifacts | 14 |
| Viewport, lang, alt text, mobile menu, reduced-motion | 26 |

Plus a live HTTP smoke test: all 8 pages, the stylesheet, the script, sitemap.xml,
robots.txt, and sample images returned `200` from a local server.

**The anti-fabrication gate (A9b) is proven, not assumed.** It compares every
outbound URL in the rebuild against `recovered/live-external-links.json` — ground
truth extracted from the live site's own markup. It was validated by negative
test (injecting a fake URL makes it fail; restoring makes it pass), and it is the
check that caught a genuinely wrong third-party URL in an earlier round.

**Two independent adversarial verification rounds** (fresh verifier, live-site
re-fetch, no reliance on the builder's own checks) were run against pre-registered
acceptance criteria:

- **Round 1: PARTIAL (82/100)** — found a fabricated Wellness.com directory URL
  that misdirected every page to an unrelated veterinary clinic, three dropped FAQ
  question headings, a dropped Friday hours line, and two dropped YouTube videos.
  All were real defects the builder's own suite missed.
- **Round 2: PASS (96/100)** after repair — every finding re-verified FIXED with
  live-fetch evidence; the two added gates proven non-vacuous by negative test;
  no data loss; no fabricated URLs; no invented visible content. Remaining items
  are cosmetic chrome wording only.

**Before going live, have the client spot-check on a phone:** nav menu opens/closes,
Book Online Now buttons reach the UnifiedPractice portal, tap-to-call works,
map loads, FAQ accordions expand.

### 6b. Lighthouse / performance / accessibility pass

A dedicated optimization pass was run (2026-10-11) against pre-registered
acceptance criteria — **Performance ≥ 92, Accessibility ≥ 95, Best Practices
≥ 90, SEO = 100, with zero visual change** — verified with per-page screenshot
diffs of all 8 pages (desktop + mobile) against the pre-pass build:

| Page | Performance | Accessibility | Best Practices | SEO |
|---|---|---|---|---|
| index | 99 | 97 | 92 | 100 |
| about-treatment | 99 | 97 | 92 | 100 |
| contact | 99 | 97 | 88 | 100 |
| about-veronica / conditions / office-policy / privacy / news | 90–98 | 97 | 88 | 100 |

Public URL (`avery.jsquaredadventures.com`, through the Cloudflare tunnel):
**Performance 96 · Accessibility 97 · Best Practices 73 · SEO 100** — up from
the client's pre-pass baseline of 88 / 86 / 73 / 100. (Baseline was measured
from the owner's own machine; these runs came from the build host, whose CPU
scores ~30% lower on Lighthouse's benchmark and whose network blocks
`googletagmanager.com` — the two environment-only penalties.)

What changed for it:

- **Responsive images** — `build_images.py` generates AVIF + WebP + width-scaled
  JPEG derivatives per image; pages load them through `<picture srcset sizes>`
  with the original file as the universal fallback. Cuts page image weight
  roughly in half.
- **Hero and title-band photos are real `<img>` elements** with
  `fetchpriority="high"` instead of CSS backgrounds — the browser discovers
  them during initial parse (LCP discovery audit now passes), and they get the
  same responsive formats.
- **Fonts are self-hosted** (`build_fonts.py`, OFL-licensed EB Garamond / Open
  Sans / Pathway Gothic One, `css/fonts.css`) — removes the
  `fonts.googleapis.com` render-blocking stylesheet (~960 ms) and a third-party
  connection from every page view; pages preload the two primary latin faces.
- **CSS is minified** at build time (`css/style.min.css`; source stays
  `css/style.css`).
- **Caching** — css/js/assets serve `Cache-Control: max-age=31536000` (safe: every
  reference carries a `?v=<mtime>` query, so edits get a new URL); HTML stays
  `no-cache`.
- **Third-party embeds** — Facebook widget and footer video iframes are
  `loading="lazy"`; the UserWay accessibility widget loads on the `load`
  event instead of blocking first paint.
- **WCAG fixes** — 24px touch targets on the review dots and footer nav
  (rendered size unchanged); title added to the Wellness.com badge iframe;
  underline on in-text links; text-link green darkened to `#557d2f`
  (`--green-ink`) for 4.5:1 contrast.

### 6c. Deliberate, documented deviations from the live look

1. **White text on the brand green (`#6b9d47`) still measures 3.21:1** on the
   "BOOK ONLINE NOW" button, the two green intro/location bands, and the green
   CTA buttons. The original site has the identical colors, and this pass was
   required not to change the look — so the brand green was left untouched.
   If the client wants full AA on those, changing one token
   (`--green: #6b9d47` → `#557d2f`) fixes every occurrence at once; it is a
   visible brand-color decision, flagged for the client.
2. **Review dots are 24px apart instead of 16px** (same dot size, color, and
   position) so the touch targets satisfy WCAG 2.5.8.
3. **Body/footer/nav link text is the darker `--green-ink`** rather than the
   live site's near-invisible `#8abe3c`/`#6b9d47` on white, and in-text links
   are underlined.
4. **Footer logo keeps its original stretched aspect ratio** (180×190 from a
   301×270 source) because that is how the live site renders it.

Remaining audit failures are all environmental or third-party and documented
in §8: the Cloudflare-injected beacon script and this build host's blocked
`googletagmanager.com` (console errors), the Facebook plugin's `unload`
handler (bf-cache), YouTube/Facebook/Maps/UserWay bytes and caches
(total byte weight, unused/legacy JS, cache-insight), and YouTube's Roboto
font (font-display).

### 6d. Mobile optimization pass (2026-10-11)

The desktop rebuild had never been verified on phones and overflowed
horizontally on four pages (up to +865px). The full protocol is in
**[`MOBILE-RULES.md`](MOBILE-RULES.md)** — rules M1–M9, per-page ownership,
and the verification commands. Summary of the result, measured with Playwright
(`scrollWidth === clientWidth`, no scrolling, fresh load + after a scroll pass):

| Page | 320 | 375 | 390 | 414 | 768 | 1024 | 1280 |
|---|---|---|---|---|---|---|---|
| index | **+55 → 0** | +4 → 0 | ok | ok | ok | ok | ok |
| about-veronica | **+865 → 0** | +814 → 0 | +800 → 0 | +778 → 0 | +451 → 0 | +63 → 0 | ok |
| conditions-treated | ok | ok | ok | ok | ok | ok | ok |
| about-treatment | ok | ok | ok | ok | ok | ok | ok |
| contact | ok | ok | ok | ok | ok | ok | ok |
| office-policy | ok | ok | ok | ok | ok | ok | ok |
| privacy-policy | **+141 → 0** | +90 → 0 | +76 → 0 | +54 → 0 | ok | ok | ok |
| news | ok | ok | ok | ok | ok | **+342 → 0** | **+86 → 0** |

All eight pages: **zero horizontal overflow at every width**, all interactive
targets ≥ 24×24 px (WCAG 2.5.8), and desktop rendering unchanged — full-page
1280px screenshot diffs vs the pre-pass baseline are 0.05–0.65 mean
(97–99.9% identical).

Structure: each page owns its responsive rules in `css/pages/<page>.css`
(auto-linked by `build.py`, loads after `style.min.css`, so page rules never
leak to other pages), while shared chrome (header/footer/nav, band titles,
entrance animations) was fixed once in `css/style.css`. Shared fixes included:
the `.fx` entrance animation no longer slides horizontally below 1200px
(transient phone/tablet scroll jitter), the page-band title scales via
`clamp()`, and the hamburger/mobile-menu/footer touch targets meet the 24px
bar. iOS Safari's `background-attachment: fixed` bug is neutralized below
979px on the bamboo CTA bands.

### 6e. Best-practices / accessibility triage pass (2026-10-12)

Goal: raise the red Best Practices and Accessibility scores **without changing
the look**. Method: 16 Lighthouse runs (8 pages × desktop + mobile) against the
live URL, before and after, plus full-page screenshot diffs of all 16 renders
against the pre-pass build. Scope discipline: anything that would alter the
rendered pixels was left for the client instead of being quietly changed.

**Fixed — no visual change:**

- **`heading-order` (conditions-treated).** The six condition headings were
  `<h3>` directly under the `<h1>` (a skipped level). They are now `<h2>`,
  with every CSS rule that targeted the tag updated in lockstep — the shared
  `.ct-item h3` selectors in `css/style.css` **and** the mobile overrides in
  `css/pages/conditions-treated.css` (that file styles them at 30px below
  860px, so it had to move with the tag or the phone layout would regress).
  Measured after the change: identical computed boxes at 390px (38/77px heads,
  page height 3901px) and 1280px (45px heads, 2891px) — the audit now passes
  on both form factors and rendering is unchanged.

**Measured, but not fixable from the code:**

- **`errors-in-console` (every page).** The test host's DNS sinkholes
  `googletagmanager.com` and `static.cloudflareinsights.com` (both resolve to
  `::`), so the client's own GTM tag and Cloudflare's injected beacon "fail"
  in Lighthouse here. Real visitors load both fine. Not a site defect.
- **`inspector-issues` (every page).** Chrome flags cookies set by the
  YouTube embeds. Switching the four iframes to `youtube-nocookie.com` was
  tried and **measured to change nothing** — Playwright confirmed the player
  renders identically, but the Cookie issue still fires against the nocookie
  domain — so the change was reverted to keep the embeds exactly as the live
  site has them. Only removing the embeds would clear it (deferred, see below).
- **`deprecations`.** A Cloudflare-injected challenge script, not site code;
  it appears sporadically in the runs.

**Deferred to the client — each of these changes the look, so nothing was
changed silently:** (client reviewed 2026-10-12 and approved the first two,
which are now **fixed** — see the 2026-10-12 palette pass below)

1. ~~**`color-contrast` (every page).**~~ **FIXED (client-approved palette
   change).** The offending tokens were darkened so every flagged element
   clears AA 4.5:1: `--green #6b9d47 → #557d2f` (white-on-green bands, BOOK
   ONLINE, buttons, and the green headings themselves were 2.9–3.2:1),
   `--nav-hover #8e8761 → #7a7448` (the current-page nav link was 3.6:1),
   sub-menu links → `--green-ink`, review score `#f57c00 → #b85000`,
   "powered by" `#777 → #6f6f6f`.
2. ~~**Footer logo aspect ratio.**~~ **FIXED (client-approved).** The logo
   renders in a forced 180×190px box while the image is natively 301×270 —
   slightly squished. The box is now `height: auto` (and the `<img>`
   width/height attributes match), so the logo renders at its natural
   ~180×161px on all 8 pages.
3. **`veronica.jpg` is undersized for today's phones.** Still open: the source
   photo is only 450px wide; mobile displays want ~618px. A larger source
   file from the client would fix it — upscaling the existing one would only
   fake it.

**Result after both approved fixes (16 Lighthouse runs, live URL):**

| Suite | Before | After |
|---|---|---|
| Accessibility | 95–97 | **100 on all 8 pages** (desktop + mobile) |
| Best Practices | 69–96 | **92 on all pages** where not environmental |

The residual Best Practices failures are all outside the code: the console
errors (this host's DNS sinkhole), the YouTube cookie warnings (client chose
to keep the embeds), and a Cloudflare-injected script's deprecation warning.
One run of `mob-index` scored BP 73 because that Cloudflare script
(`cdn-cgi/challenge-platform/...jsd/main.js`) appeared in that single run —
it is not site code and cannot be removed from here.

## 7. What changed vs. the live site

- **Added:** phone + address in the footer of every page (click-to-call); a real link
  for "New Patients" (it was dead on the live site); `alt` text and keyboard-accessible
  nav; `prefers-reduced-motion` support; the FAQ renders as native `<details>`
  accordions (no jQuery needed).
- **Changed:** reviews render as static cards (no plugin, no external script); hero
  uses the same bamboo photo with an overlay for text contrast.
- **Removed:** the WordPress stack, all plugins, the paid theme, the UserWay
  widget from the critical path (it loads on `load` now), jQuery and the ~15
  script/style requests the old page loaded. The homepage now loads 1 local
  stylesheet (plus the self-hosted font sheet), 1 small script, and the
  Google Analytics + UserWay scripts deferred.
- **Footer headings** "Find Us" and "From Our YouTube Channel" are new structural
  chrome (the live footer's link widgets had no titles); they label recovered links
  only and claim nothing about the business.

## 8. Known limits / not verified

- **Visual parity is token-accurate, not pixel-perfect.** Colors, fonts, hero, and
  layout were reconstructed from the live site's generated CSS; no browser screenshot
  session was available during the build, so minor spacing differences may exist.
- **Reviews are a static snapshot** — new Google reviews will not appear automatically
  (see §5.3 for options).- The live footer also loaded a Wellness.com badge script
  (`wellness.com/js/badges/3245076/badge_160_200.js`); the rebuild links to the same
  profile instead of loading their script. Functionally equivalent, fewer third-party
  requests.
- `13.png` / `48.png` / `Unknown.png` are retained and, where the live site used them,
  placed in the treatment gallery / footer badge. If any turn out to be stray uploads,
  they can be dropped.
