"""Export the door rig assets for the reel: rectified real door faces (closed photo), inner faces (open photo),
the real interior fitted into the openings (RGBA layer in closed-photo geometry), the drawer front, and rig.json."""
import sys, json, numpy as np, cv2
sys.path.insert(0, "flow")
from doors_geom import *
closed = cv2.imread("reel/assets/closed.png"); openi = cv2.imread("work/open_g.png")
A = "reel/assets/"
def rect(src, quad, w, h):
    return cv2.warpPerspective(src, cv2.getPerspectiveTransform(np.float32(quad), np.float32([(0, 0), (w, 0), (w, h), (0, h)])), (w, h), flags=cv2.INTER_LANCZOS4)
BACKQ = {"upper": [(268, 158), (375, 83), (375, 276), (268, 326)], "ward": [(557, 273), (666, 233), (666, 1107), (557, 1071)]}
rig = {"K": K.tolist(), "rx": rx.tolist(), "ry": ry.tolist(), "rz": rz.tolist(), "O": O.tolist(), "doors": {}}
for n, d in DOORS.items():
    P = door_world(n)
    wW = np.linalg.norm(P[1] - P[0]); hW = (np.linalg.norm(P[3] - P[0]) + np.linalg.norm(P[2] - P[1])) / 2
    tw = 400 if n == "upper" else 260; th = int(round(tw * hW / wW))
    cv2.imwrite(A + f"door_{n}_front.png", rect(closed, d["quad"], tw, th))
    cv2.imwrite(A + f"door_{n}_back.png", rect(openi, BACKQ[n], tw, th))
    rig["doors"][n] = {"P": [p.tolist() for p in P], "tw": tw, "th": th, "open": d["open"]}
# interior layers (one per door): the real interior fitted into each opening, shown only while that door is open
H_, W_ = closed.shape[:2]
for n, d in DOORS.items():
    lay = np.zeros((H_, W_, 4), np.uint8)
    Hm = cv2.getPerspectiveTransform(np.float32(INTERIOR[n]), np.float32(d["quad"]))
    w = cv2.warpPerspective(openi, Hm, (W_, H_), flags=cv2.INTER_LANCZOS4)
    m = np.zeros((H_, W_), np.uint8); cv2.fillConvexPoly(m, np.int32(np.round(d["quad"])), 255)
    lay[m > 0, :3] = w[m > 0]; lay[..., 3] = m
    cv2.imwrite(A + f"interior_{n}.png", lay)
# drawer
Pd = [back(*p) for p in DRAWER["quad"]]
dw = np.linalg.norm(Pd[1] - Pd[0]); dh = np.linalg.norm(Pd[3] - Pd[0])
tw = 400; th = int(round(tw * dh / dw))
cv2.imwrite(A + "drawer_front.png", rect(closed, DRAWER["quad"], tw, th))
rig["drawer"] = {"P": [p.tolist() for p in Pd], "tw": tw, "th": th, "pull": 0.62 * dw}
# the real open drawer: its dark open top (seen from above) and its left side, from the open photo
cv2.imwrite(A + "drawer_top.png", rect(openi, [(6, 958), (300, 931), (350, 941), (57, 986)], 400, 120))
cv2.imwrite(A + "drawer_side.png", rect(openi, [(8, 960), (57, 986), (57, 1110), (10, 1082)], 60, 160))
json.dump(rig, open(A + "rig.json", "w"))
print(json.dumps({k: (v if k != "doors" else {n: {kk: vv for kk, vv in dd.items() if kk != "P"} for n, dd in v.items()}) for k, v in rig.items() if k in ("doors", "drawer")}, default=str)[:400])
