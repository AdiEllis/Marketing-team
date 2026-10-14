# Her new copies (1122x1402) are sharper than the earlier set but carry the old logo stamp (bottom-left, on the floor)
# and, on the mauve closet, a thin white frame. Fill the logo with the SAME photo's pixels from the earlier logo-free
# copy (projects/2026-10-whole-home/input), aligned by homography and tone-matched on a ring around the mask.
import cv2, numpy as np, glob, os
os.makedirs('work/clean', exist_ok=True)
OLD = '../2026-10-whole-home/input/'
for f in sorted(glob.glob('input/0*.jpg')):
    n = os.path.basename(f)[:-4]; key = n[:2]
    new = cv2.imread(f)
    if key == '02': new = new[:, 87:1036]
    old = cv2.imread(glob.glob(OLD + key + '_*.jpg')[0])
    orb = cv2.ORB_create(6000)
    k1, d1 = orb.detectAndCompute(cv2.cvtColor(old, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = orb.detectAndCompute(cv2.cvtColor(new, cv2.COLOR_BGR2GRAY), None)
    m = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, True).match(d1, d2), key=lambda x: x.distance)[:1500]
    H, inl = cv2.findHomography(np.float32([k1[x.queryIdx].pt for x in m]), np.float32([k2[x.trainIdx].pt for x in m]), cv2.RANSAC, 2.0)
    h, w = new.shape[:2]
    wo = cv2.warpPerspective(old, H, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    # logo mask: strong difference in the bottom-left box
    box = np.zeros((h, w), np.uint8); box[int(h*0.75):, :int(w*0.32)] = 1
    d = cv2.absdiff(cv2.GaussianBlur(new, (3, 3), 0), cv2.GaussianBlur(wo, (3, 3), 0)).max(2)
    mk = ((d > 28) & (box > 0)).astype(np.uint8)
    mk = cv2.morphologyEx(mk, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    num, lab, st, _ = cv2.connectedComponentsWithStats(mk)
    keep = np.zeros_like(mk)
    for i in range(1, num):
        if st[i, 4] > 60: keep[lab == i] = 1
    ys, xs = np.nonzero(keep); x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
    rect = np.zeros_like(keep); rect[max(0,y0-14):y1+15, max(0,x0-14):x1+15] = 1   # whole logo block + margin
    ring = cv2.dilate(rect, np.ones((31, 31), np.uint8)) - rect
    fill = wo.astype(np.float32)
    for c in range(3):
        fill[..., c] += new[..., c][ring > 0].mean() - wo[..., c][ring > 0].mean()
    a = cv2.GaussianBlur(rect.astype(np.float32), (0, 0), 3)[..., None]
    out = (new * (1 - a) + fill * a).clip(0, 255).astype(np.uint8)
    cv2.imwrite(f'work/clean/{n}.png', out)
    print(n, out.shape[:2], 'inliers', int(inl.sum()), 'logo box', (x0, y0, x1, y1))
