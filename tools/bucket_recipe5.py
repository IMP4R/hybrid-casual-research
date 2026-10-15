"""bucket_v5 — точь-в-точь по прямому рефу Sand Loop. Спека L0-L3 в docstring.
L1: ёмкость (H/D=1.09, сужение 15%), кромка (обод 6%W), переноска (чёрная, пивоты
на кромке). Щита нет (в рефе отсутствует). L2: градиент #DC4D00->#F27400 (замер),
полость #F39000, ручка #2A2A2E, rough 0.35. Чёрное кольцо рефа = обводка, не меш.
"""
import sys, math
sys.path.insert(0, "/Users/user0/golden-land-new/../godot-hybrid-casual/tools")
import bpy, bmesh
from clay_lib import Asset

TOP_C   = (0.94, 0.51, 0.0)   # #F08200 тело у обода
BOT_C   = (0.94, 0.47, 0.0)   # #F07800 низ тела
INNER_C = (0.92, 0.50, 0.0)   # тёплая внутренность из вырезки
RIM_C   = (1.0, 0.64, 0.05)   # светлый обод-валик #FFA40D
BLACK_H = (0.165, 0.165, 0.18)
H, R_TOP, WALL = 0.93, 0.50, 0.05   # H из аспекта вырезки (1.06 vs 0.94)

R_BOT = 0.44   # дно
def radius_at(t):
    """лоуполи-усечённый конус: зев 1.0W -> дно 0.92W (по вырезке v2)"""
    return R_BOT + (R_TOP - R_BOT) * t

def grad_mat():
    m = bpy.data.materials.new("v5_grad"); m.use_nodes = True
    m.diffuse_color = (*TOP_C, 1)   # Workbench красит по diffuse_color!
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.35
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Max"].default_value = H
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*srgb(TOP_C), 1)
    ramp.color_ramp.elements[1].color = (*srgb(BOT_C), 1)
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs[0], ramp.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.0
    nt.links.new(ramp.outputs["Color"], em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m

def srgb(t):
    """sRGB (0..1) -> linear для входов материалов Blender"""
    return tuple(x ** 2.2 for x in t)

def flat_mat(color):
    """плоский тун-материал: emission цветом (свет не засвечивает)"""
    m = bpy.data.materials.new("flat"); m.use_nodes = True
    m.diffuse_color = (*color, 1)
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*srgb(color), 1)
    em.inputs[1].default_value = 1.0
    nt.links.new(em.outputs[0], out.inputs[0])
    return m

a = Asset("paintloop", "bucket_v5")

