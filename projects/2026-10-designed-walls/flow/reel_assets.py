"""Reel assets: AI x4 -> area-downscale to x2 (lossless PNG, natural colours; stages keep source-px coordinates)
+ bloom of each photo's own brightest pixels (neutral, no orange tint: R5)."""
import cv2, numpy as np
for n in ["dark", "panels", "slats", "white"]:
    src = cv2.imread(f"work/prep/{n}_s.png"); h, w = src.shape[:2]
    im = cv2.resize(cv2.imread(f"work/ai/{n}_x4.png"), (w * 2, h * 2), interpolation=cv2.INTER_AREA)
    cv2.imwrite(f"reel/assets/{n}.png", im)
    lum = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY).astype(np.float32)
    thr = np.percentile(lum, 98)
    m = np.clip((lum - thr) / (255 - thr + 1e-3), 0, 1)[..., None]
    b = src.astype(np.float32) * m
    b = 0.6 * cv2.GaussianBlur(b, (0, 0), 5) + 0.7 * cv2.GaussianBlur(b, (0, 0), 18)
    cv2.imwrite(f"reel/assets/{n}_bloom.jpg", np.clip(b * 1.2, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(n, (w, h))

# white wall: +200 source rows of plain ceiling above (vertical stretch of the top 40 ceiling rows; environment only,
# the carpentry pixels are untouched) so the last card sits on ceiling, not on the slat band (R8 scope: surroundings).
for f, k in [("white.png", 2), ("white_bloom.jpg", 1)]:
    im = cv2.imread(f"reel/assets/{f}")
    top = cv2.resize(im[:40 * k], (im.shape[1], 240 * k), interpolation=cv2.INTER_CUBIC)
    if f.endswith(".jpg"): top[:] = 0
    cv2.imwrite(f"reel/assets/{f.replace('white', 'white_ext')}", np.vstack([top, im[40 * k:]]))
