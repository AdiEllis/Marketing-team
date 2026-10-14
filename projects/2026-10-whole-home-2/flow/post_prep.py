"""Post photos at 1080x1350 from the sharpest copy (work/hq AI x2, else work/clean), area-downscaled (no sharpening).
No grade.py: on this exact set grade.py shifted the fronts' colour (whole-home P15, ΔE 3.4-5.6) -> source colours.
Also the palette slide's material samples: straight crops of each real front (no handles/seams)."""
import cv2, os, subprocess, numpy as np
C = "carousel/"
def src(n): return cv2.imread(f"work/hq/{n}.png") if os.path.exists(f"work/hq/{n}.png") else cv2.imread(f"work/clean/{n}.png")
names = {"oak_c": "03_oak_closet_closed", "oak_o": "05_oak_closet_open", "white_o": "04_white_closet_open",
         "white_c": "07_white_closet_closed", "grey": "06_grey_closet", "tv": "01_tv_wall_lit"}
for k, n in names.items():
    cv2.imwrite(C + f"p_{k}.png", cv2.resize(src(n), (1080, 1350), interpolation=cv2.INTER_AREA))
m = src("02_mauve_closet"); cv2.imwrite("work/mauve_src.png", m)
subprocess.run(["python3", "-I", "flow/extend_mauve.py", "work/mauve_src.png", "work/mauve_ext.png"], check=True)
cv2.imwrite(C + "p_mauve.png", cv2.resize(cv2.imread("work/mauve_ext.png"), (1080, 1350), interpolation=cv2.INTER_AREA))
# material samples (x0, y0, x1, y1 in 1122-unit photo coords; mauve in its 949 crop): plain front surfaces only
S = {"mauve": ("02_mauve_closet", 70, 100, 380, 1200), "oak": ("03_oak_closet_closed", 340, 330, 455, 800),
     "white": ("07_white_closet_closed", 760, 180, 960, 1000), "grey": ("06_grey_closet", 330, 150, 540, 600),
     "tvwood": ("01_tv_wall_lit", 360, 140, 600, 420), "tvdark": ("01_tv_wall_lit", 130, 1010, 330, 1150)}
for k, (n, x0, y0, x1, y1) in S.items():
    im = src(n); f = im.shape[0] / 1402
    # her note 14.10 "no crops": the palette shows each front's real colour as a flat swatch (median of a plain area)
    med = np.median(im[int(y0 * f):int(y1 * f), int(x0 * f):int(x1 * f)].reshape(-1, 3), 0).astype(int)
    print(k, "#%02x%02x%02x" % (med[2], med[1], med[0]))
print("post photos ok")
