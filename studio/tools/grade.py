"""Photo enhancement for posts: brighter, warmer, cleaner — the product stays the real photo.

Usage:
  python3 -I studio/tools/grade.py IN OUT.png [--strength 1.0]

Steps (all global or very local tone moves; nothing is redrawn):
  1. auto-levels per channel (0.5% clip) for a clean black/white point
  2. gentle lift of shadows / midtones (gamma), slight warmth
  3. local contrast with CLAHE on lightness (low clip) — "clarity" without sharpening halos
  4. a touch of saturation
Writes a lossless PNG. Compare before/after at 100% — undo if anything looks artificial.
"""
import argparse
import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--strength", type=float, default=1.0)
    a = ap.parse_args()
    k = a.strength
    img = cv2.imread(a.src).astype(np.float32)

    # 1. levels
    lo = np.percentile(img, 0.5, axis=(0, 1))
    hi = np.percentile(img, 99.5, axis=(0, 1))
    lev = np.clip((img - lo) / np.maximum(hi - lo, 1) * 255, 0, 255)
    img = img + (lev - img) * min(1.0, 0.8 * k)

    # 2. lift + warmth (BGR)
    x = img / 255.0
    x = np.power(x, 1 / (1 + 0.10 * k))
    x[..., 2] *= 1 + 0.025 * k   # R
    x[..., 0] *= 1 - 0.025 * k   # B
    img = np.clip(x, 0, 1) * 255

    # 3. clarity (CLAHE on L)
    lab = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2LAB)
    l, aa, bb = cv2.split(lab)
    cl = cv2.createCLAHE(clipLimit=1.2 + 0.6 * k, tileGridSize=(8, 8)).apply(l)
    l2 = cv2.addWeighted(l, 1 - 0.45 * k, cl, 0.45 * k, 0)
    img = cv2.cvtColor(cv2.merge([l2, aa, bb]), cv2.COLOR_LAB2BGR).astype(np.float32)

    # 4. saturation
    hsv = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * (1 + 0.08 * k), 0, 255)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    cv2.imwrite(a.out, out)


if __name__ == "__main__":
    main()
