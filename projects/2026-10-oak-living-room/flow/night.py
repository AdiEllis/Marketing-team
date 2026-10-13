# "Evening falls": the room darkens, the carpentry's REAL light stays exactly as photographed (R5: same tone,
# no added glow). Kept = whole lit boxes (niche, vitrine; hand-measured, hq px) + thin bright structures
# (LED strips, their floor reflections, downlights) via top-hat + warm lit pixels. No local-ratio term
# (it invented a TV backlight halo).
import cv2, numpy as np, sys
BOX = {  # x0,y0,x1,y1 in hq (2x) pixels
 '01_room_wide': [(226,1246,430,1436), (428,1110,498,1592)],
 '02_niche_wall_angle': [(656,1080,1144,1680), (1308,668,1472,2062)],
 '04_tv_wall_front': [],
}
def night(n, k=0.26, spill=0.45):
    im = cv2.imread(f'work/hq/{n}.png').astype(np.float32) / 255
    hsv = cv2.cvtColor((im*255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = hsv[...,0]*2, hsv[...,1]/255, hsv[...,2]/255
    warm = ((h > 12) & (h < 50)).astype(np.float32)
    lit = warm * np.clip((s-0.30)/0.25, 0, 1) * np.clip((v-0.6)/0.2, 0, 1)
    th = cv2.morphologyEx(v, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21)))
    lines = np.clip((th-0.10)/0.12, 0, 1) * np.clip((v-0.6)/0.2, 0, 1)
    m = np.maximum(lit, lines)
    for x0,y0,x1,y1 in BOX[n]:
        b = np.zeros_like(m); b[y0:y1, x0:x1] = 1; m = np.maximum(m, b)
    m = cv2.GaussianBlur(m, (0,0), 2.5)
    halo = cv2.GaussianBlur(m, (0,0), 30)          # the photo's own light spill nearby stays partly visible
    keep = np.clip(np.maximum(m*1.1, halo*spill), 0, 1)[...,None]
    dark = im * k * np.array([1.06, 0.98, 0.92], np.float32)   # BGR: slightly cooler evening shadow
    out = dark*(1-keep) + im*keep
    cv2.imwrite(f'work/hq/{n}_night.png', np.clip(out*255+0.5, 0, 255).astype(np.uint8))
for n in sys.argv[1:]: night(n)
