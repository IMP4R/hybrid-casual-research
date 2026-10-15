# V22 — пересборка с нуля по вердикту критика:
# (1) профиль ИЗМЕРЕН из маски рефа (w(y)) — lathe, 64 сегмента
# (2) точная палитра emission (детерминизм, Standard)
# (3) обе позы, пост-контур отдельно, метрика numpy отдельно (внешний цикл)
import math, os as _os
import bpy, bmesh
from mathutils import Vector, Matrix

REF_DN = "/tmp/ref_dome_v2_1788244974.png"
OUT_UP = _os.environ.get("OUT_UP", "/tmp/v22_up.png")
OUT_DN = _os.environ.get("OUT_DN", "/tmp/v22_dn.png")

# ---------- ПАЛИТРА (медианы пикселей рефа, sRGB) ----------
C_BODY_TOP = (237/255, 104/255, 0)
C_BODY_BOT = (232/255, 92/255, 0)
C_RIM      = (245/255, 130/255, 0)
C_INNER    = (222/255, 72/255, 0)
C_FLOOR    = (240/255, 144/255, 0)
C_BAND     = (107/255, 53/255, 14/255)
C_HANDLE   = (0.04, 0.04, 0.05)

# ---------- ИЗМЕРЕННЫЙ ПРОФИЛЬ (прямое, w(t)/W; t сверху вниз) ----------
MEAS = [(0.15,0.681),(0.20,0.779),(0.25,0.867),(0.30,0.938),(0.35,0.956),(0.40,0.973),
        (0.45,0.973),(0.50,0.982),(0.55,0.929),(0.60,0.912),(0.65,0.832),(0.70,0.717),
        (0.75,0.699),(0.80,0.655),(0.85,0.611)]

def interp(t, pts):
    if t <= pts[0][0]: return pts[0][1]
    if t >= pts[-1][0]: return pts[-1][1]
    for (t0, w0), (t1, w1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            return w0 + (w1 - w0) * u
    return pts[-1][1]

# ---------- ПАРАМЕТРЫ ----------
H      = 0.90
R_TOP  = 0.50
WALL   = 0.11
SEG    = 64
STEPS  = 30
FLOOR_Z = 0.50
BOT_R  = 0.30          # радиус низа корпуса (0.61 обода по замеру t=0.85)
SINK   = float(_os.environ.get("SINK", "0.62"))
RAISE  = float(_os.environ.get("RAISE", "-0.20"))
ELEV_UP = float(_os.environ.get("ELEV_UP", "56"))
DIST_UP = float(_os.environ.get("DIST_UP", "3.4"))
ELEV_DN = float(_os.environ.get("ELEV_DN", "24"))
DIST_DN = float(_os.environ.get("DIST_DN", "2.6"))
SAMPLES = int(_os.environ.get("SAMPLES", "32"))
ZMIN = float(_os.environ.get("ZMIN", "0.0"))
ZMAX = float(_os.environ.get("ZMAX", "0.9"))
WORLD_SRGB = _os.environ.get("WORLD_SRGB", "16,16,32")
RES     = int(_os.environ.get("RES", "512"))
SKIP_UP = _os.environ.get("SKIP_UP", "0") == "1"
SKIP_DN = _os.environ.get("SKIP_DN", "0") == "1"

S = bpy.context.scene
S.render.engine = 'BLENDER_EEVEE_NEXT'
S.render.resolution_x = S.render.resolution_y = RES
S.view_settings.view_transform = 'Standard'
S.view_settings.look = 'None'
S.eevee.taa_render_samples = SAMPLES

def srgb(c):
    return tuple(v ** 2.2 if v > 0.04045 else v / 12.92 for v in c)
wld = bpy.data.worlds.new("W"); S.world = wld; wld.use_nodes = True
_wc = [float(x)/255 for x in WORLD_SRGB.split(",")]
wld.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(_wc), 1)
wld.node_tree.nodes["Background"].inputs[1].default_value = 1.0

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ---------- МАТЕРИАЛЫ ----------
def srgb(c):
    return tuple(v ** 2.2 if v > 0.04045 else v / 12.92 for v in c)

