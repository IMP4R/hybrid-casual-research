#!/usr/bin/env python3
"""sp_ricochet.py — генерация/правка кадров Shot Painter (рикошеты) через gpt-image-2.
usage:
  sp_ricochet.py gen  OUT.png
  sp_ricochet.py edit SRC.png OUT.png STEP   (STEP: f2|f3|f4)
Промты зашиты здесь: геометрия = эталон из tools/ricochet_layout.py.
"""
import base64, json, pathlib, re, sys, time, uuid
import urllib.request

BASE = "https://ru.cheapvibecode.ru/v1/images/edits"
GEN = "https://ru.cheapvibecode.ru/v1/images/generations"
M = pathlib.Path("/Users/user0/godot-hybrid-casual/research/mockups")

def key():
    m = re.search(r"CHEAPVIBECODE_API_KEY:\s*['\"]?([^'\"\n]+)",
                  (pathlib.Path.home() / ".dsh" / ".credentials.yaml").read_text())
    return m.group(1).strip()

STYLE = ("Mobile game screenshot, vertical 9:16, casual puzzle game in the soft candy-toy style of "
         "top-store hyper-casual hits (Sand Loop / Marble Sort art quality). The whole scene sits on a "
         "FLAT SOLID PALE SKY-BLUE background, perfectly clean and completely empty: NO furniture, NO "
         "shelves, NO window, NO wooden room, NO tools, NO clutter - only smooth pastel blue. Chunky "
         "rounded 3D shapes, gentle soft shading, soft drop shadows, sweet candy pastel palette, large "
         "rounded white UI pills, crisp numbers, airy minimal composition. No watermark, no marketing text. ")

P1 = STYLE + ("TOP UI: white pill with three red hearts, white pill 'Level 40', coin pill '512', "
"round gear button. "
"CENTER: one big vertical WHITE game board, a rounded rectangle like a clean pegboard with a very "
"faint light-grey DOT GRID of tiny dots inside and a soft drop shadow; its thick smooth edge acts as "
"a solid WALL. NOT wood, NOT a framed picture - a clean white toy board floating on the blue. "
"On the board exactly 12 large rounded-square ghost tiles in 4 clusters, each tile filled with a "
"pale desaturated candy pastel of its color and a soft inner bevel: "
"3 pale ROSE tiles in the TOP-LEFT corner area arranged as a small diagonal staircase; 3 pale "
"SKY-BLUE tiles along the RIGHT edge in the upper-middle area; 3 pale PEACH tiles in the CENTER "
"of the board; 3 pale MINT tiles along the LEFT edge in the middle area. All the rest of the "
"board is clean white empty space. Tiles are big, clearly separated, easy to count. "
"AIM GUIDE: from the cannon muzzle a RED DASHED aim line made of EXACTLY TWO STRAIGHT RULER "
"SEGMENTS, like a billiard ball reflecting off a cushion, like a laser beam reflecting off a "
"mirror: (1) segment one starts at the cannon muzzle below the board, goes diagonally UP-RIGHT at "
"45 degrees, crosses the bottom edge of the board and runs to the RIGHT BORDER of the board, "
"meeting it exactly ON the wall at about 55% of the board height; right at that contact "
"point a small yellow four-point star spark sits ON the wall. (2) At that star the line makes a "
"SHARP ANGULAR CORNER (perfect mirror reflection) and segment two goes diagonally UP-LEFT at 45 "
"degrees, visibly passing OVER one pale sky-blue tile, then over one pale peach tile, then over a "
"pale rose tile, and finally ends with a small red triangular arrowhead INSIDE the FARTHEST pale "
"rose tile at the top-left corner of the board. Both segments are perfectly straight with a crisp "
"angular bend only at the wall. ABSOLUTELY NO curved lines, NO arcs, NO semicircles anywhere in "
"the entire image. "
"BOTTOM: a small cute navy-black cartoon mortar cannon on tiny dark wheels, its big round muzzle "
"with a thick white rim tilted 45 degrees UP-RIGHT matching segment one, a glossy RED rounded "
"candy tile loaded and visible in the muzzle; a simple cartoon hand with an index finger taps the "
"cannon with a white tap-ripple - the tap affordance. Below the cannon a white pill '0/12'. "
"A white rounded tray at the bottom with three next candy tiles: orange, green and sky-blue.")

P2 = ("Edit this game screenshot. Keep EVERYTHING exactly the same: same flat pale-blue background, same "
"white pegboard board, same 12 pale ghost tiles in their 4 clusters, same two-segment "
"red dashed aim line with the yellow star spark exactly ON the right wall and the red arrowhead "
"inside the farthest top-left rose tile, same UI pills (three hearts, Level 40, 512), same "
"'0/12' pill, same tray with orange, green, blue tiles, same lighting. CHANGE ONLY THIS: "
"(1) The red cube is no longer in the cannon muzzle - the cannon muzzle is now open and empty, "
"still tilted 45 degrees up-right. "
"(2) A glossy RED rounded cube now flies IN MID-AIR along the SECOND upper-left straight segment "
"of the dashed line, positioned about one tile length away from the right wall past the yellow "
"star, with a short straight motion trail of red streaks behind it pointing exactly back along "
"that same straight segment toward the yellow star on the wall. The flying cube sits exactly ON "
"the dashed line, slightly rotated, slightly motion-blurred. "
"All line segments stay perfectly straight, sharp bend only at the wall, no curves anywhere.")

