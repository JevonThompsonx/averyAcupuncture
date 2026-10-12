#!/usr/bin/env python3
"""
Avery Acupuncture — static site builder.

Regenerates the full site from the recovered content inventory so the
client's words are preserved verbatim and the site can be rebuilt/edited
without any third-party tooling.

Usage:  python3 build.py
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.abspath(__file__))
INV = json.load(open(os.path.join(ROOT, "recovered", "content-inventory.json")))
REVIEWS = json.load(open(os.path.join(ROOT, "recovered", "reviews.json")))

BOOKING = "https://patient.unifiedpractice.com/avery-acupuncture-natural-medicine-inc"
PHONE_DISPLAY = "(805) 400-9723"
PHONE_TEL = "805-400-9723"
MAP_SRC = ('https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3242.823179779206'
           '!2d-120.69375458445003!3d35.63208534027264!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1'
           '!3m3!1m2!1s0x80ecc55e6350d303%3A0x7430f658ca4bd501!2s1704%20Spring%20St%20%23202%2C'
           '%20Paso%20Robles%2C%20CA%2093446%2C%20USA!5e0!3m2!1sen!2sin!4v1577686125064'
           '!5m2!1sen!2sin')
MAP_TITLE = "Map of Avery Acupuncture, 1704 Spring Street Suite 202, Paso Robles, CA"
FB_SRC = ('https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com'
          '%2FAvery-Acupuncture-Natural-Medicine-128162903891118%2F%3Ffref%3Dnf&tabs=timeline'
          '&width=275&height=370&small_header=false&adapt_container_width=true&hide_cover=false'
          '&show_facepile=false&appId')
FB_TITLE = "Avery Acupuncture on Facebook"

PLAY_ICON = ('<svg class="embed-facade__icon" viewBox="0 0 24 24" aria-hidden="true" '
             'focusable="false"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>')


def embed_facade(variant, src, title, label, preview=None, pw=None, ph=None, allow=None,
                 sizes="(max-width: 860px) 100vw, 1162px"):
    """Click-to-load embed facade. The heavy third-party player (YouTube's
    ~1.6 MB of JS, the Google Maps API) is fetched only when the visitor
    asks for it; until then the frame shows the video's YouTube thumbnail
    or a screenshot of the live embed, so the page looks the same. On click
    the facade is swapped for the real iframe, matching the original markup
    exactly. (Lighthouse performance pass: keeps the players' JS, requests
    and cookies out of page load.)"""
    attrs = f' data-src="{esc(src)}" data-title="{esc(title)}"'
    if allow:
        attrs += f' data-allow="{esc(allow)}"'
    # NB: not named `img` — that would shadow the img() helper used below.
    preview_html = ''
    if preview:
        if preview.startswith("assets/"):
            # Our own preview screenshot: route it through the responsive
            # image helper so phones pull the width-appropriate AVIF/WebP
            # instead of the 1162px original (94 KB -> 17 KB on a 390px
            # viewport). Remote previews (YouTube thumbnails) have no local
            # variants and keep the plain <img>.
            # img() takes a bare assets/img/ filename (it adds the prefix).
            preview_html = img(preview[len("assets/img/"):], "", w=pw, h=ph,
                               cls="embed-facade__img", decorative=True,
                               sizes=sizes)
        else:
            dim = f' width="{pw}" height="{ph}"' if pw and ph else ''
            preview_html = (f'<img class="embed-facade__img" src="{esc(preview)}" alt=""{dim} '
                            'loading="lazy" decoding="async">')
    return (f'<div class="embed-facade embed-facade--{variant}"{attrs}>{preview_html}'
            f'<button type="button" class="embed-facade__btn" aria-label="{esc(label)}">'
            f'<span class="embed-facade__circle">{PLAY_ICON}</span></button></div>')


def yt_facade(variant, vid, title, label=None):
    """YouTube embed facade: thumbnail preview, real player on click."""
    return embed_facade(
        variant, f"https://www.youtube.com/embed/{vid}?autoplay=1&rel=0", title,
        label or f"Play video: {title}",
        preview=f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", pw=480, ph=360,
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture")


def map_facade(variant):
    """Google Maps embed facade: screenshot preview, live map on click."""
    return embed_facade(variant, MAP_SRC, MAP_TITLE,
                        f"Show interactive map: {MAP_TITLE}",
                        preview="assets/img/map-embed-preview.jpg", pw=1162, ph=451)


def fb_slot():
    """Facebook page-plugin slot: the plugin loads only once the footer
    scrolls into view (js/main.js defers it), so its ~390 KB of JS and
    autoplaying video stay out of page load. Renders the same plugin
    markup once loaded."""
    return f'<div class="fb-slot" data-src="{esc(FB_SRC)}" data-title="{esc(FB_TITLE)}"></div>'


CAL_ICON = ('<svg viewBox="0 0 20 19" fill="none" aria-hidden="true" focusable="false">'
            '<rect x="1.5" y="3" width="17" height="14.5" rx="1.5" stroke="#fff" stroke-width="2"/>'
            '<line x1="1.5" y1="7.5" x2="18.5" y2="7.5" stroke="#fff" stroke-width="2"/>'
            '<line x1="6" y1="1" x2="6" y2="5" stroke="#fff" stroke-width="2" stroke-linecap="round"/>'
            '<line x1="14" y1="1" x2="14" y2="5" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>')
BOOKING_PREVIOUS = "https://patient.unifiedpractice.com/avery-acupuncture-natural-medicine-inc/booking/previous-visit"
# Public origin of THIS rebuild (used for canonicals, sitemap, OG URLs).
# If the site ever moves to its own domain, update this one constant.
SITE_URL = "https://avery.jsquaredadventures.com"
# Natural image dimensions (measured once) so width/height attributes can
# reserve layout space (no CLS) while CSS scales images down responsively.
DIMS = {
    "veronica.jpg": (450, 302), "IMG_3467-min.jpg": (2048, 1152),
    "IMG_3507.jpg": (1500, 844), "avery-acupuncture-office.jpg": (1000, 628),
    "48.png": (410, 235), "Veronica13-e12809438349151.jpg": (410, 235),
    "proofs-0096.jpg": (410, 274), "proofs-0024.jpg": (410, 614),
    "proofs-0042.jpg": (410, 274), "proofs-0071.jpg": (410, 614),
    "proofs-0068.jpg": (410, 614), "proofs-0063.jpg": (410, 614),
    "avery-herbs.jpg": (1042, 1389),
    "veronica-avery-acupuncture-treatment-room1.jpg": (800, 1041),
    "13.png": (410, 235),
}
# Responsive image variants manifest (written by build_images.py). Absent when
# variants have not been generated — build.py then emits plain <img> markup.
def _load_variants():
    try:
        return json.load(open(os.path.join(ROOT, "assets", "img", "variants.json")))
    except (OSError, ValueError):
        return {}

VARIANTS = _load_variants()

JSONLD = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"MedicalClinic",
"name":"Avery Acupuncture & Natural Medicine, Inc.",
"description":"Acupuncture and Natural Medicine in Paso Robles, CA.",
"url":"https://averyacupuncture.com/",
"telephone":"+1-805-400-9723",
"address":{"@type":"PostalAddress","streetAddress":"1704 Spring Street Suite 202",
"addressLocality":"Paso Robles","addressRegion":"CA","addressCountry":"US"},
"geo":{"@type":"GeoCoordinates","latitude":35.63208534027264,"longitude":-120.69375458445003},
"openingHoursSpecification":[
{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Thursday"],"opens":"08:30","closes":"17:00"},
{"@type":"OpeningHoursSpecification","dayOfWeek":"Friday","opens":"08:30","closes":"16:30"}],
"sameAs":["https://www.facebook.com/Avery-Acupuncture-Natural-Medicine-128162903891118/",
"https://www.yelp.com/biz/avery-acupuncture-and-natural-medicine-paso-robles"]}
</script>"""

