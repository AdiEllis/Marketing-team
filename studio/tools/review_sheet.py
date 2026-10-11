"""One review image for the gate: key moments of the reel (full detail where it matters) instead of dozens of frames.

Usage:
  python3 -I studio/tools/review_sheet.py reel.mp4 OUT.jpg --at 0,3.1,5.5,8.6,12.0,last [--labels "frame0,whip,..."]
  python3 -I studio/tools/review_sheet.py reel.mp4 OUT.jpg --at ... --zoom 5.5:540,700,600   (extra 1:1 crop: t:cx,cy,size)

Pick: frame 0, every transition (just after the cut), the signature/wow peak, the light moment, each card, end card, last.
Tiles are 432x768 (40%), enough to judge framing, flow and text placement; use --zoom for a suspicious region (UI
remnant, door edge, text on a niche) instead of opening full frames.
"""
import argparse

import cv2
import numpy as np


def grab(cap, fps, n, t):
    i = n - 1 if t == "last" else min(n - 1, int(round(float(t) * fps)))
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ok, f = cap.read()
    return f, i / fps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("out")
    ap.add_argument("--at", required=True)
    ap.add_argument("--labels", default="")
    ap.add_argument("--zoom", action="append", default=[])
    a = ap.parse_args()
    cap = cv2.VideoCapture(a.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ts = [s.strip() for s in a.at.split(",") if s.strip()]
    labels = a.labels.split(",") if a.labels else [""] * len(ts)
    tiles = []
    for t, lab in zip(ts, labels + [""] * len(ts)):
        f, sec = grab(cap, fps, n, t)
        f = cv2.resize(f, (432, 768), interpolation=cv2.INTER_AREA)
        cv2.rectangle(f, (0, 0), (432, 34), (0, 0, 0), -1)
        cv2.putText(f, f"{sec:5.2f}s {lab}", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        # IG UI zone guide (y>1536 and right 100px strip) as thin lines, only on the review copy
        cv2.line(f, (0, int(1536 * 0.4)), (432, int(1536 * 0.4)), (0, 0, 255), 1)
        cv2.line(f, (int(980 * 0.4), 0), (int(980 * 0.4), 768), (0, 0, 255), 1)
        tiles.append(f)
    for z in a.zoom:
        t, rest = z.split(":"); cx, cy, size = (int(v) for v in rest.split(","))
        f, sec = grab(cap, fps, n, t)
        h = size // 2
        crop = f[max(0, cy - h):cy + h, max(0, cx - h):cx + h]
        crop = cv2.resize(crop, (432, 432 * crop.shape[0] // max(1, crop.shape[1])), interpolation=cv2.INTER_AREA)
        tile = np.full((768, 432, 3), 30, np.uint8); tile[:min(768, crop.shape[0])] = crop[:768]
        cv2.putText(tile, f"zoom {sec:.2f}s", (8, 760), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        tiles.append(tile)
    cols = 4
    while len(tiles) % cols:
        tiles.append(np.full((768, 432, 3), 30, np.uint8))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    cv2.imwrite(a.out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"review sheet: {a.out} ({len(ts)} moments, {len(a.zoom)} zooms)")


if __name__ == "__main__":
    main()
