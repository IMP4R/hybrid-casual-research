"""key_recipe — золотой ключ 1:1 по реальному кадру Sand Loop (лоток).
Двойная бобышка = 2 эллиптических тора (сквозные овальные дырки),
пухлый узел, стержень-капсула с 3 рёбрами-кольцами, tip + 2 зубца.
Золото #F5A300 rough 0.22 (замер с рефа).
"""
import sys, math
sys.path.insert(0, "/Users/user0/golden-land-new/../godot-hybrid-casual/tools")
import bpy, math
from clay_lib import Asset

GOLD = (1.0, 0.60, 0.0)   # #FF9900, сочнее
a = Asset("paintloop", "key_gold")

def step_bow():
    """Две пухлые бобышки с овальными сквозными дырками (тор, ось дырки вдоль Y)."""
    a.stage()
    for sx in (-1, 1):
        a.torus(R=0.26, r=0.165, loc=(sx * 0.225, 0, 1.05), rot=(math.radians(90), 0, 0),
                scale=(0.85, 1.0, 0.55), mat=a.mat(GOLD, rough=0.15))
    a.torus(R=0.10, r=0.055, loc=(0, 0, 1.44), rot=(math.radians(90), 0, 0),
            mat=a.mat(GOLD, rough=0.18))
    print("[S1] бобышки жирные (R=0.28 r=0.175, дырки меньше) + колечко сверху")

def step_knot_shaft():
    a.sphere(r=0.15, loc=(0, 0, 0.68), scale=(1, 0.6, 0.9), mat=a.mat(GOLD, rough=0.18))
    a.cyl(r=0.13, depth=1.0, loc=(0, 0, 0.17), verts=32, mat=a.mat(GOLD, rough=0.18), bevel=0.02)
    for z in (0.42, 0.20, -0.02):
        a.torus(R=0.138, r=0.028, loc=(0, 0, z), rot=(math.radians(90), 0, 0),
                mat=a.mat(GOLD, rough=0.18))
    a.sphere(r=0.17, loc=(0, 0, -0.40), scale=(1, 0.75, 1), mat=a.mat(GOLD, rough=0.18))
    for sx in (-1, 1):
        a.cube(size=1.0, loc=(sx * 0.16, 0, -0.26), scale=(0.07, 0.085, 0.11),
               mat=a.mat(GOLD, rough=0.18), bevel=0.025)
    print("[S2] узел + стержень-капсула + 3 ребра + tip + 2 зубца")

step_bow(); step_knot_shaft()
a.lights()
a.camera(dist=3.3, azimuth=90, elevation=2)
a.render("/Users/user0/godot-hybrid-casual/assets/key_front.png", res=720)
a.camera(dist=3.5, azimuth=135, elevation=24)
a.render("/Users/user0/godot-hybrid-casual/assets/key_34.png", res=720)
# поза референса: ключ лежит плашмя, вид сверху-сбоку
pivot = bpy.data.objects.new("pivot", None)
bpy.context.scene.collection.objects.link(pivot)
for o in a.objects:
    o.parent = pivot
pivot.rotation_euler = (math.radians(90), 0, 0)
pivot.location = (0, 0.25, 0.60)
a.camera(dist=4.2, azimuth=90, elevation=68)
a.render("/Users/user0/godot-hybrid-casual/assets/key_flat.png", res=720)
a.export("/Users/user0/godot-hybrid-casual/assets/games/paintloop/proc/key_gold.glb")
import bpy as _b
pivot = _b.data.objects.get("pivot")
if pivot:
    pivot.rotation_euler = (0, 0, 0); pivot.location = (0, 0, 0)
a.camera(dist=3.2, azimuth=95, elevation=8)
S = _b.context.scene
S.render.engine = "CYCLES"; S.cycles.device = "CPU"; S.cycles.samples = 48
S.cycles.use_denoising = False; S.view_settings.view_transform = "Standard"
S.render.resolution_x = 720; S.render.resolution_y = 720
S.world.use_nodes = True
S.world.node_tree.nodes["Background"].inputs[0].default_value = (0.85, 0.90, 0.95, 1)
S.world.node_tree.nodes["Background"].inputs[1].default_value = 0.3
S.render.filepath = "/Users/user0/godot-hybrid-casual/assets/key_cycles.png"
_b.ops.render.render(write_still=True)
print("KEY CYCLES DONE")
print("KEY DONE")