NAV = [
    ("Meet Veronica Avery", "about-veronica.html", []),
    ("Conditions Treated", "conditions-treated.html", []),
    ("New Patients", "about-treatment.html", [
        ("About Treatment", "about-treatment.html"),
        ("Office Policy", "office-policy.html"),
    ]),
    ("Contact", "contact.html", []),
]
# Bottom colophon nav mirrors the live site: the four parent items only.
FOOTER_NAV = [(label, href) for label, href, _ in NAV]

TITLES = {
    "index": "Avery Acupuncture | Acupuncture &amp; Natural Medicine Paso Robles",
    "about-veronica": "About Veronica | Avery Acupuncture",
    "about-treatment": "About Treatment | Avery Acupuncture",
    "conditions-treated": "Conditions Treated | Avery Acupuncture",
    "contact": "Contact | Avery Acupuncture",
    "office-policy": "Office Policy | Avery Acupuncture",
    "privacy-policy": "Privacy Policy | Avery Acupuncture",
    "news": "News | Avery Acupuncture",
}

# ---------------------------------------------------------------------------
# helpers

def esc(t):
    return html.escape(t, quote=False)

def localize(text):
    """Rewrite live-site asset URLs to local relative paths + auto-link phones."""
    def repl(m):
        return "assets/img/" + os.path.basename(m.group(0))
    text = re.sub(r'(?:https?:)?//averyacupuncture\.com/wp-content/uploads/[^\s"\')]+', repl, text)
    # link phone numbers (both "(805) 400-9723" and "805-400-9723" styles)
    text = re.sub(r'\(?\b(805)[.\-) ]*(\d{3})[.\- ]*(\d{4})\b',
                  r'<a href="tel:\1\2\3">\g<0></a>', text)
    return text

def anchor_headings(blocks, page):
    """Give h2s on about-treatment an id for the New Patients anchor."""
    out = []
    for b in blocks:
        if page == "about-treatment" and b.get("type") == "h2" and b["text"].strip() == "New Patients":
            out.append({"type": "h2", "text": b["text"], "id": "new-patients"})
        else:
            out.append(b)
    return out

def render_blocks(blocks, page, imgs):
    """Render the recovered block inventory to HTML."""
    buf = []
    for b in blocks:
        t = b["type"]
        if t in ("h1", "h2", "h3", "h4", "h5", "h6"):
            bid = f' id="{b["id"]}"' if b.get("id") else ""
            buf.append(f'<{t}{bid}>{localize(esc(b["text"]))}</{t}>')
        elif t == "p":
            body = localize(esc(b.get("text", "")))
            if body.strip():
                buf.append(f"<p>{body}</p>")
        elif t == "list":
            tag = "ol" if b.get("ordered") else "ul"
            items = []
            for it in b["items"]:
                li = localize(esc(it["text"]))
                if it.get("sub"):
                    sub = "".join(f"<li>{localize(esc(s))}</li>" for s in it["sub"])
                    li += f"<ul>{sub}</ul>"
                items.append(f"<li>{li}</li>")
            buf.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
        elif t == "blockquote":
            buf.append(f'<blockquote>{localize(esc(b["text"]))}</blockquote>')
    return "\n".join(buf)

