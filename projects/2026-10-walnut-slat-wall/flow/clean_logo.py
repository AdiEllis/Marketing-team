"""Remove the old Even & Etz watermark (bottom-left, on the marble floor) from the three photos.
1. exact mask: template-match the brand logo asset (studio/assets/logo_alpha.png) -> alpha at the found scale/position
2. fill = low frequencies from a harmonic fill (tone/light) + high frequencies (marble veins/grain) copied from the
   real floor just beside the logo. Floor only; joinery is never touched."""
import cv2, numpy as np
S = "/tmp/claude-0/-home-user-Marketing-team/7f9a15bc-27ce-5d25-99d6-2dc96cdb74ce/scratchpad/walnut"
logo = cv2.imread("../../studio/assets/logo_alpha.png", cv2.IMREAD_UNCHANGED)
LA = logo[..., 3].astype(np.float32) / 255.0
LR = logo[..., :3].astype(np.float32)

def find(img, region):
    x0, y0, x1, y1 = region
    g = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32)
    best = (-1, None)
    for sc in np.arange(0.16, 0.34, 0.005):
        w, h = int(536 * sc), int(784 * sc)
        if h >= g.shape[0] or w >= g.shape[1]: continue
        a = cv2.resize(LA, (w, h), interpolation=cv2.INTER_AREA)
        lg = cv2.cvtColor(cv2.resize(LR, (w, h), interpolation=cv2.INTER_AREA).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
        tmpl = lg * a + 128 * (1 - a)
        r = cv2.matchTemplate(g, tmpl, cv2.TM_CCOEFF_NORMED, mask=(a > 0.05).astype(np.float32))
        _, mv, _, ml = cv2.minMaxLoc(np.nan_to_num(r, nan=-1))
        if mv > best[0]: best = (mv, (sc, ml[0] + x0, ml[1] + y0, w, h))
    return best

def harmonic(img, m, iters=2500):
    out = img.astype(np.float32)
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min() - 3, ys.max() + 4, xs.min() - 3, xs.max() + 4
    sub = out[y0:y1, x0:x1].copy(); mm = m[y0:y1, x0:x1]
    ring = cv2.dilate(mm.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~mm
    sub[mm] = sub[ring].mean(0)
    k = np.array([[0, .25, 0], [.25, 0, .25], [0, .25, 0]], np.float32)
    for _ in range(iters):
        sm = cv2.filter2D(sub, -1, k, borderType=cv2.BORDER_REPLICATE); sub[mm] = sm[mm]
    out[y0:y1, x0:x1] = sub
    return out

for name, dx, dy in [("detail", 230, 0), ("closed", 230, -25), ("open", 230, -25)]:
    img = cv2.imread(f"input/{name}.png")
    score, (sc, x, y, w, h) = find(img, (0, 1150, 420, 1473))
    a = np.zeros(img.shape[:2], np.float32)
    ah = cv2.resize(LA, (w, h), interpolation=cv2.INTER_AREA)
    hh = min(h, img.shape[0] - y); a[y:y + hh, x:x + w] = ah[:hh]
    m = cv2.dilate((a > 0.04).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    lf = harmonic(img, m)
    f = img.astype(np.float32)
    M = np.float32([[1, 0, -dx], [0, 1, -dy]])           # tex(x,y) = img(x+dx, y+dy)
    tex = cv2.warpAffine(f, M, (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_REFLECT)
    hf = tex - cv2.GaussianBlur(tex, (0, 0), 6)
    filled = lf + hf
    feather = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5)[..., None]
    out = np.clip(filled * feather + f * (1 - feather), 0, 255).astype(np.uint8)
    cv2.imwrite(f"work/{name}_clean.png", out)
    print(name, "match", round(float(score), 3), "scale", round(float(sc), 3), "at", x, y, w, h)
    A = img[1120:1473, 0:380]; B = out[1120:1473, 0:380]
    cv2.imwrite(f"{S}/clean_{name}.jpg", cv2.resize(np.hstack([A, B]), None, fx=1.4, fy=1.4))
