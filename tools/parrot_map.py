#!/usr/bin/env python3
"""parrot_map.py v2 — эталон ПОДРОБНОГО попугая из 24 вокселей + проверка лучей.
Попугай смотрит влево: R гребень+голова(6), O клюв+грудь(6), G шея+тело(6), B крыло+хвост(6).
Красный: морда(4.5,11.2) → излом(9,9) → перелёт B(7,7),B(6,6),B(5,5),G(4,4),СВОЕЙ R(3,3)
→ посадка в ДАЛЬНЮЮ красную — затылок головы (2,2).
Оранжевый: морда → излом(0,8) → перелёт СВОЕЙ O(2,5), G(3,4) → раскол о зелёную шею G(4,3).
"""
from PIL import Image, ImageDraw, ImageFont
import math

CELL = 60; COLS, ROWS = 9, 12
SAT = {"R": (232, 58, 58), "B": (52, 140, 245), "O": (245, 150, 40), "G": (86, 190, 92)}
GHOST = {"R": (246, 216, 216), "B": (212, 230, 250), "O": (249, 228, 202), "G": (214, 240, 216)}
CELLS = {
    (3, 1): "R", (4, 1): "R",                            # гребень
    (2, 2): "R", (3, 2): "R", (2, 3): "R", (3, 3): "R",  # голова (глаз на (2,3))
    (1, 3): "O", (1, 4): "O",                            # клюв изогнут вниз
    (2, 4): "O", (2, 5): "O", (3, 5): "O", (2, 6): "O",  # щека + грудь
    (4, 3): "G", (3, 4): "G", (4, 4): "G", (4, 5): "G", (3, 6): "G", (4, 6): "G",  # шея/тело
    (5, 4): "B", (5, 5): "B", (6, 5): "B",               # крыло
    (6, 6): "B", (7, 6): "B", (7, 7): "B",               # хвост ступенькой
}
EYE = (2, 3)
MUZZLE = (4.5, 11.2)

def font(sz):
    for p in ("/System/Library/Fonts/Helvetica.ttc",):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()

def panel(path, title, pts, star, target, mode, overfly):
    m = 42
    W, H = COLS * CELL + 2 * m, ROWS * CELL + 2 * m + 66
    im = Image.new("RGB", (W, H), (198, 224, 248))
    d = ImageDraw.Draw(im)
    x0, y0 = m, m + 52
    d.rounded_rectangle([x0 - 14, y0 - 14, x0 + COLS * CELL + 14, y0 + ROWS * CELL + 14],
                        20, fill=(252, 252, 250), outline=(228, 226, 220), width=3)
    for c in range(COLS):
        for r in range(ROWS):
            cx, cy = x0 + c * CELL + CELL // 2, y0 + r * CELL + CELL // 2
            d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(232, 230, 226))
    def P(cx, cy): return (x0 + cx * CELL, y0 + cy * CELL)
    for (c, r), col in CELLS.items():
        a, b = P(c, r)
        box = [a + 4, b + 4, a + CELL - 4, b + CELL - 4]
        base = GHOST[col] if not (target == (c, r) and mode == "fill") else SAT[col]
        d.rounded_rectangle([box[0], box[1] + 5, box[2], box[3] + 5], 10,
                            fill=tuple(max(0, v - 36) for v in base))
        d.rounded_rectangle(box, 10, fill=base)
        d.rounded_rectangle([box[0] + 4, box[1] + 4, box[2] - 4, box[1] + 14], 6,
                            fill=tuple(min(255, v + 26) for v in base))
        d.ellipse([box[0] + 7, box[1] + 8, box[0] + 15, box[1] + 16],
                  fill=tuple(min(255, v + 70) for v in base))
    ex, ey = P(*EYE)
    d.ellipse([ex + 16, ey + 18, ex + 28, ey + 30], fill=(255, 255, 255))
    pts_px = [P(*p) for p in pts]
    for a, b in zip(pts_px, pts_px[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(2, int(L // 20))
        for i in range(n):
            t0, t1 = i / n, min((i + 0.5) / n, 1)
            d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                    (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)],
                   fill=(214, 40, 40) if mode != "break" else (236, 130, 30), width=6)
    for (c, r) in overfly:
        a, b = P(c, r)
        d.rounded_rectangle([a + 3, b + 3, a + CELL - 3, b + CELL - 3], 10,
                            outline=(60, 60, 66), width=3)
    sx, sy = P(*star)
    for rr in (15, 9):
        d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], outline=(255, 186, 20), width=5)
    tx, ty = P(target[0] + 0.5, target[1] + 0.5)
    d.polygon([(tx, ty - 15), (tx - 12, ty + 9), (tx + 12, ty + 9)], fill=(214, 40, 40))
    mx, my = P(*MUZZLE)
    d.ellipse([mx - 20, my - 20, mx + 20, my + 20], fill=(38, 42, 56), outline=(240, 240, 238), width=4)
    d.text((m, 12), title, fill=(30, 34, 44), font=font(26))
    notes = [(P(*star), f"излом {star}"), (P(target[0] + 0.5, target[1] - 1.2),
             ("дальняя СВОЯ — посадка" if mode == "fill" else "дальняя ЧУЖАЯ — раскол"))]
    for (nx, ny), txt in notes:
        tw = d.textlength(txt, font=font(19)); nx = min(max(nx - tw / 2, 6), W - tw - 14)
        d.rounded_rectangle([nx - 7, ny - 5, nx + tw + 7, ny + 23], 7, fill=(30, 34, 44))
        d.text((nx, ny), txt, fill=(255, 255, 255), font=font(19))
    im.save(path); print(path, im.size)

panel("parrot_map_red.png", "КРАСНЫЙ: перелёт 4 чужих + своей ближней → дальняя своя (затылок)",
      [MUZZLE, (9, 9), (2.5, 2.5)], (9, 9), (2, 2), "fill",
      overfly=[(7, 7), (6, 6), (5, 5), (4, 4), (3, 3)])
panel("parrot_map_orange.png", "ОРАНЖЕВЫЙ: перелёт СВОЕЙ груди и тела → раскол о зелёную шею",
      [MUZZLE, (0, 8), (4.5, 3.5)], (0, 8), (4, 3), "break", overfly=[(2, 5), (3, 4)])
