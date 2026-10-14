"""Check every uploaded photo before the post (client-voice P17): resolution, sharpness, tilt.

Usage:
  python3 -I studio/tools/photo_check.py projects/<p>/input/*.jpg

Prints one line per photo + a verdict:
  UPSCALE   short side < 1350px, or soft/compressed -> AI upscale first (studio/tools/upscale_ai.js), only these photos
  STRAIGHTEN verticals lean > 0.4 deg -> studio/tools/straighten.py
  OK        leave it as it is (no upscale for good photos: her note 14.10 "רק תמונות שהן ברזולוציה נמוכה")
Never drops a photo: what she uploaded is what there is (P17). Cleaning the surroundings is judged by eye.
"""
import sys
import cv2
import numpy as np


def tilt_deg(gray):
    """median lean of near-vertical lines (carpentry edges), degrees; + = top leans right."""
    e = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
    h = gray.shape[0]
    lines = cv2.HoughLinesP(e, 1, np.pi / 720, 80, minLineLength=h // 6, maxLineGap=8)
    if lines is None:
        return None, 0
    a = []
    for x1, y1, x2, y2 in np.asarray(lines).reshape(-1, 4):
        dx, dy = x2 - x1, y2 - y1
        if abs(dy) < 1:
            continue
        ang = np.degrees(np.arctan2(dx, dy))
        if ang > 90: ang -= 180
        if ang < -90: ang += 180
        if abs(ang) < 8:
            a.append((ang, np.hypot(dx, dy)))
    if len(a) < 3:
        return None, len(a)
    a = np.array(a)
    order = np.argsort(a[:, 0]); w = np.cumsum(a[order, 1])
    med = a[order, 0][np.searchsorted(w, w[-1] / 2)]
    return float(med), len(a)


def main(paths):
    for p in paths:
        im = cv2.imread(p)
        if im is None:
            print(f"{p}: cannot read"); continue
        h, w = im.shape[:2]
        g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(g, (1080, round(1080 * h / w))) if w > 1080 else g
        sharp = cv2.Laplacian(small, cv2.CV_64F).var()
        t, n = tilt_deg(cv2.resize(g, (1200, round(1200 * h / w))))
        verdict = []
        if min(h, w) < 1350 or sharp < 60:
            verdict.append("UPSCALE")
        if t is not None and abs(t) > 0.4:
            verdict.append(f"STRAIGHTEN({t:+.2f}deg)")
        print(f"{p}: {w}x{h} sharp={sharp:.0f} tilt={'?' if t is None else f'{t:+.2f}'} ({n} lines) -> {' + '.join(verdict) or 'OK'}")


if __name__ == "__main__":
    main(sys.argv[1:])
