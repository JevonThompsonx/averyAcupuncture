# Mobile optimization — rules and per-page protocol

**Mission.** The client's original site (averyacupuncture.com) is properly
mobile-optimized; this rebuild was verified for desktop parity only and
overflows horizontally on several phones/tablets. Make every page properly
mobile-optimized **without changing the desktop look**.

**Status — COMPLETE (2026-10-11).** Every page now renders with zero horizontal
overflow at all tested widths; the numbers in the table below are the *pre-fix*
baseline that motivated this protocol, not the current state. Outcome evidence
(per-page overflow before → after, desktop screenshot diffs, touch-target
audits) is summarised in [README §6d](README.md). This file is retained as the
rules record (M1–M9) and the per-page ownership map for future work.

Measured on 2026-10-11 (Playwright, Chromium, `scrollWidth` vs
`clientWidth`, no scrolling) — **baseline, before the fixes:**

| Page | 320 | 375 | 390 | 414 | 768 | 1024 |
|---|---|---|---|---|---|---|
| index | **+55** | +4 | ok | ok | ok | ok |
| about-veronica | **+865** | +769 | +755 | +733 | +406 | +63 |
| conditions-treated | ok* | ok* | ok* | ok* | ok | ok |
| about-treatment | ok* | ok* | ok* | ok* | ok | ok* |
| contact | ok | ok | ok | ok | ok | ok |
| office-policy | ok* | ok* | ok* | ok* | ok | ok* |
| privacy-policy | **+141** | +90 | +76 | +54 | ok | ok |
| news | ok | ok | ok | ok | ok | **+342** |

(* = fixed by shared changes in this commit: the `.fx` entrance animation no
longer slides horizontally below 1200px, and `.page-band__title` now scales
with `clamp()`.)

Root causes that remain are **page-specific** and are owned by the per-page
agents below.

---

## Rules (acceptance criteria)

- **M1 — No horizontal overflow, any width.** `document.documentElement
  .scrollWidth === clientWidth` at 320, 375, 390, 414, 768, 1024, 1280, 1440,
  1920 px. No exceptions; transient animation states included (verify with the
  page freshly loaded *and* after a full scroll pass).
- **M2 — Touch targets ≥ 24×24 px** below 861 px for every interactive
  element: nav toggle, nav links, footer links, buttons, slider arrows/dots,
  FAQ toggles, tap-to-call. (WCAG 2.5.8 "Target Size (Minimum)" is the 24px
  bar this repo standardizes on and what Lighthouse audits; aim higher where
  the layout allows.) Visual size may stay as-is via the invisible-expansion
  patterns already used in this repo (padding + matching negative margin, or
  a centered radial-gradient on a transparent box — see `.grw__dot` and
  `.footer-menu a` in `css/style.css`).
- **M3 — Nothing may stick out or be cut off.** Fixed pixel widths that
  assume desktop (e.g. `width: 1161px`, `grid-template-columns: 1066px 300px`)
  must become fluid/minmax/stacked. Long unbreakable strings (URLs) must
  wrap (`overflow-wrap: anywhere`). Verify by element audit, not by eye.
- **M4 — Content and structure unchanged.** Same words, same images, same
  order. Only layout/typography-scale/affordance changes. `verify.py` must
  stay green (it includes the 113 recovered-text-block check).
- **M5 — Desktop parity is a hard gate.** Full-page screenshot diff at
  1280 px against the pre-change baseline (`/tmp/opencode/shots/before3`)
  must stay within tolerance (mean ≤ 1.0, ≥ 97% identical pixels). Typography
  may scale down below 861 px only; ≥ 861 px must render as before.
  *The 390px mobile screenshot diff is informational, not a gate* — the
  pre-change mobile baseline captured the broken (overflowing) layout, so
  any correct mobile fix necessarily diverges from it. Judge mobile quality
  by the overflow/target audits and by inspecting the render, not by the
  mobile diff number.
- **M6 — No new external requests, no new libraries.** CSS changes and (when
  unavoidable) markup changes inside your page's own `build.py` function.
- **M7 — Only touch your own files.**
  `build.py` → your `page_<name>()` function ONLY; create
  `css/pages/<page>.css` (auto-linked by `build.py`, loads after
  `style.min.css` so your overrides win). **Never** edit shared chrome
  (`header()`, `footer()`, `page()`, `reviews_section()` unless it is your
  page's), the global `css/style.css`, `verify.py`, or another page's files.
  If you find a shared/chrome bug, **report it in your final summary** — do
  not fix it.
- **M8 — Build + verify before you finish.** `python3 build.py` and
  `python3 verify.py` must both pass in your worktree, plus the per-page
  mobile audit and the desktop screenshot diff (commands below).
- **M9 — Commit your work** in your own worktree on your own branch
  (`mobile/<page>`), one commit, message describing what changed and the
  before/after overflow numbers.

## How to verify (run in your worktree)

```bash
cd <your worktree>
python3 build.py && python3 verify.py          # must pass
python3 /tmp/opencode/checkpage.py http://127.0.0.1:<port> <page>.html
    # prints: overflow status at every width (M1), element-level offenders (M3),
    # touch-target audit (M2), and desktop/mobile screenshot diff vs baseline (M5)
```

Serve your worktree on your assigned port:
`python3 -m http.server <port> --bind 127.0.0.1` (background it).

## Ownership

| Page | build.py function | CSS file | Branch |
|---|---|---|---|
| index | `page_index()` (+ `hero()`, `reviews_section()`, `location_section()`) | `css/pages/index.css` | `mobile/index` |
| about-veronica | `page_about_veronica()` | `css/pages/about-veronica.css` | `mobile/about-veronica` |
| conditions-treated | `page_conditions()` | `css/pages/conditions-treated.css` | `mobile/conditions-treated` |
| about-treatment | `page_about_treatment()` | `css/pages/about-treatment.css` | `mobile/about-treatment` |
| contact | `page_contact()` | `css/pages/contact.css` | `mobile/contact` |
| office-policy | `page_policy()` | `css/pages/office-policy.css` | `mobile/office-policy` |
| privacy-policy | `page_privacy()` | `css/pages/privacy-policy.css` | `mobile/privacy-policy` |
| news | `page_news()` | `css/pages/news.css` | `mobile/news` |

The orchestrator (primary agent) owns shared chrome, the global stylesheet,
`verify.py`, all merges, and final deployment.

## Reference: the original on mobile

`https://averyacupuncture.com` renders at 390 px with no overflow on any
page (verified 2026-10-11). Its body text is 11 px and it keeps large
desktop-scale headings wrapped in narrow columns; this rebuild intentionally
keeps larger, more readable text for the practice's older audience, so the
goal is a **clean, functional mobile layout** — not a byte-match of the
original's mobile CSS.
