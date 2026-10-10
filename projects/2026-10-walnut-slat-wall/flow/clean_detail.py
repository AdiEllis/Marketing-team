"""detail.png: remove the old watermark with a smooth (harmonic) fill + matched grain, then re-join the ONE real grout
line that runs under it (the -22deg line through (347,1314)-(418,1285)), drawn only inside the patch."""
import cv2, numpy as np
img = cv2.imread("input/detail.png"); f = img.astype(np.float32); H, W = img.shape[:2]
logo = cv2.imread("../../studio/assets/logo_alpha.png", cv2.IMREAD_UNCHANGED)
x, y, w, h = 44, 1249, 147, 215
a = np.zeros((H, W), np.float32); a[y:y + h, x:x + w] = cv2.resize(logo[..., 3] / 255.0, (w, h), interpolation=cv2.INTER_AREA)[:H - y]
m = cv2.dilate((a > 0.04).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
ys, xs = np.where(m); y0, y1, x0, x1 = ys.min() - 3, min(ys.max() + 4, H), xs.min() - 3, xs.max() + 4
sub = f[y0:y1, x0:x1].copy(); mm = m[y0:y1, x0:x1]
ring = cv2.dilate(mm.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~mm
sub[mm] = sub[ring].mean(0)
k = np.array([[0, .25, 0], [.25, 0, .25], [0, .25, 0]], np.float32)
for _ in range(3000):
    sm = cv2.filter2D(sub, -1, k, borderType=cv2.BORDER_REPLICATE); sub[mm] = sm[mm]
out = f.copy(); out[y0:y1, x0:x1] = sub
# grain matched to the surrounding floor
ref = f[1300:1460, 220:330]; sd = float((ref - cv2.GaussianBlur(ref, (0, 0), 2.5)).std())
rng = np.random.default_rng(4); n = rng.normal(0, 1, (H, W)).astype(np.float32); n = n - cv2.GaussianBlur(n, (0, 0), 2.5); n *= sd / (n.std() + 1e-6)
out[m] += n[m][:, None]
# re-join the real grout line
g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
(x1l, y1l), (x2l, y2l) = (347, 1314), (418, 1285)
d = np.array([x2l - x1l, y2l - y1l], np.float32); d /= np.linalg.norm(d); nrm = np.array([-d[1], d[0]])
depths = []
for t in np.linspace(0, 1, 30):
    px, py = x1l + (x2l - x1l) * t, y1l + (y2l - y1l) * t
    c = g[int(round(py)), int(round(px))]
    side = (g[int(round(py + 4 * nrm[1])), int(round(px + 4 * nrm[0]))] + g[int(round(py - 4 * nrm[1])), int(round(px - 4 * nrm[0]))]) / 2
    depths.append(side - c)
depth = float(np.clip(np.median(depths), 3, 25))
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dist = (xx - x1l) * nrm[0] + (yy - y1l) * nrm[1]
sel = cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & (np.abs(dist) < 5)
prof = np.exp(-(dist ** 2) / (2 * 1.1 ** 2))
out[sel] *= (1 - (depth / 170.0) * prof[sel])[:, None]
fe = cv2.GaussianBlur(cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 2.5)[..., None]
res = np.clip(out * fe + f * (1 - fe), 0, 255).astype(np.uint8)
cv2.imwrite("work/detail_clean.png", res)
print("grout depth", round(depth, 1))
S = "/tmp/claude-0/-home-user-Marketing-team/7f9a15bc-27ce-5d25-99d6-2dc96cdb74ce/scratchpad/walnut"
cv2.imwrite(S + "/dclean2.jpg", cv2.resize(np.hstack([img[1150:1473, 0:450], res[1150:1473, 0:450]]), None, fx=1.6, fy=1.6))
