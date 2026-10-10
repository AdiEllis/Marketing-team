import sys, json, numpy as np, cv2
sys.path.insert(0, "flow")
from doors_geom import *
closed = cv2.imread("work/closed_g.png") if False else cv2.imread("reel/assets/closed.png")
openi = cv2.imread("work/open_g.png")
S = "/tmp/claude-0/-home-user-Marketing-team/7f9a15bc-27ce-5d25-99d6-2dc96cdb74ce/scratchpad/walnut"

def warp_quad(src, src_quad, dst_quad, canvas, alpha=1.0, mask_extra=None):
    Hm = cv2.getPerspectiveTransform(np.float32(src_quad), np.float32(dst_quad))
    w = cv2.warpPerspective(src, Hm, (canvas.shape[1], canvas.shape[0]), flags=cv2.INTER_LINEAR)
    m = np.zeros(canvas.shape[:2], np.uint8); cv2.fillConvexPoly(m, np.int32(np.round(dst_quad)), 255)
    m = cv2.GaussianBlur(m, (3, 3), 0).astype(np.float32)[..., None] / 255 * alpha
    return (w * m + canvas * (1 - m)).astype(np.uint8)

def tex_rect(src, quad, w, h):
    return cv2.warpPerspective(src, cv2.getPerspectiveTransform(np.float32(quad), np.float32([(0, 0), (w, 0), (w, h), (0, h)])), (w, h))

TEX = {}
for n, d in DOORS.items():
    q = d["quad"]
    TEX[n + "_front"] = tex_rect(closed, q, 300, int(300 * np.linalg.norm(np.subtract(back(*q[3]), back(*q[0]))) / np.linalg.norm(np.subtract(back(*q[1]), back(*q[0])))))
BACKQ = {"upper": [(268, 158), (375, 83), (375, 276), (268, 326)],   # hinge-top, free-top, free-bottom, hinge-bottom (open photo)
         "ward": [(553, 232), (665, 232), (665, 1108), (553, 1095)]}
for n in DOORS:
    h = TEX[n + "_front"].shape[0]
    TEX[n + "_back"] = tex_rect(openi, BACKQ[n], 300, h)

def render(phis, pull):
    img = closed.copy()
    # interiors (real open-photo interior fitted into the openings), in shadow while the door is closed
    for n, d in DOORS.items():
        if phis[n] > 0.001:
            img = warp_quad(openi, INTERIOR[n], d["quad"], img)
            shade = max(0.0, 0.55 * (1 - min(1, phis[n] / np.radians(70))))
            m = np.zeros(img.shape[:2], np.float32); cv2.fillConvexPoly(m, np.int32(d["quad"]), 1.0)
            img = (img * (1 - shade * m[..., None])).astype(np.uint8)
    for n, d in DOORS.items():
        P = door_world(n); hingeX = P[1][0]
        Pr = rotate(P, hingeX, phis[n])
        pts = [proj(p) for p in Pr]          # TL, TR(hinge), BR(hinge), BL (front naming)
        front_visible = phis[n] < np.pi / 2
        if front_visible:
            t = TEX[n + "_front"]; dst = pts
            src = [(0, 0), (t.shape[1], 0), (t.shape[1], t.shape[0]), (0, t.shape[0])]
            br = 1 - 0.18 * np.sin(phis[n])
        else:
            t = TEX[n + "_back"]; dst = [pts[1], pts[0], pts[3], pts[2]]   # hinge-top, free-top, free-bottom, hinge-bottom
            src = [(0, 0), (t.shape[1], 0), (t.shape[1], t.shape[0]), (0, t.shape[0])]
            br = 1.0
        tt = np.clip(t.astype(np.float32) * br, 0, 255).astype(np.uint8)
        img = warp_quad(tt, src, dst, img)
    return img

frames = []
for k, a in enumerate([0, 30, 70, 110, 150, 172]):
    phis = {"upper": np.radians(min(a, 150)), "ward": np.radians(a)}
    fr = render(phis, 0)
    frames.append(cv2.resize(fr[0:1300, 0:760], (380, 650)))
cv2.imwrite(S + "/doors_preview.jpg", np.hstack(frames))
