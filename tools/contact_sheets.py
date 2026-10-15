"""contact_sheets.py — сетки рендеров по играм: assets/games/<game>/sheet.png"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path("/Users/user0/godot-hybrid-casual/assets")

def font(sz):
    for p in ("/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Helvetica.ttc"):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()

for rdir in sorted((ROOT / "renders").iterdir()):
    if not rdir.is_dir(): continue
    pngs = sorted(rdir.glob("*.png"))
    if not pngs: continue
    cols, cell, pad, label_h = 4, 380, 14, 40
    rows = (len(pngs) + cols - 1) // cols
    W = cols*cell + (cols+1)*pad
    H = rows*(cell+label_h) + (rows+1)*pad + 70
    sheet = Image.new("RGB", (W, H), (30, 34, 44))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 18), f"{rdir.name.upper()} — {len(pngs)} ассетов (клэй, CC0+bpy)", fill=(255,214,90), font=font(30))
    for i, p in enumerate(pngs):
        r, c = divmod(i, cols)
        x = pad + c*(cell+pad); y = 70 + pad + r*(cell+label_h)
        im = Image.open(p).resize((cell, cell))
        sheet.paste(im, (x, y))
        d.text((x+4, y+cell+6), p.stem[:38], fill=(230,230,235), font=font(22))
    out = ROOT / "games" / rdir.name / "sheet.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"sheet: {out} ({len(pngs)} шт)")
print("SHEETS DONE")