def gallery(imgs, cls="gallery", skip=()):
    """Render a responsive image gallery, skipping header/footer chrome."""
    skip = tuple(skip) + ("avery-logo", "fav-icon", "Unknown.png", "grw", "guest.png")
    seen, out = set(), []
    for i in imgs:
        src = i.get("src") or ""
        base = os.path.basename(src)
        if any(s in base for s in skip) or base in seen:
            continue
        path = os.path.join(ROOT, "assets", "img", base)
        if not os.path.exists(path):
            continue
        seen.add(base)
        alt = esc(i.get("alt") or "")
        out.append(f'<figure class="{cls}__item"><img src="assets/img/{base}" alt="{alt}" loading="lazy"></figure>')
    return f'<div class="{cls}">' + "".join(out) + "</div>"

# ---------------------------------------------------------------------------
# page chrome

def header(active, variant="wide"):
    items = []
    for label, href, sub in NAV:
        target = href.split("#")[0]
        cur = ' aria-current="page"' if target == active else ""
        if sub:
            subs = "".join(f'<li><a href="{h}"><span>{esc(l)}</span></a></li>' for l, h in sub)
            items.append(
                f'<li class="has-sub"><a href="{href}"{cur} aria-haspopup="true">'
                f"<span>{esc(label)}</span></a>"
                f'<ul class="sub-menu">{subs}</ul></li>')
        else:
            items.append(f'<li><a href="{href}"{cur}><span>{esc(label)}</span></a></li>')
    wrap = "wrap-news" if variant == "news" else "wrap"
    return f"""
<header class="site-header{' site-header--news' if variant == 'news' else ''}">
  <!-- Skip link lives INSIDE the header (banner landmark), not as a body
       child: a page-level link outside a landmark is flagged by axe's `region`
       rule the moment a proxy/CDN injects even one hidden anchor ahead of it
       (Cloudflare injects one on every response, which made the rule fire on
       the live site while it passed locally). Inside the banner it is
       landmark-wrapped on both local and proxied responses, and it stays the
       first focusable element in the page. Pixel-verified identical: `.skip`
       is position:absolute, so the header (position:relative, y=0, full
       width) gives it the same box it had against the initial containing
       block. -->
  <a class="skip" href="#main">Skip to main content</a>
  <div class="topbar">
    <div class="{wrap} topbar__inner">
      <p class="nav-phone"><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> <a class="nav-book-online" href="{BOOKING}" target="_blank" rel="noopener">BOOK ONLINE NOW</a></p>
    </div>
  </div>
  <div class="navbar">
    <div class="{wrap} navbar__inner">
      <a class="brand" href="index.html" aria-label="Avery Acupuncture — home">
        {img("avery-logo-transparent.png", "Avery Acupuncture", 245, 192)}
      </a>
      <button class="nav-toggle" aria-expanded="false" aria-controls="primary-nav" aria-label="Toggle navigation">
        <span></span><span></span><span></span>
      </button>
      <nav id="primary-nav" class="site-nav" aria-label="Primary">
        <ul>
          {''.join(items)}
        </ul>
      </nav>
    </div>
  </div>
</header>"""

def footer(variant="wide"):
    foot_links = "".join(f'<li><a href="{h}">{esc(l)}</a></li>' for l, h in FOOTER_NAV)
    return f"""
<footer class="site-footer{' site-footer--news' if variant == 'news' else ''}">
  <div class="{'wrap-news' if variant == 'news' else 'wrap'} site-footer__widgets">
    <section class="footer-widget" aria-label="Facebook">
      <h2 class="footer-widget__title">Like Us On Facebook</h2>
      {fb_slot()}
    </section>
    <section class="footer-widget footer-widget--center" aria-label="Wellness and Yelp profiles">
      <div class="wellness-badge">
        <center>
        {img("wellness-badge-preview.jpg", "Wellness.com profile badge: 5 out of 5 stars, "
              "51 reviews", 160, 176, cls="wellness-badge-img")}<a class="wellness-link" href="https://www.wellness.com">Wellness.com</a><a class="wellness-link" href="https://www.wellness.com/dir/3245076/acupuncture-specialist/ca/paso-robles/veronica-avery-avery-acupuncture--natural-medicine-lac">My Profile</a>
        </center>
        <p><a href="https://www.yelp.com/biz/avery-acupuncture-and-natural-medicine-paso-robles" target="_blank" rel="noopener">{img("Unknown.png", "People love us on Yelp", 100, 100)}</a></p>
      </div>
    </section>
    <section class="footer-widget" aria-label="Video">
      <div class="footer-widget__video">
        {yt_facade("ytfoot", "YAffgKRg6P0", "Avery Acupuncture video")}
      </div>
    </section>
  </div>
  <div class="{'wrap-news' if variant == 'news' else 'wrap'} site-footer__bottom">
    {img("avery-logo-black-wcolor2.png", "Avery Acupuncture", 180, 161, cls="footer-logo")}    <p>&nbsp;</p>
    <!-- NOTE: "Acupunture" (missing c) is the live site's own spelling,
         preserved verbatim. Jolly Creative Agency was the previous
         developer. Keep or remove this credit per the client's contract. -->
    <p>Copyright&nbsp;&copy; 2026 by Avery Acupunture- All Rights Reserved.&nbsp; | <a href="https://jollycreativeagency.com/" target="_blank" rel="noopener">Jolly Creative Agency</a></p>
  </div>
  <nav class="{'wrap-news' if variant == 'news' else 'wrap'} footer-menu" aria-label="Footer">
    <ul>
      {foot_links}
    </ul>
  </nav>
</footer>"""

def asset_ver(path):
    """Cache-busting query derived from file mtime, so the Cloudflare edge
    (which caches css/js by URL) picks up a new revision immediately."""
    full = os.path.join(ROOT, path)
    try:
        return f"{path}?v={int(os.path.getmtime(full))}"
    except OSError:
        return path


