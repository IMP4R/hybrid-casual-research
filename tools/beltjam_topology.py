#!/usr/bin/env python3
"""beltjam_topology.py — топология Belt Jam как ДАННЫЕ → PNG-эталон + текст промта.
Политика: промт сериализуется из структуры, а не пишется руками.
L1: главная линия → S1 (делит на LEFT→BLUE и RIGHT) → S2 (делит RIGHT на GREEN/YELLOW).
"""
from PIL import Image, ImageDraw, ImageFont

def font(sz):
    for p in ("/System/Library/Fonts/Helvetica.ttc",):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()

# ---------- ДАННЫЕ ТОПОЛОГИИ (единственный источник правды) ----------
W, H = 720, 1060
MAIN = [(360, 70), (360, 400)]            # главная линия до S1
S1 = (360, 400)                            # стрелочный перевод 1
BR_LEFT = [(360, 400), (250, 520), (150, 640), (150, 760)]    # к BLUE
BR_RIGHT = [(360, 400), (360, 620)]                            # до S2
S2 = (360, 620)
BR_GREEN = [(360, 620), (360, 760)]                            # к GREEN
BR_YELLOW = [(360, 620), (470, 700), (570, 760)]               # к YELLOW
GATES = {"BLUE": (150, 760), "GREEN": (360, 760), "YELLOW": (570, 760)}
SWITCHES = {"S1": (S1, ["LEFT", "RIGHT"]), "S2": (S2, ["GREEN", "YELLOW"])}
CUBES_ON_BELT = [("B", 330), ("G", 250), ("Y", 160)]           # (цвет, y) на главной

# ---------- РЕНДЕР ----------
im = Image.new("RGB", (W, H), (169, 211, 245)); d = ImageDraw.Draw(im)
d.rectangle([0, 880, W, H], fill=(150, 194, 236))
def rail(pts, wdt=46):
    d.line(pts, fill=(120, 128, 148), width=wdt + 12)
    d.line(pts, fill=(60, 66, 82), width=wdt)
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        L = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        n = int(L // 34)
        for k in range(1, n):
            t = k / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            d.line([x - 16, y - 8, x + 16, y + 8], fill=(84, 92, 112), width=4)
rail(MAIN); rail(BR_LEFT); rail(BR_RIGHT); rail(BR_GREEN); rail(BR_YELLOW)
# кубы на главной линии
for col, y in CUBES_ON_BELT:
    SATC = {"B": (52,140,245), "G": (86,190,92), "Y": (250,200,40)}[col]
    d.rounded_rectangle([330, y, 390, y + 44], 9, fill=SATC)
    d.rounded_rectangle([336, y + 4, 384, y + 14], 5, fill=tuple(min(255, v + 50) for v in SATC))
# стрелки РОВНО на точках ветвления (указывают на активную ветвь)
import math
def switch(name, pos, active_branch):
    (x, y) = pos
    d.ellipse([x - 30, y - 30, x + 30, y + 30], fill=(52, 60, 88), outline=(255, 186, 20), width=6)
    ang = {"LEFT": 200, "RIGHT": -20, "GREEN": 90, "YELLOW": 30}[active_branch]
    a = math.radians(ang)
    x2, y2 = x + 52 * math.cos(a), y - 52 * math.sin(a)
    d.line([x, y, x2, y2], fill=(255, 186, 20), width=10)
    d.text((x - 14, y + 34), name, fill=(30, 36, 56), font=font(18))
switch("S1", S1, "LEFT")     # в эталоне игрок перевёл на LEFT (синий идёт в BLUE)
switch("S2", S2, "GREEN")
# ворота
for name, (gx, gy) in GATES.items():
    col = {"BLUE": (52,140,245), "GREEN": (86,190,92), "YELLOW": (250,200,40)}[name]
    d.rounded_rectangle([gx - 60, gy, gx + 60, gy + 130], 16, fill=(250,250,248), outline=(214,212,206), width=3)
    d.rounded_rectangle([gx - 48, gy + 10, gx + 48, gy + 60], 10, fill=col)
    d.text((gx - 44, gy + 22), name, fill=(255,255,255), font=font(20))
    d.text((gx - 52, gy + 70), "принимает свой цвет", fill=(60, 66, 82), font=font(12))
    if name == "GREEN":
        d.rounded_rectangle([gx - 20, gy + 88, gx + 20, gy + 118], 6, fill=(70, 78, 96))
        d.text((gx - 12, gy + 92), "⏱", fill=(255,255,255), font=font(16))
d.text((30, 20), "BELT JAM L1: граф ветвлений. S1 делит путь: LEFT→BLUE / RIGHT→S2; S2: GREEN/YELLOW",
       fill=(20, 30, 50), font=font(17))
im.save("bj_L1_topology.png"); print("bj_L1_topology.png ✓")

# ---------- ГЕНЕРАЦИЯ ТЕКСТА ПРОМТА ИЗ ДАННЫХ ----------
def pct(y): return f"{round(100 * y / H)}% of the screen height"
PROMPT_TOPOLOGY = (
    f"TOPOLOGY - THE BELT IS A BRANCHING NETWORK, not one straight line: the MAIN BELT enters at the "
    f"top center and runs down to junction S1 at {pct(S1[1])}; there the track PHYSICALLY SPLITS into "
    f"two separate belt branches like a railway switch: the LEFT branch curves down-left and feeds the "
    f"BLUE gate at the bottom-left; the RIGHT branch continues down to junction S2 at {pct(S2[1])}, "
    f"where it SPLITS again into two branches: one straight down into the GREEN gate (center bottom) "
    f"and one curving down-right into the YELLOW gate (bottom-right). All three gates stand in a row "
    f"at the bottom, each receiving its own branch rail. Each junction has a chunky round switch base "
    f"mounted EXACTLY at the split point with a fat arrow pointer showing which branch is currently "
    f"connected: S1 currently points onto the LEFT branch, S2 points straight down to GREEN.")
print("\n=== ПРОМТ-ФРАГМЕНТ (сгенерирован из данных) ===")
print(PROMPT_TOPOLOGY)
with open("bj_topology_prompt.txt", "w") as f:
    f.write(PROMPT_TOPOLOGY)
print("\nсохранён в bj_topology_prompt.txt")
