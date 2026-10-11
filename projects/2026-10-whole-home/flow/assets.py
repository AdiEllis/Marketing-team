"""Reel stills as PNG (no re-encode loss) + bloom layers from each photo's REAL bright pixels."""
import cv2, numpy as np
A = "reel/assets/"
for src, dst in (("02_mauve_closet_round_handles", "mauve"), ("06_grey_closet_round_handle", "grey"), ("01_tv_wall_lit", "tv")):
    cv2.imwrite(A + dst + ".png", cv2.imread(f"input/{src}.jpg"))
def bloom(img, out, thr=200, warm=True, sig=22):
    f = img.astype(np.float32); lum = f.mean(2)
    m = np.clip((lum - thr) / (255 - thr), 0, 1)
    if warm: m *= np.clip((f[..., 2] - f[..., 0]) / 60.0, 0, 1)      # only the warm LED light, not white walls
    b = cv2.GaussianBlur(f * m[..., None], (0, 0), sig) * 1.6
    cv2.imwrite(out, np.clip(b, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
bloom(cv2.imread("input/01_tv_wall_lit.jpg"), A + "tv_bloom.jpg", thr=150)
