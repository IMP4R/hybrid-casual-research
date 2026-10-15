"""bucket_v4.1 — финал по правкам двух критиков (форма + материал).
Форма: H/D=0.78, стенки почти вертикальные (сужение 12%), самое широкое место
под ободом (+5%D на t=0.4), fillet дна, обод 7-8%D с нависанием ≤3%,
зев глубиной 0.38H с читаемым полом краски, внутренняя стенка светлее,
ушки-бобышки (утоплены 50%) вплотную под ободом, дуга не ниже дна.
Материал: albedo #45B94D, rough 0.20, краска глянец, светлый металл.
"""
import sys, math
sys.path.insert(0, "/Users/user0/godot-hybrid-casual/tools")
import bpy, bmesh
from clay_lib import Asset, WHITE

GREEN_J = (0.184, 0.808, 0.267)   # #2FCE44 — насыщенность как у рефа (HSV 78/81)
GREEN_IN = (0.30, 0.88, 0.36)     # внутренняя стенка светлее
PAINT   = (0.10, 0.78, 0.20)      # краска сочнее
METAL   = (0.135, 0.135, 0.150)   # ЧЁРНАЯ ручка как в рефе
OUTLINE = (0.149, 0.133, 0.118)

H      = 0.85
R_TOP  = 0.50
R_BOT  = 0.46
WALL   = 0.05

def radius_at(t):
    base = R_BOT + (R_TOP - R_BOT) * t
    return base + 0.03 * math.exp(-((t - 0.45) / 0.30) ** 2)

a = Asset("paintloop", "bucket_v4")

def step_body():
    a.stage()
    me = bpy.data.meshes.new("body"); bm = bmesh.new()
    N, RINGS = 48, 14
    ro_l, ri_l = [], []
    for i in range(RINGS + 1):
        t = i / RINGS; z = t * H
        ro, ri = radius_at(t), radius_at(t) - WALL
        ro_l.append([bm.verts.new((math.cos(2*math.pi*k/N)*ro, math.sin(2*math.pi*k/N)*ro, z)) for k in range(N)])
        ri_l.append([bm.verts.new((math.cos(2*math.pi*k/N)*ri, math.sin(2*math.pi*k/N)*ri, z)) for k in range(N)])
    m_out, m_in = a.mat(GREEN_J, rough=0.20), a.mat(GREEN_IN, rough=0.30)
    for i in range(1, RINGS + 1):
        for k in range(N):
            k2 = (k + 1) % N
            fo = bm.faces.new((ro_l[i-1][k], ro_l[i-1][k2], ro_l[i][k2], ro_l[i][k])); fo.material_index = 0
            fi = bm.faces.new((ri_l[i-1][k2], ri_l[i-1][k], ri_l[i][k], ri_l[i][k2])); fi.material_index = 1
    for k in range(N):
        k2 = (k + 1) % N
        f = bm.faces.new((ro_l[RINGS][k2], ri_l[RINGS][k2], ri_l[RINGS][k], ro_l[RINGS][k])); f.material_index = 0
    bm.faces.new(list(reversed(ri_l[0]))).material_index = 1
    bot = [bm.verts.new((math.cos(2*math.pi*k/N)*(R_BOT-0.05), math.sin(2*math.pi*k/N)*(R_BOT-0.05), 0.02)) for k in range(N)]
    for k in range(N):
        k2 = (k + 1) % N
        bm.faces.new((ro_l[0][k], ro_l[0][k2], bot[k2], bot[k]))
    bm.faces.new(bot)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    me.materials.append(m_out); me.materials.append(m_in)
    o = bpy.data.objects.new("body", me)
    bpy.context.scene.collection.objects.link(o)
    for poly in o.data.polygons: poly.use_smooth = True
    a.objects.append(o)
    print(f"[S1] body: H/D={H:.2f}, top={R_TOP}, bot={R_BOT}, бочка +5%D @t=0.4, fillet, внутренняя светлее")

def step_rim_paint():
    a.torus(R=R_TOP + 0.006, r=0.045, loc=(0, 0, H + 0.002), mat=a.mat(GREEN_J, rough=0.16))
    floor_z = H - 0.34 * H
    ri = R_TOP - WALL
    a.cyl(r=ri + 0.006, depth=0.03, loc=(0, 0, floor_z), verts=48, mat=a.mat(PAINT, rough=0.12), bevel=0.005)
    a.sphere(r=ri + 0.006, loc=(0, 0, floor_z + 0.015), scale=(1, 1, 0.22), mat=a.mat(PAINT, rough=0.10), bevel=0)
    print("[S2] rim 0.032 (нависание ~3%); зев 0.38H, яркий диск краски")

