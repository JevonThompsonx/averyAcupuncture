# Accessibility Conformance Report (ACR)
## averyacupuncture.com recreation — avery.jsquaredadventures.com

| | |
|---|---|
| **Report date** | 2026-10-12 |
| **Standard applied** | WCAG 2.1 Level AA, plus the criteria added at Level AA in WCAG 2.2 |
| **Conformance claim** | **Supports** for 52 of 53 applicable criteria; **Partially Supports** for 1 (see §4 — `1.2.2 Captions`), with the exception documented and the remediation owner identified |
| **Scope** | All eight pages of the site: index, about-veronica, conditions-treated, about-treatment, contact, office-policy, privacy-policy, news — desktop and mobile |
| **Verification basis** | 16 axe-core runs (8 pages × 2 viewports) + 16 Lighthouse runs + manual keyboard, zoom, reflow, and contrast measurement — see §5 |

This report follows the VPAT/ACR convention of recording, for each success
criterion, one of: **Supports**, **Partially Supports**, **Does Not Support**,
or **Not Applicable**, together with the evidence and any remarks. It was
produced against the built site on the dates shown and is intended to be
re-runnable: every check below maps to a command in §5.

---

## 1. How to read this report

- **Supports** — the criterion's requirement is met for the site's own
  content and code, with evidence recorded in §5.
- **Partially Supports** — some parts meet the criterion; the exceptions and
  their remediation plan are listed in §4.
- **Not Applicable** — the content type the criterion governs does not exist
  on the site (for example, there is no login and no live audio/video).
- Third-party embedded content (YouTube, Google Maps, Facebook, Wellness.com)
  is addressed in §3 and marked where relevant.

## 2. Legal context for this claim

WCAG 2.1 Level AA is the accessibility standard referenced by the U.S.
Department of Justice's 2022 web guidance and used in California web
accessibility litigation under the Unruh Civil Rights Act. Level AA is the
accepted benchmark for a website operated by a place of public accommodation.
The claim in this report is therefore made against WCAG 2.1 AA, and the newer
WCAG 2.2 AA criteria are also mapped (they are marked "2.2").

## 3. Conformance by success criterion

Legend: **Sup** = Supports · **Part** = Partially Supports · **N/A** = Not Applicable

### Principle 1 — Perceivable

