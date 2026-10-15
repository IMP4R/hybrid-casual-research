#!/usr/bin/env python3
"""paintloop_map.py v6 — эталон Paint Loop БЕЗ посредников (З12).
Ведро само подпрыгивает к канве и льёт ДУГУ краски в подсвеченную зону.
Зона = ЖИДКИЙ уровень с горизонтальной поверхностью и глянцем (не воксель-порции).
Пиксельная сетка = тонкие швы внутри областей. Эталон кадра литья: голова 3/6.
"""
from PIL import Image, ImageDraw, ImageFont
import math

CELL = 60; COLS, ROWS = 9, 12
SAT = {"R": (232, 58, 58), "B": (52, 140, 245), "O": (245, 150, 40), "G": (86, 190, 92)}
GHOST = {"R": (246, 216, 216), "B": (212, 230, 250), "O": (249, 228, 202), "G": (214, 240, 216)}
CELLS = {
    (3, 1): "R", (4, 1): "R", (2, 2): "R", (3, 2): "R", (2, 3): "R", (3, 3): "R",
    (1, 3): "O", (1, 4): "O", (2, 4): "O", (2, 5): "O", (3, 5): "O", (2, 6): "O",
    (4, 3): "G", (3, 4): "G", (4, 4): "G", (4, 5): "G", (3, 6): "G", (4, 6): "G",
    (5, 4): "B", (5, 5): "B", (6, 5): "B",
    (6, 6): "B", (7, 6): "B", (7, 7): "B",
}
EYE = (2, 3)
# жидкий уровень головы 3/6: залиты кубы (2,2),(3,2),(2,3) — но рисуем как ЕДИНУЮ
# жидкую массу нижней трети области: те же кубы + горизонтальная поверхность + блик
LIQUID = {(2, 2), (3, 2), (2, 3)}

def font(sz):
    for p in ("/System/Library/Fonts/Helvetica.ttc",):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()

W, H = 760, 980
im = Image.new("RGB", (W, H), (169, 211, 245))
d = ImageDraw.Draw(im)
bx0, by0, bw, bh = 70, 80, 470, 640
d.rounded_rectangle([bx0 - 12, by0 - 12, bx0 + bw + 12, by0 + bh + 12], 20,
                    fill=(252, 252, 250), outline=(226, 224, 218), width=3)
for c in range(COLS):
    for r in range(ROWS):
        cx, cy = bx0 + 14 + c * (CELL - 12), by0 + 14 + r * (CELL - 12)
        d.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=(228, 226, 222))
def P(c, r): return (bx0 + 14 + c * (CELL - 12), by0 + 14 + r * (CELL - 12))
for (c, r), col in CELLS.items():
    a, b = P(c, r); s = CELL - 26
    base = SAT[col] if (c, r) in LIQUID else GHOST[col]
    box = [a + 2, b + 2, a + s, b + s]
    d.rounded_rectangle(box, 7, fill=base)
    if (c, r) in LIQUID:  # глянец жидкой массы
        d.rounded_rectangle([box[0] + 3, box[1] + 3, box[2] - 3, box[1] + 9], 4,
                            fill=tuple(min(255, v + 45) for v in base))
ex, ey = P(*EYE)
d.ellipse([ex + 10, ey + 12, ex + 19, ey + 21], fill=(255, 255, 255))
# контур зоны головы (подсвечена) + бейдж 3/6
zx0, zy0 = P(2, 1); zx1, zy1 = P(4 - 1 + 1, 4 - 1 + 1)
d.rounded_rectangle([zx0 - 5, zy0 - 5, zx1 + CELL - 22, zy1 + CELL - 22], 10,
                    outline=SAT["R"], width=5)
d.rounded_rectangle([zx1 - 10, zy0 - 34, zx1 + 92, zy0 - 6], 8, fill=(30, 36, 56))
d.text((zx1 + 0, zy0 - 28), "3/6", fill=(255, 255, 255), font=font(18))
# пунктирная дуга от красного ведра к зоне (прицел литья)
tx, ty = P(3, 0)
# красное ведро НАКЛОНЕНО в воздухе над зоной (конец дуги)
bx, by = tx + 230, ty - 60
tilt = -28
bucket = Image.new("RGBA", (180, 160), (0, 0, 0, 0))
bd = ImageDraw.Draw(bucket)
bd.rounded_rectangle([30, 40, 150, 140], 16, fill=(232, 58, 58, 255))
bd.rounded_rectangle([42, 48, 138, 70], 10, fill=(255, 150, 150, 255))
bd.ellipse([48, 20, 132, 78], outline=(200, 200, 205, 255), width=8)   # обод
bd.ellipse([58, 30, 122, 66], fill=(180, 30, 30, 255))                  # краска внутри
bucket = bucket.rotate(tilt, expand=True, resample=Image.BICUBIC)
im.paste(bucket, (bx - 60, by - 70), bucket)
# струя-дуга из наклонённого ведра вниз в зону
pts2 = [(bx + 10 + (tx + 10 - bx - 10) * t - 30 * math.sin(math.pi * t), by + 50 + (ty - 10 - by - 50) * t) for t in [i / 18 for i in range(19)]]
d.line(pts2, fill=(232, 58, 58), width=9)
d.ellipse([tx - 6, ty + 8, tx + 26, ty + 30], fill=(255, 120, 120))     # всплеск
# остальные вёдра внизу
for i, col in enumerate(["O", "G", "B", "B"]):
    x = 330 + i * 110
    d.rounded_rectangle([x, 820, x + 92, 920], 14, fill=(250, 250, 248), outline=(214, 212, 206), width=3)
    d.ellipse([x + 8, 828, x + 84, 872], fill=SAT[col])
d.text((56, 20), "PAINT LOOP v6: ведро льёт САМО (дуга), зона = жидкий уровень (голова 3/6), без крана",
       fill=(20, 30, 50), font=font(19))
im.save("paintloop_map.png"); print("paintloop_map.png", im.size)
