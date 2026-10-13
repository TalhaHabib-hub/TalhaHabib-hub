"""Turn your photo into an ASCII portrait WITHOUT the background wall.

Install once (inside your .venv terminal):
    pip install pillow "rembg[cpu]"

Run:
    python make_ascii.py photo.jpg
    python make_ascii.py photo.jpg 60      # bigger number = more detail

The first run downloads a small AI model (about 170 MB) that cuts you out
of the background, so you need internet for that first run.
"""
import sys
from PIL import Image, ImageOps, ImageFilter
from rembg import remove

photo = sys.argv[1]
width = int(sys.argv[2]) if len(sys.argv) > 2 else 50

# 1. cut the person out of the background
src = Image.open(photo).convert("RGB")
cut = remove(src)                       # RGBA image, background is transparent
alpha = cut.split()[3]

# 2. crop tightly around the person so the portrait is centered
box = alpha.point(lambda a: 255 if a > 128 else 0).getbbox()
cut = cut.crop(box)
alpha = cut.split()[3]

# 3. make a brightness picture of the person
gray = cut.convert("L")
gray = ImageOps.autocontrast(gray, cutoff=1)
gray = gray.point(lambda v: int(255 * (v / 255) ** 0.6))   # lift dark areas (vest)
gray = gray.filter(ImageFilter.UnsharpMask(radius=2, percent=160))

# 4. resize (characters are about twice as tall as wide)
w, h = gray.size
height = int(width * (h / w) * 0.5)
gray = gray.resize((width, height))
alpha = alpha.resize((width, height))

# 5. turn pixels into characters; background pixels become empty space
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
lines = []
for y in range(height):
    row = ""
    for x in range(width):
        if alpha.getpixel((x, y)) < 128:
            row += " "
        else:
            row += RAMP[int(gray.getpixel((x, y)) / 255 * (len(RAMP) - 1))]
    lines.append(row.rstrip())

art = "\n".join(lines)
art = art.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# 6. put it into README.md
text = open("README.md", encoding="utf-8").read()
start, end = "<!--ASCII_START-->", "<!--ASCII_END-->"
a, b = text.index(start) + len(start), text.index(end)
open("README.md", "w", encoding="utf-8").write(text[:a] + "\n" + art + "\n" + text[b:])
print("Done. README.md updated.")