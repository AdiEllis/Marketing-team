"""Re-join the real grout lines that ran under the removed old logo (open photo).
Each line is the straight extension of a real segment detected just outside the patch; it is drawn only
inside the patch, with the measured darkness/width of the real grout next to it."""
import cv2, numpy as np
S = "/tmp/claude-0/-home-user-Marketing-team/7f9a15bc-27ce-5d25-99d6-2dc96cdb74ce/scratchpad/latte"
orig = cv2.imread("../input/angle_open.jpg"); img = cv2.imread("open_clean_v4.png").astype(np.float32)
mask = np.load(f"{S}/floormask.npy").astype(bool)
g = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY).astype(np.float32)
LINES = [((311, 1365), (520, 1231)), ((303, 1230), (364, 1200)), ((247, 1165), (307, 1141)), ((228, 1301), (292, 1347))]
H, W = g.shape
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
area = cv2.dilate(mask.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
for (x1, y1), (x2, y2) in LINES:
    d = np.array([x2 - x1, y2 - y1], np.float32); d /= np.linalg.norm(d); n = np.array([-d[1], d[0]])
    dist = (xx - x1) * n[0] + (yy - y1) * n[1]
    # measure the real grout profile on the known segment: depth relative to the tile 4 px either side
    t = np.linspace(0, 1, 40)
    depths = []
    for tt in t:
        px, py = x1 + (x2 - x1) * tt, y1 + (y2 - y1) * tt
        c = g[int(round(py)), int(round(px))]
        side = (g[int(round(py + 4 * n[1])), int(round(px + 4 * n[0]))] + g[int(round(py - 4 * n[1])), int(round(px - 4 * n[0]))]) / 2
        depths.append(side - c)
    depth = float(np.clip(np.median(depths), 4, 30))
    prof = np.exp(-(dist ** 2) / (2 * 1.1 ** 2))
    sel = area & (np.abs(dist) < 5)
    ratio = (1 - depth / 160.0)                       # multiplicative darkening keeps the tile's tone
    k = 1 - (1 - ratio) * prof[sel]
    img[sel] *= k[:, None]
    print("line", (x1, y1), (x2, y2), "depth", round(depth, 1))
out = np.clip(img, 0, 255).astype(np.uint8)
cv2.imwrite("open_clean_v5.png", out)
a = orig[1100:1469, 60:460]; b = out[1100:1469, 60:460]
cv2.imwrite(f"{S}/floor2.png", np.vstack([cv2.resize(a, None, fx=1.6, fy=1.6), cv2.resize(b, None, fx=1.6, fy=1.6)]))
