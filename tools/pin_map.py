#!/usr/bin/env python3
"""pin_map.py v2 — Г5 «Pin Away» честная модель: канал льётся в ОДНУ колбу своего
цвета; чужой кристалл при сливе = ПОТЕРЯ (выпал мимо). Спасение чужих — боковой
отвод со своим штифтом. Тап = выдернуть штифт (необратимо, З1). Провал = квоты
недостижимы. Солвер: перебор порядков штифтов.
L1: низ [B,B,B] (заглушка P0) → смесь [B,R,R,B] (P1 + боковой отвод PB для R)
→ верх [B,B] (P2). Колба BLUE квота 6, красный бокс квота 2.
Решение: PB → P0 → P1 → P2 (PB строго до P1!). Ловушка: P0/P1 раньше PB = потеря
R,R → красная квота недостижима.
"""
from PIL import Image, ImageDraw, ImageFont
import itertools

def font(sz, bold=False):
    for p in ("/System/Library/Fonts/HelveticaNeue.ttc" if bold else "/System/Library/Fonts/Helvetica.ttc",):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()

COL = {"B": (52, 140, 245), "R": (232, 58, 58)}

SECTIONS = {  # сверху вниз
    "A": ["B", "B"],            # верх, держит P2
    "M": ["B", "R", "R", "B"],  # смесь, держит P1; боковой отвод PB выводит R
    "Z": ["B", "B", "B"],       # низ, держит заглушку P0; выход в СИНЮЮ колбу
}
PINS = ["PB", "P0", "P1", "P2"]
HOLDER = {"A": "P2", "M": "P1", "Z": "P0"}
QUOTA = {"B": 6, "R": 2}
WAGON = "B"  # канал выходит в синюю колбу

def simulate(order):
    col = {k: list(v) for k, v in SECTIONS.items()}
    wagon = 0; red = 0; lost = 0; pulled = set()
    for pin in order:
        pulled.add(pin)
        if pin == "PB":  # боковой отвод: R-кристаллы смеси уходят в красный бокс
            kept = []
            for x in col["M"]:
                if x == "R": red += 1
                else: kept.append(x)
            col["M"] = kept
        else:            # освобождена секция — сыплется всё до следующего штифта
            for name, holder in HOLDER.items():
                if holder == pin and name in pulled or holder == pin:
                    for x in col[name]:
                        if x == WAGON: wagon += 1
                        else: lost += 1
                    col[name] = []
    return wagon, red, lost

best = None
for perm in itertools.permutations(PINS):
    wagon, red, lost = simulate(perm)
    if wagon >= QUOTA["B"] and red >= QUOTA["R"] and lost == 0:
        best = perm; break
assert best is not None, "решения нет!"
wagon, red, lost = simulate(best)
assert (wagon, red, lost) == (7, 2, 0), (wagon, red, lost)
print(f"PIN AWAY L1 ✓ порядок: {' → '.join(best)} → колба {wagon}/6, красный бокс {red}/2, потерь 0")
trap = ("P0", "P1", "PB", "P2")
wagon, red, lost = simulate(trap)
print(f"ловушка: {' → '.join(trap)} → колба {wagon}, красный {red}, ПОТЕРЯНО {lost} → квота R недостижима → провал")

# ---------- РЕНДЕР-ЭТАЛОН (старт; палец на PB) ----------
W, H = 640, 1000
im = Image.new("RGB", (W, H), (46, 38, 34)); d = ImageDraw.Draw(im)
def dr(): return ImageDraw.Draw(im)
d = dr()
for lx in (52, 588):
    d.ellipse([lx - 8, 110, lx + 8, 142], fill=(255, 200, 90))
    d.polygon([(lx - 40, 190), (lx + 40, 190), (lx, 142)], fill=(90, 70, 50))
cx0, cw = 220, 150
d.rounded_rectangle([cx0 - 14, 90, cx0 + cw + 14, 730], 18, fill=(210, 226, 240), outline=(150, 170, 190), width=4)
SEC_Y = {"A": 130, "M": 300, "Z": 540}
SEC_CELLS = {"A": ["B", "B"], "M": ["B", "R", "R", "B"], "Z": ["B", "B", "B"]}
for name, cells in SEC_CELLS.items():
    y = SEC_Y[name]
    for i, c in enumerate(cells[:4]):
        x = cx0 + 24 + (i % 2) * 56
        yy = y + (i // 2) * 46
        d.polygon([(x + 14, yy), (x + 30, yy + 16), (x + 14, yy + 32), (x - 2, yy + 16)], fill=COL[c])
def pin(px, py, label):
    d.ellipse([px - 24, py - 13, px + 24, py + 13], fill=(255, 186, 20), outline=(120, 90, 20), width=3)
    d.text((px - 12, py - 10), label, fill=(60, 44, 10), font=font(15))
pin(cx0 + cw + 14, SEC_Y["M"] + 96, "PB")   # боковой отвод
pin(cx0 - 4, 508, "P1")
pin(cx0 - 4, 680, "P0")
pin(cx0 - 4, 268, "P2")
# боковой жёлоб PB → красный бокс
d.line([cx0 + cw + 38, SEC_Y["M"] + 108, 520, SEC_Y["M"] + 108], fill=(150, 158, 176), width=10)
d.line([520, SEC_Y["M"] + 108, 520, 740], fill=(150, 158, 176), width=10)
d.text((cx0 + cw + 52, SEC_Y["M"] + 66), "отвод R", fill=(255, 214, 90), font=font(15))
# палец + пунктир на PB (прицел)
pbx, pby = cx0 + cw + 14, SEC_Y["M"] + 96
d.ellipse([pbx - 42, pby - 34, pbx + 30, pby + 38], outline=(255, 255, 255), width=5)
d.text((pbx - 66, pby - 56), "выдёрнуть первым!", fill=(255, 214, 90), font=font(15))
# колбы
d.rounded_rectangle([150, 800, 330, 950], 16, fill=(250, 250, 248), outline=(214, 212, 206), width=3)
d.rounded_rectangle([162, 812, 318, 900], 10, fill=COL["B"])
d.rounded_rectangle([162, 910, 318, 936], 6, fill=(30, 36, 56))
d.text((176, 912), "квота 0/6", fill=(255, 255, 255), font=font(15))
d.rounded_rectangle([420, 800, 560, 950], 16, fill=(250, 250, 248), outline=(214, 212, 206), width=3)
d.rounded_rectangle([432, 812, 548, 880], 10, fill=COL["R"])
d.rounded_rectangle([432, 910, 548, 936], 6, fill=(30, 36, 56))
d.text((446, 912), "квота 0/2", fill=(255, 255, 255), font=font(15))
d.text((30, 16), "PIN AWAY L1 (рудник): PB первым — уведи R в отвод, потом сливай синие",
       fill=(255, 214, 90), font=font(18))
im.save("pinaway_L1_map.png"); print("pinaway_L1_map.png ✓")
