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


def encode(im, path, fmt):
    if fmt == "webp":
        im.save(path, "WEBP", quality=76, method=6)
    elif fmt == "avif":
        im.save(path, "AVIF", quality=46)
    elif fmt == "jpg":
        im.save(path, "JPEG", quality=82, optimize=True, progressive=True)


def main():
    force = "--force" in sys.argv
    manifest = {}
    # never treat our own derivatives as sources: "<stem>-<1200>w.<ext>"
    variant_re = re.compile(r"-\d+w\.(jpg|jpeg|png|webp|avif)$", re.I)
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
                                encode(base, out, fmt)
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
                                encode(base, out, fmt)
                manifest[name] = entry
        except Exception as e:  # a broken file must not break the build
            print(f"  SKIP {name}: {e}")
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    total = sum(len(v["widths"]) for v in manifest.values())
    print(f"variants.json written: {len(manifest)} images, {total} width variants")


if __name__ == "__main__":
    main()
