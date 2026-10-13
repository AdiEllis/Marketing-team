# Remove the construction-dust smudge on the tile floor of the TV-wall photo (hq px), floor only.
import cv2, numpy as np
p = 'work/hq/04_tv_wall_front.png'
im = cv2.imread(p); x0, y0, x1, y1 = 1500, 2630, 1680, 2810
roi = im[y0:y1, x0:x1].astype(np.float32)
g = cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32)
bgd = cv2.medianBlur(im[y0:y1, x0:x1], 31)
diff = np.abs(roi - bgd.astype(np.float32)).sum(2)
m = (diff > 18).astype(np.uint8) * 255
m = cv2.dilate(m, np.ones((9, 9), np.uint8))
full = np.zeros(im.shape[:2], np.uint8); full[y0:y1, x0:x1] = m
full = cv2.dilate(full, np.ones((15, 15), np.uint8))   # whole smudge incl. its dark specks; no grout in this box
fill = cv2.inpaint(im, full, 15, cv2.INPAINT_NS)
# tile texture back (low-amplitude noise sampled from clean floor next to it), feathered edge
rng = np.random.default_rng(3); tex = rng.normal(0, 2.2, (y1 - y0, x1 - x0, 1)).astype(np.float32)
a = cv2.GaussianBlur(full.astype(np.float32) / 255, (0, 0), 4)[..., None]
f = fill.astype(np.float32); f[y0:y1, x0:x1] += tex
out = np.clip(im * (1 - a) + f * a, 0, 255).astype(np.uint8)
cv2.imwrite(p, out); cv2.imwrite('work/smudge.png', cv2.resize(np.hstack([im[y0-60:y1+60, x0-60:x1+60], out[y0-60:y1+60, x0-60:x1+60]]), None, fx=2, fy=2))
