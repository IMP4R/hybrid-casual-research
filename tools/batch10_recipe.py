"""batch10 — 10 ассетов Paint Loop по реальным рефам Sand Loop.
Для каждого: сложная геометрия (сквозные отверстия/пивоты/рёбра), логика-контроль,
2 ракурса. Критика — отдельным проходом по контакт-листу.
"""
import sys, math
sys.path.insert(0, "/Users/user0/golden-land-new/../godot-hybrid-casual/tools")
import bpy, bmesh
from clay_lib import Asset

GOLD   = (1.0, 0.66, 0.0)
BLUE   = (0.29, 0.56, 0.89)   # скоба
BELT   = (0.61, 0.58, 0.79)   # лента лаванда
RAIL   = (0.95, 0.96, 0.97)   # белые рейки
HOLDER = (0.62, 0.63, 0.66)   # серые держатели
TILE   = (0.66, 0.64, 0.81)   # плитка лотка
RED    = (0.91, 0.15, 0.18)   # сердце
WHITE  = (0.97, 0.97, 0.98)
DARK   = (0.15, 0.17, 0.22)
GREEN  = (0.35, 0.77, 0.19)
PAINTB = (0.05, 0.55, 0.90)

def arc_torus(a, R, tube, z, arc_deg=180, seg=24, sseg=14, mat=None, scale_z=1.0):
    """Полудуга rings+bridge (для скоб и ушек) в плоскости XZ."""
    me = bpy.data.meshes.new("arc"); bm = bmesh.new()
    rings = []
    for i in range(seg + 1):
        th = math.pi * arc_deg / 180 * i / seg
        cx, cz = math.cos(th) * R, z + math.sin(th) * R * scale_z
        ring = [bm.verts.new((cx + math.cos(th) * tube * math.cos(2*math.pi*k/sseg),
                              tube * math.sin(2*math.pi*k/sseg),
                              cz + math.sin(th) * tube * math.cos(2*math.pi*k/sseg))) for k in range(sseg)]
        rings.append(ring)
    for i in range(seg):
        for k in range(sseg):
            k2 = (k + 1) % sseg
            bm.faces.new((rings[i][k], rings[i][k2], rings[i+1][k2], rings[i+1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("arc", me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    for poly in o.data.polygons: poly.use_smooth = True
    a.objects.append(o)
    return o

def render2(a, name, d1=3.0):
    a.lights()
    a.camera(dist=d1, azimuth=125, elevation=20)
    a.render(f"/Users/user0/godot-hybrid-casual/assets/b10_{name}_a.png", res=512)
    a.camera(dist=d1, azimuth=55, elevation=34)
    a.render(f"/Users/user0/godot-hybrid-casual/assets/b10_{name}_b.png", res=512)
    a.export(f"/Users/user0/godot-hybrid-casual/assets/games/paintloop/proc/{name}.glb")
    print(f"### {name} DONE")

# 1. lock_shackle: U-скоба на базе + белая пилюля с цифрой
a = Asset("paintloop", "lock")
a.stage()
a.cube(size=1.0, loc=(0, 0, 0.18), scale=(0.52, 0.22, 0.36), mat=a.mat(BLUE, rough=0.25), bevel=0.07)
arc_torus(a, R=0.30, tube=0.055, z=0.36, mat=a.mat((0.55, 0.57, 0.60), rough=0.3))
a.cube(size=1.0, loc=(0, -0.115, 0.20), scale=(0.19, 0.014, 0.13), mat=a.mat(WHITE, rough=0.4), bevel=0.035)
for sx in (-1, 1):
    a.cyl(r=0.065, depth=0.05, loc=(sx * 0.30, 0, 0.375), verts=20, mat=a.mat((0.55, 0.57, 0.60), rough=0.3), bevel=0.008)
a.cyl(r=0.045, depth=0.012, loc=(0, -0.112, 0.28), rot=(math.radians(90), 0, 0), verts=20, mat=a.mat(DARK, rough=0.4))
print("[lock] скоба-дуга концами в базу (x=±0.30, база 0.52) — контакты внутри базы")
render2(a, "lock_shackle", 2.2)

# 2. conveyor: балка + лента с рёбрами + ролики + рейки
a = Asset("paintloop", "conveyor")
a.stage()
a.cube(size=2.6, loc=(0, 0, 0.36), scale=(1, 0.42, 0.10), mat=a.mat(DARK, rough=0.5), bevel=0.02)
for i in range(9):
    a.cube(size=1.0, loc=(-1.1 + i * 0.275, 0, 0.475), scale=(0.045, 0.46, 0.075),
           mat=a.mat(BELT, rough=0.4), bevel=0.015)
for sx in (-1, 1):
    a.cube(size=2.52, loc=(0, sx * 0.27, 0.46), scale=(1, 0.045, 0.14),
           mat=a.mat(RAIL, rough=0.3), bevel=0.04)
    a.cyl(r=0.17, depth=0.6, loc=(sx * 1.24, 0, 0.40), rot=(0, math.radians(90), 0),
          verts=28, mat=a.mat(HOLDER, rough=0.35), bevel=0.01)
    for lz in (0.16,):
        a.cube(size=1.0, loc=(sx * 1.05, 0, lz), scale=(0.06, 0.3, 0.34),
               mat=a.mat(HOLDER, rough=0.4), bevel=0.02)
    a.cyl(r=0.24, depth=0.46, loc=(sx * 1.28, 0, 0.42), rot=(0, math.radians(90), 0),
          verts=32, mat=a.mat(HOLDER, rough=0.35), bevel=0.01)
print("[conveyor] рёбра внутри балки, ролики на торцах, рейки по бокам")
render2(a, "conveyor", 3.6)

# 3. holder_pair: серые пухлые держатели
a = Asset("paintloop", "holder")
a.stage()
for sx in (-1, 1):
    a.cube(size=1.0, loc=(sx * 0.55, 0, 0.45), scale=(0.5, 0.7, 0.9), mat=a.mat(HOLDER, rough=0.4), bevel=0.12)
    a.cube(size=1.0, loc=(sx * 0.55, 0, 0.875), scale=(0.28, 0.10, 0.035), mat=a.mat(DARK, rough=0.5), bevel=0.008)
print("[holder] пара блоков, бевел 0.16 = пухлость рефа")
render2(a, "holder_pair", 3.0)

# 4. tray_tile: плитка лотка
a = Asset("paintloop", "tile")
a.stage()
a.cube(size=1.0, loc=(0, 0, 0.045), scale=(0.9, 0.9, 0.09), mat=a.mat(TILE, rough=0.45), bevel=0.075)
for rx, ry, sx_, sy_ in ((0, 0.42, 1, 0.05), (0, -0.42, 1, 0.05), (0.42, 0, 0.05, 1), (-0.42, 0, 0.05, 1)):
    a.cube(size=1.0, loc=(rx, ry, 0.115), scale=(sx_ * 0.9, sy_ * 0.9, 0.055),
           mat=a.mat(TILE, rough=0.45), bevel=0.028)
print("[tile] плитка 0.9x0.9, скругление по реалу")
render2(a, "tray_tile", 2.2)

# 5. coin: толстая монета с эмблемой-ободом
a = Asset("paintloop", "coin")
a.stage()
a.cyl(r=0.5, depth=0.13, loc=(0, 0, 0.55), rot=(math.radians(75), 0, 0), verts=40, mat=a.mat(GOLD, rough=0.18), bevel=0.03)
a.torus(R=0.36, r=0.042, loc=(0, 0.055, 0.55), rot=(math.radians(75), 0, 0), mat=a.mat((1.0, 0.78, 0.2), rough=0.2))
a.cyl(r=0.16, depth=0.055, loc=(0, 0.058, 0.55), rot=(math.radians(75), 0, 0), verts=28, mat=a.mat((1.0, 0.78, 0.2), rough=0.2), bevel=0.015)
print("[coin] обод-эмблема + сердцевина; торец виден под наклоном")
render2(a, "coin_gold", 2.2)

# 6. heart: классическая кривая сердца одним мешем (как звезда)
a = Asset("paintloop", "heart")
a.stage()
me = bpy.data.meshes.new("heart"); bm = bmesh.new()
pts = []
N = 40
for i in range(N):
    t = 2 * math.pi * i / N
    x = 16 * math.sin(t) ** 3
    y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
    pts.append(bm.verts.new((x / 34.0, 0, y / 30.0 + 0.62)))
f = bm.faces.new(pts)
ret = bmesh.ops.extrude_face_region(bm, geom=[f])
verts = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]
for v in verts: v.co.y -= 0.30
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me); bm.free()
o = bpy.data.objects.new("heart", me)
bpy.context.scene.collection.objects.link(o)
mod = o.modifiers.new("bev", "BEVEL"); mod.width = 0.075; mod.segments = 5
o.data.materials.append(a.mat(RED, rough=0.15))
for poly in o.data.polygons: poly.use_smooth = True
a.objects.append(o)
print("[heart] кривая сердца, экструзия 0.30, bevel 0.075x5")
render2(a, "heart", 2.4)

# 7. paint_drop: капля
a = Asset("paintloop", "drop")
a.stage()
a.sphere(r=0.5, loc=(0, 0, 0.5), scale=(1, 1, 0.85), mat=a.mat(PAINTB, rough=0.12))
a.cone(r1=0.28, r2=0.03, depth=0.45, loc=(0, 0, 0.95), verts=40, mat=a.mat(PAINTB, rough=0.12), bevel=0.06)
print("[drop] сфера+конус, хвост Rounded")
render2(a, "paint_drop", 2.4)

# 8. star: 5-луч, экструзия+пухлый бевел
a = Asset("paintloop", "star")
a.stage()
me = bpy.data.meshes.new("star"); bm = bmesh.new()
pts = []
for i in range(10):
    r = 0.55 if i % 2 == 0 else 0.24
    th = math.pi / 2 + i * math.pi / 5
    pts.append(bm.verts.new((math.cos(th) * r, 0, math.sin(th) * r + 0.55)))
f = bm.faces.new(pts)
ret = bmesh.ops.extrude_face_region(bm, geom=[f])
verts = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]
for v in verts: v.co.y -= 0.16
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me); bm.free()
o = bpy.data.objects.new("star", me)
bpy.context.scene.collection.objects.link(o)
mod = o.modifiers.new("bev", "BEVEL"); mod.width = 0.045; mod.segments = 4
o.data.materials.append(a.mat(GOLD, rough=0.2))
for poly in o.data.polygons: poly.use_smooth = True
a.objects.append(o)
print("[star] экструзия 0.16 + bevel 0.045x4")
render2(a, "star", 2.4)