def step_body():
    a.stage()
    me = bpy.data.meshes.new("body"); bm = bmesh.new()
    N, RINGS = 20, 8
    ro_l, ri_l, bot_l = [], [], []
    for i in range(RINGS + 1):
        t = i / RINGS; z = t * H
        ro, ri = radius_at(t), radius_at(t) - WALL
        ro_l.append([bm.verts.new((math.cos(2*math.pi*k/N)*ro, math.sin(2*math.pi*k/N)*ro, z)) for k in range(N)])
        ri_l.append([bm.verts.new((math.cos(2*math.pi*k/N)*ri, math.sin(2*math.pi*k/N)*ri, z)) for k in range(N)])
    m_out, m_in = grad_mat(), flat_mat(INNER_C)
    for i in range(1, RINGS + 1):
        for k in range(N):
            k2 = (k + 1) % N
            fo = bm.faces.new((ro_l[i-1][k], ro_l[i-1][k2], ro_l[i][k2], ro_l[i][k])); fo.material_index = 0
            fi = bm.faces.new((ri_l[i-1][k2], ri_l[i-1][k], ri_l[i][k], ri_l[i][k2])); fi.material_index = 1
    for k in range(N):
        k2 = (k + 1) % N
        f = bm.faces.new((ro_l[RINGS][k2], ri_l[RINGS][k2], ri_l[RINGS][k], ro_l[RINGS][k])); f.material_index = 0
    bm.faces.new(list(reversed(ri_l[0]))).material_index = 1
    # скругление донной кромки: 3 филлет-кольца вниз
    for (dr, dz) in ((0.03, 0.02), (0.05, 0.008), (0.065, 0.0)):   # крупный филлет днища (85% рефа)
        rl = [bm.verts.new((math.cos(2*math.pi*k/N)*(radius_at(0)-dr), math.sin(2*math.pi*k/N)*(radius_at(0)-dr), dz)) for k in range(N)]
        for k in range(N):
            k2 = (k + 1) % N
            bm.faces.new((rl[k], rl[k2], bot_l[-1][k2], bot_l[-1][k])) if False else None
        bot_l.append(rl)
    prev = ro_l[0]
    for rl in bot_l:
        for k in range(N):
            k2 = (k + 1) % N
            bm.faces.new((prev[k], prev[k2], rl[k2], rl[k]))
        prev = rl
    bm.faces.new(list(reversed(prev)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    me.materials.append(m_out); me.materials.append(m_in)
    o = bpy.data.objects.new("body", me)
    bpy.context.scene.collection.objects.link(o)
    for poly in o.data.polygons: poly.use_smooth = False
    a.objects.append(o)
    print("[S1] корпус H/D=1.09, градиент по замеру, полость #F39000")

def step_rim():
    a.torus(R=R_TOP, r=0.075, loc=(0, 0, H - 0.02), mat=flat_mat(RIM_C))   # толстый светлый обод
    print("[S2] обод 0.035")

def step_handle():
    lug_z = H + 0.005
    lug_x = R_TOP + 0.042
    for sx in (-1, 1):
        a.sphere(r=0.07, loc=(sx * (R_TOP + 0.008), 0, H - 0.02), scale=(0.62, 0.55, 0.8),
                 mat=a.mat(TOP_C, rough=0.35))
        a.cyl(r=0.024, depth=0.045, loc=(sx * lug_x, 0, lug_z), rot=(0, math.radians(90), 0),
              mat=a.mat(BLACK_H, rough=0.3), bevel=0.005)
    me = bpy.data.meshes.new("handle"); bm = bmesh.new()
    R_ARC, R_ARC_Z, R_TUBE, STEPS, SEG = lug_x, 0.52, 0.045, 24, 16
    rings = []
    for i in range(STEPS + 1):
        th = math.pi * i / STEPS
        cx, cz = math.cos(th) * R_ARC, lug_z + math.sin(th) * R_ARC_Z
        rings.append([bm.verts.new((cx + math.cos(th) * R_TUBE * math.cos(2*math.pi*k/SEG),
                                    R_TUBE * math.sin(2*math.pi*k/SEG),
                                    cz + math.sin(th) * R_TUBE * math.cos(2*math.pi*k/SEG))) for k in range(SEG)])
    for i in range(STEPS):
        for k in range(SEG):
            k2 = (k + 1) % SEG
            bm.faces.new((rings[i][k], rings[i][k2], rings[i+1][k2], rings[i+1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    h = bpy.data.objects.new("handle", me)
    bpy.context.scene.collection.objects.link(h)
    h.data.materials.append(a.mat(BLACK_H, rough=0.3))
    for poly in h.data.polygons: poly.use_smooth = True
    a.objects.append(h)
    print(f"[S3] чёрная дуга, пивоты ±{lug_x:.3f}")

def step_handle_hanging():
    """чёрная ручка: висит вдоль стенки (гравитация), уши на ободе ±X"""
    LUG_X = R_TOP + 0.04
    y_off = -0.58           # отступ от стенки, чтобы лента читалась
    for sx in (-1, 1):
        a.sphere(r=0.06, loc=(sx * (R_TOP + 0.005), y_off * 0.5, H - 0.02),
                 scale=(0.6, 0.5, 0.7), mat=flat_mat(HANDLE_C))
        a.cyl(r=0.022, depth=0.05, loc=(sx * LUG_X, y_off, H - 0.02),
              rot=(0, math.radians(90), 0), mat=flat_mat(HANDLE_C), bevel=0.004)
    # дуга: нижняя половина окружности в плоскости XZ, центр на высоте обода
    me = bpy.data.meshes.new("handle"); bm = bmesh.new()
    R_A, RZ, TUBE, STEPS, SEG = LUG_X, 0.48, 0.075, 22, 14   # трубка 15%D из рефа
    rings = []
    for i in range(STEPS + 1):
        th = math.pi + math.pi * i / STEPS      # 180..360 (нижняя половина)
        cx, cz = math.cos(th) * R_A, math.sin(th) * RZ   # относительно оси ушей (h.location даёт высоту)
        rings.append([bm.verts.new((cx + math.cos(th) * TUBE * math.cos(2*math.pi*k/SEG),
                                    TUBE * math.sin(2*math.pi*k/SEG),
                                    cz + math.sin(th) * TUBE * math.cos(2*math.pi*k/SEG))) for k in range(SEG)])
    for i in range(STEPS):
        for k in range(SEG):
            k2 = (k + 1) % SEG
            bm.faces.new((rings[i][k], rings[i][k2], rings[i+1][k2], rings[i+1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    h = bpy.data.objects.new("handle", me)
    h.location = (0, y_off, H - 0.02)   # ось вращения = линия ушей
    bpy.context.scene.collection.objects.link(h)
    h.data.materials.append(flat_mat(HANDLE_C))
    a.objects.append(h)
    print("[S4] ручка: ось на ушах обода, висит вдоль -Y")

HANDLE_C = (0.10, 0.10, 0.12)
# ---- сборка ----
step_body()
step_rim()
step_handle_hanging()

# ---- рендер-протокол: Cycles, калиброванная камера рефа, свип света по ΔE ----
a.lights()
S = bpy.context.scene
try:
    S.render.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    S.render.engine = "BLENDER_EEVEE"
S.eevee.taa_render_samples = 8
S.view_settings.view_transform = "Standard"
S.render.resolution_x = 512; S.render.resolution_y = 512
if S.world is None:
    S.world = bpy.data.worlds.new("W")
S.world.use_nodes = True
S.world.node_tree.nodes["Background"].inputs[0].default_value = (0.92, 0.94, 0.96, 1)
S.world.node_tree.nodes["Background"].inputs[1].default_value = 0.35

from mathutils import Vector
def ref_camera(elev_deg=54.5, azim_deg=90, dist=5.0):
    e, az = math.radians(elev_deg), math.radians(azim_deg)
    target = Vector((0, 0, H / 2))
    dirv = Vector((math.cos(e)*math.cos(az), math.cos(e)*math.sin(az), math.sin(e)))
    cam = S.camera
    if cam is None:
        cd = bpy.data.cameras.new("refcam")
        cam = bpy.data.objects.new("refcam", cd)
        S.collection.objects.link(cam)
        S.camera = cam
    cam.location = target + dirv * dist
    cam.rotation_euler = (math.radians(90 - elev_deg), 0, math.radians(azim_deg + 90))

def cyc_render(path):
    S.render.filepath = path
    bpy.ops.render.render(write_still=True)

# калибровка света: свип world strength
REF_BODY = (237, 108, 0)
def dE_of(path):
    im = bpy.data.images.load(path)
    w, h = im.size
    px = list(im.pixels)
    bpy.data.images.remove(im)
    def pix(x, y):
        i = 4 * (y * w + x)
        return tuple(int(c * 255) for c in px[i:i+3])
    pts = [pix(int(0.44*w)+i, int(0.62*h)+j) for i in range(0, int(0.10*w), 2) for j in range(0, int(0.08*h), 2)]
    avg = tuple(sum(p[c] for p in pts)//len(pts) for c in range(3))
    return int(math.sqrt(sum((x-y)**2 for x, y in zip(avg, REF_BODY))))

ref_camera()
best = None
for w0 in (0.15, 0.25, 0.35):
    S.world.node_tree.nodes["Background"].inputs[1].default_value = w0
    cyc_render(f"/Users/user0/godot-hybrid-casual/assets/v5_sweep_{int(w0*100)}.png")
    e = dE_of(f"/Users/user0/godot-hybrid-casual/assets/v5_sweep_{int(w0*100)}.png")
    print(f"[SWEEP] world={w0} dE={e}")
    if best is None or e < best[0]:
        best = (e, w0)
S.world.node_tree.nodes["Background"].inputs[1].default_value = best[1]

# свип яркости albedo: reset к базе каждый k
BASE_COLS = {}
for m in bpy.data.materials:
    if m.use_nodes and m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == "EMISSION":
                r, g, b, _ = n.inputs[0].default_value
                if b < 0.3 and r > 0.4:
                    BASE_COLS[(m.name, n.name)] = (r, g, b, 1)
best_k = None
for k in (1.0, 1.15, 1.3, 1.5):
    for (mn, nn), base in BASE_COLS.items():
        n = bpy.data.materials[mn].node_tree.nodes[nn]
        n.inputs[0].default_value = (min(1, base[0]*k), min(1, base[1]*k), min(1, base[2]*k), 1)
    cyc_render("/Users/user0/godot-hybrid-casual/assets/v5_k.png")
    e = dE_of("/Users/user0/godot-hybrid-casual/assets/v5_k.png")
    print(f"[KSweep] k={k} dE={e}")
    if best_k is None or e < best_k[0]:
        best_k = (e, k)
for (mn, nn), base in BASE_COLS.items():
    n = bpy.data.materials[mn].node_tree.nodes[nn]
    n.inputs[0].default_value = (min(1, base[0]*best_k[1]), min(1, base[1]*best_k[1]), min(1, base[2]*best_k[1]), 1)

ref_camera(elev_deg=54.5, dist=5.0)
cyc_render("/Users/user0/godot-hybrid-casual/assets/v5_match.png")
ref_camera(elev_deg=20, azim_deg=130, dist=4.9)
cyc_render("/Users/user0/godot-hybrid-casual/assets/v5_34.png")
a.export("/Users/user0/godot-hybrid-casual/assets/games/paintloop/proc/bucket_v5.glb")

# перевёрнутая поза: флип вокруг пивота, рот утоплен на 29% H, ручка к камере
pivot = bpy.data.objects.new("flip", None)
pivot.location = (0, 0, H / 2)
S.collection.objects.link(pivot)
bpy.context.view_layer.update()
for o in a.objects:
    if o.name.lower().startswith("cube"):
        continue
    mx = o.matrix_world.copy()
    o.parent = pivot
    o.matrix_parent_inverse = pivot.matrix_world.inverted()
    o.matrix_world = mx
pivot.rotation_euler = (math.radians(180), 0, 0)
pivot.location = (0, 0, H / 2 - 0.29)
bpy.context.view_layer.update()
import mathutils
hbo = bpy.data.objects.get("handle")
bw = bpy.data.objects.get("body")
lugL = bw.matrix_world @ mathutils.Vector((-0.52, 0.0, H - 0.02))
lug_z = lugL.z
hbo.matrix_world = (mathutils.Matrix.Translation((0.0, 0.5, lug_z))
                    @ mathutils.Matrix.Rotation(math.pi, 4, "X"))
hzs = [(hbo.matrix_world @ mathutils.Vector(v.co)).z for v in hbo.data.vertices]
print(f"[HDBG] lug_z={lug_z:.2f} handle z {min(hzs):.2f}..{max(hzs):.2f}")
ref_camera(elev_deg=54.5, azim_deg=90, dist=5.0)
ground = bpy.data.objects.get("Cube")
if ground: ground.hide_render = True
cyc_render("/Users/user0/godot-hybrid-casual/assets/v5_noground.png")
if ground: ground.hide_render = False
cyc_render("/Users/user0/godot-hybrid-casual/assets/v5_inverted.png")
pivot.rotation_euler = (0, 0, 0)
pivot.location = (0, 0, H / 2)
bpy.context.view_layer.update()
ref_camera(elev_deg=54.5, dist=5.0)
cyc_render("/Users/user0/godot-hybrid-casual/assets/v5_match.png")
print(f"BUCKET V5 DONE best_world={best[1]} dE={best[0]} (обе позы)")
