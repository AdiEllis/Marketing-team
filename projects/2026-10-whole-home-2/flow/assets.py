"""Reel stills as PNG (sharpest copy: work/hq = AI x2 when ready, else work/clean) + TV bloom from its REAL lit pixels.
Stages are laid out in 1122x1402 photo units (mauve 949x1402); the hq files are drawn at that size (x2 density)."""
import cv2, numpy as np, os
A = "reel/assets/"
def src(n): return cv2.imread(f"work/hq/{n}.png") if os.path.exists(f"work/hq/{n}.png") else cv2.imread(f"work/clean/{n}.png")
for n, d in (("01_tv_wall_lit", "tv"), ("02_mauve_closet", "mauve"), ("06_grey_closet", "grey"), ("03_oak_closet_closed", "oak")):
    cv2.imwrite(A + d + ".png", src(n))
tv = src("01_tv_wall_lit").astype(np.float32); lum = tv.mean(2)
m = np.clip((lum - 150) / 105, 0, 1) * np.clip((tv[..., 2] - tv[..., 0]) / 60.0, 0, 1)   # warm LED light only
sig = 22 * tv.shape[1] / 1122
b = cv2.GaussianBlur(tv * m[..., None], (0, 0), sig) * 1.4
cv2.imwrite(A + "tv_bloom.jpg", np.clip(b, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
print("assets ok", tv.shape)
