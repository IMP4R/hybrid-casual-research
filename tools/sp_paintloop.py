#!/usr/bin/env python3
"""sp_paintloop.py v6 — серия pl6_*: Paint Loop без посредников (З12).
Ведро льёт САМО дугой; зона = ЖИДКИЙ уровень; пиксельная сетка = швы границ.
usage:
  sp_paintloop.py gen  x OUT.png
  sp_paintloop.py edit SRC.png OUT.png STEP   (STEP: p2|p3|p4)
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
         "top-store hits Sand Loop and Pixel Flow: glossy plastic toy render, high-saturation candy "
         "colors (no pastel wash), bright specular highlights and a soft rim light, Blender-style soft "
         "studio lighting, high-end mobile game look. SETTING: a warm cozy ARTIST'S ATELIER interior: warm cream wall with two wooden shelves holding small paint jars, brushes and a tin watering can, soft daylight falling from a window on the left, light wooden floor planks, gentle depth of field on the shelves.  Every object casts a soft grounded shadow with contact shadow. UI: chunky 3D dark navy "
         "rounded pills with bold white text and thin darker outline. No watermark, no marketing text. ")

SCENE = ("CENTER: one big vertical white toy EASEL board: thick beveled rounded white frame with edge "
         "highlight, RECESSED inner playfield of warm white with a faint light-grey DOT GRID (pegboard), "
         "standing on two short legs, soft grounded shadow. On the board: a pixel-art PARROT picture "
         "facing LEFT drawn as color REGIONS of a pixel grid - thin pixel seams divide the parrot into "
         "small square cells, and thicker outlines divide it into 5 fill ZONES. Level-start state: "
         "every zone is UNFILLED - the cells show a pale translucent ghost tint of their future color: "
         "head zone 6 pale rose cells (crest + 2x2 head with a small white eye dot), beak+breast zone 6 "
         "pale peach cells, body zone 6 pale mint cells, wing zone 3 pale sky-blue cells, tail zone 3 "
         "pale sky-blue cells stepping down-right. The silhouette reads as a parrot at a glance. Each "
         "zone has a small dark navy badge with a color swatch and a counter: '0/6', '0/6', '0/6', "
         "'0/3', '0/3'. The HEAD zone is CURRENT: its outline glows bright red, badge enlarged. "
         "BOTTOM: a row of 5 chunky glossy paint BUCKETS standing on the glossy floor, each with its "
         "paint level visible at the open top and a tiny count label: red (full, 6), orange (full, 6), "
         "green (full, 6), sky-blue (half, 3), sky-blue (half, 3). "
         "TOP UI: dark navy pills: three red hearts, 'Level 25', a gold coin with '512', a round gear "
         "button; a small white pill '0/5' near the board. NO crane, NO hose, NO pipes - the buckets "
         "pour by themselves. ")

P1 = (STYLE + SCENE +
      "ACTION - AIM: a simple cartoon hand with an index finger and a white tap-ripple taps the RED "
      "bucket; a faint RED DASHED ARC curves from the red bucket up to the glowing red head zone on the "
      "board - the pour preview; the red bucket slightly bounced up from its spot with small motion "
      "lines under it. Nothing is pouring yet. Reads instantly: tap the bucket - it will hop up and "
      "pour into the glowing zone.")

P2 = ("Edit this game screenshot. Keep the same sky, board, parrot regions with pixel seams and zone "
      "badges, buckets row, UI. THE POUR: the RED bucket has HOPPED UP and hovers tilted in mid-air "
      "just above the glowing red head zone at the top of the board, pouring a smooth ARC STREAM of "
      "glossy red paint that falls into the zone with a tiny splash crown; INSIDE the head zone a "
      "LIQUID red fill has risen from the bottom covering the lower HALF of the zone as one continuous "
      "glossy mass with a perfectly flat horizontal surface and a bright specular highlight, while the "
      "upper half of the zone still shows pale ghost cells; the head badge now reads '3/6'; a few tiny "
      "red droplets around the stream. NO finger, no tap ripple. Everything else unchanged.")

P3 = ("Edit this game screenshot. Keep the same sky, board, parrot regions, buckets row, UI. THE "
      "OVERFILL MISTAKE: the head zone was already full - its badge reads '6/6' - and one extra dose "
      "has just been poured: a WAVE of red paint SPLASHES OVER the zone outline, red droplets scatter "
      "outward and a thin red PUDDLE collects on the white frame right next to the zone; the head zone "
      "itself is a full glossy red liquid mass with a flat surface; the hearts pill at the top is "
      "slightly tilted with shake arcs around it: two red hearts and a THIRD grey cracked heart, plus "
      "a small red '-1 heart' floater beside the pill; the red bucket hovers mid-air tilted, almost "
      "empty. NO finger. Everything else unchanged.")

P4 = ("Edit this game screenshot. Keep the same sky, board, UI layout. THE LEVEL IS WON: every region "
      "of the parrot is now filled with glossy liquid paint - vivid red head and crest, vivid orange "
      "beak, cheek and breast, vivid green neck and body, vivid sky-blue wing and tail; each region is "
      "one smooth continuous fill with a flat surface and bright specular highlights, thin pixel seams "
      "still visible between regions; the last filled region has a subtle golden sparkle with short "
      "radial rays; a golden ribbon banner across the top of the board reads 'LEVEL COMPLETE' in bold "
      "white letters, a few confetti pieces fall; the zone badges are gone, a white pill '5/5' near "
      "the board; the hearts pill is straight and calm: two red hearts and one grey cracked heart; "
      "all five buckets stand EMPTY on the floor. No puddles, no arcs, no dashed lines. No curved "
      "lines anywhere.")

PROMPTS = {"p2": P2, "p3": P3, "p4": P4}

def gen(out, prompt):
    body = json.dumps({"model": "gpt-image-2", "size": "1024x1536",
                       "quality": "medium", "prompt": prompt}).encode()
    req = urllib.request.Request(GEN, data=body, headers={
        "Authorization": f"Bearer {key()}", "Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
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
