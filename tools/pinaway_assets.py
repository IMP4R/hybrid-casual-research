"""Ассеты Pin Away (рудник): штифты, кристаллы, вагонетка, стеклянная секция, ящик, крепь."""
import sys; sys.path.insert(0, "/Users/user0/godot-hybrid-casual/tools")
from clay_lib import *
import math

def pin(a, color):
    a.cyl(r=0.09, depth=1.15, loc=(0,0,0.75), rot=(0,math.radians(90),0), mat=a.mat(GOLD, rough=0.3), bevel=0.015)
    a.torus(R=0.17, r=0.055, loc=(0.62,0,0.75), rot=(0,math.radians(90),0), mat=a.mat(GOLD, rough=0.3), bevel=0.015)
    a.sphere(r=0.11, loc=(-0.6,0,0.75), mat=a.mat(GOLD, rough=0.3), bevel=0.01)

def crystal(a, color):
    a.cone(r1=0.42, r2=0.02, depth=0.75, loc=(0,0,0.62), verts=6, mat=a.mat(color, rough=0.25), bevel=0.03)
    a.cone(r1=0.42, r2=0.05, depth=0.4, loc=(0,0,0.2), verts=6, mat=a.mat(tuple(c*0.7 for c in color), rough=0.3), bevel=0.03)

def minecart(a, color):
    m = a.mat(color, rough=0.5)
    a.cube(size=1.0, loc=(0,0,0.55), scale=(1.5,0.95,0.7), mat=m, bevel=0.07)
    a.cube(size=1.0, loc=(0,0,0.95), scale=(1.56,1.0,0.1), mat=a.mat(DARK), bevel=0.02)
    for sx in (-0.55,0.55):
        for sy in (-0.42,0.42):
            a.cyl(r=0.17, depth=0.1, loc=(sx,sy,0.17), rot=(0,math.radians(90),0), mat=a.mat(DARK), bevel=0.02)

def glass_tube(a, color):
    a.cyl(r=0.55, depth=1.7, loc=(0,0,0.95), verts=48, mat=a.mat(GLASS, rough=0.15, alpha=0.35), bevel=0.04)
    for zz in (0.1, 1.8):
        a.torus(R=0.55, r=0.06, loc=(0,0,zz), mat=a.mat(WHITE), bevel=0.015)

def red_box(a, color):
    a.cube(size=1.0, loc=(0,0,0.45), scale=(1.1,1.1,0.9), mat=a.mat(RED), bevel=0.06)
    a.cube(size=1.0, loc=(0,0,0.95), scale=(1.2,1.2,0.12), mat=a.mat(DARK), bevel=0.03)

def timber(a, color):
    for sx in (-0.9,0.9):
        a.cyl(r=0.14, depth=2.0, loc=(sx,0,1.0), rot=(0,math.radians(8),0), mat=a.mat(BROWN, rough=0.8), bevel=0.02)
    a.cyl(r=0.16, depth=2.2, loc=(0,0,2.0), rot=(0,math.radians(90),0), mat=a.mat(BROWN, rough=0.8), bevel=0.02)

jobs = [
    ("pin_gold", lambda a: pin(a, GOLD)),
    ("crystal_blue", lambda a: crystal(a, BLUE)),
    ("crystal_red", lambda a: crystal(a, RED)),
    ("crystal_green", lambda a: crystal(a, GREEN)),
    ("crystal_purple", lambda a: crystal(a, PURPLE)),
    ("minecart_blue", lambda a: minecart(a, BLUE)),
    ("glass_tube", lambda a: glass_tube(a, None)),
    ("red_box", lambda a: red_box(a, RED)),
    ("timber_support", lambda a: timber(a, None)),
]

for name, fn in jobs:
    make("pinaway", name, None, fn)
print("PINAWAY ASSETS DONE")
