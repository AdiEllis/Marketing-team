"""Remove the round ceiling lamp (not carpentry; her note R13) from the oak photos: the plain ceiling is rebuilt
from the clean ceiling around it (smooth 2D fit), the wardrobe is never touched. Ported from projects/2026-10-whole-home/flow/clean_lamp.py to the AI x2 copies here: every measured pixel
value scales by S = 1.217 (her new 1122 frame) x 2 (AI x2). Writes work/prep/<name>.png (P17: only the carpentry)."""
import cv2, numpy as np
S = 1.217 * 2
K = lambda n: int(round(n * S)) | 1   # odd kernel sizes
def clean(src, box, out, ell):
    im = cv2.imread(src).astype(np.float32); H, W = im.shape[:2]
    x0, y0, x1, y1 = [int(v * S) for v in box]
    g = cv2.cvtColor(im.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    m = np.zeros((H, W), np.uint8); m[y0:y1, x0:x1] = 255
    # the lamp + its glow: brighter / more saturated than the ceiling around
    hsv = cv2.cvtColor(im.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    lamp = np.zeros((H, W), np.uint8)
    cv2.ellipse(lamp, tuple(int(v * S) for v in ell[0]), tuple(int(v * S) for v in ell[1]), 0, 0, 360, 255, -1)          # the lamp + its glow, measured
    wood = ((hsv[..., 0] < 25) & (hsv[..., 1] > 55) & (hsv[..., 2] < 235)).astype(np.uint8) * 255
    wood = cv2.morphologyEx(wood, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(wood)            # carpentry = wood regions that reach down
    keep = [i for i in range(1, n) if st[i, 1] + st[i, 3] > 200 * S]      # (the lamp's gold rim stays near the ceiling)
    wood = np.isin(lab, keep).astype(np.uint8) * 255
    wood = cv2.dilate(wood, np.ones((K(7), K(7)), np.uint8))
    lamp = lamp & ~wood & m                                           # never touch the carpentry
    # fit a smooth quadratic surface per channel on the clean ceiling ring around the lamp
    ring = cv2.dilate(lamp, np.ones((K(61), K(61)), np.uint8)) & ~lamp & m
    ys, xs = np.nonzero(ring)
    A = np.stack([np.ones_like(xs), xs, ys, xs * xs, xs * ys, ys * ys], 1).astype(np.float64)
    yy, xx = np.nonzero(lamp)
    B = np.stack([np.ones_like(xx), xx, yy, xx * xx, xx * yy, yy * yy], 1).astype(np.float64)
    # inpaint from the clean ceiling edge inward, then smooth inside (the ceiling is a soft gradient)
    res = cv2.inpaint(im.astype(np.uint8), cv2.dilate(lamp, np.ones((K(5), K(5)), np.uint8)), int(25 * S), cv2.INPAINT_TELEA).astype(np.float32)
    res = cv2.GaussianBlur(res, (0, 0), 14 * S)
    # feathered blend + matching grain
    a = (cv2.GaussianBlur(lamp.astype(np.float32) / 255, (0, 0), 9 * S) * (wood == 0))[..., None]
    rng = np.random.default_rng(7); res += rng.normal(0, 1.2, res.shape)
    out_im = im * (1 - a) + res * a
    cv2.imwrite(out, np.clip(out_im, 0, 255).astype(np.uint8))
clean("work/hq/03_oak_closet_closed.png", (170, 0, 560, 160), "work/prep/03_oak_closet_closed.png", ((350, 2), (150, 78)))
clean("work/hq/05_oak_closet_open.png", (300, 0, 720, 175), "work/prep/05_oak_closet_open.png", ((510, 8), (190, 112)))
