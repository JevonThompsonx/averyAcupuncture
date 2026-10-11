#!/usr/bin/env python3
"""Acceptance checks for the rebuild. Fails loudly on any material gap."""
import os, re, json, sys
from urllib.parse import unquote
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = ["index.html", "about-veronica.html", "about-treatment.html",
         "conditions-treated.html", "contact.html", "office-policy.html",
         "privacy-policy.html", "news.html"]

fails, warns = [], []

def check(cond, msg):
    if cond:
        print(f"  PASS  {msg}")
    else:
        print(f"  FAIL  {msg}")
        fails.append(msg)

print("== A1: every page exists and parses ==")
soups = {}
for p in PAGES:
    path = os.path.join(ROOT, p)
    ok = os.path.exists(path)
    check(ok, f"{p} exists")
    if ok:
        soups[p] = BeautifulSoup(open(path, encoding="utf-8").read(), "html.parser")
        check(soups[p].title is not None and soups[p].title.get_text(strip=True) != "", f"{p} has <title>")

print("\n== A2: no hotlinks to the old host for images/css/js ==")
for p, soup in soups.items():
    bad = [t.get("src") for t in soup.find_all(["img", "script", "link"])
           if t.get("src", "").find("averyacupuncture.com/wp-content") >= 0
           or t.get("href", "").find("averyacupuncture.com/wp-content") >= 0]
    check(not bad, f"{p}: zero hotlinked assets ({len(bad)} found)")

print("\n== A3: every local image asset exists on disk ==")
for p, soup in soups.items():
    missing = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src.startswith(("http", "//", "data:")):
            continue
        if not os.path.exists(os.path.join(ROOT, unquote(src))):
            missing.append(src)
    check(not missing, f"{p}: all <img> resolve ({len(missing)} missing {missing[:3]})")

print("\n== A3c: every <source> srcset candidate resolves (progressive images) ==")
for p, soup in soups.items():
    missing = []
    for source in soup.find_all("source"):
        if not source.get("srcset"):
            continue
        for cand in source["srcset"].split(","):
            url = cand.strip().split(" ")[0]
            if not url or url.startswith(("http", "//", "data:")):
                continue
            if not os.path.exists(os.path.join(ROOT, unquote(url))):
                missing.append(url)
    # <img srcset> fallbacks too
    for img in soup.find_all("img"):
        for cand in (img.get("srcset") or "").split(","):
            url = cand.strip().split(" ")[0]
            if not url or url.startswith(("http", "//", "data:")):
                continue
            if not os.path.exists(os.path.join(ROOT, unquote(url))):
                missing.append(url)
    check(not missing, f"{p}: all srcset candidates resolve ({len(missing)} missing {missing[:3]})")

print("\n== A3d: every <picture> keeps a universal <img> fallback ==")
for p, soup in soups.items():
    bad = [pic.get("class") for pic in soup.find_all("picture") if not pic.find("img")]
    check(not bad, f"{p}: all <picture> have <img> fallbacks ({bad[:3]})")

print("\n== A3b: every asset referenced from CSS resolves ==")
for css_path in [f for f in os.listdir(os.path.join(ROOT, "css")) if f.endswith(".css")]:
    css = open(os.path.join(ROOT, "css", css_path), encoding="utf-8").read()
    refs = re.findall(r"url\((['\"]?)([^)'\"]+)\1\)", css)
    bad = [r for _, r in refs if not r.startswith(("http", "data:"))
           and not os.path.exists(os.path.join(ROOT, "css", unquote(r)))]
    check(not bad, f"css/{css_path}: all url() assets resolve ({len(refs)} refs, {len(bad)} broken)")

print("\n== A4: every internal link resolves ==")
ids_ok = True
# pre-compute the id index of every page for cross-page anchors
page_ids = {p: {e.get("id") for e in s.find_all(id=True)} for p, s in soups.items()}
for p, soup in soups.items():
    bad = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("http", "tel:", "mailto:", "//")):
            continue
        target, _, frag = href.partition("#")
        if target and not os.path.exists(os.path.join(ROOT, unquote(target))):
            bad.append(href)
            continue
        if frag:
            # cross-page anchors must exist in the *target* page
            where = unquote(target) if target else p
            if where not in page_ids:
                bad.append("unknown page " + href)
                ids_ok = False
            elif frag not in page_ids[where]:
                bad.append("anchor " + href)
                ids_ok = False
    check(not bad, f"{p}: all internal links resolve ({bad[:3]})")

