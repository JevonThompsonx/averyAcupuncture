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
MAP_IFRAME = ('<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3242.823179779206'
              '!2d-120.69375458445003!3d35.63208534027264!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1'
              '!3m3!1m2!1s0x80ecc55e6350d303%3A0x7430f658ca4bd501!2s1704%20Spring%20St%20%23202%2C'
              '%20Paso%20Robles%2C%20CA%2093446%2C%20USA!5e0!3m2!1sen!2sin!4v1577686125064'
              '!5m2!1sen!2sin" width="100%" height="450" style="border:0" allowfullscreen="" '
              'loading="lazy" title="Map of Avery Acupuncture, 1704 Spring Street Suite 202, Paso Robles, CA"></iframe>')
FB_IFRAME = ('<iframe src="https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com'
              '%2FAvery-Acupuncture-Natural-Medicine-128162903891118%2F%3Ffref%3Dnf&tabs=timeline'
              '&width=275&height=370&small_header=false&adapt_container_width=true&hide_cover=false'
              '&show_facepile=false&appId" width="275" height="370" style="border:none;overflow:hidden" '
              'scrolling="no" frameborder="0" allowtransparency="true" title="Avery Acupuncture on Facebook"></iframe>')
WELLNESS_BADGE = ('<script src="https://www.wellness.com/js/badges/3245076/badge_160_200.js" '
                  'id="script_badge_160_200_3245076" type="text/javascript"></script>')
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
YT_HOME = "https://www.youtube.com/embed/z-_mGPgrBok"
YT_FOOT = "https://www.youtube.com/embed/YAffgKRg6P0"

