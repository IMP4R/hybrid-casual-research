"""clay_lib.py — общий bpy-фреймворк для клэй-ассетов (Blender headless).
Использование в скриптах игры:
    import sys; sys.path.insert(0, "/Users/user0/godot-hybrid-casual/tools")
    from clay_lib import *
    with asset("paintloop", "bucket", colors={"red": RED}) as a:
        b = a.add_body()  # строишь геометрию через a.add_* хелперы
Формула клэя: примитив → Bevel(пухлость) → flat-цвет → 3-point soft light.
"""
import bpy, math, os

OUT_ROOT = "/Users/user0/godot-hybrid-casual/assets"

# Палитра design_system §9 (RGB 0-1)
RED    = (0.910, 0.227, 0.227)
RED_D  = (0.620, 0.100, 0.100)
GREEN  = (0.337, 0.745, 0.361)
GREEN_D= (0.180, 0.480, 0.200)
BLUE   = (0.204, 0.549, 0.961)
BLUE_D = (0.110, 0.320, 0.600)
YELLOW = (1.000, 0.839, 0.353)
GOLD   = (1.000, 0.729, 0.078)
PURPLE = (0.588, 0.314, 0.863)
ORANGE = (1.000, 0.569, 0.157)
WHITE  = (0.980, 0.980, 0.975)
DARK   = (0.180, 0.170, 0.190)
BROWN  = (0.480, 0.310, 0.180)
CREAM  = (0.960, 0.930, 0.860)
GLASS  = (0.780, 0.900, 1.000)
GREY   = (0.700, 0.720, 0.750)

