"""Calibrated 3D door rig in a CLOSED photo's geometry (generalised from walnut v2: hinge on either side).
Camera f from the front's vanishing points (phone lens, f~871 px at 922x1152). Exports to reel/assets/<name>/:
door_<n>_front.png (real closed door), door_<n>_back.png (inner face), interior.png (real open photo fitted to the
opening, RGBA), rig.json. Usage: python3 -I flow/rig.py oak|white"""
import sys, json, os, numpy as np, cv2
W, H = 922, 1152
f = 871.0
K = np.array([[f, 0, W / 2], [0, f, H / 2], [0, 0, 1]]); Ki = np.linalg.inv(K)
def L(p, q): return np.cross([p[0], p[1], 1.0], [q[0], q[1], 1.0])
def meet(a, b): v = np.cross(a, b); return v / v[2] if abs(v[2]) > 1e-9 else v

CFG = {
  "oak": dict(closed="work/clean_03.png", open="work/clean_05.png",
    top=((46, 218), (684, 150)), bot=((50, 843), (672, 914)), vert=(((45, 250), (54, 820)), ((669, 250), (660, 820))),
    # open photo -> closed photo homography on the front plane (corner pairs measured on the frame)
    H=(((65, 175), (797, 150), (791, 926), (64, 885)), ((46, 218), (684, 150), (672, 914), (50, 843))),
    # seams x at y=250 and y=820 ; doors: (left seam, right seam, hinge side, open angle deg)
    seams=[(45, 54), (153, 155), (265, 266), (388, 385), (521, 517), (669, 660)],
    doors={"d2": (1, 2, "L", 66), "d3": (2, 3, "R", 95), "d4": (3, 4, "L", 88), "d5": (4, 5, "R", 90)},
    split={"d2": None}),
  "white": dict(closed="input/07_white_closet_closed.jpg", open="input/04_white_closet_open.jpg",
    top=((200, 36), (780, 81)), bot=((200, 1011), (780, 958)), vert=None, H=None,
    seams=[(160, 160), (380, 380), (600, 599), (810, 808)],
    doors={"dl": (0, 1, "L", 92), "dr": (1, 2, "R", 86)}, f=1800),
}
name = sys.argv[1]; C = CFG[name]
f = float(sys.argv[2]) if len(sys.argv) > 2 else C.get("f", f); K = np.array([[f, 0, W / 2], [0, f, H / 2], [0, 0, 1]]); Ki = np.linalg.inv(K)
closed = cv2.imread(C["closed"]); openi = cv2.imread(C["open"])
if C["H"]:
    Hm = cv2.getPerspectiveTransform(np.float32(C["H"][0]), np.float32(C["H"][1]))
    openw = cv2.warpPerspective(openi, Hm, (W, H), flags=cv2.INTER_LANCZOS4)
else:
    openw = openi.copy()
top, bot = L(*C["top"]), L(*C["bot"])
vx = meet(top, bot)
rx = Ki @ np.array([vx[0], vx[1], 1.0]); rx /= np.linalg.norm(rx)
if C["vert"]:
    vy = meet(L(*C["vert"][0]), L(*C["vert"][1])); ry = Ki @ np.array([vy[0], vy[1], 1.0])
else:
    ry = np.array([0, 1.0, 0])
ry = ry - rx * (rx @ ry); ry /= np.linalg.norm(ry)
if ry[1] < 0: ry = -ry
def ytop(x): (a, b), (c, d) = C["top"]; return b + (d - b) * (x - a) / (c - a)
def ybot(x): (a, b), (c, d) = C["bot"]; return b + (d - b) * (x - a) / (c - a)
x0 = C["seams"][0][0]
O = Ki @ np.array([x0, ytop(x0), 1.0]); O = O / O[2] * 1000.0
def setup(rx):
    rz = np.cross(rx, ry); rz /= np.linalg.norm(rz)
    if rz @ O > 0: rz = -rz
    return rz
rz = setup(rx)
def back(u, v):
    d = Ki @ np.array([u, v, 1.0]); s = (rz @ O) / (rz @ d); P = s * d
    return np.array([(P - O) @ rx, (P - O) @ ry, 0.0])
if back(700, 500)[0] < back(100, 500)[0]: rx = -rx; rz = setup(rx)
def proj(P):
    c = O + P[0] * rx + P[1] * ry + P[2] * rz; p = K @ c; return p[:2] / p[2]
def seamx(i, y):  # seam i at image row y (linear between rows 250 and 820, or 120/900 for white)
    a, b = C["seams"][i]; return a + (b - a) * (y - 250) / 570.0
def quad(i, j):
    xl, xr = seamx(i, 250), seamx(j, 250)
    # intersect seam lines with top / bottom edges (two iterations is plenty)
    pts = []
    for (k, fy) in ((i, ytop), (j, ytop), (j, ybot), (i, ybot)):
        y = fy(seamx(k, 500));
        for _ in range(3): y = fy(seamx(k, y))
        pts.append((seamx(k, y), y))
    return pts
def rect(src, q, w, h):
    M = cv2.getPerspectiveTransform(np.float32(q), np.float32([(0, 0), (w, 0), (w, h), (0, h)]))
    return cv2.warpPerspective(src, M, (w, h), flags=cv2.INTER_LANCZOS4)
A = f"reel/assets/{name}/"; os.makedirs(A, exist_ok=True)
rig = {"K": K.tolist(), "rx": rx.tolist(), "ry": ry.tolist(), "rz": rz.tolist(), "O": O.tolist(), "doors": {}}
opening = None
for n, (i, j, side, ang) in C["doors"].items():
    q = quad(i, j)                              # TL TR BR BL
    P = [back(*p) for p in q]
    if side == "L":                             # hinge must be P[1]: mirror the order
        q = [q[1], q[0], q[3], q[2]]; P = [P[1], P[0], P[3], P[2]]
    wW = np.linalg.norm(P[1] - P[0]); hW = (np.linalg.norm(P[3] - P[0]) + np.linalg.norm(P[2] - P[1])) / 2
    tw = 300; th = int(round(tw * hW / wW))
    fr = rect(closed, q, tw, th)
    cv2.imwrite(A + f"door_{n}_front.png", fr)
    bk = cv2.convertScaleAbs(cv2.flip(fr, 1), alpha=0.86)  # inner face: same finish, in the cabinet's shade
    cv2.imwrite(A + f"door_{n}_back.png", bk)
    rig["doors"][n] = {"P": [p.tolist() for p in P], "tw": tw, "th": th, "open": ang, "T": round(0.032 * wW, 2),
                       "q": [list(map(float, p)) for p in q]}
    print(n, side, "q", np.round(q, 1).tolist(), "w", round(wW, 1), "h", round(hW, 1))
# interior: the real open photo (fitted), shown inside the union of the moving doors' openings
m = np.zeros((H, W), np.uint8)
for n, d in rig["doors"].items(): cv2.fillConvexPoly(m, np.int32(np.round(d["q"])), 255)
lay = np.dstack([openw, m]); cv2.imwrite(A + "interior.png", lay)
cv2.imwrite(A + "closed.png", closed); cv2.imwrite(A + "open_fit.png", openw); cv2.imwrite(A + "open.png", openi)
if C["H"]: rig["Hopen"] = Hm.tolist()
json.dump(rig, open(A + "rig.json", "w"))
print("rx", np.round(rx, 3), "ry", np.round(ry, 3), "rz", np.round(rz, 3))
