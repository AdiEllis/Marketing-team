"""Oak wardrobe (03 closed / 05 open): camera from the front's vanishing points, door quads in the closed photo."""
import numpy as np
W, H = 922, 1152
def line(p, q): return np.cross([p[0], p[1], 1.0], [q[0], q[1], 1.0])
def meet(a, b): v = np.cross(a, b); return v[:2] / v[2]
# front plane edges (closed photo)
top = line((46, 218), (684, 150)); bot = line((50, 843), (672, 914))
lft = line((45, 250), (54, 820)); rgt = line((669, 250), (660, 820))
vx = meet(top, bot); vy = meet(lft, rgt)
c = np.array([W / 2, H / 2])
f2 = -np.dot(vx - c, vy - c)
print("vx", vx.round(1), "vy", vy.round(1), "f2", round(f2), "f", np.sqrt(abs(f2)).round(1))