def minify_css(src, dst):
    """Write dst from src. Regex-based and conservatively scoped to this
    project's constructs (verified by the visual regression diff); the
    source file stays the editable original. The min file is what pages
    load (~15% smaller, no more "unminified CSS")."""
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return
    text = open(src, encoding="utf-8").read()
    out = re.sub(r"/\*.*?\*/", "", text, flags=re.S)   # comments
    out = re.sub(r"\s+", " ", out)                     # collapse whitespace
    out = re.sub(r"\s*([{};:,>~])\s*", r"\1", out)     # around structural chars
    out = out.replace(";}", "}")                       # trailing semicolons
    with open(dst, "w", encoding="utf-8") as f:
        f.write(out.strip())
    print(f"wrote {os.path.relpath(dst, ROOT)} ({len(out):,} bytes from {len(text):,})")


def css_href(path):
    """<link> tag for a CSS file, minified on demand (both the shared sheet
    and per-page sheets). Keeps the Lighthouse 'minify CSS' audit clean."""
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return ""
    dst = full[:-len(".css")] + ".min.css"
    minify_css(full, dst)
    return f'<link rel="stylesheet" href="{asset_ver(path[:-len(".css")] + ".min.css")}">'

def font_preloads():
    """Preload the two most-used latin faces so text renders in the right
    face immediately (fonts are self-hosted since the Lighthouse pass —
    see build_fonts.py)."""
    css_path = os.path.join(ROOT, "css", "fonts.css")
    if not os.path.exists(css_path):
        return ""
    css = open(css_path, encoding="utf-8").read()
    latin = "U+0000-00FF"
    picks = []
    for fam, weight in (("Open Sans", "400"), ("EB Garamond", "400")):
        m = re.search(
            r"@font-face\s*{[^}]*font-family:\s*'" + re.escape(fam) + r"'[^}]*"
            r"font-style:\s*normal[^}]*font-weight:\s*" + weight + r"[^}]*"
            r"url\((\.\./assets/fonts/[^)]+\.woff2)\)[^}]*" + re.escape(latin),
            css)
        if m:
            picks.append(m.group(1).replace("../", ""))
    return "\n".join(
        f'<link rel="preload" href="{p}" as="font" type="font/woff2" crossorigin>' for p in picks)


def page(name, active, body, description):
    fname = name + ".html"
    # Per-page stylesheet (optional): css/pages/<name>.css. Lets a page own
    # its responsive rules without touching the shared sheet. Linked only
    # when it exists; the file must be committed to ship.
    page_css_link = css_href(os.path.join("css", "pages", name + ".css"))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLES[name]}</title>
<meta name="description" content="{esc(description)}">
<link rel="icon" type="image/png" href="assets/img/fav-icon.png">
<link rel="apple-touch-icon" href="assets/img/fav-icon.png">
<link rel="canonical" href="{SITE_URL}/{fname}">
<meta property="og:title" content="{TITLES[name]}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/{fname}">
<meta property="og:image" content="{SITE_URL}/assets/img/Bamboo.jpg">
<meta property="og:site_name" content="Avery Acupuncture">
<meta name="twitter:card" content="summary_large_image">
<link rel="dns-prefetch" href="https://www.youtube.com">
<link rel="dns-prefetch" href="https://www.facebook.com">
<link rel="dns-prefetch" href="https://www.google.com">
<link rel="dns-prefetch" href="https://www.wellness.com">
<!-- Video facade thumbnails are served from YouTube's image CDN (the same
     thumbnail the player shows before play), so the preview paints fast. -->
<link rel="preconnect" href="https://i.ytimg.com">
{font_preloads()}
<link rel="stylesheet" href="{asset_ver('css/fonts.css')}">
{JSONLD}
{css_href('css/style.css')}
{page_css_link}
<!-- Google Analytics (client's existing GA4 measurement ID) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-QHC78WR2RK"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-QHC78WR2RK');</script>
<!-- Accessibility widget (client's own UserWay account, same as the live
     site). Deferred to the load event: it was render-blocking on every page
     and the widget works identically once the page is up. -->
<script>
window.addEventListener('load', function () {{
  var s = document.createElement('script');
  s.src = 'https://cdn.userway.org/widget.js';
  s.setAttribute('data-account', 'veWiK0ku6v');
  document.head.appendChild(s);
}});
</script>
</head>
<body>
{header(active) if name != 'news' else ''}
{body if name == "news" else f"<main id=\"main\">\n{body}\n</main>\n" + footer()}
<script src="{asset_ver('js/main.js')}"></script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# special sections

def hero():
    # Hero image is a real <img> (fetchpriority=high) instead of a CSS
    # background: the browser discovers it during initial parse (no LCP
    # discovery delay) and gets responsive AVIF/WebP derivatives.
    hero_img = img("Bamboo-hero.jpg", "", eager=True, decorative=True, sizes="100vw", cls="hero__img")
    return f"""
<section class="hero" id="top">
  {hero_img}
  <div class="wrap">
    <h1 class="hero__quote">"Natural forces within us are the true healers of disease."<span class="hero__cite">-Hippocrates</span></h1>
  </div>
</section>

<section class="intro-band">
  <div class="wrap-1000">
    <h2>Veronica Avery Licensed Acupuncturist and Herbalist</h2>
    <p><strong>Practicing Traditional Chinese Medicine in Paso Robles since 2010.</strong></p>
    <p>We serve residents of San Luis Obispo county and Monterey County<br>
including Paso Robles, Templeton, Atascadero, King City, Lake Nacimiento.</p>
  </div>
</section>

<section class="cta-row">
  <div class="wrap-1000 cta-row__grid">
    <div class="cta-row__text">
      <h2>Make An Appointment Today</h2>
      <div class="cta-row__lead"><p>We are currently accepting new patients, and we look forward to meeting you.</p></div>
      <a class="btn" href="{BOOKING}" target="_blank" rel="noopener">Book Now</a>
    </div>
    <div class="video-frame">
      {yt_facade("yt", "z-_mGPgrBok", "Avery Acupuncture introduction video")}
    </div>
  </div>
</section>"""

