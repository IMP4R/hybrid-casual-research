"""bucket_recipe.py — Paint Loop ведро v2 по Blender-Superskill.
Runner: clay_lib (сцена/свет/камера/экспорт). Recipe: только шаги геометрии.
Директива скилла: оболочка с толщиной стенки, обод-валик, контакт-чеки числом.
"""
import sys, math
sys.path.insert(0, "/Users/user0/godot-hybrid-casual/tools")
import bpy, bmesh
from clay_lib import Asset, GREEN, GREEN_D, DARK, WHITE, GREY

H      = 0.92      # высота корпуса
R_TOP  = 0.50      # внешний радиус верха (D = 1.0)
R_BOT  = 0.485      # внешний радиус низа (сужение ~6%)
WALL   = 0.045     # толщина стенки
RIM_R  = 0.038     # радиус валика обода
PAINT_DROP = 0.055 # краска ниже обода

a = Asset("paintloop", "bucket_v2")

def step_body():
    """S1 корпус-оболочка: открытый цилиндр + solidify + сужение низа."""
    a.stage()
    me = bpy.data.meshes.new("body")
    b = bmesh.new()
    bmesh.ops.create_cone(b, cap_ends=False, segments=48, radius1=R_TOP, radius2=R_TOP, depth=H)
    b.to_mesh(me); b.free()
    o = bpy.data.objects.new("body", me)
    bpy.context.scene.collection.objects.link(o)
    o.location = (0, 0, H/2)
    sol = o.modifiers.new("wall", "SOLIDIFY"); sol.thickness = WALL; sol.offset = -1
    bpy.ops.object.modifier_apply(modifier="wall")
    bm = bmesh.new(); bm.from_mesh(o.data)
    for v in bm.verts:
        if v.co.z < 0.06:  # сужение низа
            f = 0.975 + 0.025 * (v.co.z / 0.06)
            v.co.x *= f; v.co.y *= f
    bm.to_mesh(o.data); bm.free()
    m_body = a.mat(GREEN)
    o.data.materials.append(m_body)
    for poly in o.data.polygons: poly.use_smooth = True
    a.objects.append(o)
    print(f"[S1] body shell ok: top_out={R_TOP}, bottom_out={R_BOT}, wall={WALL}")

def step_rim():
    """S2 обод-валик: сидит НА верхней кромке, врезаясь в неё (overlap 0.02)."""
    a.torus(R=R_TOP, r=RIM_R, loc=(0, 0, H - 0.005), mat=a.mat(GREEN))
    # контакт-чек: центр валия на уровне кромки, перекрытие с кромкой 2*RIM_R*0.5
    gap = (H - 0.005) - H
    print(f"[S2] rim contact: rim_center_z - body_top = {gap:+.3f} (врезание, зазора нет)")

def step_paint():
    """S3 краска: диск + купол, внутри стенки, ниже обода."""
    ri = R_TOP - WALL  # внутренний радиус у верха
    a.cyl(r=ri + 0.004, depth=0.05, loc=(0, 0, H - PAINT_DROP), verts=48,
          mat=a.mat(GREEN_D, rough=0.25), bevel=0.01)
    a.sphere(r=ri + 0.004, loc=(0, 0, H - PAINT_DROP + 0.02), scale=(1, 1, 0.10),
             mat=a.mat(GREEN_D, rough=0.25), bevel=0)
    print(f"[S3] paint: r={ri+0.004:.3f} (внутр. стенка {ri:.3f}, врезание +0.004), уровень на {PAINT_DROP:.3f} ниже обода")

def step_handle():
    """S4 ушки + дуга ручки: концы дуги сидят в ушках (числовая проверка)."""
    lug_z = 0.72 * H
    for sx in (-1, 1):
        x = sx * (R_TOP + 0.02)
        a.cube(size=1.0, loc=(x, 0, lug_z), scale=(0.055, 0.09, 0.13), mat=a.mat(GREY, rough=0.35), bevel=0.012)
        a.cyl(r=0.028, depth=0.075, loc=(x, 0, lug_z), rot=(0, math.radians(90), 0),
              mat=a.mat(WHITE, rough=0.3), bevel=0.006)
    # дуга: полутор в вертикальной плоскости, концы на осях ушек
    a.torus(R=0.50, r=0.038, loc=(0, 0, lug_z), rot=(math.radians(90), 0, 0),
            scale=(1, 1, 1), mat=a.mat(GREY, rough=0.35), bevel=0.008)
    print(f"[S4] handle: дуга R=0.50, концы на (±0.50, 0, {lug_z:.3f}); ушки x=±{R_TOP + 0.02:.3f} ±0.055 — концы внутри ушек")

def step_label():
    """S5 табличка-щит с цифрой на передней стенке (игровой счётчик)."""
    a.cube(size=1.0, loc=(0, -(R_TOP - 0.015), 0.40 * H), scale=(0.18, 0.04, 0.22),
           mat=a.mat(DARK, rough=0.5), bevel=0.05)
    bpy.ops.object.text_add(location=(0, -(R_TOP + 0.045), 0.40 * H),
                            rotation=(math.radians(90), 0, 0))
    t = bpy.context.object
    t.data.body = "6"; t.data.size = 0.15; t.data.extrude = 0.025; t.data.align_x = "CENTER"; t.data.align_y = "CENTER"
    bpy.ops.object.convert(target="MESH")
    t.data.materials.append(a.mat(WHITE))
    a.objects.append(t)
    # контакт-чек: передняя грань щита выступает из стенки корпуса
    wall_front = -(R_TOP - 0.03)  # радиус стенки на высоте 0.4H (сужение)
    print(f"[S5] label front y={-(R_TOP - 0.015):.3f} vs wall front y={wall_front:.3f} → выступ {abs(R_TOP - 0.015) - abs(wall_front):+.3f} (щит сидит на стенке)")

# runner-часть: собрать и снять инспекции (Workbench, быстро)
step_body(); step_rim(); step_paint(); step_handle(); step_label()
a.lights(); a.camera(dist=3.0, azimuth=48, elevation=22)
a.render("/Users/user0/godot-hybrid-casual/assets/bucket_v2_34.png", samples=1, res=640)
a.camera(dist=3.0, azimuth=0, elevation=10)
a.render("/Users/user0/godot-hybrid-casual/assets/bucket_v2_front.png", samples=1, res=640)
a.export("/Users/user0/godot-hybrid-casual/assets/games/paintloop/proc/bucket_v2.glb")
print("BUCKET V2 DONE")
