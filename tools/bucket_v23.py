# V23: ведро Paint Loop — чистые примитивы, одна mesh, две позы.
# Логические гейты: C3 одна mesh (флип = matrix), C4 симметрия (lathe), C5 ручка скрыта в прямой.
import math, os as _os, sys
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix

REF_UP = "/Users/user0/godot-hybrid-casual/assets/ref_clean_upright2.png"
REF_DN = "/tmp/ref_dome_v2_1788244974.png"
S = bpy.context.scene
S.render.engine = 'BLENDER_EEVEE_NEXT'
S.render.resolution_x = S.render.resolution_y = 512
S.eevee.taa_render_samples = int(_os.environ.get("SAMPLES", "48"))
S.view_settings.view_transform = 'Standard'
S.view_settings.look = 'None'

def srgb(c): return tuple(v ** 2.2 if v > 0.04045 else v/12.92 for v in c)

wld = bpy.data.worlds.get("W") or bpy.data.worlds.new("W")
S.world = wld; wld.use_nodes = True
wld.node_tree.nodes["Background"].inputs[0].default_value = (*srgb((16/255, 16/255, 32/255)), 1)

KT = [0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85]
KV = [float(v) for v in _os.environ.get("KNOTS", "0.711,0.887,0.976,0.973,0.949,0.842,0.719,0.631").split(",")]
MEAS = sorted([(t, v) for t, v in zip(KT, KV)] + [(0.20, (KV[0]+KV[1])/2), (0.30, (KV[1]+KV[2])/2),
               (0.40, (KV[2]+KV[3])/2), (0.50, (KV[3]+KV[4])/2), (0.60, (KV[4]+KV[5])/2),
               (0.70, (KV[5]+KV[6])/2), (0.80, (KV[6]+KV[7])/2)])

