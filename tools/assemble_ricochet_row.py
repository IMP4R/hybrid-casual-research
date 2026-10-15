#!/usr/bin/env python3
"""Коллаж 1×4 с подписями для серии рикошетов Shot Painter."""
from PIL import Image, ImageDraw, ImageFont
import pathlib

M = pathlib.Path("/Users/user0/godot-hybrid-casual/research/mockups")
FRAMES = [
    ("bj1_aim.png",   "1. ПРИЦЕЛ — S1 пульсирует (блок в 2 клетках), палец тапает, пунктир пути к воротам"),
    ("bj2_route.png", "2. ПРОХОД — стрелка повернулась (дуга+щелчок), синий ушёл в свои ворота, 1/12"),
    ("bj3_jam.png",   "3. ДЖЕМ — жёлтый вклинился в зелёные ворота: вспышка, «!», дым, −1♥; S2 срочно доворачивают"),
    ("bj4_win.png",   "4. ПОБЕДА — 12/12, ворота с ✓ и стопками, лента пуста (2♥ — цена джема)"),
]
CAP_H, PAD, COL_W = 92, 14, 506

def font(sz, bold=False):
    for p in ("/System/Library/Fonts/HelveticaNeue.ttc" if bold else "/System/Library/Fonts/Helvetica.ttc",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()

H = 900
thumbs = []
for name, _ in FRAMES:
    im = Image.open(M / name)
    w = round(im.width * H / im.height)
    thumbs.append(im.resize((w, H), Image.LANCZOS))

W = PAD + sum(t.width for t in thumbs) + PAD * (len(thumbs) - 1) + PAD
canvas = Image.new("RGB", (W, H + CAP_H + PAD * 2), (24, 26, 32))
d = ImageDraw.Draw(canvas)
x = PAD
for t, (name, cap) in zip(thumbs, FRAMES):
    canvas.paste(t, (x, PAD))
    d.rounded_rectangle([x + 4, PAD + H + 8, x + t.width - 4, PAD + H + CAP_H - 4], 14, fill=(38, 42, 52))
    # перенос подписи на 2 строки
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
out = M / "row_beltjam_canon.png"
canvas.save(out)
print(out, canvas.size)
