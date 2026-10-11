"""Remove the brand watermark from day.png / warm.png, where it sits on the left end of the unit.
Structure-aware fill (every pixel comes from the real photo):
  - right of the side panel's front edge (x >= EDGE): perspective clone along the wall's vanishing point VP
    (all sideboard / plinth / floor lines pass through VP, so a homothety about VP maps each line onto itself)
  - side panel (56 <= x < EDGE, above its bottom edge): vertical clone from the same columns higher up
  - floor below the panel's bottom edge: harmonic tone + floor texture from just below
detail.png / front.png: logo sits on plain wood / marble -> studio/tools/unwatermark.py is enough.
Usage: python3 -I flow/clean_logo.py   (from the project dir)"""
import cv2, numpy as np

VP = np.array([1688.0, 692.0])   # from LSD lines on the sideboard (s vs y@x=140 is linear -> one VP)
R = 0.86                         # homothety ratio (source lies further along the wall, toward VP)
EDGE = 138                       # side panel front edge (columns measured at y=900..1140)
logo = cv2.imread("../../studio/assets/logo_alpha.png", cv2.IMREAD_UNCHANGED)

def logo_mask(x, y, w, h, shape):
    a = np.zeros(shape, np.float32)
    al = cv2.resize(logo[..., 3].astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    a[y:y + h, x:x + w] = al[: shape[0] - y]
    return cv2.dilate((a > 0.03).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)

def harmonic(f, m, iters=1500):
    ys, xs = np.where(m); y0, y1, x0, x1 = max(ys.min() - 4, 0), ys.max() + 5, max(xs.min() - 4, 0), xs.max() + 5
    full = f.copy(); full[y0:y1, x0:x1] = _harm(f[y0:y1, x0:x1].copy(), m[y0:y1, x0:x1], iters); return full

def _harm(out, m, iters):
    ring = cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~m
    out[m] = out[ring].mean(0)
    k = np.array([[0, .25, 0], [.25, 0, .25], [0, .25, 0]], np.float32)
    for _ in range(iters):
        sm = cv2.filter2D(out, -1, k, borderType=cv2.BORDER_REPLICATE); out[m] = sm[m]
    return out

def panel_bottom(x):  # bottom edge of the side panel, visible left of the logo
    return 1355 + 1.03 * (x - 57)

for name in ["day", "warm"]:
    img = cv2.imread(f"input/{name}.png"); f = img.astype(np.float32); H, W = img.shape[:2]
    m = np.zeros((H, W), bool); m[1143:1443, 80:287] = True   # whole stamp box (anti-aliased rims leave ghosts otherwise)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # 1) perspective clone along VP
    mx = (VP[0] + (xx - VP[0]) * R).astype(np.float32); my = (VP[1] + (yy - VP[1]) * R).astype(np.float32)
    persp = cv2.remap(f, mx, my, cv2.INTER_CUBIC)
    # 2) vertical clone for the panel (same column, 300 px higher), keeping the panel's vertical light falloff
    vert = cv2.remap(f, xx, (yy - 300).astype(np.float32), cv2.INTER_LINEAR)
    gain = (f[1128:1145].mean(0) + 1) / (f[828:845].mean(0) + 1)          # per-column falloff, measured just above the stamp
    gain = cv2.GaussianBlur(gain[None], (0, 0), 2)[0]
    vert = vert * gain[None]
    # 3) floor under the panel: tone from the ring, grain from 45 px lower
    Rf = 1.045   # floor under the panel: same floor lines, nearer the camera (bottom-left, unmasked)
    floor = cv2.remap(f, (VP[0] + (xx - VP[0]) * Rf).astype(np.float32), (VP[1] + (yy - VP[1]) * Rf).astype(np.float32),
                      cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # 4) the wood frame's dark left side (vertical strip x 138-150, down to the shelf edge): tile from y 1121-1149
    strip = np.broadcast_to(f[1122:1148].mean(0, keepdims=True), f.shape)
    fill = np.where((xx >= EDGE)[..., None], persp, np.where((yy < panel_bottom(xx))[..., None], vert, floor))
    sm = (xx >= EDGE) & (xx < 150) & (yy < 1352 - 0.425 * (xx - 140))
    fill = np.where(sm[..., None], strip, fill)
    # floor tone: harmonic from the surrounding real/filled floor, grain from the floor sample
    F = m & (xx < EDGE) & (yy >= 1330)   # whole low corner, so the darker panel edge does not drive the floor tone
    comp = f.copy()
    lo = harmonic(cv2.GaussianBlur(comp, (0, 0), 1.5), F, 3000)
    floor_hf = floor - cv2.GaussianBlur(floor, (0, 0), 4)
    Fin = m & (xx < EDGE) & (yy >= panel_bottom(xx))
    fill = np.where(Fin[..., None], lo + floor_hf, fill)
    # seamless (Poisson-style) correction: the fill's offset from the real pixels on the box rim, interpolated inside
    # (only where the perspective clone was used: it fixes the plinth's tone seam on the box's right edge)
    d = harmonic(f - fill, m, 4000)
    fill = np.where(((xx >= EDGE) & m & ~sm)[..., None], fill + d, fill)
    fe = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.6)[..., None]
    out = np.clip(fill * fe + f * (1 - fe), 0, 255).astype(np.uint8)
    # soften the box seam on the plain floor only (1-2 px tone step)
    seam = (cv2.dilate(m.astype(np.uint8), np.ones((7, 7), np.uint8)) - cv2.erode(m.astype(np.uint8), np.ones((7, 7), np.uint8))).astype(bool)
    seam &= ((xx < EDGE) & (yy > panel_bottom(xx) + 4)) | (yy > 1436)
    out[seam] = cv2.GaussianBlur(out, (0, 0), 2.0)[seam]
    cv2.imwrite(f"work/{name}_clean.png", out)
    print(name, "ok")

# detail.png: a small dark object pokes in at the right edge (x 1168-1178, y 190-234) on the plain white wall.
# Fill from the same columns 70 px higher (uniform vertical wall), feathered. Run after unwatermark.py made work/detail_uw.png.
import os
if os.path.exists("work/detail_uw.png"):
    d = cv2.imread("work/detail_uw.png").astype(np.float32)
    mm = np.zeros(d.shape[:2], np.float32); mm[182:244, 1160:1179] = 1
    mm = cv2.GaussianBlur(mm, (0, 0), 2.5)[..., None]
    src = np.roll(d, 70, axis=0)   # src(y) = d(y - 70)
    cv2.imwrite("work/detail_uw.png", np.clip(src * mm + d * (1 - mm), 0, 255).astype(np.uint8))
    print("detail edge object removed")

# front.png (after unwatermark.py -> work/front_uw.png): the stamp left faint rust-coloured letter ghosts on the marble
# (screenshot JPEG chroma). Replace the chroma inside the stamp box with the chroma interpolated from around it (Lab a/b),
# and pull lightness outliers (letter rims) back toward a local median. Marble veins/tile joints stay (lightness is kept).
if os.path.exists("work/front_uw.png") and not os.path.exists("work/front_uw.done"):
    fr = cv2.imread("work/front_uw.png")
    lab = cv2.cvtColor(fr, cv2.COLOR_BGR2LAB).astype(np.float32)
    bm = np.zeros(fr.shape[:2], bool); bm[1146:1446, 78:288] = True
    for c in (1, 2):
        lab[..., c] = harmonic(np.ascontiguousarray(lab[..., c]), bm, 2500)
    L = lab[..., 0]; med = cv2.medianBlur(fr, 9); Lm = cv2.cvtColor(med, cv2.COLOR_BGR2LAB)[..., 0].astype(np.float32)
    dev = L - Lm; fix = bm & (np.abs(dev) > 6) & (np.abs(dev) < 40)   # rims, not the bright LED reflection line
    L[fix] = Lm[fix] + dev[fix] * 0.35
    out = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    fe = cv2.GaussianBlur(bm.astype(np.float32), (0, 0), 3)[..., None]
    cv2.imwrite("work/front_uw.png", np.clip(out * fe + fr * (1 - fe), 0, 255).astype(np.uint8))
    open("work/front_uw.done", "w").write("1")
    print("front ghost cleaned")
