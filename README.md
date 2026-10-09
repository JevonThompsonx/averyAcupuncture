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
python3 build.py    # rebuilds all 7 HTML pages from the recovered content
python3 verify.py   # 70+ acceptance checks (see §6)
```

Edit `build.py` to change shared chrome (nav, footer, booking links) or per-page
content; the content itself lives in `recovered/content-inventory.json`.

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

`verify.py` runs the full acceptance suite — **96 checks, all passing** as of this build:

| Area | Checks |
|---|---|
| Pages parse, titles present | 7/7 |
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

Plus a live HTTP smoke test: all 7 pages, the stylesheet, the script, and sample
images returned `200` from a local server.

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

## 7. What changed vs. the live site

- **Added:** phone + address in the footer of every page (click-to-call); a real link
  for "New Patients" (it was dead on the live site); `alt` text and keyboard-accessible
  nav; `prefers-reduced-motion` support; the FAQ renders as native `<details>`
  accordions (no jQuery needed).
- **Changed:** reviews render as static cards (no plugin, no external script); hero
  uses the same bamboo photo with an overlay for text contrast.
- **Removed:** the WordPress stack, all plugins, the paid theme, UserWay widget, jQuery
  and the ~15 script/style requests the old page loaded. The homepage now loads 1
  stylesheet, 1 small script, and Google Fonts.
- **Footer headings** "Find Us" and "From Our YouTube Channel" are new structural
  chrome (the live footer's link widgets had no titles); they label recovered links
  only and claim nothing about the business.

## 8. Known limits / not verified

- **Visual parity is token-accurate, not pixel-perfect.** Colors, fonts, hero, and
  layout were reconstructed from the live site's generated CSS; no browser screenshot
  session was available during the build, so minor spacing differences may exist.
- **Reviews are a static snapshot** — new Google reviews will not appear automatically
  (see §5.3 for options).
- The live footer also loaded a Wellness.com badge script
  (`wellness.com/js/badges/3245076/badge_160_200.js`); the rebuild links to the same
  profile instead of loading their script. Functionally equivalent, fewer third-party
  requests.
- `13.png` / `48.png` / `Unknown.png` are retained and, where the live site used them,
  placed in the treatment gallery / footer badge. If any turn out to be stray uploads,
  they can be dropped.
