"""Input cleanup: screenshot bar (white), people reflected in TV screens + TV menu (dark, panels).
The screen glass is not the product: its interior is replaced by a mask-normalised heavy blur of itself
(keeps the real dark gradient / curtain glow, removes the people and the on-screen menu)."""
import cv2, numpy as np
def screen(src, dst, quad, inset=7, sig=40, darken=0.9):
    im = cv2.imread(src).astype(np.float32)
    q = np.array(quad, np.float32); c = q.mean(0)
    qi = c + (q - c) * (1 - inset / np.linalg.norm(q - c, axis=1))[:, None]
    m = np.zeros(im.shape[:2], np.float32); cv2.fillPoly(m, [qi.astype(np.int32)], 1)
    num = cv2.GaussianBlur(im * m[..., None], (0, 0), sig); den = cv2.GaussianBlur(m, (0, 0), sig)[..., None]
    fill = num / np.maximum(den, 1e-4) * darken
    fill += np.random.default_rng(1).normal(0, 1.2, fill.shape)        # match sensor grain
    a = cv2.GaussianBlur(m, (0, 0), 1.2)[..., None]
    cv2.imwrite(dst, np.clip(im * (1 - a) + fill * a, 0, 255).astype(np.uint8))
screen("input/raw_dark.jpg", "input/dark.png", [(428, 555), (892, 560), (885, 822), (427, 817)])
screen("input/raw_panels.jpg", "input/panels.png", [(401, 592), (935, 589), (927, 927), (399, 877)])
w = cv2.imread("input/raw_white.jpg"); cv2.imwrite("input/white.png", w[:1147])
cv2.imwrite("input/slats.png", cv2.imread("input/raw_slats.jpg"))
