"""Remove the OLD Even & Etz watermark (the brand logo stamped on her Instagram screenshots) from a photo.

Usage:
  python3 -I studio/tools/unwatermark.py IN OUT [--region x0,y0,x1,y1] [--tex-dx 230] [--tex-dy 0]

1. exact mask: multi-scale template match of studio/assets/logo_alpha.png (the same logo) in the region
   (default: bottom-left quarter); prints the match score (expect > 0.9; lower = check by eye).
2. fill = low frequencies from a harmonic fill (tone, light falloff) + high frequencies (grain, marble veins)
   copied from the real surface beside the logo (tex-dx/dy), feathered 1.5px.
Works on floors/plain surfaces. If the logo sits on joinery, a light fixture or a pattern (grout lines, wood grain
seams), check at 200% — and if it is not flawless, ask her for the original instead (agents/post-designer.md v6).
"""
import argparse
import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--region", default="")
ap.add_argument("--tex-dx", type=int, default=230)
ap.add_argument("--tex-dy", type=int, default=0)
a = ap.parse_args()
import os
here = os.path.dirname(os.path.abspath(__file__))
logo = cv2.imread(os.path.join(here, "..", "assets", "logo_alpha.png"), cv2.IMREAD_UNCHANGED)
LA = logo[..., 3].astype(np.float32) / 255.0
LR = logo[..., :3].astype(np.float32)
img = cv2.imread(a.src)
H, W = img.shape[:2]
x0, y0, x1, y1 = [int(v) for v in a.region.split(",")] if a.region else (0, H // 2, W // 2, H)
g = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32)
best = (-1, None)
for sc in np.arange(0.10, 0.45, 0.005):
    w, h = int(536 * sc), int(784 * sc)
    if h >= g.shape[0] or w >= g.shape[1]:
        continue
    al = cv2.resize(LA, (w, h), interpolation=cv2.INTER_AREA)
    lg = cv2.cvtColor(cv2.resize(LR, (w, h), interpolation=cv2.INTER_AREA).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    r = cv2.matchTemplate(g, lg * al + 128 * (1 - al), cv2.TM_CCOEFF_NORMED, mask=(al > 0.05).astype(np.float32))
    _, mv, _, ml = cv2.minMaxLoc(np.nan_to_num(r, nan=-1))
    if mv > best[0]:
        best = (mv, (ml[0] + x0, ml[1] + y0, w, h))
score, (x, y, w, h) = best
alpha = np.zeros((H, W), np.float32)
ah = cv2.resize(LA, (w, h), interpolation=cv2.INTER_AREA)
hh = min(h, H - y); alpha[y:y + hh, x:x + w] = ah[:hh]
m = cv2.dilate((alpha > 0.04).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
f = img.astype(np.float32)
ys, xs = np.where(m)
by0, by1, bx0, bx1 = max(ys.min() - 3, 0), min(ys.max() + 4, H), max(xs.min() - 3, 0), min(xs.max() + 4, W)
sub = f[by0:by1, bx0:bx1].copy(); mm = m[by0:by1, bx0:bx1]
ring = cv2.dilate(mm.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~mm
sub[mm] = sub[ring].mean(0)
k = np.array([[0, .25, 0], [.25, 0, .25], [0, .25, 0]], np.float32)
for _ in range(2500):
    sm = cv2.filter2D(sub, -1, k, borderType=cv2.BORDER_REPLICATE); sub[mm] = sm[mm]
lf = f.copy(); lf[by0:by1, bx0:bx1] = sub
tex = cv2.warpAffine(f, np.float32([[1, 0, -a.tex_dx], [0, 1, -a.tex_dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
filled = lf + (tex - cv2.GaussianBlur(tex, (0, 0), 6))
fe = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5)[..., None]
cv2.imwrite(a.out, np.clip(filled * fe + f * (1 - fe), 0, 255).astype(np.uint8))
print(f"watermark match {score:.3f} at x={x} y={y} w={w} h={h}" + ("" if score > 0.9 else "  <-- LOW: check by eye"))
