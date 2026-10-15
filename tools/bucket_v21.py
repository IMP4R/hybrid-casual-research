"""bucket_v21 — ЛОГИЧНОЕ ведро по критике: H/D=0.78 (приземистое), дно 70% обода,
узкий обод-валик (r=0.047), отверстие 76% D, внутреннее дно поднято (толстое дно,
полость уже), дно снаружи выпуклым куполом, ручка висит на ушах обода и после
флипа ложится лентой на купол. Плоский тун (emission), sRGB->linear, EEVEE."""
import math, os as _os
import bpy, bmesh
SINK   = float(_os.environ.get("SINK", "0.50"))
RAISE  = float(_os.environ.get("RAISE", "0.00"))
SAMPLES = int(_os.environ.get("SAMPLES", "48"))
SKIP_UP = _os.environ.get("SKIP_UP", "0") == "1"
OUT    = _os.environ.get("OUT", "/tmp/v21_dn.png")
OUT_UP = _os.environ.get("OUT_UP", "/tmp/v21_up.png")
SKIP_DN = _os.environ.get("SKIP_DN", "0") == "1"
H_ENV  = _os.environ.get("HV", None)
ELEV_UP = float(_os.environ.get("ELEV_UP", "52"))
DIST_UP = float(_os.environ.get("DIST_UP", "3.0"))
ELEV_DN = float(_os.environ.get("ELEV_DN", "48"))
from mathutils import Vector, Matrix

# ---------- ПАЛИТРА (sRGB hex -> задаются через srgb()) ----------
def srgb(t):
    return tuple(x ** 2.2 for x in t)

TOP_C   = (237/255, 104/255, 0)   # тело #ED6800 (медиана рефа)
BOT_C   = (224/255, 80/255, 0)   # низ #E05000
INNER_C = (224/255, 96/255, 0)   # внутренность #E06000
RIM_C   = (255/255, 152/255, 0)  # обод #FF9800 (свет рефа)
HANDLE_C= (0.04, 0.04, 0.05)  # ручка #0A0A0D

# ---------- ПАРАМЕТРЫ (из замеров вырезки v2 + критика) ----------
H      = 0.90     # финал (сетка: 79.1%)
if H_ENV: H = float(H_ENV)
R_TOP  = 0.50     # зев 1.0W
R_BOT  = 0.35     # дно 70% обода
WALL   = 0.13     # зёв шире: 74% D
RIM_R  = 0.047    # узкий обод-валик (критик п.3)
FLOOR_Z= 0.47     # полость глубокая: дно на 50% высоты (критик итер.1 п.1)
FLOOR_R= 0.21     # дно полости уже (55% отверстия)
BOT_DOME = 0.24   # корона-холм (непрерывная)

def radius_at(t):
    """прямой конус + мягкая выпуклость низа (пик +0.025 на t=0.3)"""
    r = R_BOT + (R_TOP - R_BOT) * t
    if t < 0.55:
        r += 0.025 * math.sin(math.pi * (0.55 - t) / 0.55)
    return r

def flat_mat(name, color, rough=0.45):
    m = bpy.data.materials.new(name); m.use_nodes = True
    m.diffuse_color = (*srgb(color), 1)
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*srgb(color), 1)
    em.inputs[1].default_value = 1.0
    nt.links.new(em.outputs[0], out.inputs[0])
    return m