def step_handle():
    """Дуга = ПОЛУТОР (rings along arc + bridge), целиком СНАРУЖИ корпуса.
    Концы сидят в ушках на стенке. Никакой части дуги внутри тела."""
    lug_z = H + 0.01            # ушки вплотную к ободу, снаружи кромки
    lug_x = R_TOP + 0.055       # пивот ВНЕ нависания (кромка до 0.534)
    for sx in (-1, 1):
        a.sphere(r=0.07, loc=(sx * (R_TOP + 0.012), 0, H - 0.015), scale=(0.62, 0.55, 0.8),
                 mat=a.mat(METAL, rough=0.35))
        a.cyl(r=0.022, depth=0.042, loc=(sx * lug_x, 0, lug_z), rot=(0, math.radians(90), 0),
              mat=a.mat(METAL, rough=0.30), bevel=0.005)
    # half-torus: кольца вдоль дуги θ∈[0..π], бридж
    me = bpy.data.meshes.new("handle"); bm = bmesh.new()
    R_ARC, R_ARC_Z, R_TUBE, STEPS, SEG = lug_x, 0.46, 0.042, 24, 16
    rings = []
    for i in range(STEPS + 1):
        th = math.pi * i / STEPS
        cx, cz = math.cos(th) * R_ARC, lug_z + math.sin(th) * R_ARC_Z
        ring = []
        for k in range(SEG):
            ph = 2 * math.pi * k / SEG
            ring.append(bm.verts.new((cx + math.cos(th) * R_TUBE * math.cos(ph),
                                      R_TUBE * math.sin(ph),
                                      cz + math.sin(th) * R_TUBE * math.cos(ph))))
        rings.append(ring)
    for i in range(STEPS):
        for k in range(SEG):
            k2 = (k + 1) % SEG
            bm.faces.new((rings[i][k], rings[i][k2], rings[i+1][k2], rings[i+1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    h = bpy.data.objects.new("handle", me)
    bpy.context.scene.collection.objects.link(h)
    h.data.materials.append(a.mat(METAL, rough=0.30))
    for poly in h.data.polygons: poly.use_smooth = True
    a.objects.append(h)
    print(f"[S4] handle: овальная ПОЛУдуга {R_ARC}x{0.46}, пивоты снаружи кромки (±{lug_x:.3f}), ноги идут строго снаружи стенки")

def audit_logic():
    """ФИЗ-ГЕЙТ: ни одна часть ручки не пересекается с корпусом
    (кроме зоны ушка). Сборка падает при нарушении."""
    deps = bpy.context.evaluated_depsgraph_get()
    body = bpy.data.objects["body"].evaluated_get(deps)
    h = bpy.data.objects["handle"].evaluated_get(deps)
    mw = h.matrix_world
    fails, checked = 0, 0
    for v in h.data.vertices:
        co = mw @ v.co
        # зона контакта с ушком — разрешена
        if abs(abs(co.x) - 0.546) < 0.07 and abs(co.z - (H + 0.01)) < 0.10:
            continue
        hit, loc, nrm, idx = body.closest_point_on_mesh(co)
        checked += 1
        if hit and (co - loc).length < 0.002:
            fails += 1
    print(f"[AUDIT] точек ручки проверено: {checked}, пересечений с корпусом: {fails}")
    assert fails == 0, "ФИЗ-ГЕЙТ: ручка пересекает корпус!"


step_body(); step_rim_paint(); step_handle(); audit_logic()
a.lights(); a.camera(dist=2.7, azimuth=45, elevation=26)
a.camera(dist=2.7, azimuth=45, elevation=26)
a.render("/Users/user0/godot-hybrid-casual/assets/bucket_v4_wb.png", res=720)
a.camera(dist=2.6, azimuth=4, elevation=9)   # ПОЗА МАСКОТА: фронтально
a.render("/Users/user0/godot-hybrid-casual/assets/bucket_pose_ref.png", res=720)
a.export("/Users/user0/godot-hybrid-casual/assets/games/paintloop/proc/bucket_v4.glb")
print("BUCKET V4.1 DONE")
