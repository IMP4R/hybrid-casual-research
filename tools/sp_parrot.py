#!/usr/bin/env python3
"""sp_parrot.py — серия sr3: попугай-воксели + стиль референсов + АНИМАЦИИ действий.
usage:
  sp_parrot.py gen  x OUT.png
  sp_parrot.py edit SRC.png OUT.png STEP   (STEP: f2|f3|f4)
Канон карты: tools/parrot_map.py. Стиль: research/analyses/style_gap.md.
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
         "colors (no pastel wash), bright specular highlights and a soft rim light on every tile and "
         "button, Blender-style soft studio lighting, high-end mobile game look. Background: vivid blue "
         "SETTING: a sunny outdoor TERRACE: warm terracotta brick wall behind the scene, a leafy climbing plant hanging into the top corner, wooden deck floor boards, warm afternoon sunlight, gentle depth of field. "
         "grounded drop shadow with gentle contact shadow where it meets a surface. UI: chunky 3D dark "
         "navy rounded pills with bold white text, subtle bevel and thin darker outline. No watermark, "
         "no marketing text. ")

BOARD = ("CENTER: one big vertical white toy EASEL: a thick white board with a heavy beveled rounded "
         "frame, bright edge highlight, and a RECESSED inner playfield of very light warm white with a "
         "faint light-grey DOT GRID of tiny dots (pegboard, like an unfilled silicone mold); a soft "
         "grounded shadow under the board on the blue background. ")

PARROT = ("On the board: a LARGE detailed pixel-art PARROT built from exactly 24 big rounded voxel "
          "candy cubes (same voxel unit as Pixel Flow), facing LEFT - the mosaic fills most of the "
          "board like a coloring poster and the full parrot silhouette reads at a glance. Level-start "
          "state: EVERY voxel is an EMPTY GHOST cube - a shallow recessed slot holding a pale "
          "translucent ghost cube of its final color, same bevels as a filled cube. Anatomy by color: "
          "6 PALE ROSE ghost cubes - two crest cubes on top and a 2x2 square head below them, with one "
          "small white round eye dot on the front head cube; 6 PALE PEACH ghost cubes - two cubes of a "
          "hooked beak sticking out to the LEFT, the cheek and a column of breast cubes below the "
          "head; 6 PALE MINT ghost cubes - the neck and the tall body behind the breast; 6 PALE "
          "SKY-BLUE ghost cubes - the wing on the back and a tail stepping down to the right. All "
          "other playfield stays empty pegboard. ")

CANNON = ("BOTTOM: a small cute navy-black mortar cannon on tiny dark wheels, big round muzzle with a "
          "thick white rim, standing on the implied glossy floor with a soft contact shadow; below it "
          "a chunky white pill '0/24'; a white rounded tray at the bottom edge holds the next candy "
          "cubes: orange, green, sky-blue. ")

UI = ("TOP: dark navy rounded pills: three red hearts, 'Level 40', a gold coin with '512', a round "
      "gear button. ")

LINE = ("AIM LINE: a RED DASHED aim line made of EXACTLY TWO STRAIGHT RULER SEGMENTS, like a billiard "
        "ball reflecting off a cushion: segment one starts at the cannon muzzle below the board, goes "
        "diagonally UP-RIGHT, crosses the board edge and meets the RIGHT edge exactly ON the frame, "
        "where a small yellow four-point star spark sits ON the frame; there the line makes a SHARP "
        "ANGULAR mirror-reflection corner and segment two goes diagonally UP-LEFT at 45 degrees, "
        "visibly passing OVER the far sky-blue tail cubes, then over the sky-blue wing cube, then over "
        "the mint body cube, and even over the NEAR pale rose head cube, and ends with a small red "
        "triangular arrowhead INSIDE the FARTHEST pale rose cube - the BACK of the parrot's head at "
        "the top-left of the parrot. Both segments "
        "perfectly straight, crisp bend only at the frame. ABSOLUTELY NO curved lines, NO arcs anywhere. ")

P1 = (STYLE + BOARD + PARROT + LINE +
      "ACTION STATE: the aim line glows softly as if pulsing; the cannon is loaded and aimed - a "
      "glossy RED candy cube sits in the muzzle tilted 45 degrees up-right matching segment one; a "
      "simple cartoon hand with an index finger and a white tap-ripple taps the cannon (tap "
      "affordance). " + CANNON + UI +
      "The image must read instantly: the red cube will bounce off the right frame and land in the "
      "farthest red ghost cube - the parrot's head.")

P2 = ("Edit this game screenshot. Keep EVERYTHING exactly the same: same gradient sky background with "
      "floating candy cubes, same white pegboard easel board, same 12 ghost voxels of the parrot in the "
      "same positions, same red dashed two-segment aim line with the yellow star on the right frame and "
      "the arrowhead inside the pale rose head voxel, same UI pills, same '0/12' pill, same tray. THE "
      "ACTION HAS JUST HAPPENED - show the moment of launch: (1) the cannon has just FIRED: body kicked "
      "slightly back in recoil with the wheels a touch squashed, a bright white-yellow star muzzle "
      "flash at the muzzle opening with two small grey smoke puffs, and the muzzle is already empty; "
      "(2) the glossy RED candy cube flies IN MID-AIR exactly along the SECOND upper-left straight "
      "segment, about one tile past the yellow star, slightly rotated, with a short straight spark "
      "trail behind it pointing back along that same segment to the star; the yellow star itself FLARES "
      "larger with radiating impact sparks; (3) from the bottom tray the next ORANGE candy cube is "
      "half-risen into the cannon muzzle - the reload is in progress. NO finger and NO tap ripple "
      "anywhere - the finger only exists before the shot. All segments perfectly straight, no curves "
      "anywhere.")

P3 = ("Edit this game screenshot. Keep the same gradient sky with floating cubes, board, parrot ghost "
      "positions, UI layout and lighting. CHANGES - two shots have happened: "
      "(1) SUCCESS BEFORE: the pale rose HEAD voxel of the parrot is freshly stamped: it is now a "
      "SATURATED glossy red cube sitting flush in the grid, with a small white checkmark badge in its "
      "corner, short white radial rays and a thin dust ring bursting around it; "
      "(2) THE CANNON BODY IS NOW PHYSICALLY ROTATED COUNTERCLOCKWISE ABOUT 40 DEGREES - body leaning "
      "into the turn, wheels flat in the same spot, the white-rimmed muzzle points UP-LEFT and holds a "
      "glossy GREEN candy cube; "
      "(3) a NEW ORANGE DASHED aim line of exactly TWO STRAIGHT RULER SEGMENTS starting exactly at the "
      "muzzle opening: UP-LEFT to the LEFT edge of the board meeting it exactly ON the frame with a "
      "small yellow star spark there, then a sharp angular mirror corner and the second segment "
      "UP-RIGHT at 45 degrees passing over its own pale peach breast cube and over a mint body cube and ending at the mint NECK cube "
      "- where an ORANGE cube has JUST SHATTERED: a bright impact star at the contact point, orange "
      "shards and crumbs flying outward with small rotations over the pale mint neck cube, a bold red X "
      "floating beside the burst; "
      "(4) the hearts pill at the top is slightly tilted with three small shake motion arcs around it: "
      "two red hearts and a THIRD heart that is grey with a visible crack, and a tiny red '-1 heart' "
      "floater beside the pill; "
      "(5) the progress pill now reads '1/24' with a pop effect; the bottom tray now holds ONLY TWO "
      "candy cubes - orange and sky-blue - shifted to the left, and a third cube slides in from the "
      "right edge leaving a short motion streak. Remove the old red dashed line and its arrowhead. All "
      "segments perfectly straight, sharp bends only at the frame, NO curved lines anywhere.")

P4 = ("Edit this game screenshot. Keep the same gradient sky, board, UI layout, cannon position and "
      "lighting. CHANGES - THE LEVEL IS WON: "
      "(1) ALL 12 voxels of the parrot are now SATURATED glossy candy cubes: vivid red crest and head "
      "with the white eye dot, vivid orange beak, cheek and breast, vivid green neck, body and rump, "
      "vivid sky-blue wing and two-step tail - the parrot reads as a bright finished voxel parrot "
      "popping off the pale board; the most recently filled cube still has a subtle golden sparkle "
      "burst with short radial rays around it; "
      "(2) a golden ribbon banner across the top of the board reads 'LEVEL COMPLETE' in bold white "
      "letters; a few small confetti pieces fall around the board; "
      "(3) the progress pill reads '24/24'; the hearts pill keeps two red hearts and one grey cracked "
      "heart, straight and calm now, no shake arcs, no floater; "
      "(4) the cannon stands relaxed with an empty muzzle, no aim line, no stars, no shards, no dashed "
      "lines anywhere; the bottom tray is a plain empty white pill with NO candy cubes at all - all "
      "twelve were used. No curved lines anywhere.")

PROMPTS = {"f2": P2, "f3": P3, "f4": P4}

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
