"""Align one photo onto another (same subject, slightly different framing/scale).

Usage:
  python3 -I studio/tools/align.py SRC DST OUT_WARPED [--matrix OUT.npy] [--roi x0,y0,x1,y1]

Estimates a similarity transform (rotation + uniform scale + shift) that maps SRC onto DST
with SIFT features + RANSAC, writes SRC warped into DST's pixel space, and optionally saves
the 2x3 matrix. --roi limits feature detection in SRC (e.g. to the product, away from UI marks).
Used for: closed/open photo pairs (door animation), original photo -> AI set-extension canvas.
"""
import argparse
import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("out")
    ap.add_argument("--matrix")
    ap.add_argument("--roi", help="x0,y0,x1,y1 in SRC pixels")
    a = ap.parse_args()

    src, dst = cv2.imread(a.src), cv2.imread(a.dst)
    mask = None
    if a.roi:
        x0, y0, x1, y1 = map(int, a.roi.split(","))
        mask = np.zeros(src.shape[:2], np.uint8)
        mask[y0:y1, x0:x1] = 255
    sift = cv2.SIFT_create(6000)
    ks, ds = sift.detectAndCompute(cv2.cvtColor(src, cv2.COLOR_BGR2GRAY), mask)
    kd, dd = sift.detectAndCompute(cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY), None)
    good = [m for m, n in cv2.BFMatcher().knnMatch(ds, dd, k=2) if m.distance < 0.75 * n.distance]
    p_src = np.float32([ks[g.queryIdx].pt for g in good])
    p_dst = np.float32([kd[g.trainIdx].pt for g in good])
    M, inliers = cv2.estimateAffinePartial2D(p_src, p_dst, ransacReprojThreshold=4)
    print(f"matches={len(good)} inliers={int(inliers.sum())} scale={np.hypot(M[0,0], M[1,0]):.4f}")
    if int(inliers.sum()) < 20:
        print("WARNING: few inliers — check the result visually before using it")
    warped = cv2.warpAffine(src, M, (dst.shape[1], dst.shape[0]), flags=cv2.INTER_LANCZOS4,
                            borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(a.out, warped, [cv2.IMWRITE_JPEG_QUALITY, 96])
    if a.matrix:
        np.save(a.matrix, M)


if __name__ == "__main__":
    main()
