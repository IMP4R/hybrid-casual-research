#!/usr/bin/env python3
"""beltjam_map.py — эталон Belt Jam L1 в каноне design_system v1.0.
Лента вертикальная сверху вниз (не останавливается), развилки S1/S2 — рычаги со
стрелами, внизу три ворот: синие, зелёные, жёлтые. Блоки = глянцевые кубы.
Эталон кадра: S1 пульсирует (блок в 2 клетках), палец тапает, пунктир пути.
"""
from PIL import Image, ImageDraw, ImageFont

CELL = 56
SAT = {"B": (52, 140, 245), "G": (86, 190, 92), "Y": (250, 200, 40)}

def font(sz):
    for p in ("/System/Library/Fonts/Helvetica.ttc",):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()

W, H = 720, 1000
im = Image.new("RGB", (W, H), (169, 211, 245))
d = ImageDraw.Draw(im)
# пол
d.rounded_rectangle([0, 880, W, H], 0, fill=(150, 194, 236))
# лента: вертикальный жёлоб x=320..400, от y=120 до y=700
bx0, bx1, by0, by1 = 320, 400, 120, 700
d.rounded_rectangle([bx0 - 14, by0 - 10, bx1 + 14, by1 + 10], 18, fill=(150, 158, 176))   # борта
d.rounded_rectangle([bx0, by0, bx1, by1], 10, fill=(60, 66, 82))                          # полотно
for y in range(by0 + 14, by1, 36):  # ролики-полосы
    d.line([bx0 + 6, y, bx1 - 6, y], fill=(84, 92, 112), width=5)
# очередь за верхним краем (3 полупрозрачных)
for i, col in enumerate(["G", "Y", "B"]):
    a = 120 - 3 * 44
    d.rounded_rectangle([bx0 + 8, by0 - 150 + i * 44, bx1 - 8, by0 - 150 + i * 44 + 36], 8,
                        fill=tuple(min(255, v + 90) for v in SAT[col]), outline=(255, 255, 255), width=2)
# блоки на ленте
BLOCKS = [("B", 470), ("G", 560)]
for col, y in BLOCKS:
    d.rounded_rectangle([bx0 + 6, y, bx1 - 6, y + 40], 9, fill=SAT[col])
    d.rounded_rectangle([bx0 + 10, y + 4, bx1 - 10, y + 13], 5, fill=tuple(min(255, v + 50) for v in SAT[col]))
# S1: рычаг со стрелой вправо (пульсирует — блок в 2 клетках)
def lever(cx, cy, direction, active):
    col = (255, 186, 20) if active else (226, 228, 234)
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(70, 78, 96), outline=col, width=6)
    ang = {"right": 0, "left": 180, "down": 90}[direction]
    import math
    a = math.radians(ang)
    x2, y2 = cx + 44 * math.cos(a), cy - 44 * math.sin(a)
    d.line([cx, cy, x2, y2], fill=col, width=10)
    d.polygon([(x2 + 12 * math.cos(a), y2 - 12 * math.sin(a)),
               (x2 + 10 * math.cos(a - 2.5), y2 - 10 * math.sin(a - 2.5)),
               (x2 + 10 * math.cos(a + 2.5), y2 - 10 * math.sin(a + 2.5))], fill=col)
S1Y = 250
lever(400, S1Y, "right", True)
d.text((446, S1Y - 30), "S1 пульсирует", fill=(30, 36, 56), font=font(16))
# S2: стрела вниз
S2Y = 470
lever(400, S2Y, "down", False)
d.text((446, S2Y - 30), "S2 прямо", fill=(30, 36, 56), font=font(16))
# палец + рябь на S1
d.ellipse([408, S1Y - 34, 452, S1Y + 10], outline=(255, 255, 255), width=4)
# ворота внизу: три штуки в ряд
GATES = [("B", 120, "открыты"), ("G", 300, "кулдаун: закрыты"), ("Y", 480, "ждут")]
for col, gx, label in GATES:
    d.rounded_rectangle([gx, 740, gx + 120, 850], 16, fill=(250, 250, 248), outline=(214, 212, 206), width=3)
    d.rounded_rectangle([gx + 10, 750, gx + 110, 800], 10, fill=SAT[col])
    d.text((gx + 12, 810), label, fill=(30, 36, 56), font=font(15))
    if label.startswith("кулдаун"):
        d.line([gx + 18, 760, gx + 52, 790], fill=(120, 126, 140), width=7)
        d.line([gx + 52, 760, gx + 18, 790], fill=(120, 126, 140), width=7)
# пунктир пути следующего блока (эхо-подсветка)
for y in range(500, 700, 26):
    d.line([bx0 + 22, y, bx0 + 22, y + 12], fill=(255, 255, 255), width=4)
d.text((40, 24), "BELT JAM L1: лента не останавливается; S1 пульсирует (блок в 2 клетках); палец = поворот 90°",
       fill=(20, 30, 50), font=font(18))
d.text((40, 950), "Ворота принимают свой цвет; после пропуска — кулдаун 1 блок. Счётчик 0/12, сердца 3.",
       fill=(20, 30, 50), font=font(17))
im.save("beltjam_map.png"); print("beltjam_map.png", im.size)
