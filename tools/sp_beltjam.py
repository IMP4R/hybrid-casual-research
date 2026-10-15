#!/usr/bin/env python3
"""sp_beltjam.py — серия bj_*: Belt Jam в каноне design_system v1.0.
usage:
  sp_beltjam.py gen  x OUT.png
  sp_beltjam.py edit SRC.png OUT.png STEP   (STEP: b2|b3|b4)
Кадры: b1 прицел (палец на пульсирующем S1) → b2 проход (поворот+куб ушёл в ворота)
→ b3 джем (куб вклинился, −♥) → b4 победа. Эталон: tools/beltjam_map.py.
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
         "studio lighting, high-end mobile game look. SETTING: a warm industrial SORTING DEPOT interior: soft grey-blue concrete wall with metal shelving holding wooden crates in soft blur, two hanging industrial lamps casting warm light cones over the conveyor, concrete floor with a painted yellow guide line.  Every object casts a soft grounded shadow with "
         "contact shadow. UI: chunky 3D dark navy rounded pills with bold white text and thin darker "
         "outline. No watermark, no marketing text. ")

SCENE = ("CENTER: a chunky toy SORTING CONVEYOR crossing the screen vertically: a dark rubber belt "
         "with roller slats inside polished metal side rails with bright edge highlights, standing on "
         "sturdy rounded legs on the glossy floor. TOPOLOGY - THE BELT IS A BRANCHING NETWORK, not one straight line: the MAIN BELT enters at the top center and runs down to junction S1 at 38% of the screen height; there the track PHYSICALLY SPLITS into two separate belt branches like a railway switch: the LEFT branch curves down-left and feeds the BLUE gate at the bottom-left; the RIGHT branch continues down to junction S2 at 58% of the screen height, where it SPLITS again into two branches: one straight down into the GREEN gate (center bottom) and one curving down-right into the YELLOW gate (bottom-right). All three gates stand in a row at the bottom, each receiving its own branch rail. Each junction has a chunky round switch base mounted EXACTLY at the split point with a fat arrow pointer showing which branch is currently connected: S1 currently points onto the LEFT branch, S2 points straight down to GREEN. Chunky glossy candy CUBES (blue, green, yellow) ride down the belt; "
         "the next cubes peek above the top edge as a queue. "
         "TOP UI: dark navy pills: three red hearts, 'Level 1', a gold coin with '512', a round gear "
         "button; a small white pill '0/12' near the conveyor. ")

P1 = (STYLE + SCENE +
      "ACTION - AIM: the first BLUE cube is just two cells above the S1 switch; the S1 arrow pointer "
      "PULSES with a bright glowing outline (it is time to decide); a simple cartoon hand with an "
      "index finger and a white tap-ripple taps the S1 lever; a faint white dashed line runs along the "
      "belt from the blue cube down past S2 to the gates - the planned path preview; the S2 arrow "
      "points straight down; a green cube follows behind the blue one on the belt; the blue gate is "
      "open, the green gate is closed with a small padlock icon (cooldown), the yellow gate waits.")

P2 = ("Edit this game screenshot. Keep the same sky, conveyor, gates, queue and UI. THE TAP HAPPENED: "
      "(1) the S1 arrow pointer has ROTATED 90 degrees to the new direction, with a short curved "
      "motion arc around the lever base and a tiny click spark; (2) the BLUE cube rides PAST S1 "
      "leaning slightly into the turn, with small speed streaks on the belt behind it, and the GREEN "
      "cube approaches S1 right behind it; (3) further down, the BLUE gate flaps are OPEN and a blue "
      "cube has just dropped through with a small blue puff at the opening; (4) the progress pill now "
      "reads '1/12'. NO finger, no tap ripple. Everything else unchanged.")

P3 = ("Edit this game screenshot. Keep the same sky, conveyor, gates, queue and UI. A JAM HAS HAPPENED "
      "deeper down: a YELLOW cube has wedged itself diagonally across the GREEN gate opening and is "
      "stuck half-in: the green gate flashes warning red, a bold red '!' badge floats above it, small "
      "grey smoke puffs rise from the wedged cube; the hearts pill at the top is slightly tilted with "
      "shake arcs around it: two red hearts and a THIRD grey cracked heart, plus a small red '-1 "
      "heart' floater beside the pill; meanwhile the belt keeps moving - the next blue cube "
      "approaches the S2 switch and the S2 arrow pointer is mid-rotation with a curved motion arc as "
      "the player fixes the route; the progress pill reads '7/12'. Everything else unchanged.")

P4 = ("Edit this game screenshot. Keep the same sky, conveyor, gates and UI. THE LEVEL IS SORTED: the "
      "belt is completely EMPTY and still - no cubes anywhere, the queue above the top edge is gone; "
      "all three gates stand OPEN with soft color glows and each has a white checkmark badge on its "
      "panel, sorted cube stacks visible inside their openings: a blue stack, a green stack, a yellow "
      "stack; a golden ribbon banner across the top of the screen reads 'LEVEL COMPLETE' in bold white "
      "letters, a few confetti pieces fall around the conveyor; the progress pill reads '12/12'; the "
      "hearts pill is straight and calm: two red hearts and one grey cracked heart - the price of the "
      "jam; the levers stand relaxed. No smoke, no dashes, no warning flashes.")

PROMPTS = {"b2": P2, "b3": P3, "b4": P4}

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