def stars(n=5, cls="stars"):
    return f'<span class="{cls}" role="img" aria-label="{n} out of 5 stars">' + "★" * n + "</span>"

def reviews_section():
    cards = []
    for r in REVIEWS:
        avatar = ""
        base = os.path.basename(r.get("img") or "")
        if base and os.path.exists(os.path.join(ROOT, "assets", "img", base)):
            avatar = img(base, "", 44, 44, cls="grw__avatar", decorative=True)
        cards.append(f"""
      <figure class="grw__card">
        {img("grw-g-logo.png", "Google review", 20, 20, cls="grw__g")}
        <div class="grw__head">{avatar}
          <div><a class="grw__name" href="{r['profile']}" target="_blank" rel="noopener">{esc(r['name'])}</a>
          <span class="grw__time">{esc(r['time'])}</span></div>
        </div>
        <div class="grw__stars">{stars()}</div>
        <blockquote class="grw__text">{esc(r['text'])}</blockquote>
      </figure>""")
    return f"""
<section class="reviews" id="reviews">
  <div class="reviews-hr"><div class="wrap-1000"><div class="reviews-hr__pad"><hr class="rule-reviews"></div></div></div>
  <div class="wrap">
    <div class="grw">
      <p class="reviews__label">We Care About Our Patients</p>
      <div class="grw__summary">
        <div class="grw__head">{img("grw-business.jpg", "Avery Acupuncture office", 44, 44, cls="grw__avatar")}
          <div><span class="grw__biz">Avery Acupuncture &amp; Natural Medicine, Inc.</span></div>
        </div>
        <p class="grw__score">5.0 {stars()}</p>
        <p class="grw__based">Based on 55 reviews</p>
        <p class="grw__powered">powered by {img("grw-google-logo.png", "Google", 60, 20)}</p>
        <p><a class="grw__write" href="https://search.google.com/local/writereview?placeid=ChIJuRLeDkPF7IARdquigwOGvhE" target="_blank" rel="noopener">review us on {img("grw-g-logo.png", "Google", 16, 16)}</a></p>
      </div>
      <div class="grw__track">
        <button class="grw__arrow grw__prev" type="button" aria-label="Previous reviews"><span aria-hidden="true">&lsaquo;</span></button>
        <div class="grw__slider">
{''.join(cards)}
        </div>
        <button class="grw__arrow grw__next" type="button" aria-label="Next reviews"><span aria-hidden="true">&rsaquo;</span></button>
        <div class="grw__dots" role="group" aria-label="Review pages">
          <button class="grw__dot is-active" type="button" data-page="0" aria-label="Reviews page 1"></button>
          <button class="grw__dot" type="button" data-page="1" aria-label="Reviews page 2"></button>
          <button class="grw__dot" type="button" data-page="2" aria-label="Reviews page 3"></button>
        </div>
      </div>
    </div>
  </div>
</section>"""

def location_section():
    return """
<section class="loc-band" id="location">
  <div class="wrap">
    <h2>Centrally located in Paso Robles</h2>
    <p>We serve residents of San Luis Obispo county and Monterey County including Paso Robles, Templeton, Atascadero, King City, Lake Nacimiento.</p>
  </div>
</section>
<section class="loc-info">
  <div class="wrap-1000 loc-info__grid">
    <div>
      <h2>Address</h2>
      <p><br><strong>1704 Spring Street Suite 202<br>Paso Robles, CA</strong></p>
    </div>
    <div>
      <h2>Hours</h2>
      <!-- NOTE: homepage and contact page on the live site list different hours.
           Client to confirm the correct schedule. -->
      <p></p>
      <p><strong>Monday<br></strong>8:00 to 4:00 p.m.</p>
      <p><strong>Tuesday and Thursday<br></strong>8:00 to 5:30 p.m.</p>
    </div>
    <div>
      <h2>Phone</h2>
      <p><br><strong>(805) 400-9723</strong></p>
    </div>
  </div>
  <div class="wrap-1000 rule-wrap"><hr class="rule"></div>
</section>
<div class="map-full">""" + map_facade("map") + """</div>"""

# ---------------------------------------------------------------------------
# page bodies

def page_index():
    return hero() + reviews_section() + location_section()

# ---------------------------------------------------------------------------
# inner page building blocks

def band(title, height):
    """Full-width Bamboo title band, centered white serif title. The photo is
    a real <img> (like the hero) so the browser discovers it during initial
    parse — a CSS background made Lighthouse's lcp-discovery audit fail on
    every inner page."""
    band_img = img("Bamboo-hero.jpg", "", eager=True, decorative=True, sizes="100vw", cls="page-band__img")
    return f"""
<section class="page-band" style="height:{height}px">
  {band_img}
  <h1 class="page-band__title">{esc(title)}</h1>
</section>"""

def xtext(blocks):
    """Render recovered p/list blocks as an X-theme text column."""
    return render_blocks(blocks, "", {})