def interp(t, pts=MEAS):
    if t <= pts[0][0]: return pts[0][1]
    if t >= pts[-1][0]: return pts[-1][1]
    for (t0, w0), (t1, w1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            return w0 + (w1 - w0) * u
    return pts[-1][1]

H = 0.90
R_TOP = 0.50
WALL = 0.11
SEG, STEPS = 64, 30
RAISE = float(_os.environ.get("RAISE", "-0.12"))
ELEV_UP = float(_os.environ.get("ELEV_UP", "22"))
DIST_UP = float(_os.environ.get("DIST_UP", "2.4"))
ELEV_DN = float(_os.environ.get("ELEV_DN", "24"))
DIST_DN = float(_os.environ.get("DIST_DN", "1.6"))
SINK = float(_os.environ.get("SINK", "0.62"))

def build():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    def link(o): S.collection.objects.link(o); return o
    stops = [(0.00, (240,86,0)), (0.45, (237,104,0)), (0.85, (255,157,0)), (1.00, (255,169,0))]
    m_body = bpy.data.materials.new("body"); m_body.use_nodes = True
    nt = m_body.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0; mr.inputs["From Max"].default_value = H
    mr.clamp = True
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = 'LINEAR'
    while len(ramp.color_ramp.elements) < len(stops):
        ramp.color_ramp.elements.new(0.5)
    for e, (pos, col) in zip(ramp.color_ramp.elements, stops):
        e.position = pos; e.color = (*srgb(tuple(v/255 for v in col)), 1)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[1].default_value = 1.0
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs[0])
    nt.links.new(mr.outputs[0], ramp.inputs[0])
    nt.links.new(ramp.outputs["Color"], em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    m_hnd = bpy.data.materials.new("hnd"); m_hnd.use_nodes = True
    nth = m_hnd.node_tree; nth.nodes.clear()
    outh = nth.nodes.new("ShaderNodeOutputMaterial")
    emh = nth.nodes.new("ShaderNodeEmission")
    emh.inputs[0].default_value = (*srgb((70/255, 70/255, 74/255)), 1)
    nth.links.new(emh.outputs[0], outh.inputs[0])

    # тело: lathe-профиль (сферическое дно + борта)
    mesh = bpy.data.meshes.new("body"); bm = bmesh.new()
    R_WATER = interp(0.85) * R_TOP
    Z_WL = 0.30 * H; Z_TIP = 0.08 * H
    rings = []
    for i in range(STEPS + 1):
        v = i / STEPS
        if v < 0.30:
            u = v / 0.30; th = u * math.pi / 2
            r = R_WATER * math.sin(th); z = Z_TIP + (Z_WL - Z_TIP) * math.sin(th)
        else:
            u2 = (v - 0.30) / 0.70
            t = 0.85 - u2 * 0.70
            r = interp(t) * R_TOP
            z = Z_WL + u2 * (H - Z_WL)
        rings.append([bm.verts.new((r * math.cos(2*math.pi*j/SEG), r * math.sin(2*math.pi*j/SEG), z)) for j in range(SEG)])
    for i in range(len(rings) - 1):
        for j in range(SEG):
            bm.faces.new((rings[i][j], rings[i][(j+1)%SEG], rings[i+1][(j+1)%SEG], rings[i+1][j]))
    bc = bm.verts.new((0, 0, Z_TIP))
    for j in range(SEG):
        bm.faces.new((rings[0][j], rings[0][(j+1)%SEG], bc))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh); bm.free()
    body = link(bpy.data.objects.new("body", mesh)); body.data.materials.append(m_body)
    for p in mesh.polygons: p.use_smooth = True
    # внутренность
    im_ = bpy.data.meshes.new("cavity"); bmi = bmesh.new()
    rings = []
    FLOOR_Z = 0.50
    for i in range(13):
        v = i / 12
        z = H - v * (H - FLOOR_Z)
        t = 0.15 + v * 0.55
        r = interp(t) * R_TOP - WALL
        rings.append([bmi.verts.new((r * math.cos(2*math.pi*j/SEG), r * math.sin(2*math.pi*j/SEG), z)) for j in range(SEG)])
    for i in range(len(rings) - 1):
        for j in range(SEG):
            bmi.faces.new((rings[i][j], rings[i+1][(j+1)%SEG], rings[i+1][j], rings[i][(j+1)%SEG]))
    bmesh.ops.recalc_face_normals(bmi, faces=bmi.faces)
    bmi.to_mesh(im_); bmi.free()
    cav = link(bpy.data.objects.new("cavity", im_)); cav.data.materials.append(m_body)
    fm = bpy.data.meshes.new("floor"); bmf = bmesh.new()
    r_f = interp(0.70) * R_TOP - WALL
    vs = [bmf.verts.new((r_f * math.cos(2*math.pi*j/SEG), r_f * math.sin(2*math.pi*j/SEG), FLOOR_Z)) for j in range(SEG)]
    bmf.faces.new(vs); bmf.to_mesh(fm); bmf.free()
    flr = link(bpy.data.objects.new("floor", fm)); flr.data.materials.append(m_body)
    # ручка: пояс-горизонтальный тор вокруг корпуса (реф перевёрнутой: лента через нижнюю треть)
    BELT_Z = 0.16
    BELT_R = interp(BELT_Z / H) * R_TOP + 0.015
    BTUBE = 0.05
    SPAN = math.radians(300)
    hm = bpy.data.meshes.new("handle"); b = bmesh.new()
    NARC2, NPROF = 36, 10
    for i in range(NARC2 + 1):
        u = -SPAN/2 + SPAN * i / NARC2
        for j in range(NPROF):
            ph = 2 * math.pi * j / NPROF
            rr = BELT_R + BTUBE * math.cos(ph)
            zz = BELT_Z + BTUBE * math.sin(ph)
            b.verts.new((rr * math.cos(u), rr * math.sin(u), zz))
    b.verts.ensure_lookup_table()
    def vi_(i, j): return b.verts[i * NPROF + (j % NPROF)]
    for i in range(NARC2):
        for j in range(NPROF):
            b.faces.new((vi_(i, j), vi_(i, j+1), vi_(i+1, j+1), vi_(i+1, j)))
    b.to_mesh(hm); b.free()
    hnd = link(bpy.data.objects.new("handle", hm)); hnd.data.materials.append(m_hnd)
    for p2 in hm.polygons: p2.use_smooth = True
    hnd.rotation_euler = (math.radians(-8), 0, 0)  # наклон ленты как в рефе
    # walltop
    m_wt = bpy.data.materials.new("wt"); m_wt.use_nodes = True
    ntw = m_wt.node_tree; ntw.nodes.clear()
    outw = ntw.nodes.new("ShaderNodeOutputMaterial")
    emw = ntw.nodes.new("ShaderNodeEmission")
    emw.inputs[0].default_value = (*srgb((222/255, 72/255, 0)), 1)
    ntw.links.new(emw.outputs[0], outw.inputs[0])
    wm = bpy.data.meshes.new("walltop"); bmw = bmesh.new()
    r_in = interp(0.15) * R_TOP - WALL
    vo = [bmw.verts.new((R_TOP * math.cos(2*math.pi*j/SEG), R_TOP * math.sin(2*math.pi*j/SEG), H - 0.002)) for j in range(SEG)]
    vi = [bmw.verts.new((r_in * math.cos(2*math.pi*j/SEG), r_in * math.sin(2*math.pi*j/SEG), H - 0.002)) for j in range(SEG)]
    for j in range(SEG):
        bmw.faces.new((vo[j], vo[(j+1)%SEG], vi[(j+1)%SEG], vi[j]))
    bmw.to_mesh(wm); bmw.free()
    wt = link(bpy.data.objects.new("walltop", wm)); wt.data.materials.append(m_wt)
    verts_total = sum(len(o.data.vertices) for o in [body, cav, flr, hnd, wt])
    return [body, cav, flr, hnd, wt], verts_total

