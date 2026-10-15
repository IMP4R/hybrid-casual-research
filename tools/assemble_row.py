#!/usr/bin/env python3
"""assemble_row.py — коллаж 1×N с подписями.
usage: assemble_row.py OUT.png f1.png "подпись" [f2.png "подпись" ...]
"""
from PIL import Image, ImageDraw, ImageFont
import sys, pathlib

def font(sz):
    for p in ("/System/Library/Fonts/Helvetica.ttc",):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()

a = sys.argv[1:]
out = a[0]; items = a[1:]
M = pathlib.Path("/Users/user0/godot-hybrid-casual/research/mockups")
frames = [(items[i], items[i + 1]) for i in range(0, len(items), 2)]
CAP_H, PAD, H = 92, 14, 900
thumbs = []
for name, _ in frames:
    im = Image.open(M / name)
    w = round(im.width * H / im.height)
    thumbs.append(im.resize((w, H), Image.LANCZOS))
W = PAD + sum(t.width for t in thumbs) + PAD * len(thumbs)
cv = Image.new("RGB", (W, H + CAP_H + PAD * 2), (24, 26, 32))
d = ImageDraw.Draw(cv)
x = PAD
for t, (name, cap) in zip(thumbs, frames):
    cv.paste(t, (x, PAD))
    d.rounded_rectangle([x + 4, PAD + H + 8, x + t.width - 4, PAD + H + CAP_H - 4], 14, fill=(38, 42, 52))
    words, lines, cur = cap.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=font(24)) > t.width - 40:
            lines.append(cur); cur = w_
        else:
            cur = trial
    lines.append(cur)
    ty = PAD + H + 16
    for ln in lines[:2]:
        d.text((x + 20, ty), ln, font=font(24), fill=(235, 238, 245))
        ty += 30
    x += t.width + PAD
path = M / out
cv.save(path)
print(path, cv.size)
