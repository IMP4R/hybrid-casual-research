#!/usr/bin/env python3
"""sp_loopaway.py — серия la1_*: Loop Away (Г4) в каноне design_system v1.0.
usage:
  sp_loopaway.py gen  x OUT.png
  sp_loopaway.py edit SRC.png OUT.png STEP   (STEP: w2|w3|w4)
Кадры: w1 прицел (палец на паре соседних бусин) → w2 свап (узел исчез, ✓)
→ w3 ошибка (новый узел, «!», ход сожжён) → w4 победа (0 узлов).
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

STYLE = ("Mobile game screenshot, vertical 9:16, casual puzzle game in the soft candy-clay style of "
         "top-store hits: glossy clay-plastic toy render, high-saturation candy colors (no pastel "
         "wash), bright specular highlights and a soft rim light on every object, Blender-style soft "
         "studio lighting, high-end mobile game look. "
         "SETTING: a quiet SEA PIER at dusk: weathered wooden deck planks, thick mooring ropes "
         "wrapped around wooden mooring posts at the sides, two warm harbor lamps glowing softly, a "
         "far lighthouse silhouette in a gentle sea mist, calm dark water with subtle ripples along "
         "the very bottom edge; gentle depth of field. Every object casts a soft grounded shadow with "
         "a contact shadow. UI: chunky 3D dark navy rounded pills with bold white text and a thin "
         "darker outline. No watermark, no marketing text. ")

SCENE = ("CENTER: one big CIRCULAR white toy frame like a porthole - a thick beveled white ring with "
         "an edge highlight, a RECESSED round playfield of warm white with a faint light-grey DOT GRID "
         "of tiny dots, standing on three short legs, soft grounded shadow. Inside the ring: a festive "
         "GARLAND - glossy candy BEADS sitting on the ring at even positions, connected by slightly "
         "sagging THREADS of yarn stretched across the circle. There are exactly 6 beads: two glossy "
         "RED, two glossy GREEN, two glossy SKY-BLUE, placed so the three threads (red, green, blue) "
         "CROSS each other near the center forming 3 visible KNOTS - the garland looks tangled. The "
         "threads slightly sag like real yarn with soft shading. "
         "TOP UI: a dark navy pill 'MOVES' with three glowing golden dots in a row (three moves left); "
         "a dark navy pill 'knots: 3'; a dark navy pill 'Level 1'; a gold coin '512'; a round gear "
         "button. No other text. ")

P1 = (STYLE + SCENE +
      "ACTION - AIM: a simple cartoon hand with an index finger and a white tap-ripple points between "
      "two ADJACENT beads on the ring - the glossy RED bead at the upper-right and the glossy GREEN "
      "bead at the right; a short white dashed line connects exactly these two beads showing the swap "
      "hint; nothing has moved yet. Reads instantly: tap the pair to swap them and untangle.")

P2 = ("Edit this game screenshot. Keep the same pier setting, circular frame, thread layout, pills. "
      "THE SWAP HAPPENED: (1) the red and green beads have SWAPPED places along the ring with a "
      "springy motion arc and a tiny dust puff at both spots; (2) the RED thread is now STRAIGHT and "
      "no longer crosses any other thread - it glows softly with a small white checkmark spark on it; "
      "(3) only TWO thread crossings remain near the center; (4) in the MOVES pill the third golden "
      "dot has gone dark grey - one move spent, two left; the knots pill reads 'knots: 2'. NO finger, "
      "no tap ripple. Everything else unchanged.")

P3 = ("Edit this game screenshot. Keep the same pier setting, circular frame, thread layout, pills. "
      "A MISTAKE: the player made a careless swap that created a NEW crossing: (1) two threads now "
      "cross in a NEW place lower-left with a bold red '!' badge floating above the fresh knot and "
      "the two beads next to it slightly trembling with small motion arcs; (2) only ONE golden dot "
      "remains lit in the MOVES pill, two dots are dark grey; (3) the knots pill reads 'knots: 2'. "
      "Everything else unchanged, same pier background and lighting.")

P4 = ("Edit this game screenshot. Keep the same pier setting, circular frame, pills, crane-free "
      "layout. THE LEVEL IS SOLVED: the garland is perfectly UNTANGLED - all threads run as clean "
      "parallel arcs with ZERO crossings, each thread glowing in its color with a bright specular "
      "line, beads vivid and glossy; every thread has a tiny white checkmark spark; a golden ribbon "
      "banner across the top of the ring reads 'LEVEL COMPLETE' in bold white letters, a few confetti "
      "pieces float around; the MOVES pill shows ONE golden dot and two dark grey dots; a dark navy "
      "pill reads 'knots: 0' with the zero in gold. No finger, no dashes, no warning marks. No curved "
      "lines except the natural thread arcs and ring circle.")

PROMPTS = {"w2": P2, "w3": P3, "w4": P4}

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
            if attempt < 3: time.sleep(35)
