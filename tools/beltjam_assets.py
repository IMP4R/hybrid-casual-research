"""Ассеты Belt Jam (цех): блоки, лента, изгиб, стрелка, ворота, ящик."""
import sys; sys.path.insert(0, "/Users/user0/godot-hybrid-casual/tools")
from clay_lib import *
import math

def block(a, color):
    a.cube(size=0.9, loc=(0,0,0.45), mat=a.mat(color), bevel=0.09)

def parcel(a, color):
    a.cube(size=0.9, loc=(0,0,0.45), mat=a.mat(CREAM), bevel=0.08)
    a.cube(size=0.94, loc=(0,0,0.45), scale=(1,0.18,1.02), mat=a.mat(color), bevel=0.04)

def conveyor(a, color):
    gm = a.mat((0.45,0.47,0.5))
    a.cube(size=1.0, loc=(0,0,0.42), scale=(2.2,0.9,0.16), mat=gm, bevel=0.04)
    for x in (-0.85,-0.42,0,0.42,0.85):
        a.cyl(r=0.16, depth=0.8, loc=(x,0,0.52), rot=(0,math.radians(90),0), mat=a.mat((0.72,0.74,0.78)), bevel=0.02)
    for sx in (-0.8,0.8):
        for sy in (-0.35,0.35):
            a.cyl(r=0.05, depth=0.4, loc=(sx,sy,0.2), mat=a.mat(DARK), bevel=0.01)

def curve(a, color):
    gm = a.mat((0.45,0.47,0.5))
    import math as M
    n = 7
    for i in range(n):
        t = M.radians(90) * i/(n-1)
        x, y = 1.1*M.cos(t), 1.1*M.sin(t)
        a.cube(size=0.62, loc=(x,y,0.42), rot=(0,0,t+M.radians(90)), scale=(1.05,1.05,0.16), mat=gm, bevel=0.03)
        a.cyl(r=0.14, depth=0.8, loc=(x*1.1, y*1.1, 0.52), rot=(0,M.radians(90),t), mat=a.mat((0.72,0.74,0.78)), bevel=0.02)
    a.cyl(r=0.06, depth=0.42, loc=(1.05,0,0.2), mat=a.mat(DARK), bevel=0.01)
    a.cyl(r=0.06, depth=0.42, loc=(0,1.05,0.2), mat=a.mat(DARK), bevel=0.01)

def switch_arrow(a, color):
    a.cyl(r=0.3, depth=0.18, loc=(0,0,0.1), verts=40, mat=a.mat(DARK), bevel=0.03)
    a.cone(r1=0.16, r2=0.02, depth=0.9, loc=(0,0,0.45), rot=(0,math.radians(90),0), mat=a.mat(YELLOW), bevel=0.02)
    a.sphere(r=0.14, loc=(-0.42,0,0.45), mat=a.mat(color), bevel=0)

def gate(a, color):
    for sx in (-0.7,0.7):
        a.cyl(r=0.12, depth=1.5, loc=(sx,0,0.75), mat=a.mat((0.45,0.47,0.5)), bevel=0.02)
    a.cube(size=1.0, loc=(0,0,1.56), scale=(1.7,0.25,0.16), mat=a.mat((0.45,0.47,0.5)), bevel=0.03)
    a.torus(R=0.34, r=0.07, loc=(0,0,1.15), mat=a.mat(color), bevel=0.02)

def crate(a, color):
    a.cube(size=1.0, loc=(0,0,0.5), mat=a.mat(BROWN, rough=0.75), bevel=0.05)
    for zz in (0.28, 0.72):
        a.cube(size=1.0, loc=(0,0,zz), scale=(1.04,1.04,0.08), mat=a.mat(BROWN, rough=0.75), bevel=0.01)

jobs = []
for c, cn in ((RED,"red"),(GREEN,"green"),(BLUE,"blue"),(YELLOW,"yellow"),(PURPLE,"purple")):
    jobs.append((f"block_{cn}", lambda a,c=c: block(a,c)))
jobs.append(("parcel_blue", lambda a: parcel(a,BLUE)))
jobs.append(("parcel_red", lambda a: parcel(a,RED)))
jobs.append(("conveyor_straight", lambda a: conveyor(a,None)))
jobs.append(("conveyor_curve", lambda a: curve(a,None)))
jobs.append(("switch_arrow", lambda a: switch_arrow(a,RED)))
for c, cn in ((RED,"red"),(GREEN,"green"),(BLUE,"blue")):
    jobs.append((f"gate_{cn}", lambda a,c=c: gate(a,c)))
jobs.append(("crate_wood", lambda a: crate(a,None)))

for name, fn in jobs:
    make("beltjam", name, None, fn)
print("BELTJAM ASSETS DONE")
