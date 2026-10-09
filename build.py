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
    # link phone numbers
    text = re.sub(r'\(?\b(805)[.\-) ]?(\d{3})[.\- ]?(\d{4})\b',
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

def header(active):
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
    return f"""
<header class="site-header">
  <div class="topbar">
    <div class="wrap topbar__inner">
      <p class="nav-phone"><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> <a class="nav-book-online" href="{BOOKING}" target="_blank" rel="noopener">BOOK ONLINE NOW</a></p>
    </div>
  </div>
  <div class="navbar">
    <div class="wrap navbar__inner">
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

def footer():
    foot_links = "".join(f'<li><a href="{h}">{esc(l)}</a></li>' for l, h in FOOTER_NAV)
    return f"""
<footer class="site-footer">
  <div class="wrap site-footer__widgets">
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
        <iframe src="{YT_FOOT}" width="100%" height="315" title="Avery Acupuncture video" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
      </div>
    </section>
  </div>
  <div class="wrap site-footer__bottom">
    <img class="footer-logo" src="assets/img/avery-logo-black-wcolor2.png" alt="Avery Acupuncture" width="180" height="190" loading="lazy">
    <p>&nbsp;</p>
    <!-- NOTE: "Acupunture" (missing c) is the live site's own spelling,
         preserved verbatim. Jolly Creative Agency was the previous
         developer. Keep or remove this credit per the client's contract. -->
    <p>Copyright&nbsp;&copy; 2026 by Avery Acupunture- All Rights Reserved.&nbsp; | <a href="https://jollycreativeagency.com/" target="_blank" rel="noopener">Jolly Creative Agency</a></p>
  </div>
  <nav class="wrap footer-menu" aria-label="Footer">
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
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLES[name]}</title>
<meta name="description" content="{esc(description)}">
<link rel="icon" type="image/png" href="assets/img/fav-icon.png">
<link rel="apple-touch-icon" href="assets/img/fav-icon.png">
<link rel="canonical" href="https://averyacupuncture.com/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=Open+Sans:ital,wght@0,300;0,400;0,600;0,700;1,300;1,700&family=Pathway+Gothic+One&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset_ver('css/style.css')}">
<!-- Google Analytics (client's existing GA4 measurement ID) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-QHC78WR2RK"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-QHC78WR2RK');</script>
<!-- Accessibility widget (client's own UserWay account, same as the live site) -->
<script src="https://cdn.userway.org/widget.js" data-account="veWiK0ku6v"></script>
</head>
<body>
{header(active)}
<main>
{body}
</main>
{footer()}
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
            avatar = f'<img class="grw__avatar" src="assets/img/{base}" alt="" width="50" height="50" loading="lazy">'
        cards.append(f"""
      <figure class="grw__card">
        <img class="grw__g" src="assets/img/grw-g-logo.png" alt="Google review" width="20" height="20" loading="lazy">
        <div class="grw__head">{avatar}
          <div><a class="grw__name" href="{r['profile']}" target="_blank" rel="noopener">{esc(r['name'])}</a>
          <span class="grw__time">{esc(r['time'])}</span></div>
        </div>
        <div class="grw__stars">{stars()}</div>
        <blockquote class="grw__text">{esc(r['text'])}</blockquote>
        <button class="grw__more" type="button" aria-expanded="false">read more</button>
      </figure>""")
    return f"""
<section class="reviews" id="reviews">
  <div class="reviews-hr"><div class="wrap-1000"><div class="reviews-hr__pad"><hr class="rule-reviews"></div></div></div>
  <div class="wrap">
    <p class="reviews__label">We Care About Our Patients</p>
    <div class="grw">
      <div class="grw__summary">
        <div class="grw__head"><img class="grw__avatar" src="assets/img/grw-business.jpg" alt="Avery Acupuncture office" width="50" height="50" loading="lazy">
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

def page_about_veronica():
    data = INV["about-veronica"]
    body = render_blocks(anchor_headings(data["blocks"], "about-veronica"), "about-veronica", data["images"])
    # figure first: veronica.jpg, then the two wide shots
    return f"""
<nav class="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="index.html">Home</a></li><li aria-current="page">Meet Veronica Avery</li></ol></nav>
<article class="prose">
  <div class="container container--narrow">
    <figure class="prose__lead-img">
      <img src="assets/img/veronica.jpg" alt="Veronica Avery, Licensed Acupuncturist and Herbalist" width="450" height="302">
    </figure>
    {body}
    <div class="prose__gallery">
      <figure><img src="assets/img/IMG_3467-min.jpg" alt="Veronica Avery at work" loading="lazy"></figure>
      <figure><img src="assets/img/IMG_3507.jpg" alt="Inside the Avery Acupuncture practice" loading="lazy"></figure>
    </div>
    <p class="prose__end"><a class="btn" href="{BOOKING}" target="_blank" rel="noopener">Book an Appointment</a></p>
  </div>
</article>"""

def page_about_treatment():
    data = INV["about-treatment"]
    blocks = anchor_headings(data["blocks"], "about-treatment")
    body = render_blocks(blocks, "about-treatment", data["images"])
    featured = f"""
    <figure class="prose__lead-img">
      <img src="assets/img/avery-acupuncture-office.jpg" alt="The Avery Acupuncture office" loading="lazy">
    </figure>"""
    gal = gallery(data["images"], skip={"avery-acupuncture-office.jpg"})
    # the two videos that sit in the Cupping section on the live page
    vids = f"""
    <div class="video-inline">
      <iframe src="https://www.youtube.com/embed/NODHaSuXo5c" title="Avery Acupuncture video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
      <iframe src="https://www.youtube.com/embed/NjkSy0s9hz0" title="Avery Acupuncture video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
    </div>"""
    body = body.replace("<h3>Massage</h3>", vids + "\n    <h3>Massage</h3>")
    body = body.replace('<h2 id="new-patients">New Patients</h2>',
                        featured + gal + '\n<h2 id="new-patients">New Patients</h2>')
    return f"""
<nav class="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="index.html">Home</a></li><li aria-current="page">About Treatment</li></ol></nav>
<article class="prose">
  <div class="container container--narrow">
    {body}
    <p class="prose__end"><a class="btn" href="{BOOKING}" target="_blank" rel="noopener">Book Now</a></p>
  </div>
</article>"""

def page_conditions():
    data = INV["conditions-treated"]
    body = render_blocks(data["blocks"], "conditions-treated", data["images"])
    return f"""
<nav class="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="index.html">Home</a></li><li aria-current="page">Conditions Treated</li></ol></nav>
<article class="prose">
  <div class="container container--narrow">
    {body}
    <p class="prose__end"><a class="btn" href="{BOOKING}" target="_blank" rel="noopener">Schedule Now</a></p>
  </div>
</article>"""

def page_contact():
    """Contact page — hand-built from the live markup: the live FAQ is a
    3-question accordion and the hours include a Friday line, neither of
    which the generic block renderer captured."""
    return f"""
<nav class="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="index.html">Home</a></li><li aria-current="page">Contact</li></ol></nav>
<article class="prose">
  <div class="container">
    <h2>Visit Us Today</h2>
    <h2>Paso Robles</h2>
    <p>1704 Spring Street, Suite 202 Paso Robles, CA</p>
    <h2>Hours</h2>
    <p><strong>Monday, Tuesday, Thursday:</strong> 8:30am-5:00pm<br><strong>Friday:</strong> 8:30-4:30</p>
    <h2>Phone</h2>
    <p><a href="tel:{PHONE_TEL}">805.400.9723</a></p>
    <h2>FAQ</h2>
    <div class="faq">
      <details>
        <summary>How do I book an appointment?</summary>
        <div class="faq__body">
          <p>We are currently accepting new patients! Please call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> to schedule an appointment, or click the link below. We look forward to meeting you soon!</p>
          <p><a class="btn" href="{BOOKING}" target="_blank" rel="noopener">Book an Appointment</a></p>
        </div>
      </details>
      <details>
        <summary>How do I cancel an appointment?</summary>
        <div class="faq__body">
          <p>If you need to change or cancel your appointment please do so with 24 hours notice. With the exception of emergencies, failure to do so will result in being charged the full fee for your appointment.</p>
        </div>
      </details>
      <details>
        <summary>Do you accept insurance?</summary>
        <div class="faq__body">
          <p>If you have insurance, please bring your insurance card with you. For your convenience, we will gladly call to verify your acupuncture coverage including eligibility and benefits.</p>
        </div>
      </details>
    </div>
    <div class="location__map location__map--full">{MAP_IFRAME}</div>
  </div>
</article>"""

def page_policy():
    data = INV["office-policy"]
    body = render_blocks(data["blocks"], "office-policy", data["images"])
    return f"""
<nav class="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="index.html">Home</a></li><li aria-current="page">Office Policy</li></ol></nav>
<article class="prose prose--policy">
  <div class="container container--narrow">{body}</div>
</article>"""

def page_privacy():
    data = INV["privacy-policy"]
    blocks = [b for b in data["blocks"]]
    # first block is h1; promote it
    body = render_blocks(blocks, "privacy-policy", data["images"])
    body = body.replace("<h1>", '<h1 class="prose__full-title">', 1)
    return f"""
<nav class="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="index.html">Home</a></li><li aria-current="page">Privacy Policy</li></ol></nav>
<article class="prose prose--policy">
  <div class="container container--narrow">{body}</div>
</article>"""

PAGES = {
    "index.html":        ("index.html", page_index,       "Acupuncture & Natural Medicine in Paso Robles — Veronica Avery, Licensed Acupuncturist and Herbalist."),
    "about-veronica.html": ("about-veronica.html", page_about_veronica, "The story of Veronica Avery, Licensed Acupuncturist and Herbalist practicing Traditional Chinese Medicine in Paso Robles."),
    "about-treatment.html": ("about-treatment.html", page_about_treatment, "What to expect from acupuncture, cupping, massage, and Chinese herbal medicine at Avery Acupuncture."),
    "conditions-treated.html": ("conditions-treated.html", page_conditions, "Conditions treated at Avery Acupuncture: pain, immunity, pediatrics, emotional health, GI, women's health."),
    "contact.html":      ("contact.html", page_contact,          "Contact Avery Acupuncture in Paso Robles — address, hours, phone, and online booking."),
    "office-policy.html": ("office-policy.html", page_policy,     "Avery Acupuncture office policy: fees and insurance, confidentiality, missed appointments."),
    "privacy-policy.html": ("privacy-policy.html", page_privacy,  "Privacy policy for Avery Acupuncture."),
}

def main():
    for fname, (active, fn, desc) in PAGES.items():
        out = page(fname.split(".")[0], active, fn(), desc)
        with open(os.path.join(ROOT, fname), "w", encoding="utf-8") as f:
            f.write(out)
        print(f"wrote {fname} ({len(out):,} bytes)")

if __name__ == "__main__":
    main()
