"""bucket_v3 — пропорции из РЕАЛЬНОГО скрина Sand Loop (research/screens/sand_loop).
Анатомия: пухлый кубышка H=0.62D, бочка +4%, сужение 15%, толстый обод-валик,
глянцевый купол краски у кромки. Щит-счётчик — отдельный ассет (не здесь).
"""
import sys, math
sys.path.insert(0, "/Users/user0/godot-hybrid-casual/tools")
import bpy, bmesh
from clay_lib import Asset, GREEN, GREEN_D, DARK, WHITE, GREY

H     = 0.62
R_TOP = 0.50
R_BOT = 0.425   # сужение 15%
BULGE = 0.025   # бочка
WALL  = 0.05

a = Asset("paintloop", "bucket_v3")

def radius_at(t):
    """бочковой профиль: базовый конус + выпуклость в середине"""
    base = R_BOT + (R_TOP - R_BOT) * t
    return base + BULGE * math.sin(math.pi * t)

def step_body():
    a.stage()
    me = bpy.data.meshes.new("body")
    bm = bmesh.new()
    N, RINGS = 48, 14
    rings_out, rings_in = [], []
    for i in range(RINGS + 1):
        t = i / RINGS
        z = t * H
        ro, ri = radius_at(t), radius_at(t) - WALL
        lo, li = [], []
        for k in range(N):
            ang = 2 * math.pi * k / N
            lo.append(bm.verts.new((math.cos(ang) * ro, math.sin(ang) * ro, z)))
            li.append(bm.verts.new((math.cos(ang) * ri, math.sin(ang) * ri, z)))
        rings_out.append(lo); rings_in.append(li)
    # стенка: внешняя + внутренняя поверхности между соседними кольцами
    for i in range(1, RINGS + 1):
        po, pi_ = rings_out[i-1], rings_in[i-1]
        co, ci = rings_out[i], rings_in[i]
        for k in range(N):
            k2 = (k + 1) % N
            bm.faces.new((po[k], po[k2], co[k2], co[k]))       # внешняя
            bm.faces.new((pi_[k2], pi_[k], ci[k], ci[k2]))     # внутренняя
    # верхняя кромка: замыкание толщины стенки (открытый верх)
    lo, li = rings_out[RINGS], rings_in[RINGS]
    for k in range(N):
        k2 = (k + 1) % N
        bm.faces.new((lo[k2], li[k2], li[k], lo[k]))
    # дно внутреннее (пол)
    bm.faces.new(list(reversed(rings_in[0])))
    # дно внешнее: кольцо-фаска + крышка
    bot = [bm.verts.new((math.cos(2*math.pi*k/N) * (R_BOT - 0.012),
                         math.sin(2*math.pi*k/N) * (R_BOT - 0.012), 0.006)) for k in range(N)]
    lo0 = rings_out[0]
    for k in range(N):
        k2 = (k + 1) % N
        bm.faces.new((lo0[k], lo0[k2], bot[k2], bot[k]))
    bm.faces.new(bot)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("body", me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(a.mat(GREEN, rough=0.5))
    for poly in o.data.polygons: poly.use_smooth = True
    a.objects.append(o)
    print(f"[S1] body: H={H}, top={R_TOP}, bot={R_BOT}, bulge={BULGE}, wall={WALL}")


def step_rim():
    a.torus(R=R_TOP + 0.01, r=0.058, loc=(0, 0, H + 0.008), mat=a.mat(GREEN, rough=0.5))
    print(f"[S2] rim: толстый валик r=0.058 на z={H + 0.008:.3f} (обхват кромки)")

def step_paint():
    ri = R_TOP - WALL
    a.cyl(r=ri + 0.005, depth=0.04, loc=(0, 0, H - 0.045), verts=48, mat=a.mat(GREEN_D, rough=0.18), bevel=0.008)
    a.sphere(r=ri + 0.005, loc=(0, 0, H - 0.028), scale=(1, 1, 0.16), mat=a.mat(GREEN_D, rough=0.12), bevel=0)
    print(f"[S3] paint: глянцевый купол у кромки (уровень -0.03 от обода)")

def step_handle():
    lug_z = 0.80 * H
    for sx in (-1, 1):
        a.cube(size=1.0, loc=(sx * (R_TOP + 0.03), 0, lug_z), scale=(0.05, 0.08, 0.11),
               mat=a.mat(GREY, rough=0.35), bevel=0.012)
        a.cyl(r=0.026, depth=0.07, loc=(sx * (R_TOP + 0.03), 0, lug_z), rot=(0, math.radians(90), 0),
              mat=a.mat(WHITE, rough=0.3), bevel=0.006)
    a.torus(R=0.46, r=0.036, loc=(0, 0, lug_z), rot=(math.radians(90), 0, 0),
            mat=a.mat(GREY, rough=0.35), bevel=0.008)
    print(f"[S4] handle: дуга R=0.46, концы в ушках x=±{R_TOP + 0.03:.2f} (z={lug_z:.2f})")

step_body(); step_rim(); step_paint(); step_handle()
a.lights(); a.camera(dist=2.6, azimuth=48, elevation=16)
a.render("/Users/user0/godot-hybrid-casual/assets/bucket_v3_wb.png", res=640)
a.camera(dist=2.9, azimuth=40, elevation=14)
a.export("/Users/user0/godot-hybrid-casual/assets/games/paintloop/proc/bucket_v3.glb")
print("BUCKET V3 DONE")
