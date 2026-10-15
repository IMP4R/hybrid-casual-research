#!/usr/bin/env python3
"""Эталонная геометрия рикошетов Shot Painter (проверка логики перед промтами).
Сетка 9x12, 12 ghost-клеток (4 кластера), два выстрела по 45° с отражением от стен.
Красный: излом на ПРАВОЙ стене (9,7), перелёт blue(7,5)/orange(5,3)/red(3,1), посадка в ДАЛЬНЮЮ red(2,0).
Оранжевый: излом на ЛЕВОЙ стене (0,6), перелёт green(1,4), раскол в green(2,3) — чужой цвет.
"""
from PIL import Image, ImageDraw, ImageFont

CELL = 60; COLS, ROWS = 9, 12
SAT = {"R": (215, 60, 50), "B": (60, 130, 230), "O": (240, 140, 40), "G": (80, 180, 80)}
GHOST = {"R": (243, 213, 213), "B": (205, 224, 242), "O": (246, 224, 196), "G": (208, 236, 212)}
CELLS = {  # (col,row) -> цвет
    (2, 0): "R", (3, 1): "R", (1, 2): "R",      # красные, top-left
    (7, 5): "B", (8, 3): "B", (8, 4): "B",      # синие, правый край
    (5, 3): "O", (4, 4): "O", (5, 5): "O",      # оранжевые, центр
    (1, 4): "G", (2, 3): "G", (2, 5): "G",      # зелёные, левый край
}

def font(sz):
    for p in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()

def panel(path, title, path_pts, star_pt, target_cell, target_mode, skipped):
    m = 46
    W, H = COLS * CELL + 2 * m, ROWS * CELL + 2 * m + 90
    im = Image.new("RGB", (W, H), (250, 247, 242))
    d = ImageDraw.Draw(im)
    x0, y0 = m, m + 70
    # доска + толстые стены
    d.rounded_rectangle([x0 - 10, y0 - 10, x0 + COLS * CELL + 10, y0 + ROWS * CELL + 10],
                        18, fill=(255, 255, 255), outline=(176, 168, 158), width=10)
    # клетки
    for (c, r), col in CELLS.items():
        fill = GHOST[col]
        if (c, r) == target_cell and target_mode == "fill":
            fill = SAT[col]
        d.rounded_rectangle([x0 + c * CELL + 3, y0 + r * CELL + 3, x0 + (c + 1) * CELL - 3, y0 + (r + 1) * CELL - 3],
                            10, fill=fill, outline=(255, 255, 255), width=3)
    # подсветка "перелетаемых" клеток
    for (c, r) in skipped:
        d.rounded_rectangle([x0 + c * CELL + 1, y0 + r * CELL + 1, x0 + (c + 1) * CELL - 1, y0 + (r + 1) * CELL - 1],
                            10, outline=SAT[CELLS[(c, r)]], width=3)
    def P(cx, cy):  # координаты в клетках -> px
        return (x0 + cx * CELL, y0 + cy * CELL)
    # траектория: ломаная из ПРЯМЫХ сегментов
    pts = [P(*p) for p in path_pts]
    d.line(pts, fill=(50, 50, 55), width=6)
    for a, b in zip(pts, pts[1:]):  # пунктир поверх
        seg_len = ((b[0]-a[0])**2 + (b[1]-a[1])**2) ** 0.5
        n = int(seg_len // 22)
        for i in range(n + 1):
            t0, t1 = i / (n + 1), min((i + 0.55) / (n + 1), 1)
            d.line([ (a[0]+(b[0]-a[0])*t0, a[1]+(b[1]-a[1])*t0),
                     (a[0]+(b[0]-a[0])*t1, a[1]+(b[1]-a[1])*t1) ], fill=(225, 45, 35) if target_mode != "break" or True else (225,45,35), width=6)
    # звезда отскока РОВНО на стене
    sx, sy = P(*star_pt)
    for rr in (16, 10):
        d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], outline=(255, 180, 20), width=5)
    for ang in range(8):
        import math
        a = ang * math.pi / 4
        d.line([sx + 18 * math.cos(a), sy + 18 * math.sin(a), sx + 27 * math.cos(a), sy + 27 * math.sin(a)],
               fill=(255, 180, 20), width=4)
    # наконечник в целевой клетке
    tx, ty = P(target_cell[0] + 0.5, target_cell[1] + 0.5)
    d.polygon([(tx, ty - 16), (tx - 13, ty + 10), (tx + 13, ty + 10)], fill=(225, 45, 35))
    # пушка-морда в старте
    mx, my = P(*path_pts[0])
    d.ellipse([mx - 24, my - 24, mx + 24, my + 24], fill=(52, 60, 88), outline=(230, 200, 90), width=5)
    # подписи
    d.text((m, 16), title, fill=(40, 40, 45), font=font(30))
    notes = [
        (P(*star_pt), f"излом РОВНО на стене {star_pt}"),
        (P(target_cell[0] + 0.5, target_cell[1] - 1.3),
         ("дальняя СВОЯ — посадка ✓" if target_mode == "fill" else "дальняя ЧУЖАЯ — раскол ✗ −♥")),
    ]
    for (nx, ny), txt in notes:
        tw = d.textlength(txt, font=font(21))
        nx = min(max(nx - tw / 2, 8), W - tw - 8)
        d.rounded_rectangle([nx - 8, ny - 6, nx + tw + 8, ny + 26], 8, fill=(40, 40, 45))
        d.text((nx, ny), txt, fill=(255, 255, 255), font=font(21))
    im.save(path); print(path, im.size)

# ВЫСТРЕЛ 1 (красный): (5,11) -> излом (9,7) -> дальняя red(2,0)
panel("ricochet_layout_red.png", "ВЫСТРЕЛ 1: КРАСНЫЙ по 45°",
      [(5, 11), (9, 7), (2.5, 0.5)], (9, 7), (2, 0), "fill",
      skipped=[(7, 5), (5, 3), (3, 1)])
# ВЫСТРЕЛ 3 (оранжевый): (5,11) -> излом (0,6) -> раскол в green(2,3)
panel("ricochet_layout_orange.png", "ВЫСТРЕЛ 3: ОРАНЖЕВЫЙ — промах",
      [(5, 11), (0, 6), (2.5, 3.5)], (0, 6), (2, 3), "break",
      skipped=[(1, 4)])
