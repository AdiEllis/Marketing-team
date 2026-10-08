"""Composite the REAL product photo back onto an AI set-extension (zoomed-out room).

Usage:
  python3 -I studio/tools/set_extension.py ORIGINAL EXTENDED_AI OUT_PREFIX \
      [--also OTHER_ALIGNED_PHOTO ...] [--keep x0,y0,x1,y1] [--grow-top auto|0]

1. Aligns ORIGINAL to EXTENDED_AI (SIFT + similarity transform).
2. Builds a canvas in ORIGINAL's pixel scale (so the product keeps its full resolution) and
   warps the AI image into it — the AI supplies only the room around the product.
3. Pastes ORIGINAL's pixels (region --keep, default whole photo) over it with a soft edge.
4. --grow-top auto: if the photo is cropped at the top and the AI drew the product higher,
   the real top rows are stretched up to the AI's top edge (the AI's own drawing of the
   product is never used — it tends to invent cabinets/details).
5. --also: more photos already aligned to ORIGINAL (e.g. the "open" photo) get the same
   treatment, so every state shares one room.
Writes OUT_PREFIX_<name>.jpg and OUT_PREFIX_meta.txt (offset/size for the composition).
Inspect the seams afterwards; reject any furniture/joinery the AI invented.
"""
import argparse
import os
import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("original")
    ap.add_argument("extended")
    ap.add_argument("out_prefix")
    ap.add_argument("--also", nargs="*", default=[])
    ap.add_argument("--keep", help="x0,y0,x1,y1 region of ORIGINAL to keep (default: all)")
    ap.add_argument("--grow-top", default="auto")
    a = ap.parse_args()

    orig, ext = cv2.imread(a.original), cv2.imread(a.extended)
    sift = cv2.SIFT_create(6000)
    ko, do = sift.detectAndCompute(cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY), None)
    ke, de = sift.detectAndCompute(cv2.cvtColor(ext, cv2.COLOR_BGR2GRAY), None)
    good = [m for m, n in cv2.BFMatcher().knnMatch(do, de, k=2) if m.distance < 0.75 * n.distance]
    T, inl = cv2.estimateAffinePartial2D(np.float32([ko[g.queryIdx].pt for g in good]),
                                         np.float32([ke[g.trainIdx].pt for g in good]),
                                         ransacReprojThreshold=4)
    print(f"matches={len(good)} inliers={int(inl.sum())}")
    A = np.vstack([T, [0, 0, 1]])
    Ainv = np.linalg.inv(A)
    ox, oy = -Ainv[0, 2], -Ainv[1, 2]
    s = 1 / np.hypot(T[0, 0], T[1, 0])
    W, H = int(round(ext.shape[1] * s)), int(round(ext.shape[0] * s))
    M = (np.array([[1, 0, ox], [0, 1, oy], [0, 0, 1]]) @ Ainv)[:2]
    env = cv2.warpAffine(ext, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)

    h, w = orig.shape[:2]
    x0, y0, x1, y1 = map(int, a.keep.split(",")) if a.keep else (0, 0, w, h)
    grow = 0
    if a.grow_top == "auto" and oy > 20:
        g = cv2.cvtColor(env, cv2.COLOR_BGR2GRAY).astype(float)
        prof = np.abs(np.diff(g[:, int(ox + w * .2):int(ox + w * .8)].mean(1)))
        lo = max(0, int(oy) - 400)
        top = int(np.argmax(prof[lo:int(oy) - 5]) + lo)
        grow = max(0, int(round(oy)) - top - 2)
        print(f"growing real top by {grow}px up to the AI's top edge (row {top})")

    def build(path, name):
        src = cv2.imread(path)
        cut = 40 if grow else 0                       # drop the photo's very top rows (screenshot edges)
        band = cv2.resize(src[cut + 10:cut + 30], (w, grow + cut), interpolation=cv2.INTER_LINEAR) if grow else None
        stack = np.vstack([band, src[cut:]]) if grow else src
        mask = np.zeros(stack.shape[:2], np.float32)
        mask[(grow + y0 if y0 else 0):grow + y1, x0:x1] = 1
        mask = cv2.GaussianBlur(mask, (0, 0), 4)
        P = np.float32([[1, 0, ox], [0, 1, oy - grow]])
        sw = cv2.warpAffine(stack, P, (W, H), flags=cv2.INTER_LANCZOS4)
        mw = cv2.warpAffine(mask, P, (W, H))[..., None]
        out = (sw * mw + env * (1 - mw)).astype(np.uint8)
        cv2.imwrite(f"{a.out_prefix}_{name}.jpg", out, [cv2.IMWRITE_JPEG_QUALITY, 95])

    build(a.original, "main")
    for p in a.also:
        build(p, os.path.splitext(os.path.basename(p))[0])
    with open(f"{a.out_prefix}_meta.txt", "w") as f:
        f.write(f"canvas {W}x{H}\nphoto_offset_x {ox:.2f}\nphoto_offset_y {oy:.2f}\ngrow_top {grow}\n"
                f"product_top_in_canvas {oy - grow:.1f}\n")
    print(open(f"{a.out_prefix}_meta.txt").read())


if __name__ == "__main__":
    main()
