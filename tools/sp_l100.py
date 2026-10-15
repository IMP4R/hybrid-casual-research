#!/usr/bin/env python3
"""sp_l100.py — GPT-превью СОТЫХ уровней в сеттингах игр (данные из complex_levels.py).
usage: sp_l100.py OUT.png GAME   (GAME: pl|sp|bj)
"""
import base64, json, pathlib, re, sys, time
import urllib.request

GEN = "https://ru.cheapvibecode.ru/v1/images/generations"
M = pathlib.Path("/Users/user0/godot-hybrid-casual/research/mockups")

def key():
    m = re.search(r"CHEAPVIBECODE_API_KEY:\s*['\"]?([^'\"\n]+)",
                  (pathlib.Path.home() / ".dsh" / ".credentials.yaml").read_text())
    return m.group(1).strip()

MATERIAL = ("glossy clay-plastic toy render, high-saturation candy colors, bright specular highlights, "
            "soft rim light, chunky rounded shapes with bevels, soft grounded contact shadows, "
            "Blender-style soft studio lighting, high-end mobile game look. UI: chunky 3D dark navy "
            "rounded pills with bold white text. No watermark, no marketing text. ")

PROMPTS = {
"pl": ("Mobile game screenshot, vertical 9:16, casual puzzle game in soft candy-clay style. "
"SETTING: a warm cozy ARTIST'S ATELIER interior: warm cream wall with wooden shelves holding paint "
"jars, brushes and a watering can, soft daylight from a window on the left, wooden floor planks, "
"gentle depth of field. " + MATERIAL +
"CENTER: one big vertical white easel board with a recessed pegboard playfield with a faint dot grid. "
"On it: a LARGE pixel-art PARROT picture divided into FIFTY small fill zones - a dense mosaic of "
"hundreds of tiny square cells; every zone has a thin colored outline (rose, peach, mint, sky, "
"yellow, lavender) and a tiny dark navy badge with a counter like '0/6' or '0/9'; a few zones "
"already show saturated liquid-paint fills with flat glossy surfaces, most are pale ghosts. The "
"parrot silhouette reads through the dense zoning. "
"BOTTOM: a long row of 21 chunky glossy paint buckets of six colors with visible paint levels and "
"tiny count labels, two buckets marked with a big '?' disc instead of a color. "
"TOP UI: three red hearts, 'Level 100', a gold coin with '512', a round gear button; a white pill "
"'12/50' near the board. The scene must feel BUSY and challenging - a hard late level."),

"sp": ("Mobile game screenshot, vertical 9:16, casual puzzle game in soft candy-clay style. "
"SETTING: a sunny outdoor TERRACE: warm terracotta brick wall behind, a leafy climbing plant in the "
"top corner, wooden deck floor, warm afternoon light, gentle depth of field. " + MATERIAL +
"CENTER: one big vertical white pegboard on legs with a faint dot grid. On it: a DENSE mosaic of 150 "
"small rounded ghost tiles in 5 pastel colors (rose, peach, mint, sky, lavender) forming an abstract "
"pixel picture; each tile outlined in its future color; about a third of the tiles are already "
"filled with SATURATED glossy candy cubes, the rest pale ghosts. "
"BELOW THE BOARD: a small navy mortar cannon with a red candy cube loaded, aimed by a dashed red "
"ricochet line that bounces between the board edges with small yellow star sparks at the bounce "
"points; a white tray holds the next 4 cubes; a white pill '86/150'. "
"TOP UI: two red hearts and one grey cracked heart, 'Level 100', gold coin '512', gear button. The "
"scene must feel DENSE and challenging - a hard late level."),

"bj": ("Mobile game screenshot, vertical 9:16, casual puzzle game in soft candy-clay style. "
"SETTING: a warm industrial SORTING DEPOT interior: grey-blue concrete wall, metal shelving with "
"wooden crates in soft blur, hanging industrial lamps with warm light cones, concrete floor with a "
"painted yellow guide line. " + MATERIAL +
"CENTER: a BRANCHING NETWORK of toy conveyor tracks: one main belt enters top center and SPLITS at a "
"junction into two branches; each branch SPLITS again at further junctions - TEN round switch bases "
"with fat yellow arrow pointers in total, mounted exactly at the split points; the branch rails "
"curve and descend feeding SIX toy gates standing in two groups at the bottom: blue, green, yellow, "
"red, orange, lavender - each gate a rounded station with a glossy color panel, an opening, a small "
"quota pill like '12/20' and a tiny padlock on some gates. Chunky glossy candy cubes of all six "
"colors ride the belts; a queue of next cubes peeks above the top edge. "
"TOP UI: two red hearts and one grey cracked heart, 'Level 100', gold coin '512', gear button; a "
"white pill '84/120'. The scene must feel BUSY and challenging - a hard late level with many "
"switches."),
}

def gen(out, prompt):
    body = json.dumps({"model": "gpt-image-2", "size": "1024x1536",
                       "quality": "medium", "prompt": prompt}).encode()
    req = urllib.request.Request(GEN, data=body, headers={
        "Authorization": f"Bearer {key()}", "Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    (M / out).write_bytes(base64.b64decode(r["data"][0]["b64_json"]))
    print(f"{out} ok ({(M / out).stat().st_size} bytes)")

if __name__ == "__main__":
    out, game = sys.argv[1], sys.argv[2]
    for attempt in (1, 2, 3):
        try:
            gen(out, PROMPTS[game]); break
        except Exception as e:
            print(f"[{out}] попытка {attempt}: {str(e)[:160]}")
            if attempt < 3: time.sleep(35)