P3 = ("Edit this game screenshot. Keep the same flat pale-blue background, same board: its smooth edge is the "
"frame, same 12 pale ghost tiles in 4 clusters, same UI layout, same bottom tray, same lighting. "
"CHANGES: "
"(1) The farthest pale rose tile at the top-left corner is now FILLED with a SATURATED glossy "
"red rounded cube sitting inside it - the first shot succeeded. "
"(2) The old red dashed line and its arrowhead are REMOVED. A NEW ORANGE DASHED aim line made of "
"exactly TWO STRAIGHT RULER SEGMENTS now runs from the cannon muzzle diagonally UP-LEFT at 45 "
"degrees to the LEFT edge of the board, meeting it exactly ON the wall at half the board height with a "
"small yellow star spark at that contact point, then a sharp angular mirror-reflection corner, "
"and the second straight segment goes diagonally UP-RIGHT passing over one pale mint tile and "
"ending at the NEXT pale mint tile to the right of it, where an ORANGE tile has just SHATTERED: "
"orange shards and fragments burst over that pale mint tile, a bold red X floats above the "
"shards and a small red '-1' with a tiny broken heart sits next to it. "
"(3) The top hearts pill now shows only TWO red hearts, the third heart is empty and grey. "
"(4) The progress pill now reads '1/12'. "
"(5) The cannon muzzle now holds a glossy GREEN rounded cube tilted 45 degrees up-left, matching "
"the first segment of the new orange line. "
"All segments perfectly straight, sharp bends only at the wall, NO curved lines anywhere.")

P4 = ("Edit this game screenshot. Keep the same flat pale-blue background, the same board, UI layout "
"and lighting. CHANGES - the level is WON: "
"(1) ALL 12 tiles on the board are now FILLED with SATURATED glossy rounded cubes in their "
"cluster colors: the 3 top-left tiles vivid red, the 3 right-edge tiles vivid sky-blue, the 3 "
"center tiles vivid orange, the 3 left-edge tiles vivid green. The board reads as a bright "
"finished mosaic of chunky candy-like cubes. "
"(2) All dashed aim lines, yellow wall stars and shards are REMOVED. "
"(3) A golden ribbon banner across the upper part of the board reads 'LEVEL COMPLETE' in bold "
"white letters, with a few small confetti pieces floating around the board. "
"(4) The progress pill now reads '12/12'. The hearts pill keeps two red hearts and one empty "
"grey heart. "
"(5) The cannon stands relaxed with an empty muzzle, no aim line. No curved lines anywhere.")

PROMPTS = {"f2": P2, "f3": P3, "f4": P4}

def gen(out, prompt):
    body = json.dumps({"model": "gpt-image-2", "size": "1024x1536",
                       "quality": "medium", "prompt": prompt}).encode()
    req = urllib.request.Request(GEN, data=body, headers={
        "Authorization": f"Bearer {key()}", "Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=300)
        r = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]}")
    (M / out).write_bytes(base64.b64decode(r["data"][0]["b64_json"]))
    print(f"{out} ok ({(M / out).stat().st_size} bytes)")

def edit(src, out, prompt):
    boundary = uuid.uuid4().hex
    parts = []
    for name, val in (("model", "gpt-image-2"), ("size", "1024x1536"),
                      ("quality", "medium"), ("prompt", prompt)):
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}\r\n'.encode())
    img = (M / src).read_bytes()
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{src}"\r\n'
                 f'Content-Type: image/png\r\n\r\n'.encode() + img + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    req = urllib.request.Request(BASE, data=b"".join(parts), headers={
        "Authorization": f"Bearer {key()}",
        "Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        resp = urllib.request.urlopen(req, timeout=300)
        r = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]}")
    (M / out).write_bytes(base64.b64decode(r["data"][0]["b64_json"]))
    print(f"{out} ok ({(M / out).stat().st_size} bytes)")

if __name__ == "__main__":
    a = sys.argv[1:]
    mode = a[0]
    if mode == "gen":
        src, out, step = None, a[2], None
    else:
        src, out, step = a[1], a[2], a[3]
    for attempt in (1, 2, 3):
        try:
            if mode == "gen":
                gen(out, P1)
            else:
                edit(src, out, PROMPTS[step])
            break
        except Exception as e:
            print(f"[{out}] попытка {attempt}: {str(e)[:160]}")
            if attempt < 3:
                time.sleep(35)
