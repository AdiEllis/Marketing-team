"""Reel assets: graded photos (lossless PNG) + bloom layers (the photo's own brightest pixels, blurred) for light moves.
Run from the project dir after flow/clean.py and grade.py (work/*_g.png)."""
import cv2, numpy as np, shutil
for n in ["panels", "slats", "white", "dark"]:
    im = cv2.imread(f"work/{n}_g.png"); cv2.imwrite(f"reel/assets/{n}.png", im)
    lum = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    thr = np.percentile(lum, 97)
    w = np.clip((lum - thr) / (255 - thr + 1e-3), 0, 1)[..., None]
    b = im.astype(np.float32) * w
    b = 0.6 * cv2.GaussianBlur(b, (0, 0), 6) + 0.8 * cv2.GaussianBlur(b, (0, 0), 22)
    b = b * np.array([0.80, 0.93, 1.10])          # warm tint (BGR)
    cv2.imwrite(f"reel/assets/{n}_bloom.jpg", np.clip(b * 1.4, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(n, im.shape)
for f in ["gsap.min.js", "heebo.ttf", "logo_light.png"]:
    shutil.copy(f"../../studio/assets/{f}", "reel/assets/")
