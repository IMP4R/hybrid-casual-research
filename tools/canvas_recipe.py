"""canvas_recipe — канвас Paint Loop 1:1 по реальному кадру Sand Loop.
Рамка #F7FBF3, поле #FFF8EA, пиксель-арт 14x14 сэмплирован из референса
(6 цветов, assets/canvas_cells.json). Клетки — экструд 0.015, скругление рамы.
"""
import sys, math, json
sys.path.insert(0, "/Users/user0/godot-hybrid-casual/tools")
import bpy, bmesh
from clay_lib import Asset

FRAME   = (0.968, 0.984, 0.953)   # #F7FBF3
FIELD   = (1.0, 0.973, 0.918)     # #FFF8EA
CELLS   = [tuple(c/255 for c in v) for v in json.load(open("/Users/user0/godot-hybrid-casual/assets/canvas_cells.json"))]  # 0-255 → 0-1
N       = 14
SIDE    = 2.0                     # сторона канваса
FW      = 0.16                    # ширина рамы

a = Asset("paintloop", "canvas")

def step_board():
    """Рама: скруглённая пластина 2x2 (толщина 0.12) + поле спереди (+Y)."""
    a.stage()
    inner = SIDE - 2 * FW
    a.cube(size=SIDE, loc=(0, 0, SIDE/2), scale=(1, 0.06, 1),
           mat=a.mat(FRAME, rough=0.35), bevel=0.03)
    a.cube(size=inner, loc=(0, 0.062, SIDE/2), scale=(1, 0.036, 1),
           mat=a.mat(FIELD, rough=0.5), bevel=0.01)
    print(f"[S1] рама {SIDE}x{SIDE}x0.12, поле {inner:.2f} на +Y")

def step_pixels():
    """Пиксель-арт 14x14 в плоскости XZ на передней стороне (+Y)."""
    cell = (SIDE - 2 * FW) / N
    for idx, col in enumerate(CELLS):
        cx, cy = idx % N, idx // N
        x = -(SIDE/2 - FW) + cell * (cx + 0.5)
        z = (SIDE - FW) - cell * cy - cell/2   # верх арта у верха поля
        a.cube(size=cell * 0.94, loc=(x, 0.098, z), scale=(1, 0.15, 1),
               mat=a.mat(col, rough=0.55), bevel=0.004)
    print(f"[S2] пиксель-арт: {N*N} клеток в XZ, {len(set(map(tuple, CELLS)))} цветов")

step_board(); step_pixels()
a.lights(); a.camera(dist=5.4, azimuth=90, elevation=4)   # фронт = азимут 90 (от +X)
a.render("/Users/user0/godot-hybrid-casual/assets/canvas_pose_ref.png", res=720)
a.camera(dist=6.2, azimuth=128, elevation=16)
a.render("/Users/user0/godot-hybrid-casual/assets/canvas_34.png", res=720)
a.export("/Users/user0/godot-hybrid-casual/assets/games/paintloop/proc/canvas.glb")
print("CANVAS DONE")
