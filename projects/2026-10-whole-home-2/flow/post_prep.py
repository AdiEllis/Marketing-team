"""Post v2 (her format 14.10, P16-P17): photos only. Each photo prepared: old logo stamp removed (flow/clean_logo.py),
AI x2 (all were < 1350 px short side, photo_check UPSCALE; mean Lab shift < 0.25), ceiling lamp removed from the two oak
photos (flow/clean_lamp.py, ceiling only), mauve sides extended with plain wall/floor (flow/extend_mauve.py).
TV wall NOT straightened: photo_check's angle came from 3 lines and rotating made the cladding lean (checked by eye).
No grade.py (it shifted the fronts' colour on this set, P15). Area-downscale to 1080x1350, no sharpening."""
import cv2, os, subprocess
C = "carousel/"
def get(n):
    for d in ("work/prep", "work/hq"):
        if os.path.exists(f"{d}/{n}.png"): return cv2.imread(f"{d}/{n}.png")
order = ["01_tv_wall_lit", "02_mauve_closet", "03_oak_closet_closed", "05_oak_closet_open",
         "07_white_closet_closed", "04_white_closet_open", "06_grey_closet"]
for i, n in enumerate(order, 1):
    if n == "02_mauve_closet":
        cv2.imwrite("work/mauve_src.png", get(n))
        subprocess.run(["python3", "-I", "flow/extend_mauve.py", "work/mauve_src.png", "work/prep/02_mauve_ext.png"], check=True)
        im = cv2.imread("work/prep/02_mauve_ext.png")
    else:
        im = get(n)
    cv2.imwrite(C + f"p{i}.png", cv2.resize(im, (1080, 1350), interpolation=cv2.INTER_AREA))
print("post photos ok")
