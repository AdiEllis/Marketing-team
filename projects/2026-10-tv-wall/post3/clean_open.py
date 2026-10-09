"""Remove the old logo (on floor tiles) and the mute icon (on a plain door) from the open photo.
Tight masks (mark pixels only), harmonic fill + matched grain, then grout lines re-joined from their
real ends outside the mask. Nothing on the joinery is touched."""
import cv2
import numpy as np

S = "/tmp/claude-0/-home-user-Marketing-team/7f9a15bc-27ce-5d25-99d6-2dc96cdb74ce/scratchpad/latte"
img = cv2.imread("../input/angle_open.jpg")

def harmonic(out, m, iters=4000):
    out = out.astype(np.float32)
    k = np.array([[0, .25, 0], [.25, 0, .25], [0, .25, 0]], np.float32)
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min() - 3, ys.max() + 4, xs.min() - 3, xs.max() + 4
    sub = out[y0:y1, x0:x1].copy(); mm = m[y0:y1, x0:x1]
    # start from the mean of the ring to converge faster
    ring = cv2.dilate(mm.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~mm
    sub[mm] = sub[ring].mean(0)
    for _ in range(iters):
        sm = cv2.filter2D(sub, -1, k, borderType=cv2.BORDER_REPLICATE)
        sub[mm] = sm[mm]
    out[y0:y1, x0:x1] = sub
    return out

def grain_like(out, m, ref_box, seed):
    x0, y0, x1, y1 = ref_box
    ref = img[y0:y1, x0:x1].astype(np.float32)
    hp = ref - cv2.GaussianBlur(ref, (0, 0), 3)
    sd = float(hp.std())
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, out.shape[:2]).astype(np.float32)
    n = n - cv2.GaussianBlur(n, (0, 0), 3)
    n *= sd / (n.std() + 1e-6)
    out[m] += n[m][:, None]
    return out

# --- logo on the floor: letters are dark grey (neutral) or tan; the floor is light neutral grey
x0, y0, x1, y1 = 35, 1195, 300, 1450
r = img[y0:y1, x0:x1].astype(int)
lum = r.mean(2); B, G, R = r[..., 0], r[..., 1], r[..., 2]
floor_lum = np.median(lum)
letters = (lum < floor_lum - 22) | ((R - B) > 28)
m = np.zeros(img.shape[:2], bool)
m[y0:y1, x0:x1] = letters
# keep the real side table out of the mask (it is left of x~68 and above y~1300 in this photo)
m[:, :66] = False
mu = cv2.dilate(m.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
mu[:, :66] = False
cv2.imwrite(f"{S}/open_logo_mask.png", (mu[1150:1469, 0:420] * 255).astype(np.uint8))
out = harmonic(img, mu)
out = grain_like(out, mu, (300, 1250, 420, 1400), 5)

# --- mute icon on the door / floor glow
cx, cy, rr = 1097, 1387, 46
mm = np.zeros(img.shape[:2], np.uint8)
cv2.circle(mm, (cx, cy), rr, 1, -1)
mm = mm.astype(bool)
out = harmonic(out, mm)
out = grain_like(out, mm, (1000, 1270, 1050, 1340), 9)
cv2.imwrite("open_clean_v4.png", np.clip(out, 0, 255).astype(np.uint8))
