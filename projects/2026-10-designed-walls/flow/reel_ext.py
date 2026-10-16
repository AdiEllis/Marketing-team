"""Set extension for whole-wall framing at 9:16 (R8: surroundings only; carpentry pixels untouched).
dark: ceiling rebuilt above the slat top (rows < 256 src) as a smooth per-column gradient (the ceiling lamp, cut at the
photo's top edge and burnt out, goes with it), +440 rows of that ceiling above, +130 rows of plain floor below
(stretch of the last 60 floor rows).  white: +300 rows of plain ceiling above (stretch of the top 40 ceiling rows)."""
import cv2, numpy as np
rng = np.random.default_rng(7)
def ceiling(im, k, cut, extra):
    h, w = im.shape[:2]; f = im.astype(np.float32)
    a = f[200 * k:255 * k].mean(0); b = f[150 * k:175 * k].mean(0)          # per-column colour at two heights
    a = cv2.GaussianBlur(a[None], (0, 0), 60 * k)[0]; b = cv2.GaussianBlur(b[None], (0, 0), 60 * k)[0]
    slope = np.clip((a - b) / (65 * k), -0.04, 0.04)                        # per source px
    ys = np.arange(-extra * k, cut * k, dtype=np.float32)[:, None, None]
    y0 = 227 * k
    c = a[None] + (ys - y0) * slope[None] * 0.5
    c += rng.normal(0, 1.2, c.shape).astype(np.float32)
    out = np.vstack([c, f[cut * k:]])
    bl = 24 * k; s = extra * k + cut * k                                   # blend the seam into the real ceiling
    for i in range(bl):
        t = i / bl; out[s - bl + i] = (1 - t) * out[s - bl + i] + t * f[cut * k - bl + i]
    return np.clip(out, 0, 255).astype(np.uint8)
def floor(im, k, extra):
    f = cv2.resize(im[-60 * k:], (im.shape[1], (60 + extra) * k), interpolation=cv2.INTER_CUBIC)
    return np.vstack([im[:-60 * k], f])
d = cv2.imread("reel/assets/dark.png")
d = floor(ceiling(d, 2, 256, 440), 2, 130); cv2.imwrite("reel/assets/dark_ext.png", d); print("dark_ext", d.shape)
bd = cv2.imread("reel/assets/dark_bloom.jpg"); bd[:256] = 0
bd = np.vstack([np.zeros((440, bd.shape[1], 3), np.uint8), bd, np.zeros((130, bd.shape[1], 3), np.uint8)])
cv2.imwrite("reel/assets/dark_ext_bloom.jpg", bd)
for f, k in [("white.png", 2), ("white_bloom.jpg", 1)]:
    im = cv2.imread(f"reel/assets/{f}")
    top = cv2.resize(im[:40 * k], (im.shape[1], 340 * k), interpolation=cv2.INTER_CUBIC)
    if f.endswith(".jpg"): top[:] = 0
    cv2.imwrite(f"reel/assets/{f.replace('white', 'white_ext')}", np.vstack([top, im[40 * k:]]))
print("white_ext", cv2.imread("reel/assets/white_ext.png").shape)
