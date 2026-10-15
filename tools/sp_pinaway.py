#!/usr/bin/env python3
"""sp_pinaway.py — серия pa1_*: Pin Away (Г5) в каноне design_system v1.0.
usage:
  sp_pinaway.py gen  x OUT.png
  sp_pinaway.py edit SRC.png OUT.png STEP   (STEP: w2|w3|w4)
Кадры: w1 прицел (палец на боковом штифте PB) → w2 R ушли в отвод →
w3 ошибка (слив смеси раньше отвода: потеря кристаллов) → w4 победа.
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
         "top-store hits: glossy clay-plastic toy render, high-saturation candy colors, bright "
         "specular highlights and soft rim light, Blender-style soft studio lighting, high-end mobile "
         "game look. "
         "SETTING: a warm CRYSTAL MINE interior: dark rock walls with wooden support beams, two warm "
         "miner lanterns casting light cones, small glowing crystal formations in the rock, dusty "
         "wooden floor; gentle depth of field. Every object casts a soft grounded shadow with a "
         "contact shadow. UI: chunky 3D dark navy rounded pills with bold white text. No watermark, "
         "no marketing text. ")

SCENE = ("CENTER: one vertical toy GLASS CHANNEL - a rounded translucent glass tube mounted on a "
         "wooden stand, inside it three SECTIONS of chunky candy CRYSTALS (small rounded diamond "
         "gems) separated by two golden pins stuck horizontally through the glass: top section has 2 "
         "glossy BLUE crystals held by the upper golden pin P2; middle section is a MIXTURE of 2 blue "
         "and 2 red crystals held by pin P1; bottom section has 3 glossy BLUE crystals held by the "
         "bottom plug pin P0. A THIRD golden pin PB with a small red flag sticks out of the SIDE of "
         "the middle section: a short metal SPOUT leads from it right and down to a small wooden RED "
         "BOX with a quota pill '0/2'. Below the channel stands a chunky wooden BLUE WAGON with a "
         "quota pill '0/6'. "
         "TOP UI: dark navy pills: 'Level 1', a gold coin with '512', a round gear button. No hearts. "
         "The quota pills are the only counters. ")

P1 = (STYLE + SCENE +
      "ACTION - AIM: a simple cartoon hand with an index finger and a white tap-ripple grips the "
      "side pin PB with the red flag (about to pull it out); a short white dashed line runs from the "
      "PB spout along the metal spout into the red box showing the route: pull PB first and the red "
      "crystals will roll into the red box. Nothing has moved yet.")

P2 = ("Edit this game screenshot. Keep the same mine setting, glass channel, sections, wagon and "
      "boxes. THE PULL HAPPENED: (1) the side pin PB is PULLED OUT - it lies on the wooden floor next "
      "to the stand; (2) the two RED crystals rolled out of the middle section along the metal spout "
      "and landed in the red box - the box quota pill now reads '2/2' with a tiny white checkmark "
      "spark; (3) the middle section now contains only the two blue crystals; (4) NO finger, no tap "
      "ripple. Everything else unchanged: pins P0, P1, P2 still in place, blue wagon '0/6'.")

P3 = ("Edit this game screenshot. Keep the same mine setting, glass channel, sections, wagon and "
      "boxes. A MISTAKE: the player pulled the bottom plug P0 while the mixture was still inside: "
      "(1) pin P0 lies pulled out on the floor; (2) the bottom section AND the middle section have "
      "poured down: three blue crystals sit inside the blue wagon, but the TWO RED crystals fell "
      "PAST the wagon opening and SHATTERED on the wooden floor - red shards and fragments next to "
      "the wagon with a bold red '!' badge floating above them and a small 'crystal lost' note; "
      "(3) the red box stays '0/2' - its quota is now unreachable; (4) the middle section is empty. "
      "Everything else unchanged.")

P4 = ("Edit this game screenshot. Keep the same mine setting, glass channel and UI. THE LEVEL IS "
      "DONE: (1) the blue wagon is FULL of glossy blue crystals with a white checkmark spark and its "
      "quota pill reads '6/6'; (2) the red box is full with two red crystals and reads '2/2' with a "
      "checkmark; (3) the glass channel is completely EMPTY and clean, all golden pins lie pulled out "
      "on the wooden floor in a small tidy row; (4) a golden ribbon banner across the top reads "
      "'LEVEL COMPLETE' in bold white letters with a few confetti pieces. No shards, no warnings, no "
      "finger. No curved lines anywhere.")

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
