#!/usr/bin/env python3
"""rope_map.py — Г4 «Loop Away»: матмодель + солвер + эталон-рендер (L1).
Модель: N бусин по кругу, хорды соединяют ПАРЫ одного цвета. Пересечение хорд
= узел. Тап = обмен местами двух соседних бусин. Победа: 0 пересечений.
Состояние: перестановка бусин. Действие: swap соседних. Ограничение: ходы.
Горлышко (З2): каждый swap меняет пересечения ВСЕХ хорд вокруг — решения
взаимодействуют. Провал: ходы кончились при ненулевых пересечениях.
Солвер: BFS по перестановкам (оптимальное число свапов), assert решаемости.
"""
from PIL import Image, ImageDraw, ImageFont
import itertools, random, math
from collections import deque

random.seed(9)

def font(sz, bold=False):
    for p in ("/System/Library/Fonts/HelveticaNeue.ttc" if bold else "/System/Library/Fonts/Helvetica.ttc",):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()

# ---------- ДАННЫЕ УРОВНЯ L1: 6 бусин, 3 пары, 3 хорды ----------
PAIRS = [(0, 3), (1, 4), (2, 5)]     # индексы бусин в ТЕКУЩЕЙ перестановке, цвета: R, G, B
START = ["R", "G", "B", "R", "G", "B"]  # стартовая расстановка (переплетена)
BUDGET = 4

def crossings(order):
    """хорды i-j и k-l пересекаются, если концы чередуются на окружности"""
    chords = []
    seen = {}
    for i, c in enumerate(order):
        if c in seen:
            chords.append((seen[c], i)); seen.pop(c)
        else:
            seen[c] = i
    n = 0
    for (a, b), (c, dd) in itertools.combinations(chords, 2):
        if (a < c < b < dd) or (c < a < dd < b): n += 1
    return n, chords

def solve(order, budget):
    """BFS: минимальное число соседних свапов до 0 пересечений"""
    start = tuple(order)
    if crossings(start)[0] == 0: return 0, []
    q = deque([(start, [])]); seen = {start}
    while q:
        cur, path = q.popleft()
        if len(path) >= budget: continue
        for i in range(len(cur) - 1):
            nxt = list(cur); nxt[i], nxt[i + 1] = nxt[i + 1], nxt[i]; nxt = tuple(nxt)
            if nxt in seen: continue
            p2 = path + [(i, i + 1)]
            if crossings(nxt)[0] == 0: return len(p2), p2
            seen.add(nxt); q.append((nxt, p2))
    return None, None

k, solution = solve(START, BUDGET)
assert k is not None and k <= BUDGET, (k, solution)
assert k == 3, f"ожидали оптимально 3 свапа, получили {k}"
# проверка решения по шагам
cur = list(START)
for i, j in solution:
    cur[i], cur[j] = cur[j], cur[i]
assert crossings(cur)[0] == 0
print(f"LOOP AWAY L1 ✓ 6 бусин / 3 пары / старт: {crossings(START)[0]} пересечения; "
      f"решение BFS: {k} свапа {solution}; бюджет 4 (1 лишний — обучающий запас)")

# ---------- РЕНДЕР-ЭТАЛОН (старт; раствор свапа: бусины 4↔5 нет — показываем подсказку) ----------
W, H = 760, 940
im = Image.new("RGB", (W, H), (169, 211, 245)); d = ImageDraw.Draw(im)
SAT = {"R": (232, 58, 58), "G": (86, 190, 92), "B": (52, 140, 245)}
GHO = {"R": (246, 216, 216), "G": (214, 240, 216), "B": (212, 230, 250)}
cx, cy, RR = 380, 470, 300
# круглая рама-доска
d.ellipse([cx - RR - 46, cy - RR - 46, cx + RR + 46, cy + RR + 46],
          fill=(252, 252, 250), outline=(226, 224, 218), width=4)
# хорды стартовой раскладки (пересекающиеся) — рисуем дугами-«нитями»
ang = [-90 + i * 60 for i in range(6)]  # бусины каждый 60°
def P(i):
    a = math.radians(ang[i] + 30)  # сдвиг чтобы пары легли красиво
    return (cx + RR * math.cos(a), cy + RR * math.sin(a))
# хорды: 0-3 (R), 1-4 (G), 2-5 (B) — диаметры через центр: пересекаются все тройкой
for (a, b), col in zip(PAIRS, ["R", "G", "B"]):
    pa, pb = P(a), P(b)
    mid = ((pa[0] + pb[0]) / 2 + random.randint(-40, 40), (pa[1] + pb[1]) / 2 + random.randint(-40, 40))
    d.line([pa, mid, pb], fill=SAT[col], width=10)
# бусины
for i in range(6):
    x, y = P(i)
    col = START[i]
    d.ellipse([x - 34, y - 34, x + 34, y + 34], fill=SAT[col], outline=(255, 255, 255), width=5)
    d.ellipse([x - 18, y - 22, x - 2, y - 8], fill=tuple(min(255, v + 60) for v in SAT[col]))
# палец + пунктир между бусинами 4 и 5 (подсказка свапа)
x1, y1 = P(0); x2, y2 = P(1)
d.line([x1, y1, x2, y2], fill=(255, 255, 255), width=6)
for t in [i / 6 for i in range(7)]:
    xx, yy = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
    d.ellipse([xx - 3, yy - 3, xx + 3, yy + 3], fill=(255, 255, 255))
d.ellipse([x2 + 30, y2 - 10, x2 + 96, y2 + 56], outline=(255, 255, 255), width=5)
d.text((x2 + 40, y2 + 4), "свап 1-й", fill=(30, 36, 56), font=font(17))
# ходы: пилюля с 3 точками (З6: ходы = точки, не цифры)
d.rounded_rectangle([40, 40, 260, 96], 20, fill=(30, 36, 56))
d.text((56, 52), "ходы", fill=(255, 255, 255), font=font(22))
for i in range(3):
    d.ellipse([150 + i * 34, 56, 150 + i * 34 + 26, 82], fill=(255, 214, 90))
# счётчик узлов
d.rounded_rectangle([300, 40, 470, 96], 20, fill=(30, 36, 56))
d.text((314, 52), "узлы: 3", fill=(255, 214, 90), font=font(22))
d.rounded_rectangle([540, 40, 720, 96], 20, fill=(30, 36, 56))
d.text((554, 52), "Level 1", fill=(255, 255, 255), font=font(22))
d.text((40, 8), "LOOP AWAY L1: свап соседних бусин убирает пересечение хорды; цель 0 узлов",
       fill=(20, 30, 50), font=font(17))
im.save("loopaway_L1_map.png"); print("loopaway_L1_map.png ✓")
