"""Reel assets: graded photos (lossless PNG) + bloom layers (bright real pixels only, blurred) for light moves.
Run from the project dir after flow/clean_logo.py, align.py (warm->day) and grade.py."""
import cv2, numpy as np, subprocess
T = "../../studio/tools"
subprocess.run(["python3", "-I", f"{T}/grade.py", "work/warm_al.png", "work/warm_al_g.png", "--strength", "0.3"], check=True)
for src, dst in [("work/front_g.png", "front"), ("work/day_g.png", "day"), ("work/warm_al_g.png", "warm"), ("work/detail_g.png", "detail")]:
    im = cv2.imread(src); cv2.imwrite(f"reel/assets/{dst}.png", im)
    lum = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    thr = np.percentile(lum, 97)
    w = np.clip((lum - thr) / (255 - thr + 1e-3), 0, 1)[..., None]
    b = im.astype(np.float32) * w
    b = 0.6 * cv2.GaussianBlur(b, (0, 0), 6) + 0.8 * cv2.GaussianBlur(b, (0, 0), 22)
    b = b * np.array([0.78, 0.92, 1.12])          # warm tint (BGR)
    cv2.imwrite(f"reel/assets/{dst}_bloom.jpg", np.clip(b * 1.4, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(dst, im.shape)
