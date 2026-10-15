"""clay_bucket.py — Blender headless: ведро Paint Loop из примитивов (клэй-стиль).
Запуск: /Applications/Blender.app/Contents/MacOS/Blender -b -P clay_bucket.py
Выход: bucket.glb (в Godot) + bucket_render.png (сверка стиля).
Формула клэя: примитив → Bevel(пухлость) → flat-цвет → 3-point soft light."""
import bpy, math

# --- чистая сцена ---
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene

def mat(name, color, rough=0.55):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = 0.0
    return m

def bevel(obj, w=0.02, seg=4):
    m = obj.modifiers.new("Bevel", "BEVEL")
    m.width = w; m.segments = seg; m.limit_method = "ANGLE"; m.angle_limit = math.radians(40)

def smooth(obj):
    for p in obj.data.polygons: p.use_smooth = True

# --- ведро: корпус (конус) + обод (тор) + ручка (полутор) ---
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.62, depth=0.9, location=(0, 0, 0.45))
body = bpy.context.object; smooth(body)
body.data.materials.append(mat("clay_red", (0.86, 0.16, 0.16)))
bevel(body, 0.025)

bpy.ops.mesh.primitive_torus_add(major_radius=0.62, minor_radius=0.055, location=(0, 0, 0.9))
rim = bpy.context.object; smooth(rim)
rim.data.materials.append(mat("clay_red_dark", (0.62, 0.10, 0.10)))
bevel(rim, 0.012, 3)

bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.028, location=(0, 0, 0.92))
handle = bpy.context.object
handle.rotation_euler = (0, math.radians(90), 0)
handle.scale = (1.0, 0.5, 1.0)
smooth(handle)
handle.data.materials.append(mat("clay_dark", (0.25, 0.22, 0.22)))
bevel(handle, 0.008, 3)

# --- земля ---
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
bpy.context.object.data.materials.append(mat("ground", (0.93, 0.93, 0.92), 0.9))

# --- 3-point soft light ---
key = bpy.data.lights.new("key", "AREA"); key.energy = 220; key.size = 3
ko = bpy.data.objects.new("key", key); ko.location = (2.5, -2.5, 3.5)
ko.rotation_euler = (math.radians(45), 0, math.radians(45)); S.collection.objects.link(ko)
fill = bpy.data.lights.new("fill", "AREA"); fill.energy = 70; fill.size = 4
fo = bpy.data.objects.new("fill", fill); fo.location = (-3, -1.5, 2)
fo.rotation_euler = (math.radians(60), 0, math.radians(-60)); S.collection.objects.link(fo)
S.world = bpy.data.worlds.new("w"); S.world.use_nodes = True
S.world.node_tree.nodes["Background"].inputs[0].default_value = (0.85, 0.9, 1.0, 1)
S.world.node_tree.nodes["Background"].inputs[1].default_value = 0.6

# --- камера ---
cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam)
co.location = (2.2, -2.4, 1.6); co.rotation_euler = (math.radians(66), 0, math.radians(42))
S.collection.objects.link(co); S.camera = co

# --- рендер Cycles CPU (headless-надёжно) ---
S.render.engine = "CYCLES"
S.cycles.device = "CPU"; S.cycles.samples = 32
S.render.resolution_x = 900; S.render.resolution_y = 900
S.render.filepath = "/Users/user0/godot-hybrid-casual/assets/bucket_render.png"
bpy.ops.render.render(write_still=True)

# --- GLB для Godot ---
bpy.ops.object.select_all(action="DESELECT")
for o in (body, rim, handle):
    o.select_set(True)
bpy.ops.export_scene.gltf(filepath="/Users/user0/godot-hybrid-casual/assets/bucket.glb", use_selection=True)
print("DONE bucket.glb + bucket_render.png")
