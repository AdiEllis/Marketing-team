# Post photos 1080x1350 from the cleaned x2 originals (no grade: grade.py moved the oak by dE>2, P15).
import cv2, numpy as np
H = 'work/hq/'; C = 'carousel/'
def fit(im, y0, y1, out):
    """crop rows y0..y1 at full width, scale to 1350 tall; if narrower than 1080, extend the plain wall/floor at the sides"""
    c = im[y0:y1]; s = 1350 / c.shape[0]; c = cv2.resize(c, (round(c.shape[1]*s), 1350), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LANCZOS4)
    if c.shape[1] < 1080:
        p = (1080 - c.shape[1]) // 2; q = 1080 - c.shape[1] - p
        e = cv2.copyMakeBorder(c, 0, 0, p, q, cv2.BORDER_REPLICATE)
        bl = cv2.GaussianBlur(e, (0, 0), 5); m = np.zeros(e.shape[:2], np.float32); m[:, :p] = 1; m[:, e.shape[1]-q:] = 1
        m = cv2.GaussianBlur(m, (0, 0), 3)[..., None]; c = (bl*m + e*(1-m)).astype(np.uint8)
    elif c.shape[1] > 1080:
        x = (c.shape[1] - 1080) // 2; c = c[:, x:x+1080]
    cv2.imwrite(C + out, c); print(out, c.shape[:2], 'scale vs source x%.2f' % (2*s))
room = cv2.imread(H + '01_room_wide.png'); tv = cv2.imread(H + '04_tv_wall_front.png'); ni = cv2.imread(H + '02_niche_wall_angle.png')
fit(room, 300, 2220, 'p1.png')          # 1536x1920 = exact 4:5 at full width
fit(tv, 330, 2580, 'p2.png')            # 1800x2250 = exact 4:5
n5 = cv2.imread(H + '05_niche_wall_angle_sharp.png')
fit(n5, 250, 2822, 'p4.png')            # v3: her sharp angled photo, whole wall incl. plinth, ceiling above for the line; sides +~45px plain wall
# detail rows (slide 3, v2 after her note): each crop composed on purpose, subject whole and centred (hq px)
def crop(im, x0, y0, x1, y1, out, W=500, Hh=340):
    c = im[y0:y1, x0:x1]; s = W / c.shape[1]
    c = cv2.resize(c, (W, Hh), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LANCZOS4); cv2.imwrite(C + out, c); print(out, 'x%.2f' % (2*s))
fr = cv2.imread(H + '03_niche_wall_front_install.png')   # frontal niche only (no legs in this crop)
crop(tv, 30, 1850, 1750, 2387, 'd_console.png', 960, 300)    # the whole floating console, grooves above and below, floor gap
crop(fr, 386, 970, 1140, 1684, 'd_niche.png', 465, 440)      # lit niche, frontal and centred, oak fronts around
crop(room, 178, 1116, 922, 1820, 'd_slats.png', 465, 440)    # the joint: niche wall + vitrine | lit slat column | TV wall + console