def img(src, alt, w=None, h=None, sizes=None, cls="", eager=False, decorative=False):
    """Responsive image: AVIF + WebP <source>s over a width/height-reserved
    <img> fallback pointing at the untouched original (zero CLS, works in
    every browser). Degrades to a plain <img> when variants.json is absent.
    sizes: srcset sizes attribute (drives candidate selection)."""
    if w is None and src in DIMS:
        w, h = DIMS[src]
    dim = f' width="{w}" height="{h}"' if w and h else ""
    alt_attr = ' alt=""' if decorative else f' alt="{esc(alt)}"'
    cls_attr = f' class="{cls}"' if cls else ""
    prio = " fetchpriority=\"high\"" if eager else ""
    loading = "eager" if eager else "lazy"
    if not sizes:
        sizes = "(max-width: 860px) 100vw, 560px"
    v = VARIANTS.get(src, {})
    widths = v.get("widths", [])
    stem = os.path.splitext(src)[0]
    if widths:
        nat_w = v.get("natural", [w or 0, h or 0])[0]
        tail = f"assets/img/{src} {nat_w}w"
        def srcset(fmt):
            return ", ".join([f"assets/img/{stem}-{x}w.{fmt} {x}w" for x in widths] + [tail])
        return (
            f'<picture>'
            f'<source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
            f'<img src="assets/img/{src}" srcset="{srcset("jpg")}" sizes="{sizes}"'
            f'{cls_attr}{alt_attr}{dim} loading="{loading}" decoding="async"{prio}>'
            f'</picture>')
    if os.path.exists(os.path.join(ROOT, "assets", "img", stem + ".webp")):
        # fixed-size asset (logo/avatar/badge): single-size modern variants
        return (
            f'<picture>'
            f'<source type="image/avif" srcset="assets/img/{stem}.avif">'
            f'<source type="image/webp" srcset="assets/img/{stem}.webp">'
            f'<img src="assets/img/{src}"{cls_attr}{alt_attr}{dim} loading="{loading}" decoding="async"{prio}>'
            f'</picture>')
    return f'<img src="assets/img/{src}"{cls_attr}{alt_attr}{dim} loading="{loading}" decoding="async"{prio}>'

def page_about_veronica():
    d = INV["about-veronica"]
    b = d["blocks"]
    t1 = xtext(b[1:4])    # three opening paragraphs (brown)
    t2 = xtext(b[4:10])   # remaining six paragraphs (black on the live page)
    return f"""
{band("About Veronica", 248)}
<section class="av-photo">
  {img("veronica.jpg", "Veronica Avery, Licensed Acupuncturist and Herbalist", 450, 302, sizes="(max-width: 860px) 100vw, 450px").replace("<img ", '<img class="av-portrait fx" ')}
</section>
<section class="av-body">
  <div class="wrap-max">
    <div class="x-text x-text--shift fx fx--l">{t1}</div>
    <div class="av-pair fx">
      {img("IMG_3467-min.jpg", "Veronica Avery treating a patient")}
      {img("IMG_3507.jpg", "Inside the Avery Acupuncture practice")}
    </div>
    <div class="x-text x-text--ink fx fx--l">{t2}</div>
  </div>
</section>"""

def page_about_treatment():
    d = INV["about-treatment"]
    b = d["blocks"]
    seconds = b[16]["text"]
    herbs_list = [x for x in b if x["type"] == "list"][0]
    np_first = (
        f'<p><strong>{esc(seconds)}</strong></p>'
        + render_blocks(b[17:20], "", {})
        + render_blocks([b[20]], "", {})
    )
    return f"""
{band("About Treatment", 209)}

<section class="at-intro">
  <div class="wrap-max">
    <h2 class="x-h2 fx fx--r">Expert Acupuncture Care with Veronica Avery</h2>
    <hr class="x-hr">
  </div>
</section>

<section class="at-sec">
  <div class="wrap-1000 x-row">
    <div class="fx fx--l">
      <h3 class="x-h3">Comfortable and Complete Care</h3>
      <div class="x-text">{xtext(b[3:5])}</div>
    </div>
    <div class="fx fx--r x-imgpad">
      {img("avery-acupuncture-office.jpg", "The Avery Acupuncture treatment office")}
    </div>
  </div>
</section>

<section class="at-sec at-sec--center">
  <div class="wrap-max">
    <hr class="x-hr">
    <h3 class="x-h3">Acupuncture</h3>
    <div class="x-text">{xtext([b[6]])}</div>
  </div>
</section>

<div class="at-imgrow">
  <div class="wrap-1000 x-row x-row--fixed">
    <div class="fx fx--l">{img("48.png", "Acupuncture treatment in progress")}</div>
    <div class="fx fx--r">{img("Veronica13-e12809438349151.jpg", "Veronica Avery performing acupuncture")}</div>
  </div>
</div>

<section class="at-sec at-sec--center">
  <div class="wrap-max">
    <hr class="x-hr">
    <h3 class="x-h3">Cupping</h3>
    <div class="x-text">{xtext([b[8]])}</div>
  </div>
</section>

<div class="at-imgrow">
  <div class="wrap-1000 x-row x-row--3">
    <div class="fx">{img("proofs-0096.jpg", "Cupping therapy session", sizes="(max-width: 860px) 100vw, 360px")}</div>
    <div class="fx">{img("proofs-0024.jpg", "Fire cupping technique", sizes="(max-width: 860px) 100vw, 360px")}</div>
    <div class="fx">{img("proofs-0042.jpg", "Cupping glasses on a patient's back", sizes="(max-width: 860px) 100vw, 360px")}</div>
  </div>
</div>

<div class="at-imgrow">
  <div class="wrap-max x-row x-row--videos">
    <div class="x-video fx fx--l">
      {yt_facade("yt", "NODHaSuXo5c", "Avery Acupuncture treatment video, April 4 2024 (first of two)")}
    </div>
    <div class="x-video fx fx--r">
      {yt_facade("yt", "NjkSy0s9hz0", "Avery Acupuncture treatment video, April 4 2024 (second of two)")}
    </div>
  </div>
</div>

<section class="at-sec at-sec--center at-sec--massage">
  <div class="wrap-max">
    <hr class="x-hr">
    <h3 class="x-h3">Massage</h3>
    <div class="x-text">{xtext([b[10]])}</div>
  </div>
</section>

<div class="at-imgrow at-imgrow--last">
  <div class="wrap-1000 x-row x-row--3">
    <div class="fx">{img("proofs-0071.jpg", "Massage therapy at Avery Acupuncture", sizes="(max-width: 860px) 100vw, 360px")}</div>
    <div class="fx">{img("proofs-0068.jpg", "Therapeutic massage session", sizes="(max-width: 860px) 100vw, 360px")}</div>
    <div class="fx">{img("proofs-0063.jpg", "Massage therapy treatment", sizes="(max-width: 860px) 100vw, 360px")}</div>
  </div>
</div>

<section class="at-hrspace">
  <div class="wrap-max"><hr class="x-hr"></div>
</section>

<div class="at-imgrow">
  <div class="wrap-1000 x-row x-row--herbs">
    <div class="fx fx--l x-imgpad">{img("avery-herbs.jpg", "Chinese herbal medicines", sizes="(max-width: 860px) 100vw, 307px")}</div>
    <div class="fx fx--r">
      <h3 class="x-h3">Herbs</h3>
      <div class="x-text">{xtext([b[12]])}</div>
      <ul class="x-list">
        {"".join(f"<li>{localize(esc(it['text']))}</li>" for it in herbs_list["items"])}
      </ul>
    </div>
  </div>
</div>

<section class="at-np">
  <div class="wrap-max">
    <h2 class="x-h2 fx fx--r" id="new-patients">New Patients</h2>
    <hr class="x-hr">
  </div>
  <div class="wrap-1000 x-row">
    <div class="fx fx--l x-imgpad">
      {img("veronica-avery-acupuncture-treatment-room1.jpg", "Avery Acupuncture treatment room")}
    </div>
    <div class="fx fx--r">
      <h3 class="x-h3">Initial Visit</h3>
      <div class="x-text">{np_first}</div>
    </div>
  </div>
  <div class="wrap-1000 x-row">
    <div class="fx fx--l">
      <h3 class="x-h3 x-h3--sub">Subsequent Visits</h3>
      <div class="x-text">{xtext([b[22]])}</div>
    </div>
    <div class="fx fx--r x-imgpad55">
      {img("13.png", "Follow-up acupuncture treatment")}
    </div>
  </div>
  <div class="wrap-max"><hr class="x-hr"></div>
</section>

<section class="x-cta-band">
  <div class="x-callout x-callout--400 x-callout--at fx">
    <h2>Schedule an Appointment</h2>
    <p>{esc(b[24]["text"])}</p>
    <a class="x-btn" href="{BOOKING}" target="_blank" rel="noopener">{CAL_ICON}Book Now</a>
  </div>
</section>"""