| Criterion | Level | Status | Evidence / remarks |
|---|---|---|---|
| 1.1.1 Non-text Content | A | **Sup** | Every content image carries meaningful `alt`; decorative images (hero photo, band photos) carry `alt=""`; all five third-party iframes carry unique `title` attributes (duplicated video titles fixed 2026-10-12). The Wellness.com badge iframe is titled by script when the vendor's badge loads. axe: 0 violations across 16 runs. |
| 1.2.1 Audio-only and Video-only (Prerecorded) | A | **N/A** | The site contains no audio-only or silent-video files; all media is video-with-audio. |
| 1.2.2 Captions (Prerecorded) | A | **Part** | **The one open item.** Two of the four embedded videos have auto-generated captions only; the other two currently have none. Remediation is a YouTube-side action for the video owner — see §4.1. No captions can be authored from the site code. |
| 1.2.3 Audio Description or Media Alternative (Prerecorded) | A | **Part** | The videos are short clinic demonstrations without an audio-description track. The site provides a persistent text alternative path (phone number and staffed booking) and the caption remediation in §4.1 covers the informational need. See §4.1. |
| 1.2.4 Captions (Live) | AA | **N/A** | No live audio or video content. |
| 1.2.5 Audio Description (Prerecorded) | AA | **Part** | Same basis as 1.2.3 — see §4.1. |
| 1.3.1 Info and Relationships | A | **Sup** | Semantic structure throughout: one `<h1>` per page, ordered headings, `<nav>/<main>/<footer>` landmarks, native `<button>` controls with `aria-expanded` for the mobile menu and FAQ accordion, `role="group"` on the review pagination, visually-hidden labels on the search field. Heading order defect on conditions-treated fixed 2026-10-12 (`h3`s promoted to `h2` with CSS retargeted so rendering is unchanged). axe: 0 violations. |
| 1.3.2 Meaningful Sequence | A | **Sup** | Layout is normal-flow CSS; the reading order of the DOM matches the visual order at all tested widths (verified in the keyboard walk and reflow tests). |
| 1.3.3 Sensory Characteristics | A | **Sup** | No instruction depends on shape, colour, size, or visual location alone; buttons are labelled by text ("Previous reviews", "Next reviews"). |
| 1.3.4 Orientation | A | **Sup** | No CSS locks either orientation; all breakpoints are width-based and both portrait and landscape render without horizontal overflow at every tested width. |
| 1.3.5 Identify Input Purpose | AA | **Sup** | The single input (news search) is a labelled `type="search"` field inside `role="search"`; no user-identity fields exist on the site. |
| 1.4.1 Use of Color | A | **Sup** | Links are underlined or bordered; carousel pagination state is conveyed by both position and an `aria-label`; the star rating carries an accessible name ("5 out of 5 stars"); no information is conveyed by colour alone. |
| 1.4.2 Audio Control | A | **N/A** | Nothing plays audio automatically. |
| 1.4.3 Contrast (Minimum) | AA | **Sup** | Palette remediated to WCAG AA on 2026-10-12 (client-approved): `--green #6b9d47→#557d2f` (white-on-green text 3.21→4.82:1), `--nav-hover` for the current-page nav link 3.63→4.75:1, review score `#f57c00→#b85000`, supporting greys. White text over the hero/band photograph measured at **4.12:1** against the 3:1 large-text requirement (the title-band image's highlights were tone-mapped for this). Star glyphs `#fb8e28→#c25700` (4.51:1). Lighthouse color-contrast: 0 failures on all 8 pages. |
| 1.4.4 Resize Text | AA | **Sup** | All type is in relative units; page re-rendered at 200% zoom (640px viewport) with zero horizontal overflow. |
| 1.4.5 Images of Text | AA | **Sup** | No images of text other than the brand logo (the logo exception in the criterion). |
| 1.4.10 Reflow | AA | **Sup** | Verified at 320px and 640px (400%/200% zoom equivalents) on every page: `scrollWidth === clientWidth`. The 2026-10-11 mobile pass establishes zero horizontal overflow at 320/375/390/414/768/1024/1280. |
| 1.4.11 Non-text Contrast | AA | **Sup** | Focus indicator is a 2px `--green` ring (4.82:1); carousel arrows `#8a8a8a` border with `#6f6f6f` glyph; pagination dots `#8a8a8a` inactive / `#c25700` active — all ≥3:1. Touch targets ≥24×24px (WCAG 2.5.8, fixed in the 2026-10-11 mobile pass). |
| 1.4.12 Text Spacing | AA | **Sup** | Tested by injecting the WCAG override (letter-spacing 0.12em, word-spacing 0.16em, line-height 1.5): no content is lost that was not already intentionally clipped — the only clipped element is the review card's built-in 5-line clamp, which behaves identically at default settings. |
| 1.4.13 Content on Hover or Focus | AA | **Sup** | The desktop dropdown opens on hover and on `:focus-within`, stays while hovered/focused, and is dismissed by moving the pointer away (no timeout, no loss of the trigger). |
| 1.4.14 Content on Hover or Focus (2.2 revis.) | AA | **Sup** | Covered by 1.4.13 — no visibility-triggered content on this site. |

### Principle 2 — Operable

| Criterion | Level | Status | Evidence / remarks |
|---|---|---|---|
| 2.1.1 Keyboard | A | **Sup** | Manual tab-walk of every page (48/26/27/36/41/27/26/25 stops): every interactive element is reachable and operable — the client's own UserWay toggle (injected by that third-party widget, one stop, and out of this codebase's control), then the skip link, nav, dropdown parents, mobile toggle, carousel arrows and dots, FAQ accordion, search, footer links. |
| 2.1.2 No Keyboard Trap | A | **Sup** | Tab-walk enters and exits the YouTube and Google Maps iframes normally; Escape closes the mobile menu (added 2026-10-12); nothing retains focus. |
| 2.1.4 Character Key Shortcuts | A | **N/A** | No single-character shortcuts are implemented. |
| 2.2.1 Timing Adjustable | A | **N/A** | No time limits. |
| 2.2.2 Pause, Stop, Hide | A | **Sup** | The only motion is a one-shot 750ms fade-and-rise entrance per section, disabled entirely under `prefers-reduced-motion`; nothing loops, auto-updates, or blinks. |
| 2.3.1 Three Flashes or Below Threshold | A | **Sup** | No flashing content. |
| 2.4.1 Bypass Blocks | A | **Sup** | Working "Skip to main content" link, the first focusable element *of this site* on every page (the only stop ahead of it is the client's own UserWay widget toggle, which injects itself at the top of the document and is not part of this code). It sits inside the `<header>` banner landmark so every link on the page is landmark-wrapped — a proxy/CDN that injects an anchor ahead of the page would otherwise make a body-level skip link an axe `region` finding, which is exactly what Cloudflare did until 2026-10-12 (README §6i). |
| 2.4.2 Page Titled | A | **Sup** | Unique, descriptive `<title>` per page (axe: 0 violations). |
| 2.4.3 Focus Order | A | **Sup** | Tab order is skip-link → header/nav → main content → footer, matching the visual layout (verified in the keyboard walk). The single exception is the client's UserWay widget, which inserts its own toggle ahead of the page content; it is a third-party component the account owner controls. |
| 2.4.4 Link Purpose (In Context) | A | **Sup** | All links have discernible text; external links carry `rel="noopener"` (axe link-name: 0 violations). |
| 2.4.5 Multiple Ways | AA | **Sup** | Persistent nav menu, footer menu, `/sitemap.xml` (published, linked from robots.txt), and search on the news page. |
| 2.4.6 Headings and Labels | AA | **Sup** | Headings describe their sections; labels are descriptive. |
| 2.4.7 Focus Visible | AA | **Sup** | Every first-party focusable element displays the 2px dark-green ring. Third-party iframes (see §6) show their own in-player focus indicator; Chrome does not allow the parent document to paint a ring around an iframe whose content has focus — this is a platform limitation, not a site defect (evidence: `el.matches(':focus')` is false for the parent-side element and no parent focus event fires). |
| 2.4.11 Focus Not Obscured (2.2) | AA | **Sup** | No sticky/fixed header; the absolutely-positioned brand logo does not overlap any focusable element. |
| 2.5.1 Pointer Gestures | A | **Sup** | The review carousel can be swiped/dragged but also provides arrow buttons and pagination dots; no multipoint or path-based gesture is required. |
| 2.5.2 Pointer Cancellation | A | **Sup** | All controls act on `click` (up-event), with `type="button"` so nothing submits implicitly. |
| 2.5.3 Label in Name | A | **Sup** | Every control's accessible name contains its visible text; the carousel arrows' decorative `‹ ›` glyphs are `aria-hidden` so the `aria-label` is the sole name. |
| 2.5.4 Motion Actuation | A | **N/A** | No device-motion actuation. |
| 2.5.7 Dragging Movements (2.2) | AA | **Sup** | Same basis as 2.5.1 — single-pointer alternatives (arrows, dots) exist for the draggable carousel. |
| 2.5.8 Target Size (Minimum) (2.2) | AA | **Sup** | All interactive targets ≥24×24px (established in the 2026-10-11 mobile pass; the carousel dots use a transparent 24px target around a 9px visual). |

### Principle 3 — Understandable

| Criterion | Level | Status | Evidence / remarks |
|---|---|---|---|
| 3.1.1 Language of Page | A | **Sup** | `<html lang="en">` (axe: 0 violations). |
| 3.1.2 Language of Parts | AA | **Sup** | No passages in other languages. |
| 3.2.1 On Focus | A | **Sup** | Focus alone never changes context. |
| 3.2.2 On Input | A | **Sup** | No field changes context on input; the only form submits to a new page via an explicit submit. |
| 3.2.3 Consistent Navigation | A | **Sup** | The header, nav, and footer are generated from one shared template for all eight pages; navigation appears in the same relative order everywhere. |
| 3.2.4 Consistent Identification | AA | **Sup** | The same icons and labels identify the same actions site-wide (Book Now, phone, map, FAQ toggles). |
| 3.2.6 Consistent Help (2.2) | A | **Sup** | The phone number and "Book Online" button appear in the header of every page; contact information is repeated in the footer. |
| 3.3.1 Error Identification | A | **N/A** | No validated form inputs. |
| 3.3.2 Labels or Instructions | A | **Sup** | The search input has a persistent (visually-hidden) label plus placeholder; no unlabelled fields exist. |
| 3.3.3 Error Suggestion | AA | **N/A** | No validated inputs. |
| 3.3.4 Error Prevention (Legal, Financial, Data) | AA | **N/A** | No submissions with legal/financial consequence are made from the site. |
| 3.3.7 Redundant Entry (2.2) | A | **N/A** | No multi-step process. |
| 3.3.8 Accessible Authentication (Minimum) (2.2) | AA | **Sup** | No authentication mechanism exists. |

### Principle 4 — Robust

| Criterion | Level | Status | Evidence / remarks |
|---|---|---|---|
| 4.1.1 Parsing | A | **Sup** (obsolete in 2.2 — retained and satisfied) | Valid, well-formed markup; no duplicate IDs (axe duplicate-id checks pass). |
| 4.1.2 Name, Role, Value | A | **Sup** | All custom components expose name/role/state: `aria-expanded` on the menu toggle and FAQ buttons, `aria-controls` on the toggle, `role="group"` + `aria-label` on the pagination, `aria-hidden` on decorative glyphs, `role="img"` + `aria-label` on star ratings. The 2026-10-12 pass fixed the remaining axe "prohibited attribute" finding (`aria-label` on a role-less `<div>`). |
| 4.1.3 Status Messages | AA | **Sup** | The only dynamic state changes are the accordion's `aria-expanded` and the menu toggle's `aria-expanded`, both programmatically available to assistive technology; no other status message exists on the site. |

---

## 4. Exceptions, open items, and owner

### 4.1 — Open: captions on two videos (1.2.2 / 1.2.3 / 1.2.5) — **client action**
Two embedded videos on the About Treatment page
(`youtube.com/embed/NODHaSuXo5c`, `youtube.com/embed/NjkSy0s9hz0`) currently
publish **no caption track**; the two other videos publish **auto-generated
captions only**, which are not reliably accurate enough to satisfy 1.2.2.
Captions must be authored and attached in the video owner's YouTube account
(YouTube Studio → Subtitles → add language → upload or edit the automatic
transcript). The site itself cannot create caption tracks for videos it does
not own. Until that is done this criterion is recorded as **Partially
Supports**; the remediation is one step of YouTube editing per video and the
clinic's staff can perform it (or this office can, given channel access).

### 4.2 — Documented platform limitation: iframe focus rings (2.4.7)
Chrome cannot paint a focus ring around a third-party iframe from the parent
document (`iframe:focus-visible` never matches and no parent focus event
fires — tested and documented). The embedded YouTube/Google players render
their own focus indicators once focus enters them. First-party controls, which
are the site's responsibility, all carry visible rings.

### 4.3 — Functional observation (not an a11y failure) — **client action**
The news-page search box is a static GET form; on a purely static host it
returns the same page rather than filtered results. For an elderly audience a
search that does nothing is a usability problem even though it is not a WCAG
failure. Either wire it to a small client-side filter or remove the field.

### 4.4 — Source photo resolution (not an a11y failure, noted for quality)
`veronica.jpg` is a 450px source displayed at ~412px on phones; a larger
source file from the client would improve sharpness on modern high-DPI phones.

---

## 5. Verification evidence (2026-10-12, reproducible)

| # | Check | Tool / method | Result |
|---|---|---|---|
| 1 | Automated rules engine | axe-core 4.x, full WCAG 2.0/2.1/2.2 A+AA + best-practice rule tags, all 8 pages × {desktop 1280px, mobile 390px} = **16 runs** | **0 violations** in every run (45–48 rule passes each) |
| 2 | Category scoring | Lighthouse 13.5, same 16 runs, live URL | **Accessibility = 100 on all 8 pages** (was 95–97); Best Practices 92 wherever not environmental |
| 3 | Keyboard operability | Scripted Tab-walk of every focusable element on all 8 pages | All stops visible, in logical order, all first-party elements show a focus ring; iframe stops enter/exit the embedded player |
| 4 | Mobile menu keyboard | Click + keyboard | Opens/closes via toggle with `aria-expanded`; **Escape now closes it** (fixed this pass) |
| 5 | Reflow / zoom | Viewport 640px (200%) and 320px (400%) on all pages | `scrollWidth === clientWidth`, zero horizontal overflow |
| 6 | Text spacing | WCAG override stylesheet injected (0.12em/0.16em/1.5) | No content loss beyond the pre-existing intentional review clamp |
| 7 | Contrast — text on solids | axe color-contrast + palette measurement | 0 failures; every text/background pair ≥4.5:1 (or ≥3:1 for large text) |
| 8 | Contrast — text over photo | Pixel measurement of the rendered background beneath the hero/title text (text hidden, background sampled) | **4.12:1** worst case vs 3:1 required for the large title type |
| 9 | Non-text contrast | Computed-value audit of focus rings, arrows, dots | All ≥3:1 after this pass |
| 10 | Caption status | YouTube player-response inspection of all four video IDs | 2 videos ASR-only, 2 with none → §4.1 |
| 11 | Regression | `verify.py` (159 content/regression checks) | ALL CHECKS PASSED |
| 12 | Visual parity | Full-page screenshots (desktop + mobile) before/after each change, pixel-diffed | Changes confined to the intended areas; see README §6f |

## 6. Third-party embedded content

The site embeds: YouTube players (4), a Google Map, a Facebook page plugin,
and the Wellness.com profile badge. Their internal content cannot be audited
from the parent page (axe reports `frame-tested` for each). The site's
obligations for these embeds are: they are labelled with unique `title`
attributes (fixed this pass), they do not trap keyboard focus, and they are
not the sole path to any information (phone, address, and booking all appear
as text). Their internal captions are covered by §4.1; their internal focus
indicators by §4.2.

## 7. Note on the UserWay widget

The live site (and this recreation, preserving the client's setup) loads the
client's UserWay accessibility widget script. Overlay widgets are not a
substitute for an accessible site: this recreation achieves its conformance in
the underlying markup and styles, and the widget is treated as a user-selected
extra, not as the conformance mechanism.

## 8. Maintenance and feedback

- The **contact page carries a public Accessibility statement** with a direct
  phone number for reporting barriers, so users have a human remediation path
  (added 2026-10-12).
- Re-run the §5 command set after any content or template change; the
  accessibility checks are part of `verify.py`'s regression suite.
- The two open items in §4 have named owners: captions (client, YouTube
  account), search-box wiring (client decision).

*Prepared for Avery Acupuncture · reproduction and redistribution to counsel,
insurers, or auditors is intended and permitted.*