def grad_mat():
    m = bpy.data.materials.new("grad"); m.use_nodes = True
    m.diffuse_color = (*TOP_C, 1)
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Max"].default_value = H
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*srgb(BOT_C), 1)
    ramp.color_ramp.elements[1].color = (*srgb(TOP_C), 1)
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs[0], ramp.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.0
    nt.links.new(ramp.outputs["Color"], em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m

for _o in list(bpy.data.objects):
    bpy.data.objects.remove(_o)
m_out = grad_mat()
m_wall  = flat_mat("innerwall", (INNER_C[0]*0.88, INNER_C[1]*0.88, 0.0))  # стенка чуть темнее тела
m_floor = flat_mat("innerfloor", (1.00, 0.71, 0.20))  # светлое дно #FFB533

# ---------- КОРПУС: лоуполи-конус + внутренность + выпуклое дно ----------
me = bpy.data.meshes.new("body"); bm = bmesh.new()
N, RINGS = 20, 8
ro_l, ri_l = [], []
for i in range(RINGS + 1):
    t = i / RINGS; z = t * H
    ro, ri = radius_at(t), radius_at(t) - WALL if t > 0.05 else FLOOR_R
    ro_l.append([bm.verts.new((math.cos(2*math.pi*k/N)*ro, math.sin(2*math.pi*k/N)*ro, z)) for k in range(N)])
    ri_l.append([bm.verts.new((math.cos(2*math.pi*k/N)*ri, math.sin(2*math.pi*k/N)*ri, max(z, FLOOR_Z))) for k in range(N)])
# внешняя стенка
for i in range(1, RINGS + 1):
    for k in range(N):
        k2 = (k + 1) % N
        bm.faces.new((ro_l[i-1][k], ro_l[i-1][k2], ro_l[i][k2], ro_l[i][k])).material_index = 0
# скругление донной кромки снаружи (филлет) + выпуклое дно
prev = ro_l[0]
bot_rings = []
for (dr, dz) in ((0.02, -0.03), (0.035, -0.08), (0.045, -0.14)):   # дно ВЫПУКЛОЕ наружу-вниз
    rl = [bm.verts.new((math.cos(2*math.pi*k/N)*(R_BOT-dr), math.sin(2*math.pi*k/N)*(R_BOT-dr), dz)) for k in range(N)]
    for k in range(N):
        k2 = (k + 1) % N
        bm.faces.new((prev[k], prev[k2], rl[k2], rl[k])).material_index = 0
    bot_rings.append(rl); prev = rl
# выпуклое дно: центр поднят на BOT_DOME
center = bm.verts.new((0, 0, -BOT_DOME))
ring = bot_rings[-1]
for k in range(N):
    k2 = (k + 1) % N
    bm.faces.new((ring[k], ring[k2], center)).material_index = 0
# внутренняя полость: от кромки зёва до приподнятого днища
for i in range(1, RINGS + 1):
    for k in range(N):
        k2 = (k + 1) % N
        bm.faces.new((ri_l[i-1][k2], ri_l[i-1][k], ri_l[i][k], ri_l[i][k2])).material_index = 1
# внутреннее дно (плоское на FLOOR_Z)
bm.faces.new(list(reversed(ri_l[0]))).material_index = 2
# верхняя кромка зёва (соединяет внешнюю и внутреннюю)
for k in range(N):
    k2 = (k + 1) % N
    bm.faces.new((ro_l[RINGS][k2], ri_l[RINGS][k2], ri_l[RINGS][k], ro_l[RINGS][k])).material_index = 0
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me); bm.free()
for pl in me.polygons: pl.use_smooth = True
me.materials.append(m_out); me.materials.append(m_wall); me.materials.append(m_floor)
body = bpy.data.objects.new("body", me)
bpy.context.scene.collection.objects.link(body)

# ---------- ОБОД-ВАЛИК ----------
def torus(name, R, r, z, mat, seg=24, rseg=12):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    verts = []
    for i in range(seg):
        ph = 2*math.pi*i/seg
        for j in range(rseg):
            th = 2*math.pi*j/rseg
            rr = R + r*math.cos(th)
            verts.append(bm.verts.new((rr*math.cos(ph), rr*math.sin(ph), z + r*math.sin(th))))
    def vid(i, j): return i*rseg + (j % rseg)
    for i in range(seg):
        i2 = (i+1) % seg
        for j in range(rseg):
            j2 = (j+1) % rseg
            bm.faces.new((verts[vid(i,j)], verts[vid(i,j2)], verts[vid(i2,j2)], verts[vid(i2,j)]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    for pl in o.data.polygons: pl.use_smooth = True
    return o

rim = torus("rim", R_TOP, RIM_R, H - 0.01, flat_mat("rim", RIM_C))
ring = torus("ring", R_TOP - WALL, 0.045, H - 0.045, flat_mat("ring", (0.42, 0.18, 0.04), 0.6))  # тень зёва толще

# ---------- РУЧКА: уши на ободе + дуга, висящая вдоль -Y ----------
lug_x = R_TOP + 0.03
ARC_X = 0.36            # концы дуги доходят до силуэта
LUG_Z = H - 0.04        # уши чуть ниже кромки
y_off = -0.46
def uvsphere(name, r, loc, mat, scale=(1,1,1)):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=r)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    o.location = loc; o.scale = scale
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    for pl in o.data.polygons: pl.use_smooth = True
    return o

def cyl(name, r, depth, loc, rot, mat):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=r, radius2=r, depth=depth)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    o.location = loc; o.rotation_euler = rot
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

for sx in (-1, 1):
    uvsphere(f"ear{sx}", 0.075, (sx*(R_TOP+0.03), -0.04, H-0.03), flat_mat("ear", HANDLE_C), (0.85, 0.55, 0.7))
