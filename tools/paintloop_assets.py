"""Ассеты Paint Loop (ате́лье): ведра, кисть, зоны, тюбик, палитра."""
import sys; sys.path.insert(0, "/Users/user0/godot-hybrid-casual/tools")
from clay_lib import *
import math

def bucket(a, color):
    m = a.mat(color)
    a.cyl(r=0.62, depth=0.9, loc=(0,0,0.45), mat=m, bevel=0.025)
    a.torus(R=0.62, r=0.055, loc=(0,0,0.9), mat=a.mat(RED_D if color==RED else DARK), bevel=0.012)
    a.torus(R=0.55, r=0.028, loc=(0,0,0.92), rot=(math.radians(90),0,0), scale=(1,1,0.5), mat=a.mat(DARK), bevel=0.008)

def brush(a, color):
    a.cyl(r=0.09, depth=1.0, loc=(0,0,0.85), rot=(0.35,0,0), mat=a.mat(BROWN), bevel=0.015)
    a.cyl(r=0.12, depth=0.22, loc=(0,-0.19,0.47), rot=(0.35,0,0), mat=a.mat(DARK), bevel=0.01)
    a.cone(r1=0.13, r2=0.16, depth=0.35, loc=(0,-0.35,0.25), rot=(0.35,0,0), mat=a.mat(ORANGE), bevel=0.01)

def zone(a, color):
    a.cube(size=1.0, loc=(0,0,0.08), scale=(1.4,1.4,0.16), mat=a.mat(CREAM, rough=0.7), bevel=0.06)
    for dx,dy,sx,sy in ((0,0.68,1.42,0.06),(0,-0.68,1.42,0.06),(0.68,0,0.06,1.42),(-0.68,0,0.06,1.42)):
        a.cube(size=1.0, loc=(dx,dy,0.10), scale=(sx,sy,0.20), mat=a.mat(DARK), bevel=0.02)
    a.cyl(r=0.34, depth=0.1, loc=(0,0,0.19), verts=40, mat=a.mat(color, rough=0.35), bevel=0.03)

def tube(a, color):
    a.cyl(r=0.22, depth=0.85, loc=(0,0,0.55), mat=a.mat(color), bevel=0.04)
    a.cyl(r=0.13, depth=0.16, loc=(0,0,1.05), mat=a.mat(WHITE), bevel=0.01)
    a.cube(size=0.3, loc=(0,0,0.55), scale=(0.9,0.4,1.4), rot=(0,0,math.radians(25)), mat=a.mat(WHITE), bevel=0.03)

def palette(a, color):
    a.cyl(r=0.7, depth=0.12, loc=(0,0,0.08), verts=48, mat=a.mat(BROWN, rough=0.7), bevel=0.05)
    for i, c in enumerate((RED, YELLOW, BLUE)):
        a.cyl(r=0.14, depth=0.06, loc=(math.cos(i*2.1)*0.38, math.sin(i*2.1)*0.38, 0.16), verts=32, mat=a.mat(c, rough=0.3), bevel=0.02)

jobs = []
for c, cn in ((RED,"red"),(BLUE,"blue"),(GREEN,"green"),(YELLOW,"yellow")):
    jobs.append((f"bucket_{cn}", lambda a,c=c: bucket(a,c)))
jobs.append(("bucket_white", lambda a: bucket(a, WHITE)))
jobs.append(("brush", lambda a: brush(a, RED)))
for c, cn in ((RED,"red"),(BLUE,"blue"),(GREEN,"green")):
    jobs.append((f"zone_{cn}", lambda a,c=c: zone(a,c)))
    jobs.append((f"tube_{cn}", lambda a,c=c: tube(a,c)))
jobs.append(("palette", lambda a: palette(a, RED)))

for name, fn in jobs:
    make("paintloop", name, None, fn)
print("PAINTLOOP ASSETS DONE")
