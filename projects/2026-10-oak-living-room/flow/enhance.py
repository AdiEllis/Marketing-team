# Quality pass for compressed phone/screenshot JPEGs (her note 13.10, T10):
# chroma-only cleanup (colour blotches from JPEG), luma untouched (wood grain is the product),
# then x2 Lanczos so later scaling in the reel/post never upsamples twice. No sharpening.
import cv2, os, glob
os.makedirs('work/hq', exist_ok=True)
for f in sorted(glob.glob('input/0*.jpg')):
    im = cv2.imread(f)
    ycc = cv2.cvtColor(im, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycc)
    cr = cv2.bilateralFilter(cr, 7, 6, 5); cb = cv2.bilateralFilter(cb, 7, 6, 5)
    W, H = im.shape[1]*2, im.shape[0]*2
    y = cv2.resize(y, (W, H), interpolation=cv2.INTER_LANCZOS4)
    cr = cv2.resize(cr, (W, H), interpolation=cv2.INTER_CUBIC); cb = cv2.resize(cb, (W, H), interpolation=cv2.INTER_CUBIC)
    out = cv2.cvtColor(cv2.merge([y, cr, cb]), cv2.COLOR_YCrCb2BGR)
    p = 'work/hq/' + os.path.basename(f).replace('.jpg', '.png'); cv2.imwrite(p, out); print(p, out.shape[:2])