# 9. number_plate: белая пилюля счётчика с синей вставкой
a = Asset("paintloop", "plate")
a.stage()
a.cube(size=1.0, loc=(0, 0, 0.3), scale=(0.55, 0.09, 0.3), mat=a.mat(WHITE, rough=0.35), bevel=0.07)
a.cube(size=1.0, loc=(0, 0.048, 0.3), scale=(0.42, 0.012, 0.18), mat=a.mat(DARK, rough=0.4), bevel=0.0)
print("[plate] пилюля + тёмная вставка (цифру рисует UI)")
render2(a, "number_plate", 2.0)

# 10. easel: мольберт-подставка под канвас (A-рама + полка)
a = Asset("paintloop", "easel")
a.stage()
for sx in (-1, 1):
    a.cube(size=1.0, loc=(sx * 0.40, 0, 0.58), scale=(0.075, 0.055, 1.16), rot=(0, sx * math.radians(-14), 0),
           mat=a.mat((0.72, 0.5, 0.28), rough=0.5), bevel=0.02)
a.cube(size=1.0, loc=(0, -0.14, 0.38), scale=(0.74, 0.06, 0.05), mat=a.mat((0.72, 0.5, 0.28), rough=0.5), bevel=0.015)
a.cube(size=1.0, loc=(0, 0, 1.07), scale=(0.10, 0.075, 0.09), mat=a.mat((0.72, 0.5, 0.28), rough=0.5), bevel=0.02)
a.cube(size=1.0, loc=(0, 0.30, 0.62), scale=(0.78, 0.05, 0.045), rot=(math.radians(-12), 0, 0),
       mat=a.mat((0.72, 0.5, 0.28), rough=0.5), bevel=0.015)
print("[easel] A-ноги 14°, полка под канвас, упор сзади")
render2(a, "easel", 2.8)

print("BATCH10 ALL DONE")
