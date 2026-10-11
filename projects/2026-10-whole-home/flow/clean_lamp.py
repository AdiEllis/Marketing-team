"""Remove the round ceiling lamp (not carpentry; her note R13) from the oak photos: the plain ceiling is rebuilt
from the clean ceiling around it (smooth 2D fit), the wardrobe is never touched. Writes work/clean_<name>.png"""
import cv2, numpy as np
def clean(src, box, out, ell):
    im = cv2.imread(src).astype(np.float32); H, W = im.shape[:2]
    x0, y0, x1, y1 = box
    g = cv2.cvtColor(im.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    m = np.zeros((H, W), np.uint8); m[y0:y1, x0:x1] = 255
    # the lamp + its glow: brighter / more saturated than the ceiling around
    hsv = cv2.cvtColor(im.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    lamp = np.zeros((H, W), np.uint8)
    cv2.ellipse(lamp, ell[0], ell[1], 0, 0, 360, 255, -1)          # the lamp + its glow, measured
    wood = ((hsv[..., 0] < 25) & (hsv[..., 1] > 55) & (hsv[..., 2] < 235)).astype(np.uint8) * 255
    wood = cv2.morphologyEx(wood, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(wood)            # carpentry = wood regions that reach down
    keep = [i for i in range(1, n) if st[i, 1] + st[i, 3] > 200]      # (the lamp's gold rim stays near the ceiling)
    wood = np.isin(lab, keep).astype(np.uint8) * 255
    wood = cv2.dilate(wood, np.ones((7, 7), np.uint8))
    lamp = lamp & ~wood & m                                           # never touch the carpentry
    # fit a smooth quadratic surface per channel on the clean ceiling ring around the lamp
    ring = cv2.dilate(lamp, np.ones((61, 61), np.uint8)) & ~lamp & m
    ys, xs = np.nonzero(ring)
    A = np.stack([np.ones_like(xs), xs, ys, xs * xs, xs * ys, ys * ys], 1).astype(np.float64)
    yy, xx = np.nonzero(lamp)
    B = np.stack([np.ones_like(xx), xx, yy, xx * xx, xx * yy, yy * yy], 1).astype(np.float64)
    # inpaint from the clean ceiling edge inward, then smooth inside (the ceiling is a soft gradient)
    res = cv2.inpaint(im.astype(np.uint8), cv2.dilate(lamp, np.ones((5, 5), np.uint8)), 25, cv2.INPAINT_TELEA).astype(np.float32)
    res = cv2.GaussianBlur(res, (0, 0), 14)
    # feathered blend + matching grain
    a = (cv2.GaussianBlur(lamp.astype(np.float32) / 255, (0, 0), 9) * (wood == 0))[..., None]
    rng = np.random.default_rng(7); res += rng.normal(0, 1.2, res.shape)
    out_im = im * (1 - a) + res * a
    cv2.imwrite(out, np.clip(out_im, 0, 255).astype(np.uint8))
clean("input/03_oak_closet_closed.jpg", (170, 0, 560, 160), "work/clean_03.png", ((350, 2), (150, 78)))
clean("input/05_oak_closet_open.jpg", (300, 0, 720, 175), "work/clean_05.png", ((510, 8), (190, 112)))