def refcam(elev, dist, target_z):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    S.collection.objects.link(cam); S.camera = cam
    th = math.radians(elev)
    cam.location = (dist * math.cos(th), 0, target_z + dist * math.sin(th))
    d = Vector((0, 0, target_z)) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

def shoot(path, ring_px=0, ring_col=(10,10,12)):
    S.render.filepath = path
    bpy.ops.render.render(write_still=True)
    if ring_px:
        img = bpy.data.images.load(path)
        w, h = img.size
        arr = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1, :, :3] * 255.0
        bg = arr[0, 0]
        m = ~(((arr - bg) ** 2).sum(axis=2) < 38.0 ** 2)
        d = m.copy()
        for _ in range(ring_px):
            d = d | np.roll(d, 1, 0) | np.roll(d, -1, 0) | np.roll(d, 1, 1) | np.roll(d, -1, 1)
        arr[d & ~m] = ring_col
        out = np.zeros((h, w, 4), np.float32)
        out[..., :3] = arr[::-1] / 255.0
        out[..., 3] = 1.0
        img.pixels = out.ravel()
        img.filepath_raw = path
        img.file_format = 'PNG'
        img.save()
        bpy.data.images.remove(img)

objs, nv = build()
import os as _oe
if _oe.environ.get("SOLO_HANDLE"):
    for o in objs:
        if o.name != "handle": o.hide_render = True
if _oe.environ.get("NO_HANDLE"):
    bpy.data.objects["handle"].hide_render = True
print(f"C3-улика: вершин в mesh {nv}", flush=True)
# прямое: ручка-пояс скрыта (в рефе прямого её нет)
bpy.data.objects["handle"].hide_render = True
refcam(ELEV_UP, DIST_UP, float(_os.environ.get('TZUP', '0.35')))
shoot("/tmp/v23_up.png", ring_px=4, ring_col=(45, 22, 8))
# перевёрнутое: та же mesh, только матрицы
M = Matrix.Translation((0, 0, H - SINK)) @ Matrix.Rotation(math.pi, 4, "X")
for o in objs:
    o.matrix_world = M @ o.matrix_world
bpy.context.view_layer.update()
bpy.data.objects["handle"].hide_render = False
refcam(ELEV_DN, DIST_DN, float(_os.environ.get('TZDN', '0.12')))
shoot("/tmp/v23_dn.png", ring_px=6, ring_col=(215, 130, 25))
print("V23 DONE", flush=True)