def page_conditions():
    d = INV["conditions-treated"]
    b = d["blocks"]
    def item(h, p):
        return f"""
      <div class="ct-item fx">
        <h2>{esc(h)}</h2>
        <hr class="x-hr x-hr--light">
        <p>{localize(esc(p))}</p>
      </div>"""
    col1 = (item(b[1]["text"], b[2]["text"]) + item(b[3]["text"], b[4]["text"]) + item(b[5]["text"], b[6]["text"])
            + '\n      <hr class="x-gap" aria-hidden="true">')
    col2 = (item(b[7]["text"], b[8]["text"])
            + item(b[9]["text"], b[10]["text"]).replace('class="ct-item fx"', 'class="ct-item ct-item--gastro fx"')
            + item(b[11]["text"], b[12]["text"]))
    return f"""
{band("Conditions Treated", 258)}
<section class="ct-sec">
  <div class="wrap-1000 x-row">
    <div class="fx fx--l">{col1}</div>
    <div class="fx fx--r">{col2}</div>
  </div>
</section>
<section class="ct-cta-band">
  <div class="x-callout x-callout--450 fx">
    <h2>{esc(b[13]["text"])}</h2>
    <p>{esc(b[14]["text"])}</p>
    <a class="x-btn" href="{BOOKING}" target="_blank" rel="noopener">{CAL_ICON}Schedule Now</a>
  </div>
</section>"""

