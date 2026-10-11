"""Leafless interior plate for the oak rig (closed-photo geometry): the real open photo (fitted), with the real open
leaves removed INSIDE the opening by continuing the neighbouring interior (shelves are horizontal) — the rig's own doors
end exactly over those strips, so the patches are seen only behind a moving door. No hand-over to another photo."""
import json, cv2, numpy as np
A = "reel/assets/oak/"
o = cv2.imread(A + "open_fit.png"); R = json.load(open(A + "rig.json")); H, W = o.shape[:2]
out = o.copy()
def fill(x0, x1, src_x, w=6):
    """columns x0..x1 <- the neighbouring interior block, shifted along the shelves' real slope (dy chosen so the
    copied block's shelf lines meet the original ones at the seam)"""
    n = x1 - x0; right = src_x >= x1                      # source block lies right (or left) of the hole
    sx0 = x1 + (src_x - x1) if right else src_x - n + w
    sx0 = src_x if right else src_x + w - n
    g = cv2.cvtColor(o, cv2.COLOR_BGR2GRAY).astype(np.float32)
    seam = g[:, x1 if right else x0 - 1]
    best = None
    for dy in range(-30, 31):
        blk = np.roll(g[:, sx0:sx0 + n], dy, 0)
        edge = blk[:, -1] if right else blk[:, 0]
        e = np.abs(np.convolve(edge - seam, np.ones(5) / 5, "same"))[200:900].mean()
        if best is None or e < best[0]: best = (e, dy)
    blk = np.roll(o[:, sx0:sx0 + n], best[1], 0)
    out[:, x0:x1] = blk
    print("fill", x0, x1, "from", sx0, "dy", best[1], "err", round(best[0], 1))
# behind leaf A: the compartment's plain inner side wall (seen from the right), lit like the interior beside it
col = np.median(o[:, 203:208].astype(np.float32), 1)                  # the real side wall's edge, per row
col = np.stack([cv2.medianBlur(np.clip(col[:, c], 0, 255).astype(np.uint8).reshape(-1, 1), 61)[:, 0] for c in range(3)], 1)
side = cv2.GaussianBlur(col.astype(np.float32).reshape(-1, 1, 3), (1, 0), 0, sigmaY=12)
out[:, 150:205] = np.clip(np.repeat(side, 55, 1), 0, 255).astype(np.uint8)
print("side wall 150-205")
fill(356, 386, 349)            # behind leaf B, left side: left compartment up to the partition
fill(391, 412, 414)            # behind leaf B, right side: right compartment from the partition
out[:, 386:391] = (196, 199, 201)   # the partition's front edge (carcass light grey, as the shelf fronts)
fill(640, 672, 634)            # behind leaf C: right compartment to its right wall
m = np.zeros((H, W), np.uint8)
for n, d in R["doors"].items(): cv2.fillConvexPoly(m, np.int32(np.round(d["q"])), 255)
cv2.imwrite(A + "interior.png", np.dstack([out, m]))
cv2.imwrite("work/interior_clean_check.png", cv2.resize(out[130:950, 90:720], None, fx=1, fy=1))

# white wardrobe (same camera for closed/open): remove the two real open leaves inside the opening; behind them are
# the plain white inner side walls -> smooth wall tone per row (hinge plates / shelf edges median-filtered away)
A = "reel/assets/white/"
o = cv2.imread(A + "open_fit.png"); R = json.load(open(A + "rig.json")); out = o.copy()
def wall(x0, x1, sx0, sx1):
    col = np.median(o[:, sx0:sx1].astype(np.float32), 1)
    col = np.stack([cv2.medianBlur(np.clip(col[:, c], 0, 255).astype(np.uint8).reshape(-1, 1), 121)[:, 0] for c in range(3)], 1)
    col = cv2.GaussianBlur(col.astype(np.float32).reshape(-1, 1, 3), (1, 0), 0, sigmaY=25)
    out[:, x0:x1] = np.clip(np.repeat(col, x1 - x0, 1), 0, 255).astype(np.uint8)
wall(158, 203, 204, 214)
wall(560, 602, 526, 557)
m = np.zeros(o.shape[:2], np.uint8)
for n, d in R["doors"].items(): cv2.fillConvexPoly(m, np.int32(np.round(d["q"])), 255)
cv2.imwrite(A + "interior.png", np.dstack([out, m]))
cv2.imwrite("work/white_clean_check.png", out[0:1100, 100:700])
