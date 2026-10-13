"""Turn your photo into an ASCII portrait and put it into README.md.

Usage:
    pip install pillow
    python make_ascii.py my_photo.jpg            # default width 44
    python make_ascii.py my_photo.jpg 52         # wider = more detail

It replaces everything between <!--ASCII_START--> and <!--ASCII_END--> in README.md.
Tip: a close-up photo with a plain background gives the cleanest result.
"""
import sys
from PIL import Image, ImageOps, ImageFilter

photo = sys.argv[1]
width = int(sys.argv[2]) if len(sys.argv) > 2 else 44

# dark -> light on a dark GitHub background: dense characters = bright areas
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

img = Image.open(photo).convert("L")
img = ImageOps.autocontrast(img, cutoff=2)
img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150))
w, h = img.size
height = int(width * (h / w) * 0.5)  # characters are about twice as tall as wide
img = img.resize((width, height))

lines = []
for y in range(height):
    row = ""
    for x in range(width):
        v = img.getpixel((x, y))
        row += RAMP[int(v / 255 * (len(RAMP) - 1))]
    lines.append(row.rstrip())
art = "\n".join(lines)
art = art.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

text = open("README.md", encoding="utf-8").read()
start, end = "<!--ASCII_START-->", "<!--ASCII_END-->"
a, b = text.index(start) + len(start), text.index(end)
open("README.md", "w", encoding="utf-8").write(text[:a] + "\n" + art + "\n" + text[b:])
print("Done. README.md updated.")