def hex1(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

class Asset:
    """Один ассет: собирает объекты, рендерит, экспортирует."""
    def __init__(self, game, name, variant=None):
        self.game, self.name, self.variant = game, name, variant
        self.objects = []
        self.mats = {}

    # ---- материалы ----
    def mat(self, color, key=None, rough=0.55, alpha=1.0):
        key = key or f"m{len(self.mats)}"
        m = bpy.data.materials.new(f"{self.name}_{key}")
        m.diffuse_color = (*color, 1)  # Workbench preview
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*color, 1)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = 0.0
        if alpha < 1.0:
            b.inputs["Alpha"].default_value = alpha
            m.blend_method = "BLEND"
        self.mats[key] = m
        return m

    # ---- хелперы геометрии ----
    def _finish(self, obj, material, bevel_w=None, seg=4, do_smooth=True):
        if material: obj.data.materials.append(material)
        if do_smooth:
            for p in obj.data.polygons: p.use_smooth = True
        if bevel_w:
            m = obj.modifiers.new("Bevel", "BEVEL")
            m.width = bevel_w; m.segments = seg
            m.limit_method = "ANGLE"; m.angle_limit = math.radians(45)
        self.objects.append(obj)
        return obj

    def cube(self, size=1.0, loc=(0,0,0), rot=(0,0,0), scale=(1,1,1), mat=None, bevel=0.03):
        bpy.ops.mesh.primitive_cube_add(size=size, location=loc, rotation=rot)
        o = bpy.context.object; o.scale = scale
        return self._finish(o, mat, bevel)

    def cyl(self, r=0.5, depth=1.0, loc=(0,0,0), rot=(0,0,0), verts=48, mat=None, bevel=0.02):
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
        return self._finish(bpy.context.object, mat, bevel)

    def cone(self, r1=0.5, r2=0.0, depth=1.0, loc=(0,0,0), rot=(0,0,0), verts=40, mat=None, bevel=0.015):
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
        return self._finish(bpy.context.object, mat, bevel)

    def sphere(self, r=0.5, loc=(0,0,0), scale=(1,1,1), rot=(0,0,0), seg=32, mat=None, bevel=0.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=seg//2, location=loc, rotation=rot)
        o = bpy.context.object; o.scale = scale
        bpy.ops.object.shade_smooth()
        return self._finish(o, mat, bevel)

    def torus(self, R=0.5, r=0.08, loc=(0,0,0), rot=(0,0,0), scale=(1,1,1), mat=None, bevel=0.0):
        bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot)
        o = bpy.context.object; o.scale = scale
        return self._finish(o, mat, bevel)

    def capsule(self, r=0.3, depth=0.8, loc=(0,0,0), rot=(0,0,0), mat=None):
        """капсула = цилиндр + 2 полусферы"""
        m = mat or self.mat(DARK)
        self.cyl(r, depth, loc, rot, mat=m, bevel=None)
        import mathutils
        d = mathutils.Vector(rot) @ mathutils.Vector((0, 0, depth/2)) if rot else (0,0,depth/2)
        dx, dy, dz = d
        self.sphere(r, (loc[0]+dx, loc[1]+dy, loc[2]+dz), mat=m)
        self.sphere(r, (loc[0]-dx, loc[1]-dy, loc[2]-dz), mat=m)

    # ---- сцена/свет/камера/вывод ----
    def _scene(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        S = bpy.context.scene
        self.objects = []
        return S

    def stage(self, ground=True):
        S = self._scene()
        if ground:
            self.cube(size=7, loc=(0,0,-0.05), scale=(1,1,0.014), mat=self.mat((0.93,0.93,0.92), key="ground", rough=0.9), bevel=None)
        return S

    def lights(self):
        S = bpy.context.scene
        key = bpy.data.lights.new("key", "AREA"); key.energy = 140; key.size = 3
        ko = bpy.data.objects.new("key", key); ko.location = (2.5, -2.5, 3.5)
        ko.rotation_euler = (math.radians(45), 0, math.radians(45)); S.collection.objects.link(ko)
        fill = bpy.data.lights.new("fill", "AREA"); fill.energy = 45; fill.size = 4
        fo = bpy.data.objects.new("fill", fill); fo.location = (-3, -1.5, 2)
        fo.rotation_euler = (math.radians(60), 0, math.radians(-60)); S.collection.objects.link(fo)
        S.world = bpy.data.worlds.new("w"); S.world.use_nodes = True
        S.world.node_tree.nodes["Background"].inputs[0].default_value = (0.85, 0.9, 1.0, 1)
        S.world.node_tree.nodes["Background"].inputs[1].default_value = 0.4

    def camera(self, dist=3.2, z=1.5, azimuth=42, elevation=28, target_z=0.35):
        S = bpy.context.scene
        cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam)
        a, e = math.radians(azimuth), math.radians(elevation)
        co.location = (dist*math.cos(e)*math.cos(a), dist*math.cos(e)*math.sin(a), dist*math.sin(e)+target_z+(z-1.5))
        # доказанный Эйлер: камера смотрит на target (проверено smoke-тестом bucket)
        co.rotation_euler = (math.radians(90-elevation), 0, math.radians(90+azimuth))
        S.collection.objects.link(co); S.camera = co

    def render(self, png_path, samples=32, res=640):
        S = bpy.context.scene
        S.render.engine = "BLENDER_WORKBENCH"
        S.display.shading.light = "STUDIO"
        S.display.shading.color_type = "TEXTURE"
        S.display.shading.show_shadows = False
        S.display.render_aa = "FXAA"
        S.render.resolution_x = res; S.render.resolution_y = res
        S.render.filepath = png_path
        os.makedirs(os.path.dirname(png_path), exist_ok=True)
        bpy.ops.render.render(write_still=True)

    def export(self, glb_path):
        os.makedirs(os.path.dirname(glb_path), exist_ok=True)
        bpy.ops.object.select_all(action="DESELECT")
        for o in self.objects:
            if o.name.startswith(("key", "fill")): continue
            try: o.select_set(True)
            except Exception: pass
        bpy.ops.export_scene.gltf(filepath=glb_path, use_selection=True)

def make(game, name, variant, builder, dist=3.2, z=1.5, azimuth=42, elevation=28, samples=32, res=640):
    """Полный цикл: сцена → builder(a) → свет/камера → рендер → GLB.
    builder(a, color) получает Asset и основной цвет варианта."""
    rdir = f"{OUT_ROOT}/renders/{game}"
    gdir = f"{OUT_ROOT}/games/{game}/proc"
    a = Asset(game, name, variant)
    a.stage()
    builder(a)
    a.lights()
    a.camera(dist=dist, z=z, azimuth=azimuth, elevation=elevation)
    suffix = f"_{variant}" if variant else ""
    a.render(f"{rdir}/{name}{suffix}.png", samples=samples, res=res)
    a.export(f"{gdir}/{name}{suffix}.glb")
    print(f"[ok] {game}/{name}{suffix}")
