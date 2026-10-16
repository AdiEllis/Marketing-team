"""Post photos (P16/P17): AI x4 -> whole wall, 4:5 crop of empty edges only, area-downscale to 1080x1350 PNG.
Lab shift vs source printed (<1 keeps the natural colours)."""
import cv2, numpy as np
def lab(im): return cv2.cvtColor(im, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(float).mean(0)
# (x0, x1) crop in source px; extra = rows of plain floor mirrored at the bottom (source px)
plan = {"dark": (69, 1109, 90), "panels": (110, 1106, 0), "slats": (89, 977, 0), "white": (8, 926, 0)}
for n, (x0, x1, extra) in plan.items():
    src = cv2.imread(f"work/prep/{n}_s.png"); up = cv2.imread(f"work/ai/{n}_x4.png")
    im = up[:, x0 * 4:x1 * 4]
    if extra:  # plain floor only: stretch the last 60 source rows of floor to 60+extra (no carpentry touched)
        f = cv2.resize(im[-60 * 4:], (im.shape[1], (60 + extra) * 4), interpolation=cv2.INTER_CUBIC)
        im = np.vstack([im[:-60 * 4], f])
    h, w = im.shape[:2]; tw = round(h * 0.8)
    if w > tw: c = (w - tw) // 2; im = im[:, c:c + tw]
    elif w < tw: th = round(w / 0.8); c = (h - th) // 2; im = im[c:c + th]
    out = cv2.resize(im, (1080, 1350), interpolation=cv2.INTER_AREA)
    ref = cv2.resize(src[:, x0:x1], (100, 100)); o = cv2.resize(out, (100, 100))
    print(n, im.shape[:2], "Lab shift", np.round(lab(o) - lab(ref), 2))
    cv2.imwrite(f"carousel/p_{n}.png", out)
