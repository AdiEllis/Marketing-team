# The mauve wardrobe photo is narrower than 4:5 once her white frame is removed. Extend the plain wall and floor
# sideways (environment only, R8/P5); the wardrobe pixels are untouched. Wall rows continue their own edge colour
# (so the chair-rail and skirting lines run on) with matched fine grain; floor rows (left) repeat the real floor strip at
# the edge (mirrored), its tone pinned to the edge column. Usage: python3 -I flow/extend_mauve.py IN OUT
import sys, cv2, numpy as np
im = cv2.imread(sys.argv[1]).astype(np.float32); h, w = im.shape[:2]; k = w / 949.0
W = int(round(h * 0.8)); pl = (W - w) // 2; pr = W - w - pl
fy = int(1245 * k); n = int(44 * k)                     # floor starts ~y1245; edge strip narrower than the side wall
rng = np.random.default_rng(7)
def ext(edge_strip, col, m):
    out = np.repeat(col, m, axis=1)
    reps = np.concatenate([edge_strip, edge_strip[:, ::-1]] * (m // (2 * n) + 2), 1)[:, :m]
    lo = cv2.GaussianBlur(reps, (0, 0), 6 * k); fl = reps - lo + np.repeat(cv2.GaussianBlur(col, (0, 0), 1, sigmaY=3 * k), m, 1)
    out[fy:] = fl[fy:]
    out[:fy] += rng.normal(0, 1.1, out[:fy].shape[:2])[..., None]
    return out
L = ext(im[:, :n][:, ::-1], im[:, :1], pl)[:, ::-1]
# right: a receding side wall. Its horizontals (chair rail y=695+0.375(x-872), skirting y=1321+1.81(x-904)) meet at
# the vanishing point VP=(476,546); each new pixel takes the colour where its line to VP crosses the photo's last
# column, so the rail and skirting run on straight, in perspective.
vx, vy, xs = 476 * k, 546 * k, w - 6 * k
X, Y = np.meshgrid(np.arange(w, w + pr, dtype=np.float32), np.arange(h, dtype=np.float32))
my = (vy + (Y - vy) * (xs - vx) / (X - vx)).astype(np.float32); mx = np.full_like(my, xs)
Rs = cv2.remap(im, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE) + rng.normal(0, 1.1, (h, pr))[..., None]
out = np.concatenate([L, im, Rs], 1)
cv2.imwrite(sys.argv[2], np.clip(out, 0, 255).astype(np.uint8)); print(out.shape)
