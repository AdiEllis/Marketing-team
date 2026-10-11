"""Post photos: whole wall in every slide, 4:5 (1080x1350), lossless PNG. Crops trim only empty edges (curtain/ceiling side)."""
import cv2, numpy as np
def out(im, name):
    cv2.imwrite(f"carousel/p_{name}.png", cv2.resize(im, (1080, 1350), interpolation=cv2.INTER_LANCZOS4))
w = cv2.imread("work/white_g.png");  out(w[:, 8:926], "white")             # 918x1147
p = cv2.imread("work/panels_g.png"); out(p[:, 120:1126], "panels")         # 1006x1258
s = cv2.imread("work/slats_g.png");  out(s[:, 89:977], "slats")            # 888x1110
d = cv2.imread("work/dark_g.png")[:, 95:1095]                              # whole unit (107..1083) needs 1000 wide
d = np.vstack([d, d[-40:][::-1]])                                          # +40 rows of plain floor (mirrored) -> 1000x1250
out(d, "dark")
