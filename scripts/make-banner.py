"""Compose docs/assets/banner.jpg (1600 wide) and social.jpg (1280x640) from banner-source.jpg.

Run from the repository root, with Inter 4.1 (SIL OFL 1.1, not committed) unpacked somewhere:

    uv run --no-project --python 3.13 --with pillow==13.0.0 python -I scripts/make-banner.py \
        docs/assets/banner-source.jpg <dir with InterDisplay-Bold.ttf and Inter-Regular.ttf> docs/assets

The wordmark is drawn here, not by the image model, so no generated lettering ends up garbled.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

source, fonts, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
OFF_WHITE, TEAL, AMBER = (244, 241, 234), (43, 179, 163), (242, 165, 65)
WORD, TAG = fonts / "InterDisplay-Bold.ttf", fonts / "Inter-Regular.ttf"
TAGLINE = ("a governed co-pilot", "for Claude Code")


def background(img: Image.Image) -> tuple[int, int, int]:
    """The navy of the empty left third, as a median, so pads blend in."""
    w, h = img.size
    region = img.crop((int(w * 0.18), int(h * 0.30), int(w * 0.30), int(h * 0.60)))
    return tuple(int(v) for v in ImageStat.Stat(region).median)


def wordmark(canvas: Image.Image, x: int, y_center: int, size: int) -> None:
    draw = ImageDraw.Draw(canvas)
    word = ImageFont.truetype(str(WORD), size)
    tag = ImageFont.truetype(str(TAG), int(size * 0.27))
    word_h = word.getbbox("cobot")[3]
    line_h = int(size * 0.36)
    block = word_h + int(size * 0.22) + line_h * len(TAGLINE)
    top = y_center - block // 2
    draw.text((x, top - word.getbbox("cobot")[1] + size * 0.04), "cobot", font=word, fill=OFF_WHITE)
    bar_y = top + word_h + int(size * 0.08)
    draw.rectangle((x + 4, bar_y, x + 4 + int(size * 0.5), bar_y + max(4, size // 22)), fill=AMBER)
    for i, line in enumerate(TAGLINE):
        draw.text((x + 2, bar_y + int(size * 0.16) + i * line_h), line, font=tag, fill=TEAL)


img = Image.open(source).convert("RGB")
w, h = img.size

banner = img.resize((1600, round(1600 * h / w)), Image.LANCZOS)
wordmark(banner, 92, banner.height // 2, 128)
banner.save(out / "banner.jpg", quality=82, optimize=True, progressive=True)

bg = background(img)
social = Image.new("RGB", (1280, 640), bg)
scaled = img.resize((1280, round(1280 * h / w)), Image.LANCZOS)
fade = 70
mask = Image.new("L", scaled.size, 255)
draw = ImageDraw.Draw(mask)
for i in range(fade):
    alpha = int(255 * i / fade)
    draw.line((0, i, scaled.width, i), fill=alpha)
    draw.line((0, scaled.height - 1 - i, scaled.width, scaled.height - 1 - i), fill=alpha)
social.paste(scaled, (0, (640 - scaled.height) // 2), mask)
wordmark(social, 70, 320, 112)
social.save(out / "social.jpg", quality=85, optimize=True, progressive=True)
print("banner", banner.size, "social", social.size, "bg", bg)