NAV = [
    ("Meet Veronica Avery", "about-veronica.html", []),
    ("Conditions Treated", "conditions-treated.html", []),
    ("New Patients", "about-treatment.html#new-patients", [
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
  <div class="topbar">
    <div class="{wrap} topbar__inner">
      <p class="nav-phone"><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> <a class="nav-book-online" href="{BOOKING}" target="_blank" rel="noopener">BOOK ONLINE NOW</a></p>
    </div>
  </div>
  <div class="navbar">
    <div class="{wrap} navbar__inner">
      <a class="brand" href="index.html" aria-label="Avery Acupuncture — home">
        <img src="assets/img/avery-logo-transparent.png" alt="Avery Acupuncture" width="245" height="192">
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
      {FB_IFRAME}
    </section>
    <section class="footer-widget footer-widget--center" aria-label="Wellness and Yelp profiles">
      <div class="wellness-badge">
        <center>
        {WELLNESS_BADGE}<a href="https://www.wellness.com" style="color:#d5d5d5">Wellness.com</a><a href="https://www.wellness.com/dir/3245076/acupuncture-specialist/ca/paso-robles/veronica-avery-avery-acupuncture--natural-medicine-lac" style="color:#d5d5d5">My Profile</a>
        </center>
        <p><a href="https://www.yelp.com/biz/avery-acupuncture-and-natural-medicine-paso-robles" target="_blank" rel="noopener"><img src="assets/img/Unknown.png" alt="People love us on Yelp" width="100" height="100" loading="lazy"></a></p>
      </div>
    </section>
    <section class="footer-widget" aria-label="Video">
      <div class="footer-widget__video">
        <iframe src="{YT_FOOT}" width="100%" height="315" title="Avery Acupuncture video" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div>
    </section>
  </div>
  <div class="{'wrap-news' if variant == 'news' else 'wrap'} site-footer__bottom">
    <img class="footer-logo" src="assets/img/avery-logo-black-wcolor2.png" alt="Avery Acupuncture" width="180" height="190" decoding="async">
    <p>&nbsp;</p>
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

def page(name, active, body, description):
    fname = name + ".html"
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="dns-prefetch" href="https://www.youtube.com">
<link rel="dns-prefetch" href="https://www.facebook.com">
<link rel="dns-prefetch" href="https://www.google.com">
<link rel="dns-prefetch" href="https://www.wellness.com">
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=Open+Sans:ital,wght@0,300;0,400;0,600;0,700;1,300;1,700&family=Pathway+Gothic+One&display=swap&display=swap" rel="stylesheet">
{JSONLD}
<link rel="stylesheet" href="{asset_ver('css/style.css')}">
<!-- Google Analytics (client's existing GA4 measurement ID) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-QHC78WR2RK"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-QHC78WR2RK');</script>
<!-- Accessibility widget (client's own UserWay account, same as the live site) -->
<script src="https://cdn.userway.org/widget.js" data-account="veWiK0ku6v"></script>
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
{header(active) if name != 'news' else ''}
{body if name == "news" else f"<main id=\"main\">\n{body}\n</main>\n" + footer()}
<script src="{asset_ver('js/main.js')}"></script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# special sections

def hero():
    return f"""
<section class="hero" id="top">
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
      <iframe src="{YT_HOME}" width="560" height="315" title="Avery Acupuncture introduction video" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
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
            avatar = f'<img class="grw__avatar" src="assets/img/{base}" alt="" width="44" height="44" loading="lazy">'
        cards.append(f"""
      <figure class="grw__card">
        <img class="grw__g" src="assets/img/grw-g-logo.png" alt="Google review" width="20" height="20" loading="lazy">
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
        <div class="grw__head"><img class="grw__avatar" src="assets/img/grw-business.jpg" alt="Avery Acupuncture office" width="44" height="44" loading="lazy">
          <div><span class="grw__biz">Avery Acupuncture &amp; Natural Medicine, Inc.</span></div>
        </div>
        <p class="grw__score">5.0 {stars()}</p>
        <p class="grw__based">Based on 55 reviews</p>
        <p class="grw__powered">powered by <img src="assets/img/grw-google-logo.png" alt="Google" width="60" height="20" loading="lazy"></p>
        <p><a class="grw__write" href="https://search.google.com/local/writereview?placeid=ChIJuRLeDkPF7IARdquigwOGvhE" target="_blank" rel="noopener">review us on <img src="assets/img/grw-g-logo.png" alt="Google" width="16" height="16" loading="lazy"></a></p>
      </div>
      <div class="grw__track">
        <button class="grw__arrow grw__prev" type="button" aria-label="Previous reviews">&lsaquo;</button>
        <div class="grw__slider">
{''.join(cards)}
        </div>
        <button class="grw__arrow grw__next" type="button" aria-label="Next reviews">&rsaquo;</button>
        <div class="grw__dots" aria-label="Review pages">
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
<div class="map-full">""" + MAP_IFRAME + """</div>"""

# ---------------------------------------------------------------------------
# page bodies

def page_index():
    return hero() + reviews_section() + location_section()

# ---------------------------------------------------------------------------
# inner page building blocks

def band(title, height):
    """Full-width Bamboo title band, centered white serif title."""
    return f"""
<section class="page-band" style="height:{height}px">
  <h1 class="page-band__title">{esc(title)}</h1>
</section>"""

def xtext(blocks):
    """Render recovered p/list blocks as an X-theme text column."""
    return render_blocks(blocks, "", {})

def img(src, alt, w=None, h=None):
    if w is None and src in DIMS:
        w, h = DIMS[src]
    dim = f' width="{w}" height="{h}"' if w and h else ""
    return f'<img src="assets/img/{src}" alt="{esc(alt)}"{dim} loading="lazy" decoding="async">'

def page_about_veronica():
    d = INV["about-veronica"]
    b = d["blocks"]
    t1 = xtext(b[1:4])    # three opening paragraphs (brown)
    t2 = xtext(b[4:10])   # remaining six paragraphs (black on the live page)
    return f"""
{band("About Veronica", 248)}
<section class="av-photo">
  {img("veronica.jpg", "Veronica Avery, Licensed Acupuncturist and Herbalist", 450, 302).replace("<img ", '<img class="av-portrait fx" ')}
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
    <div class="fx">{img("proofs-0096.jpg", "Cupping therapy session")}</div>
    <div class="fx">{img("proofs-0024.jpg", "Fire cupping technique")}</div>
    <div class="fx">{img("proofs-0042.jpg", "Cupping glasses on a patient's back")}</div>
  </div>
</div>

<div class="at-imgrow">
  <div class="wrap-max x-row x-row--videos">
    <div class="x-video fx fx--l">
      <iframe src="https://www.youtube.com/embed/NODHaSuXo5c" title="Avery Acupuncture treatment video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
    </div>
    <div class="x-video fx fx--r">
      <iframe src="https://www.youtube.com/embed/NjkSy0s9hz0" title="Avery Acupuncture treatment video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
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
    <div class="fx">{img("proofs-0071.jpg", "Massage therapy at Avery Acupuncture")}</div>
    <div class="fx">{img("proofs-0068.jpg", "Therapeutic massage session")}</div>
    <div class="fx">{img("proofs-0063.jpg", "Massage therapy treatment")}</div>
  </div>
</div>

<section class="at-hrspace">
  <div class="wrap-max"><hr class="x-hr"></div>
</section>

<div class="at-imgrow">
  <div class="wrap-1000 x-row x-row--herbs">
    <div class="fx fx--l x-imgpad">{img("avery-herbs.jpg", "Chinese herbal medicines")}</div>
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
        <h3>{esc(h)}</h3>
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
      <div class="x-text"><p><br><strong>Monday, Tuesday, Thursday:</strong> 8:30am-5:00pm<br></p><strong>Friday:</strong> 8:30-4:30</div>
    </div>
  </div>
  <div class="wrap-max">
    <hr class="x-hr">
    <h2 class="x-h2">Phone</h2>
    <div class="x-text"><p><a href="tel:{PHONE_TEL}">805.400.9723</a></p></div>
  </div>
</section>
<section class="cp-map">
  <div class="wrap-max">{MAP_IFRAME.replace('width="100%"', 'width="1161"')}</div>
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
    for fname, (active, fn, desc) in PAGES.items():
        out = page(fname.split(".")[0], active, fn(), desc)
        with open(os.path.join(ROOT, fname), "w", encoding="utf-8") as f:
            f.write(out)
        print(f"wrote {fname} ({len(out):,} bytes)")

if __name__ == "__main__":
    main()