def emat(name, color):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*srgb(color), 1)
    em.inputs[1].default_value = 1.0
    nt.links.new(em.outputs[0], out.inputs[0])
    return m

def grad3_mat(name, stops):
    """stops: [(pos, color), ...] по Object-Z/H, CONSTANT-рамп"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = ZMIN
    mr.inputs["From Max"].default_value = ZMAX
    mr.clamp = True
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = 'LINEAR'
    while len(ramp.color_ramp.elements) < len(stops):
        ramp.color_ramp.elements.new(0.5)
    for e, (pos, col) in zip(ramp.color_ramp.elements, stops):
        e.position = pos
        e.color = (*srgb(col), 1)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[1].default_value = 1.0
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs[0])
    nt.links.new(mr.outputs[0], ramp.inputs[0])
    nt.links.new(ramp.outputs["Color"], em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m

# мировой градиент (замер рефов): низ #F05600 -> середина #ED6800 -> верх #FF9D00..#FFA900
m_body = grad3_mat("body", [
    (0.00, (240/255, 86/255, 0)),
    (0.45, (237/255, 104/255, 0)),
    (0.85, (255/255, 157/255, 0)),
    (1.00, (255/255, 169/255, 0)),
])
m_rim   = emat("rim", C_RIM)
m_inner = emat("inner", C_INNER)
m_floor = emat("floor", C_FLOOR)
m_ring  = emat("ring", C_BAND)
m_hnd   = emat("hnd", C_HANDLE)
m_ear   = emat("ear", C_HANDLE)

def link(o):
    S.collection.objects.link(o); return o

# ---------- КОРПУС: lathe по измеренному профилю ----------
mesh = bpy.data.meshes.new("body")
bm = bmesh.new()
rings = []
R_WATER = interp(0.85, MEAS) * R_TOP     # радиус у ватерлинии низа
Z_WL = 0.30 * H                          # высота ватерлинии
Z_TIP = 0.08 * H                         # подъём макушки днища
for i in range(STEPS + 1):
    v = i / STEPS                       # 0 низ .. 1 обод
    if v < 0.38:
        # сферический (эллиптический) купол днища: макушка -> ватерлиния
        u = v / 0.38
        th = u * math.pi / 2
        r = R_WATER * math.sin(th)
        z = Z_TIP + (Z_WL - Z_TIP) * math.sin(th)
    else:
        u2 = (v - 0.30) / 0.70
        t = 0.85 - u2 * 0.70
        r = interp(t, MEAS) * R_TOP
        z = Z_WL + u2 * (H - Z_WL)
    ring = [bm.verts.new((r * math.cos(2*math.pi*j/SEG), r * math.sin(2*math.pi*j/SEG), z)) for j in range(SEG)]
    rings.append(ring)
for i in range(len(rings) - 1):
    for j in range(SEG):
        a, b_ = rings[i][j], rings[i][(j+1) % SEG]
        c, d = rings[i+1][j], rings[i+1][(j+1) % SEG]
        bm.faces.new((a, b_, d, c))
# дно: веер к центру с лёгким подъёмом (выпуклое дно)
bc = bm.verts.new((0, 0, Z_TIP))
for j in range(SEG):
    bm.faces.new((rings[0][j], rings[0][(j+1) % SEG], bc))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh); bm.free()
body = link(bpy.data.objects.new("body", mesh))
body.data.materials.append(m_body)
for p in mesh.polygons: p.use_smooth = True

# ---------- ПОЛОСТЬ: внутренняя стена + дно ----------
im = bpy.data.meshes.new("cavity")
bmi = bmesh.new()
rings = []
n_st = 12
for i in range(n_st + 1):
    v = i / n_st                        # 0 = верх полости .. 1 = дно полости
    z = H - v * (H - FLOOR_Z)
    t = 0.15 + v * 0.55                 # у верха шире (обод), к дну уже
    r = interp(t, MEAS) * R_TOP - WALL
    ring = [bmi.verts.new((r * math.cos(2*math.pi*j/SEG), r * math.sin(2*math.pi*j/SEG), z)) for j in range(SEG)]
    rings.append(ring)
for i in range(len(rings) - 1):
    for j in range(SEG):
        a, b_ = rings[i][j], rings[i][(j+1) % SEG]
        c, d = rings[i+1][j], rings[i+1][(j+1) % SEG]
        bmi.faces.new((a, d, c, b_))
fc = bmi.verts.new((0, 0, FLOOR_Z + 0.015))
for j in range(SEG):
    bmi.faces.new((rings[-1][(j+1) % SEG], rings[-1][j], fc))
bmesh.ops.recalc_face_normals(bmi, faces=bmi.faces)
bmi.to_mesh(im); bmi.free()
cav = link(bpy.data.objects.new("cavity", im))
cav.data.materials.append(m_inner)
for p in im.polygons: p.use_smooth = True

# диск дна полости
fm = bpy.data.meshes.new("floor")
bmf = bmesh.new()
r_f = interp(0.70, MEAS) * R_TOP - WALL
vs = [bmf.verts.new((r_f * math.cos(2*math.pi*j/SEG), r_f * math.sin(2*math.pi*j/SEG), FLOOR_Z)) for j in range(SEG)]
bmf.faces.new(vs)
bmf.to_mesh(fm); bmf.free()
flr = link(bpy.data.objects.new("floor", fm))
flr.data.materials.append(m_floor)
for p in fm.polygons: p.use_smooth = True

# ---------- ОБОД-ВАЛИК ----------
def torus(name, R, r, z, mat):
    msh = bpy.data.meshes.new(name)
    b = bmesh.new()
    for i in range(24):
        u = 2 * math.pi * i / 24
        for j in range(12):
            vv = 2 * math.pi * j / 12
            x = (R + r * math.cos(vv)) * math.cos(u)
            y = (R + r * math.cos(vv)) * math.sin(u)
            b.verts.new((x, y, z + r * math.sin(vv)))
    b.verts.ensure_lookup_table()
    for i in range(24):
        for j in range(12):
            a1 = b.verts[(i * 12 + j) % (24 * 12)]
            a2 = b.verts[(i * 12 + (j+1) % 12) % (24 * 12)]
            b1 = b.verts[(((i+1) % 24) * 12 + j) % (24 * 12)]
            b2 = b.verts[(((i+1) % 24) * 12 + (j+1) % 12) % (24 * 12)]
            b.faces.new((a1, a2, b2, b1))
    b.to_mesh(msh); b.free()
    o = link(bpy.data.objects.new(name, msh))
    o.data.materials.append(mat)
    for p in msh.polygons: p.use_smooth = True
    return o

rim = torus("rim", R_TOP - 0.02, 0.045, H - 0.01, m_rim)
ring = torus("ring", R_TOP - WALL, 0.045, H - 0.045, m_ring)

# ---------- УШИ ----------
def uvsphere(name, r, loc, mat, scale=(1, 1, 1)):
    m = bpy.data.meshes.new(name)
    b = bmesh.new()
    bmesh.ops.create_uvsphere(b, u_segments=12, v_segments=8, radius=r)
    b.to_mesh(m); b.free()
    o = link(bpy.data.objects.new(name, m))
    o.location = loc; o.scale = scale
    o.data.materials.append(mat)
    for p in m.polygons: p.use_smooth = True
    return o

earL = uvsphere("earL", 0.075, (-(R_TOP + 0.03), -0.04, H - 0.03), m_ear, (0.85, 0.55, 0.7))
earR = uvsphere("earR", 0.075, (+(R_TOP + 0.03), -0.04, H - 0.03), m_ear, (0.85, 0.55, 0.7))

# ---------- РУЧКА (дуга + лента) ----------
hm = bpy.data.meshes.new("handle")
b = bmesh.new()
ARC_X, RZ, TUBE = 0.36, 0.42, 0.08
prev = None
NARC = 18
for i in range(NARC + 1):
    th = math.pi + 0.50 + (math.pi - 1.00) * i / NARC
    cx, cz = ARC_X * math.cos(th), RZ + RZ * math.sin(th)
    for s in range(8):
        ph = 2 * math.pi * s / 8
        b.verts.new((cx + TUBE * math.cos(ph) * math.cos(th), TUBE * math.sin(ph), cz + TUBE * math.cos(ph) * math.sin(th)))
b.verts.ensure_lookup_table()
for i in range(NARC):
    for s in range(8):
        a1 = b.verts[i * 8 + s]; a2 = b.verts[i * 8 + (s+1) % 8]
        b1 = b.verts[(i+1) * 8 + s]; b2 = b.verts[(i+1) * 8 + (s+1) % 8]
        b.faces.new((a1, a2, b2, b1))
b.to_mesh(hm); b.free()
hnd = link(bpy.data.objects.new("handle", hm))
hnd.data.materials.append(m_hnd)
for p in hm.polygons: p.use_smooth = True
coils = []
# coil-утолщения — включаются только в позе купола (см. dn-ветку)
if not SKIP_UP:
    pass
else:
    for i in range(5):
        th = 3 * math.pi / 2 + (-0.44 + 0.22 * i)
        cx, cz = ARC_X * math.cos(th), RZ + RZ * math.sin(th)
        co = uvsphere(f"coil{i}", 0.088, (cx, 0, cz + 0.02), m_hnd, (1.15, 1.5, 1.15))
        co.hide_render = False
        coils.append(co)

# лента ручки (поперёк купола после флипа — визуально на теле)
band = torus("band", R_TOP - 0.06, 0.055, H - 0.10, m_ring)

m_walltop = emat("walltop", (222/255, 72/255, 0))
wm = bpy.data.meshes.new("walltop"); bmw = bmesh.new()
r_in = interp(0.15, MEAS) * R_TOP - WALL
vs_out = [bmw.verts.new((R_TOP * math.cos(2*math.pi*j/SEG), R_TOP * math.sin(2*math.pi*j/SEG), H - 0.002)) for j in range(SEG)]
vs_in = [bmw.verts.new((r_in * math.cos(2*math.pi*j/SEG), r_in * math.sin(2*math.pi*j/SEG), H - 0.002)) for j in range(SEG)]
for j in range(SEG):
    bmw.faces.new((vs_out[j], vs_out[(j+1)%SEG], vs_in[(j+1)%SEG], vs_in[j]))
bmw.to_mesh(wm); bmw.free()
walltop = link(bpy.data.objects.new("walltop", wm))
walltop.data.materials.append(m_walltop)

bucket_objs = [o for o in S.collection.objects if o.name != "Cube"]
m_ground = emat("ground", (16/255, 16/255, 32/255))   # пол = цвет мира (не ломает bg)
gm = bpy.data.meshes.new("ground"); bmg = bmesh.new()
bmesh.ops.create_grid(bmg, x_segments=1, y_segments=1, size=12)
bmg.to_mesh(gm); bmg.free()
ground = link(bpy.data.objects.new("ground", gm))
ground.location = (0, 0, -0.001)
ground.data.materials.append(m_ground)
ground.hide_render = True

# ---------- КАМЕРА И РЕНДЕР ----------
def refcam(elev, azim, dist, target_z):
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 50
    cam = link(bpy.data.objects.new("cam", cam_data))
    S.camera = cam
    th = math.radians(elev)
    cam.location = (dist * math.cos(th) * math.cos(math.radians(azim)),
                    dist * math.cos(th) * math.sin(math.radians(azim)),
                    target_z + dist * math.sin(th))
    d = Vector((0, 0, target_z)) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam_data.clip_end = 100

def shoot(path):
    S.render.filepath = path
    bpy.ops.render.render(write_still=True)

if not SKIP_UP:
    refcam(ELEV_UP, 90, DIST_UP, H * 0.42)
    for co in coils: co.hide_render = True
    shoot(OUT_UP)

if not SKIP_DN:
    M = Matrix.Translation((0, 0, -SINK)) @ Matrix.Rotation(math.pi, 4, "X") @ Matrix.Translation((0, 0, -H))
    for o in bucket_objs:
        o.matrix_world = M @ o.matrix_world
    bpy.context.view_layer.update()
    h = bpy.data.objects.get("handle")
    h.matrix_world = Matrix.Translation((0, -0.10, RAISE)) @ h.matrix_world
    refcam(ELEV_DN, 90, DIST_DN, H * 0.22)
    shoot(OUT_DN)

print("V22 DONE")
