"""Ассеты Loop Away (пирс): бусины, нить, рама-венец, узел."""
import sys; sys.path.insert(0, "/Users/user0/godot-hybrid-casual/tools")
from clay_lib import *
import bpy, math

def bead(a, color):
    a.sphere(r=0.5, loc=(0,0,0.5), mat=a.mat(color, rough=0.4), bevel=0)
    a.torus(R=0.5, r=0.07, loc=(0,0,0.5), rot=(0,math.radians(90),0), mat=a.mat(RED_D if color==RED else (color[0]*0.6,color[1]*0.6,color[2]*0.6)), bevel=0.02)

def thread(a, color):
    """провисающая нить: bezier → tube → mesh"""
    S = bpy.context.scene
    cu = bpy.data.curves.new("t", "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth = 0.045; cu.bevel_resolution = 4
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(3)
    pts = [(-1.5,0,1.1),(-0.5,0,0.72),(0.5,0,0.72),(1.5,0,1.1)]
    for i, p in enumerate(sp.bezier_points):
        p.co = pts[i]; p.handle_left_type = p.handle_right_type = "AUTO"
    o = bpy.data.objects.new("thread", cu); S.collection.objects.link(o)
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target="MESH")
    self_ = Asset.__new__(Asset); self_.objects=[]; self_.mats={}; self_.name="thread"
    a._finish(bpy.context.object, a.mat(color, rough=0.65), bevel_w=None)

def ring_frame(a, color):
    a.cyl(r=1.35, depth=0.12, loc=(0,0,1.35), verts=64, mat=a.mat(WHITE), bevel=0.04)
    a.torus(R=1.15, r=0.1, loc=(0,0,1.35), mat=a.mat(WHITE), bevel=0.03)
    for i in range(3):
        ang = math.radians(120*i + 90)
        a.cyl(r=0.09, depth=1.35, loc=(math.cos(ang)*0.9, math.sin(ang)*0.9, 0.675),
              rot=(math.radians(math.sin(ang)*12), math.radians(math.cos(ang)*12), 0), mat=a.mat(WHITE), bevel=0.02)

def knot(a, color):
    a.sphere(r=0.55, loc=(0,0,0.55), scale=(1.25,1.0,0.85), mat=a.mat(color, rough=0.6), bevel=0)
    a.torus(R=0.42, r=0.13, loc=(0,0,0.62), rot=(math.radians(60),0,0), mat=a.mat(color, rough=0.6))
    a.torus(R=0.34, r=0.11, loc=(0.05,0.05,0.7), rot=(math.radians(20),math.radians(40),0), mat=a.mat(color, rough=0.6))


jobs = [
    ("bead_red", lambda a: bead(a, RED)),
    ("bead_green", lambda a: bead(a, GREEN)),
    ("bead_blue", lambda a: bead(a, BLUE)),
    ("thread_red", lambda a: thread(a, RED)),
    ("thread_blue", lambda a: thread(a, BLUE)),
    ("ring_frame", lambda a: ring_frame(a, WHITE)),
    ("knot_red", lambda a: knot(a, RED)),
    ("knot_blue", lambda a: knot(a, BLUE)),
]

for name, fn in jobs:
    make("loopaway", name, None, fn, dist=3.6, samples=16)
print("LOOPAWAY FULL DONE")