def page_contact():
    """Contact page — hand-built from the live markup: the live FAQ is a
    3-question accordion and the hours include a Friday line, neither of
    which the generic block renderer captured."""
    return f"""
{band("Visit Us Today", 182)}
<section class="cp-sec">
  <div class="wrap-1000 x-row">
    <div class="fx fx--l">
      <h2 class="x-h2">Paso Robles</h2>
      <div class="x-text"><p>1704 Spring Street, Suite 202<br>Paso Robles, CA</p></div>
    </div>
    <div class="fx fx--r">
      <h2 class="x-h2">Hours</h2>
      <div class="x-text"><p><br><strong>Monday, Tuesday, Thursday:</strong> <span class="cp-hrs">8:30am-5:00pm</span><br></p><strong>Friday:</strong> <span class="cp-hrs">8:30-4:30</span></div>
    </div>
  </div>
  <div class="wrap-max">
    <hr class="x-hr">
    <h2 class="x-h2">Phone</h2>
    <div class="x-text"><p><a href="tel:{PHONE_TEL}">805.400.9723</a></p></div>
  </div>
</section>
<section class="cp-map">
  <div class="wrap-max">{map_facade("mapcp")}</div>
</section>
<section class="cp-sec">
  <div class="wrap-1000">
    <h2 class="x-h2">Accessibility</h2>
    <div class="x-text">
      <p>Avery Acupuncture is committed to making this website usable by
      everyone &mdash; including our older patients and people who use assistive
      technology such as screen readers, screen magnification, or keyboard-only
      navigation.</p>
      <p>This site is built and tested to meet the Web Content Accessibility
      Guidelines (WCAG) 2.1 Level AA &mdash; the standard referenced by the U.S.
      Department of Justice and California accessibility law &mdash; and it is
      re-checked whenever anything on it changes.</p>
      <p>If any part of this site is hard for you to use, please tell us. Call
      <a href="tel:{PHONE_TEL}">805.400.9723</a> and we will help you directly,
      fix the problem, and confirm the fix with you. We would much rather hear
      about a barrier than have you work around it.</p>
    </div>
  </div>
</section>
<section class="cp-faq">
  <h2 class="fx">FAQ</h2>
  <div class="cp-faq__list fx">
    <div class="cp-faq__item is-open">
      <button class="cp-faq__q" type="button" aria-expanded="true"><span class="cp-faq__icon">&times;</span>How do I book an appointment?</button>
      <div class="cp-faq__a">
        <div class="cp-faq__a-inner">
          <p>We are currently accepting new patients! Please call <strong>805-400-9723</strong> to schedule an appointment, or click the link below. We look forward to meeting you soon!</p>
          <p><a class="cp-faq__book" href="{BOOKING_PREVIOUS}" target="_blank" rel="noopener">Book an Appointment</a></p>
        </div>
      </div>
    </div>
    <div class="cp-faq__item">
      <button class="cp-faq__q" type="button" aria-expanded="false"><span class="cp-faq__icon">+</span>How do I cancel an appointment?</button>
      <div class="cp-faq__a">
        <div class="cp-faq__a-inner">
          <p>If you need to change or cancel your appointment please do so with 24 hours notice. With the exception of emergencies, failure to do so will result in being charged the full fee for your appointment.</p>
        </div>
      </div>
    </div>
    <div class="cp-faq__item">
      <button class="cp-faq__q" type="button" aria-expanded="false"><span class="cp-faq__icon">+</span>Do you accept insurance?</button>
      <div class="cp-faq__a">
        <div class="cp-faq__a-inner">
          <p>If you have insurance, please bring your insurance card with you. For your convenience, we will gladly call to verify your acupuncture coverage including eligibility and benefits.</p>
        </div>
      </div>
    </div>
  </div>
</section>"""

def page_policy():
    data = INV["office-policy"]
    b = data["blocks"]
    body = xtext(b[8:10])
    # Live markup keeps a <br> before the phone number (two-line paragraph).
    body = body.replace("please call: <a", "please call:<br>\n<a")
    return f"""
{band("Office Policy", 248)}
<section class="op-sec op-sec--first">
  <div class="wrap-max">
    <h2 class="x-h2 fx fx--r">Fees and Insurance</h2>
    <hr class="x-hr">
    <div class="x-text fx">{xtext(b[2:5])}</div>
  </div>
</section>
<section class="op-sec">
  <div class="wrap-max">
    <h2 class="x-h2 fx fx--r">Confidentiality</h2>
    <hr class="x-hr">
    <div class="x-text fx">{xtext([b[6]])}</div>
  </div>
</section>
<section class="op-sec">
  <div class="wrap-max">
    <h2 class="x-h2 fx fx--r">Missed Appointment Policy</h2>
    <hr class="x-hr">
    <div class="x-text fx">{body}</div>
  </div>
</section>"""

def page_privacy():
    data = INV["privacy-policy"]
    blocks = data["blocks"]
    body = render_blocks(blocks, "privacy-policy", data["images"])
    body = body.replace("<h1>", '<h1 class="pp-title">', 1)
    return f"""
<section class="pp">
  <div class="wrap-max">{body}</div>
</section>"""

def page_news():
    data = INV["news"]
    body = render_blocks(data["blocks"], "news", data["images"])
    return f"""
<div class="news-layout">
  <div class="news-col">
    {header("news.html", variant="news")}
    <main id="main">
      <article class="news-main">
        <h1>Nothing to Show Right Now</h1>
        <div class="x-text">{body}</div>
      </article>
    </main>
  </div>
  <aside class="news-side">
    <form class="news-search" role="search" action="news.html" method="get">
      <label for="news-search-input">Search</label>
      <input id="news-search-input" type="search" name="s" placeholder="Search">
    </form>
  </aside>
  <div class="news-footcol">
    {footer(variant="news")}
  </div>
</div>"""

PAGES = {
    "index.html":        ("index.html", page_index,       "Acupuncture & Natural Medicine in Paso Robles — Veronica Avery, Licensed Acupuncturist and Herbalist."),
    "about-veronica.html": ("about-veronica.html", page_about_veronica, "The story of Veronica Avery, Licensed Acupuncturist and Herbalist practicing Traditional Chinese Medicine in Paso Robles."),
    "about-treatment.html": ("about-treatment.html", page_about_treatment, "What to expect from acupuncture, cupping, massage, and Chinese herbal medicine at Avery Acupuncture."),
    "conditions-treated.html": ("conditions-treated.html", page_conditions, "Conditions treated at Avery Acupuncture: pain, immunity, pediatrics, emotional health, GI, women's health."),
    "contact.html":      ("contact.html", page_contact,          "Contact Avery Acupuncture in Paso Robles — address, hours, phone, and online booking."),
    "office-policy.html": ("office-policy.html", page_policy,     "Avery Acupuncture office policy: fees and insurance, confidentiality, missed appointments."),
    "privacy-policy.html": ("privacy-policy.html", page_privacy,  "Privacy policy for Avery Acupuncture."),
    "news.html":         ("news.html", page_news,          "News from Avery Acupuncture."),
}

def main():
    minify_css(os.path.join(ROOT, "css", "style.css"),
               os.path.join(ROOT, "css", "style.min.css"))
    for fname, (active, fn, desc) in PAGES.items():
        out = page(fname.split(".")[0], active, fn(), desc)
        with open(os.path.join(ROOT, fname), "w", encoding="utf-8") as f:
            f.write(out)
        print(f"wrote {fname} ({len(out):,} bytes)")

if __name__ == "__main__":
    main()
