"""Straighten a tilted carpentry photo (client-voice P17): rotate so the verticals are vertical, crop the empty corners.

Usage:
  python3 -I studio/tools/straighten.py IN OUT.png [--deg D]
    --deg  force the angle (from photo_check.py, + = top leans right); default: measured here.
Rotation only (no perspective warp: keeps proportions honest). Max 6 deg; above that, judge by eye.
Writes PNG (lossless). Prints the angle used and the crop kept.
"""
import argparse
import math
import cv2
import numpy as np
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photo_check import tilt_deg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--deg", type=float)
    a = ap.parse_args()
    im = cv2.imread(a.inp, cv2.IMREAD_COLOR)
    h, w = im.shape[:2]
    d = a.deg
    if d is None:
        g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        s = 1200 / w
        d, n = tilt_deg(cv2.resize(g, (1200, round(h * s))))
        if d is None:
            print("no reliable verticals; nothing done"); cv2.imwrite(a.out, im); return
    if abs(d) > 6:
        raise SystemExit(f"angle {d:.2f} > 6 deg: check by eye, pass --deg")
    # rotating by -d makes the leaning lines vertical
    M = cv2.getRotationMatrix2D((w / 2, h / 2), -d, 1.0)
    r = cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    # largest axis-aligned rectangle inside the rotated frame (same aspect), so no reflected edge stays
    t = math.radians(abs(d))
    c, sn = math.cos(t), math.sin(t)
    k = min(w / (w * c + h * sn), h / (w * sn + h * c))
    cw, ch = int(w * k), int(h * k)
    x0, y0 = (w - cw) // 2, (h - ch) // 2
    out = r[y0:y0 + ch, x0:x0 + cw]
    cv2.imwrite(a.out, out)
    print(f"rotated {-d:+.2f} deg, kept {cw}x{ch} of {w}x{h} -> {a.out}")


if __name__ == "__main__":
    main()
