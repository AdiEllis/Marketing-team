"""3D door rig for the walnut wall, in the CLOSED photo's geometry.
Camera: f=1100 px (from the drawer's perpendicular edges + wall vanishing point), principal point = image centre,
wall direction r_x from the wall vanishing point, level camera. Doors rotate about their real hinge (right edge),
textures are the real doors (closed photo); the revealed interior is the real interior (open photo) fitted to the opening."""
import json
import numpy as np, cv2

W, H = 1179, 1473
f = 1100.0; cx, cy = W / 2, H / 2
K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]])
Ki = np.linalg.inv(K)
vp = np.load("work/vp_closed.npy")
rx = Ki @ np.array([vp[0], vp[1], 1.0]); rx /= np.linalg.norm(rx)
ry = np.array([0, 1.0, 0]); ry -= rx * (rx @ ry); ry /= np.linalg.norm(ry)
rz = np.cross(rx, ry); rz /= np.linalg.norm(rz)
O = Ki @ np.array([521, 268, 1.0]); O = O / O[2] * 1000.0      # wall origin: wardrobe hinge top, depth 1000
if rz @ O > 0: rz = -rz                                           # normal points toward the camera

def back(u, v):
    d = Ki @ np.array([u, v, 1.0]); s = (rz @ O) / (rz @ d); P = s * d
    return np.array([(P - O) @ rx, (P - O) @ ry, 0.0])
def proj(Pw):
    Pc = O + Pw[0] * rx + Pw[1] * ry + Pw[2] * rz
    p = K @ Pc; return p[:2] / p[2]

# closed-photo door quads (TL, TR, BR, BL), hinge on the RIGHT edge for all doors (seen open in the open photo)
DOORS = {
    "upper": {"quad": [(6, 64), (271, 178), (271, 345), (6, 268)], "open": 150},
    "ward":  {"quad": [(405, 238), (521, 268), (521, 1112), (405, 1138)], "open": 172},
}
DRAWER = {"quad": [(0, 975), (272, 935), (272, 1053), (0, 1113)], "pull": 0.0}
# open-photo interior quads (TL, TR, BR, BL) to fit into the openings
INTERIOR = {
    "upper": [(42, 75), (268, 155), (268, 322), (42, 258)],
    "ward":  [(380, 205), (553, 238), (553, 1105), (380, 1112)],
}

def door_world(name):
    q = DOORS[name]["quad"]
    P = [back(*p) for p in q]
    return P

def rotate(P, hingeX, phi):
    out = []
    for X, Y, Z in P:
        dx = X - hingeX
        out.append(np.array([hingeX + dx * np.cos(phi), Y, -dx * np.sin(phi)]))
    return out

if __name__ == "__main__":
    info = {}
    for n, d in DOORS.items():
        P = door_world(n)
        widths = [np.linalg.norm(P[1] - P[0]), np.linalg.norm(P[2] - P[3])]
        heights = [np.linalg.norm(P[3] - P[0]), np.linalg.norm(P[2] - P[1])]
        print(n, "world w", np.round(widths, 1), "h", np.round(heights, 1))
        info[n] = {"P": [p.tolist() for p in P]}
    Pd = [back(*p) for p in DRAWER["quad"]]
    print("drawer w", np.round(np.linalg.norm(Pd[1] - Pd[0]), 1), "h", np.round(np.linalg.norm(Pd[3] - Pd[0]), 1))
    print("K", K.tolist()); print("rx", rx.round(4), "ry", ry.round(4), "rz", rz.round(4)); print("O", O.round(2))
    json.dump({"K": K.tolist(), "rx": rx.tolist(), "ry": ry.tolist(), "rz": rz.tolist(), "O": O.tolist(), "doors": info,
               "drawer": [p.tolist() for p in Pd]}, open("work/rig.json", "w"))
