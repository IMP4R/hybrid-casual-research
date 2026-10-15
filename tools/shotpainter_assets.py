"""Ассеты Shot Painter (терраса): пушка, шары-краска, мишени-купола, балюстрада, ПОПУГАЙ."""
import sys; sys.path.insert(0, "/Users/user0/godot-hybrid-casual/tools")
from clay_lib import *
import math

def cannon(a, color):
    a.cyl(r=0.3, depth=1.3, loc=(0,0,0.75), rot=(0,math.radians(90),0), mat=a.mat(DARK), bevel=0.04)
    a.torus(R=0.3, r=0.06, loc=(0.65,0,0.75), rot=(0,math.radians(90),0), mat=a.mat(color), bevel=0.02)
    a.sphere(r=0.42, loc=(-0.55,0,0.55), mat=a.mat(DARK), bevel=0.03)
    for sy in (-0.42,0.42):
        a.torus(R=0.3, r=0.09, loc=(-0.15,sy,0.32), rot=(0,math.radians(90),0), mat=a.mat(BROWN), bevel=0.02)
        a.cyl(r=0.08, depth=0.08, loc=(-0.15,sy,0.32), rot=(0,math.radians(90),0), mat=a.mat(GOLD), bevel=0.01)
    a.cube(size=0.8, loc=(0,0,0.28), scale=(1.5,1.1,0.16), mat=a.mat(BROWN, rough=0.75), bevel=0.03)

def ball(a, color):
    a.sphere(r=0.42, loc=(0,0,0.42), mat=a.mat(color, rough=0.35), bevel=0)

def target_cell(a, color):
    a.sphere(r=0.55, loc=(0,0,0.02), scale=(1,1,0.45), mat=a.mat(color, rough=0.4), bevel=0)
    a.torus(R=0.55, r=0.05, loc=(0,0,0.02), scale=(1,1,0.45), mat=a.mat(WHITE), bevel=0.015)

def baluster(a, color):
    a.cyl(r=0.16, depth=0.14, loc=(0,0,0.07), mat=a.mat(WHITE), bevel=0.02)
    a.cyl(r=0.09, depth=0.75, loc=(0,0,0.5), mat=a.mat(WHITE), bevel=0.02)
    a.sphere(r=0.13, loc=(0,0,0.92), mat=a.mat(color), bevel=0.01)

def parrot(a, color):
    m_body = a.mat(RED)
    a.sphere(r=0.55, loc=(0,0,0.75), scale=(0.9,1.0,1.1), mat=m_body)                # тело
    a.sphere(r=0.34, loc=(0,0.18,0.62), scale=(0.85,0.7,0.9), mat=a.mat(CREAM))      # живот
    a.sphere(r=0.36, loc=(0,-0.12,1.38), mat=m_body)                                 # голова
    a.cone(r1=0.14, r2=0.02, depth=0.34, loc=(0,-0.42,1.36), rot=(math.radians(-90),0,0), mat=a.mat(YELLOW), bevel=0.01)  # клюв
    for sx in (-0.15,0.15):
        a.sphere(r=0.09, loc=(sx,-0.28,1.47), mat=a.mat(WHITE))
        a.sphere(r=0.045, loc=(sx,-0.34,1.47), mat=a.mat((0,0,0)))
    for sx in (-0.5,0.5):                                                            # крылья
        a.sphere(r=0.3, loc=(sx,0.05,0.8), scale=(0.35,1.1,0.7), mat=a.mat(BLUE))
    for i, c in enumerate((BLUE, GREEN, YELLOW)):                                    # хвост веером
        a.cube(size=0.5, loc=(0, 0.55+i*0.02, 0.35-i*0.06),
               rot=(math.radians(35), 0, math.radians(-18+i*18)),
               scale=(0.16, 1.5, 0.05), mat=a.mat(c), bevel=0.01)
    for sx in (-0.14,0.14):                                                          # лапы
        a.cyl(r=0.05, depth=0.16, loc=(sx,-0.05,0.16), mat=a.mat(ORANGE), bevel=0.008)

jobs = [
    ("cannon_dark", lambda a: cannon(a, RED_D)),
    ("paintball_red", lambda a: ball(a, RED)),
    ("paintball_blue", lambda a: ball(a, BLUE)),
    ("paintball_green", lambda a: ball(a, GREEN)),
    ("target_red", lambda a: target_cell(a, RED)),
    ("target_blue", lambda a: target_cell(a, BLUE)),
    ("target_green", lambda a: target_cell(a, GREEN)),
    ("target_yellow", lambda a: target_cell(a, YELLOW)),
    ("baluster_white", lambda a: baluster(a, BLUE)),
    ("parrot", lambda a: parrot(a, RED)),
]

for name, fn in jobs:
    make("shotpainter", name, None, fn)
print("SHOTPAINTER ASSETS DONE")
