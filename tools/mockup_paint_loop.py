#!/usr/bin/env python3
"""mockup_paint_loop.py — процедурный фейк-скриншот концепта «Paint Loop» (Г1: S1 × жидкость).

Скелет S1 «Канва + Питатели» (доказан рынком на $189M+), материал = жидкая краска.
Рисуем PIL'ом: канва с пиксель-артом, частично залитая «мокрой» краской,
снизу очереди вёдер с краской и счётчиками, верхний UI.
Запуск:  /Users/user0/.venv/ytools/bin/python tools/mockup_paint_loop.py
Выход:   research/mockups/paint_loop_v1.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pathlib

W, H = 1080, 1920
OUT = pathlib.Path("/Users/user0/godot-hybrid-casual/research/mockups/paint_loop_v1.png")

def font(sz, bold=True):
    for p in (["/System/Library/Fonts/Supplemental/Arial Bold.ttf"] if bold else []) + \
             ["/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"]:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            continue
    return ImageFont.load_default()

# ---------- палитра ----------
BG_TOP, BG_BOT = (146, 196, 255), (108, 165, 245)
CANVAS_BG = (245, 238, 221)
INK = (43, 47, 68)
WHITE = (255, 255, 255)

# пиксель-арт попугая 14x14: . пусто, b синий, o оранжевый, g зелёный
ART = [
    "....bbbb......",
    "...b....b.....",
    "..b.oooo.b....",
    "..bo....ob....",
    ".bo......ob...",
    ".b..oo....b...",
    ".b.oooooo..b..",
    "..b.o..oo..b..",
    "..b.oo.o.ob...",
    ".bg.booo.bg...",
    ".bg..bb..bg...",
    "..b..bb..b....",
    "...bbbbbb.....",
    "....gg.g......",
]
# залито ~55% слева-снизу (мокрая краска)
FILLED = {(c, r) for r in range(14) for c in range(14)
          if ART[r][c] != "." and (c < 7 or (r > 8 and c < 11))}

def rr(d, box, rad, fill, outline=None, width=0):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline, width=width)

def main():
    img = Image.new("RGB", (W, H))
    # фон-градиент
    for y in range(H):
        t = y / H
        img.putpixel((0, y), tuple(int(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOT))) if y % 4 == 0 else None
    bg = img.load()
    for y in range(H):
        t = y / H
        c = tuple(int(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOT))
        for x in range(0, W, 4):
            for dx in range(4):
                if x + dx < W: bg[x + dx, y] = c
    d = ImageDraw.Draw(img, "RGBA")

    # ---------- верхний UI ----------
    rr(d, [24, 30, 92, 98], 20, (255, 255, 255, 230))                      # gear-кнопка
    d.ellipse([40, 46, 76, 82], outline=INK, width=6)
    d.ellipse([52, 58, 64, 70], fill=INK)
    rr(d, [W // 2 - 150, 30, W // 2 + 150, 98], 34, (74, 62, 160, 235))     # Level 17
    d.text((W // 2, 64), "Level 17", font=font(44), fill=WHITE, anchor="mm")
    rr(d, [W - 260, 30, W - 24, 98], 34, (255, 202, 40, 240))               # монеты
    d.ellipse([W - 244, 44, W - 204, 84], fill=(255, 232, 120), outline=(200, 140, 20), width=4)
    d.text((W - 190, 64), "3 460", font=font(40), fill=INK, anchor="lm")

    # ---------- канва ----------
    CX0, CY0, CX1, CY1 = 90, 200, W - 90, 200 + 900
    d.rounded_rectangle([CX0 - 26, CY0 - 26, CX1 + 26, CY1 + 26], 46, (222, 230, 245, 255), outline=(180, 195, 225), width=3)
    rr(d, [CX0, CY0, CX1, CY1], 24, CANVAS_BG)
    cell = (CX1 - CX0) // 14
    ox, oy = CX0 + (CX1 - CX0 - cell * 14) // 2, CY0 + 20
    cmap = {"b": (66, 108, 245), "o": (255, 146, 40), "g": (72, 190, 96)}
    # незалитая текстура (точки «холста»)
    for r in range(14):
        for c in range(14):
            x, y = ox + c * cell, oy + r * cell
            if (c, r) not in FILLED and ART[r][c] != ".":
                d.ellipse([x + cell * 0.35, y + cell * 0.35, x + cell * 0.65, y + cell * 0.65],
                          fill=(224, 214, 190))
    # залитые клетки — «мокрая краска» с бликом
    for (c, r) in FILLED:
        x, y = ox + c * cell, oy + r * cell
        col = cmap[ART[r][c]]
        d.rounded_rectangle([x + 1, y + 1, x + cell - 1, y + cell - 1], cell // 5, col)
        d.ellipse([x + cell * 0.15, y + cell * 0.12, x + cell * 0.55, y + cell * 0.4],
                  fill=(255, 255, 255, 70))
    # блик-полоса на весь залитый массив
    gloss = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    gd.ellipse([-100, 120, W + 100, 340], fill=(255, 255, 255, 46))
    gloss = gloss.filter(ImageFilter.GaussianBlur(18))
    img.paste(gloss.crop((CX0, CY0, CX1, CY0 + 300)), (CX0, CY0), gloss.crop((CX0, CY0, CX1, CY0 + 300)))
    d = ImageDraw.Draw(img, "RGBA")

    # ---------- труба подачи (жидкость капает из трубки) ----------
    PY = CY1 + 60
    rr(d, [W // 2 - 90, PY, W // 2 + 90, PY + 46], 22, (168, 178, 205))
    d.rounded_rectangle([W // 2 - 70, PY + 10, W // 2 + 70, PY + 30], 10, (140, 152, 185))
    for i, dx in enumerate((-46, 0, 46)):                                   # капли
        col = [(66, 108, 245), (255, 146, 40), (66, 108, 245)][i]
        cy = PY + 80 + (18 if i == 1 else 0)
        d.ellipse([W // 2 + dx - 22, cy, W // 2 + dx + 22, cy + 40], fill=col)
        d.ellipse([W // 2 + dx - 12, cy + 5, W // 2 + dx - 2, cy + 16], fill=(255, 255, 255, 90))

    # ---------- вёдра с краской (питатели) ----------
    colors = [(255, 146, 40), (66, 108, 245), (72, 190, 96), (255, 90, 120)]
    labels = ["20", "?", "14", "?"]
    bw, bh, gap = 210, 170, 40
    total = bw * 4 + gap * 3
    x0 = (W - total) // 2
    BY = H - 380
    for i, (col, lab) in enumerate(zip(colors, labels)):
        x = x0 + i * (bw + gap)
        rr(d, [x, BY, x + bw, BY + bh], 26, (255, 255, 255, 235), outline=(210, 218, 235), width=3)
        rr(d, [x + 22, BY + 20, x + bw - 22, BY + bh - 66], 16, col)         # «краска» в ведре
        d.ellipse([x + 34, BY + 30, x + 64, BY + 56], fill=(255, 255, 255, 80))
        rr(d, [x + 20, BY + bh - 52, x + bw - 20, BY + bh - 12], 20, (238, 242, 250))
        d.text((x + bw / 2, BY + bh - 32), lab, font=font(36), fill=INK, anchor="mm")

    # ---------- прогресс 0/5 + бустер-плюс ----------
    rr(d, [W // 2 - 170, H - 170, W // 2 + 10, H - 96], 37, (52, 58, 88, 235))
    d.text((W // 2 - 80, H - 133), "0/5", font=font(46), fill=WHITE, anchor="mm")
    rr(d, [W // 2 + 40, H - 172, W // 2 + 130, H - 94], 39, (92, 200, 92))
    d.text((W // 2 + 85, H - 134), "+", font=font(56), fill=WHITE, anchor="mm")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print("saved:", OUT)

if __name__ == "__main__":
    main()