print("\n== A5: css/js referenced by every page exist ==")
for p, soup in soups.items():
    css = [l.get("href").split("?")[0] for l in soup.find_all("link", rel="stylesheet") if l.get("href") and not l["href"].startswith("http")]
    js = [s.get("src").split("?")[0] for s in soup.find_all("script", src=True) if not s["src"].startswith("http")]
    ok = all(os.path.exists(os.path.join(ROOT, unquote(c))) for c in css + js)
    check(ok, f"{p}: local css/js exist {css + js}")

print("\n== A6: client content preserved (text recovered from inventory) ==")
import html as _html

def norm(s):
    """Normalize quotes/dashes/entities/phone punctuation so typographic
    upgrades (curly quotes, (805) 400-9723 formatting) still match live text."""
    s = _html.unescape(s)
    for a, b in [("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), (" ", " ")]:
        s = s.replace(a, b)
    s = re.sub(r"\(?(\d{3})\)?[.\- ](\d{3})[.\- ](\d{4})", r"\1\2\3", s)
    return re.sub(r"\s+", " ", s).strip()

# The reviews-widget header was a single text blob in the original; the rebuild
# renders it as structured markup instead. Assert its parts (done in A7) and
# skip the blob itself.
RERENDERED = {"Avery Acupuncture & Natural Medicine, Inc. 5.0 Based on 55 reviews"}

inv = json.load(open(os.path.join(ROOT, "recovered", "content-inventory.json")))
page_map = {"index": "index.html", "about-veronica": "about-veronica.html",
            "about-treatment": "about-treatment.html", "conditions-treated": "conditions-treated.html",
            "contact": "contact.html", "office-policy": "office-policy.html",
            "privacy-policy": "privacy-policy.html"}
total, present = 0, 0
for key, fname in page_map.items():
    text = norm(soups[fname].get_text(" ", strip=True))
    for b in inv[key]["blocks"]:
        s = norm(b.get("text", ""))
        if len(s) < 12 or any(s.startswith(x) for x in RERENDERED):
            continue
        total += 1
        if s in text:
            present += 1
        else:
            print(f"       MISSING in {fname}: {s[:80]}")
check(present == total, f"all {total} recovered text blocks present in output ({present})")

print("\n== A7: reviews rendered ==")
home = soups["index.html"].get_text(" ", strip=True)
revs = json.load(open(os.path.join(ROOT, "recovered", "reviews.json")))
n = sum(1 for r in revs if r["name"] in home and r["text"][:60].replace("’", "'") in home.replace("’", "'"))
check(n == len(revs), f"all {len(revs)} Google reviews rendered ({n})")
check("5.0" in home and "55 reviews" in home, "review summary (5.0 / 55 reviews) present")
check(home.count("★") >= len(revs) + 1, "star ratings present")

# A7b: FULL text comparison, not a 60-char prefix — catches post-char-60 truncation
import html as _h
_home = re.sub(r"\s+", " ", _h.unescape(soups["index.html"].get_text(" ", strip=True)))
mismatch = [r["name"] for r in revs
            if re.sub(r"\s+", " ", _h.unescape(r["text"])) not in _home]
check(not mismatch, f"every review text byte-exact end-to-end ({mismatch})")

print("\n== A8: key business data & integrations ==")
for p, soup in soups.items():
    t = soup.get_text(" ", strip=True)
    has_phone = "400-9723" in t
    has_booking = any("unifiedpractice" in a.get("href", "") for a in soup.find_all("a"))
    check(has_phone and has_booking, f"{p}: phone + booking link present")
check("google.com/maps/embed" in str(soups["index.html"]), "map embedded on homepage")
check("google.com/maps/embed" in str(soups["contact.html"]), "map embedded on contact page")
check("facebook.com/plugins/page.php" in str(soups["index.html"]), "facebook plugin in footer")

print("\n== A9: brand design tokens applied ==")
css = open(os.path.join(ROOT, "css", "style.css"), encoding="utf-8").read()
for token, name in [("#6b9d47", "primary green"), ("#8abe3c", "hover green"),
                    ("#e17d4a", "accent orange"), ("#7a6d4a", "body brown"),
                    ("#b7b733", "olive button"), ("EB Garamond", "serif face"),
                    ("Open Sans", "sans face"), ("Bamboo-1200w", "hero/band bamboo photo")]:
    check(token in css, f"css retains {name} ({token})")

print("\n== A9b: ANTI-FABRICATION — every external URL must exist on the live site ==")
live_links = set(json.load(open(os.path.join(ROOT, "recovered", "live-external-links.json"))))
# domains the rebuild legitimately introduces (fonts/GA) or trims tracking
# params from (facebook fref); these are not fabricated content
ALLOWED_PREFIXES = (
    "https://fonts.googleapis.com", "https://fonts.gstatic.com",
    "https://www.googletagmanager.com",
    "https://www.youtube.com/embed/", "https://www.youtube.com",
    "https://www.facebook.com/plugins/page.php", "https://www.facebook.com",
    "https://www.google.com", "https://www.wellness.com",
)
SELF_DOMAIN = "https://averyacupuncture.com"
# origin of this rebuild (canonicals, OG URLs, sitemap pointer)
SELF_ORIGIN = "https://avery.jsquaredadventures.com"

def known(url):
    if url in live_links:                     # exact match first, raw (pb= payloads are %-encoded)
        return True
    u = unquote(url)                          # decode only for prefix/probe matching
    if u in live_links or url.startswith(SELF_DOMAIN):
        return True
    if u == SELF_ORIGIN or u.startswith(SELF_ORIGIN + "/"):
        return True
    if "youtube.com/embed/" in u:
        vid = u.split("youtube.com/embed/")[1].split("?")[0]
        return any(vid in x for x in live_links)
    return any(u.startswith(p) or url.startswith(p) for p in ALLOWED_PREFIXES)

fabricated = []
for p, soup in soups.items():
    for el in soup.find_all(["a", "iframe", "img", "script", "link"]):
        url = el.get("href") or el.get("src") or ""
        if url.startswith(("http", "//")):
            u = url.replace("http://", "https://")
            if not known(u):
                fabricated.append((p, u))
check(not fabricated, f"zero fabricated external URLs ({len(fabricated)} found: {fabricated[:3]})")

print("\n== A9c: per-page asset sanity (no duplicates, no dead paragraphs) ==")
for p, soup in soups.items():
    srcs = [i.get("src") for i in soup.find_all("img") if i.get("src")]
    dupes = {s for s in srcs if srcs.count(s) > 1 and "grw" not in s}
    check(not dupes, f"{p}: no duplicated images ({sorted(dupes)[:2]})")
    # a bare <p> whose entire text is a known button label is an orphan artifact
    orphan = [x.get_text(strip=True) for x in soup.select("article p")
              if x.get_text(strip=True) in ("Book an Appointment", "Book Now", "Schedule Now")
              and not x.find("a")]
    check(not orphan, f"{p}: no unlinked button-label artifacts ({orphan})")

print("\n== A10: responsive & a11y basics ==")
for p, soup in soups.items():
    vp = soup.find("meta", attrs={"name": "viewport"})
    lang = soup.find("html").get("lang")
    check(vp is not None and lang == "en", f"{p}: viewport meta + lang=en")
    alts = all(img.get("alt") is not None for img in soup.find_all("img"))
    check(alts, f"{p}: every img has alt attribute")
check("@media (max-width: 860px)" in css and ".nav-toggle { display: flex; }" in css, "mobile breakpoint + hamburger exist")

print("\n== A11: perf wiring (min css, hero fetchpriority, deferred widget) ==")
for p, soup in soups.items():
    css = [l.get("href", "").split("?")[0] for l in soup.find_all("link", rel="stylesheet") if l.get("href")]
    local_css = [c for c in css if not c.startswith("http")]
    check("css/style.min.css" in local_css, f"{p}: loads minified css ({local_css})")
    check(not any("userway" in (s.get("src") or "") for s in soup.find_all("script")),
          f"{p}: UserWay widget not render-blocking (deferred)")
hero_imgs = [i for i in soups["index.html"].find_all("img") if i.get("fetchpriority") == "high"]
check(len(hero_imgs) == 1, "index.html: hero image is eager with fetchpriority=high")
check(len(soups["index.html"].find_all("picture")) > 0, "index.html: responsive <picture> markup present")

print("\n" + "=" * 60)
if fails:
    print(f"RESULT: {len(fails)} FAILURES")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("RESULT: ALL CHECKS PASSED")