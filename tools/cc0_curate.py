"""cc0_curate.py — раскладка CC0-моделей по играм (ключевые слова → папка игры + манифест)."""
import pathlib, re, shutil

CC0 = pathlib.Path("/Users/user0/godot-hybrid-casual/assets/cc0")
GAMES = pathlib.Path("/Users/user0/godot-hybrid-casual/assets/games")

RULES = {
    "beltjam":     r"conveyor|belt|pallet|crate|box|barrel|pipe|gear|funnel|industrial",
    "paintloop":   r"table|chair|shelf|easel|lamp|ladder|drawer|desk|cabinet|stool",
    "shotpainter": r"column|pillar|fence|plant|pot|bench|railing|bush|flower",
    "loopaway":    r"barrel|crate|rope|anchor|buoy|mast|lantern|raft|lighthouse|pier",
    "pinaway":     r"cart|mine|rock|torch|fence|pickaxe|trolley|stone|rail|barrel",
}

for game, pattern in RULES.items():
    dst = GAMES / game / "cc0"
    dst.mkdir(parents=True, exist_ok=True)
    manifest = []
    rx = re.compile(pattern, re.I)
    for glb in CC0.rglob("*.glb"):
        if rx.search(glb.stem):
            target = dst / glb.name
            if not target.exists():
                shutil.copy2(glb, target)
            manifest.append(f"{glb.name}  <=  {glb.relative_to(CC0)}")
    (dst / "manifest.txt").write_text("\n".join(sorted(manifest)) or "(совпадений нет)")
    print(f"{game}: {len(manifest)} моделей")
print("CC0 CURATION DONE")
