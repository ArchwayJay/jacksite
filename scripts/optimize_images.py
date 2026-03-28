#!/usr/bin/env python3
"""
Resize and export images to PNG and WebP versions for the site.
Generates: images/<name>-400.png, images/<name>-800.png and corresponding .webp files.
"""
from PIL import Image
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / 'images'
TARGETS = [400, 800]

pairs = [
    (IMAGES / 'alien.png', 'alien'),
    (IMAGES / 'lone.png', 'lone')
]

# Add green invaders source so we generate responsive variants
pairs.append((IMAGES / 'green-invaders.png', 'green-invaders'))
# Add Zombie Dodger sourced from Construct
pairs.append((IMAGES / 'zombie-dodger.png', 'zombie-dodger'))

IMAGES.mkdir(parents=True, exist_ok=True)

for src_path, name in pairs:
    if not src_path.exists():
        print(f"Skipping {src_path} — file not found")
        continue
    img = Image.open(src_path).convert('RGBA')
    for w in TARGETS:
        img_copy = img.copy()
        # maintain aspect ratio, fit to width=w
        orig_w, orig_h = img_copy.size
        if orig_w > w:
            h = int((w / orig_w) * orig_h)
            img_copy = img_copy.resize((w, h), Image.LANCZOS)
        # else keep original size (avoid upscaling)
        png_out = IMAGES / f"{name}-{w}.png"
        webp_out = IMAGES / f"{name}-{w}.webp"
        img_copy.save(png_out, optimize=True)
        img_copy.save(webp_out, format='WEBP', quality=80, method=6)
        print(f"Wrote {png_out} and {webp_out}")

print('Done')
