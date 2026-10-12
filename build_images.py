#!/usr/bin/env python3
"""
Avery Acupuncture — image variant generator.

Generates modern-format derivatives (AVIF + WebP) and width-scaled JPEG
fallbacks next to each source image in assets/img/, then writes
variants.json so build.py can emit responsive <picture> markup WITHOUT
needing Pillow at page-build time.

Idempotent: variants whose target file exists are skipped, so re-running
after editing build.py costs nothing. Requires Pillow (pip install Pillow);
build.py degrades gracefully (plain <img>) when this step has not been run.

Usage:  python3 build_images.py [--force]
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(ROOT, "assets", "img")
MANIFEST = os.path.join(IMG_DIR, "variants.json")

# Candidate widths for srcset. A width is only materialised when it is
# meaningfully smaller than the natural width (the original file stays in
# the srcset as the largest candidate).
CANDIDATES = [400, 800, 1200]

# Files that must not be touched/replaced (variants of themselves).
SKIP_PREFIX = ("fav-icon",)

# Screenshots of third-party widgets (the click-to-load facades) contain fine
# text — map street labels, badge copy — where a low-quality encode is visible.
# They encode harder and never emit a width below 800px: a phone at DPR 1 then
# gets an 800px source supersampled down to its ~390px box, which is sharper
# than a browser downscale of a 400px derivative and identical to what it saw
# before this optimisation (the original 1162px JPEG).
PREVIEWS = {
    "map-embed-preview.jpg":    {"min_width": 800, "avif": 60},
    "wellness-badge-preview.jpg": {"avif": 60},
}

try:
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
except ImportError:
    print("Pillow not installed — nothing to do (site still builds without variants).")
    sys.exit(0)


def variants_for(nat_w):
    """Pick meaningful widths for an image of natural width nat_w.
    A width only qualifies when it is smaller than the natural width
    (never upscale) and saves at least ~5%."""
    return [w for w in CANDIDATES if w < nat_w * 0.95]


def encode(im, path, fmt, q=None):
    q = q or {}
    if fmt == "webp":
        im.save(path, "WEBP", quality=q.get("webp", 76), method=6)
    elif fmt == "avif":
        im.save(path, "AVIF", quality=q.get("avif", 46))
    elif fmt == "jpg":
        im.save(path, "JPEG", quality=q.get("jpg", 82), optimize=True, progressive=True)


def main():
    force = "--force" in sys.argv
    manifest = {}
    # never treat our own derivatives as sources: "<stem>-<1200>w.<ext>"
    variant_re = re.compile(r"-\d+w\.(jpg|jpeg|png|webp|avif)$", re.I)
    # The Bamboo photo is a large decorative background/hero: encode it harder.
    # Content photos keep the defaults.
    HARDER_Q = {"webp": 70, "avif": 40, "jpg": 80}
    names = sorted(n for n in os.listdir(IMG_DIR)
                   if n.lower().endswith((".jpg", ".jpeg", ".png"))
                   and not variant_re.search(n))
    for name in names:
        if any(name.startswith(p) for p in SKIP_PREFIX):
            continue
        src = os.path.join(IMG_DIR, name)
        stem = os.path.splitext(name)[0]
        try:
            with Image.open(src) as im:
                im = im.convert("RGB") if im.mode not in ("RGB", "RGBA") else im
                nat_w, nat_h = im.size
                widths = variants_for(nat_w)
                pol = PREVIEWS.get(name, {})
                widths = [w for w in widths if w >= pol.get("min_width", 0)]
                entry = {"natural": [nat_w, nat_h], "widths": []}
                for w in widths:
                    outs = []
                    for fmt in ("avif", "webp", "jpg"):
                        out = os.path.join(IMG_DIR, f"{stem}-{w}w.{fmt}")
                        outs.append(out)
                        if force or not os.path.exists(out):
                            with Image.open(src) as base:
                                base = base.convert("RGB") if fmt == "jpg" else (
                                    base.convert("RGBA") if base.mode in ("RGBA", "LA", "P") else base.convert("RGB"))
                                h = round(base.height * w / base.width)
                                base = base.resize((w, h), Image.LANCZOS)
                                q = HARDER_Q if name.lower().startswith("bamboo") else None
                                if pol.get(fmt):
                                    q = {**(q or {}), fmt: pol[fmt]}
                                encode(base, out, fmt, q)
                    entry["widths"].append(w)
                # whole-image single-size variants (no width in the name)
                # only for images with no width candidates: keeps small assets
                # (logos, avatars, badges) a single <source> each.
                if not widths:
                    for fmt in ("avif", "webp"):
                        out = os.path.join(IMG_DIR, f"{stem}.{fmt}")
                        if force or not os.path.exists(out):
                            with Image.open(src) as base:
                                base = base.convert("RGBA") if base.mode in ("RGBA", "LA", "P") else base.convert("RGB")
                                q = {fmt: pol[fmt]} if pol.get(fmt) else None
                                encode(base, out, fmt, q)
                manifest[name] = entry
        except Exception as e:  # a broken file must not break the build
            print(f"  SKIP {name}: {e}")
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    total = sum(len(v["widths"]) for v in manifest.values())
    print(f"variants.json written: {len(manifest)} images, {total} width variants")


if __name__ == "__main__":
    main()