me = bpy.data.meshes.new("handle"); bm = bmesh.new()
R_A, RZ, TUBE, STEPS, SEG = ARC_X, 0.42, 0.08, 30, 20   # плоская прилегающая лента
rings = []
for i in range(STEPS + 1):
    th = math.pi + math.pi * i / STEPS     # нижняя полуокружность от ушей
    cx, cz = math.cos(th) * R_A, math.sin(th) * RZ
    rings.append([bm.verts.new((cx + math.cos(th)*TUBE*math.cos(2*math.pi*k/SEG),
                                TUBE*math.sin(2*math.pi*k/SEG),
                                cz + math.sin(th)*TUBE*math.cos(2*math.pi*k/SEG))) for k in range(SEG)])
for i in range(STEPS):
    for k in range(SEG):
        k2 = (k + 1) % SEG
        bm.faces.new((rings[i][k], rings[i][k2], rings[i+1][k2], rings[i+1][k]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me); bm.free()
handle = bpy.data.objects.new("handle", me)
handle.location = (0, y_off, LUG_Z)
bpy.context.scene.collection.objects.link(handle)
handle.data.materials.append(flat_mat("handle", HANDLE_C))

# ---------- СЦЕНА ----------
S = bpy.context.scene
try:
    S.render.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    S.render.engine = "BLENDER_EEVEE"
S.eevee.taa_render_samples = SAMPLES
S.view_settings.view_transform = "Standard"
S.render.resolution_x = 512; S.render.resolution_y = 512
if S.world is None:
    S.world = bpy.data.worlds.new("W")
S.world.use_nodes = True
S.world.node_tree.nodes["Background"].inputs[0].default_value = (16/255, 16/255, 32/255, 1)
S.world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
# свет-заливка чуть сверху-спереди для мягкой формы на плоском туне
sd = bpy.data.lights.new("key", type="AREA"); sd.energy = 40; sd.size = 3.0
key = bpy.data.objects.new("key", sd)
key.location = (-2.5, -2.0, 4.0)
key.rotation_euler = (math.radians(35), 0, math.radians(-50))
bpy.context.scene.collection.objects.link(key)
sd2 = bpy.data.lights.new("sun", type="SUN"); sd2.energy = 0.6
sun = bpy.data.objects.new("sun", sd)
sun.rotation_euler = (math.radians(20), 0, 0)
bpy.context.scene.collection.objects.link(sun)
gme = bpy.data.meshes.new("ground"); bmx = bmesh.new()
bmesh.ops.create_grid(bmx, x_segments=1, y_segments=1, size=6)
bmx.to_mesh(gme); bmx.free()
ground = bpy.data.objects.new("Cube", gme)
ground.location = (0, 0, -0.02)
bpy.context.scene.collection.objects.link(ground)

def refcam(elev, azim, dist, target_z):
    e, az = math.radians(elev), math.radians(azim)
    target = Vector((0, 0, target_z))
    dirv = Vector((math.cos(e)*math.cos(az), math.cos(e)*math.sin(az), math.sin(e)))
    cd = bpy.data.cameras.new("rc")
    cam = bpy.data.objects.new("rc", cd)
    S.collection.objects.link(cam)
    cam.location = target + dirv * dist
    cam.rotation_euler = (math.radians(90 - elev), 0, math.radians(azim + 90))
    S.camera = cam

def shoot(path):
    S.render.filepath = path
    bpy.ops.render.render(write_still=True)

bucket_objs = [o for o in S.collection.objects if o.type == "MESH" and o.name != "Cube"]

for o in S.collection.objects:
    print("[SCN]", o.name, o.type, "hide_r=", o.hide_render, tuple(round(v,2) for v in o.location))
print("[CAM]", S.camera, tuple(round(v,2) for v in S.camera.location) if S.camera else None)
if not SKIP_UP:
    refcam(ELEV_UP, 90, DIST_UP, H * 0.42)
    shoot(OUT_UP)

# перевёрнутое: одна матрица, рот утоплен
if not SKIP_DN:
  M = Matrix.Translation((0, 0, -SINK)) @ Matrix.Rotation(math.pi, 4, "X") @ Matrix.Translation((0, 0, -H))
  for o in bucket_objs:
    o.matrix_world = M @ o.matrix_world
  bpy.context.view_layer.update()
  hnd = bpy.data.objects.get("handle")
  hnd.matrix_world = Matrix.Translation((0, -0.10, RAISE)) @ hnd.matrix_world
  refcam(ELEV_DN, 90, 2.6, H * 0.24)
  shoot(OUT)
if not SKIP_UP:
    for o in bucket_objs:
        o.matrix_world = M.inverted() @ o.matrix_world
    bpy.context.view_layer.update()
    _os.makedirs("/Users/user0/godot-hybrid-casual/assets/games/paintloop/proc", exist_ok=True)
    bpy.ops.export_scene.gltf(filepath="/Users/user0/godot-hybrid-casual/assets/games/paintloop/proc/bucket_v21.glb", export_format="GLB")
print("V21 DONE + GLB")
