"""Automatic motion QA for a rendered reel (run on the final MP4, before any human sees it).

Usage:
  python3 -I studio/tools/reel_qa.py reel.mp4 OUTDIR [--planned-cuts 2.9,5.0,...]

Writes OUTDIR/first.png, last.png, sheet.jpg (6 fps contact sheet), report.txt and prints a PASS/FAIL summary.
Blocking checks (any FAIL = not delivered):
  - frame 0 is a complete image: no near-black / near-uniform empty area > 2% of the frame
  - no black or empty frames anywhere
  - every hard visual change (scene score) is close to a planned cut (+-0.2 s) when --planned-cuts is given
  - no hitches: inside motion, no run of >2 consecutive near-static frames (except the final rest)
  - no sudden speed jumps at cuts (ratio outside 0.4..2.5 of neighbours) - reported as WARN
"""
import argparse
import os
import subprocess

import cv2
import numpy as np


def empty_fraction(frame):
    g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    dark = g < 18
    # flat regions: low local variance AND very dark or uniform brand-dark (#1c1816 ~ 24)
    lap = np.abs(cv2.Laplacian(g, cv2.CV_32F, ksize=3))
    flat = cv2.blur((lap < 2).astype(np.float32), (25, 25)) > 0.97
    m = (dark | (flat & (g < 40))).astype(np.uint8)
    # empty canvas reaches the frame edge (bento gaps, half-open masks, black frames); a dark TV screen
    # inside the photo does not, so only border-connected dark-flat regions count
    n, lab = cv2.connectedComponents(m)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    if not edge:
        return 0.0
    return float(np.isin(lab, list(edge)).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--planned-cuts", default="")
    ap.add_argument("--rest-from", type=float, default=None, help="time after which static frames are allowed (end card / final rest)")
    ap.add_argument("--dark-ok", default="", help="planned dark windows, e.g. 2.4-2.8 (zoom-through a REAL dark element such as a TV screen); must be named in the plan")
    ap.add_argument("--frame0-dark-is-product", action="store_true", help="the dark area touching the edge in frame 0 is real product (e.g. a black base); QA must confirm on first.png")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cap = cv2.VideoCapture(a.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(cv2.resize(f, (270, 480), interpolation=cv2.INTER_AREA))
    n = len(frames)
    dur = n / fps
    rest = a.rest_from if a.rest_from is not None else dur - 2.5
    lines, fails, warns = [], [], []

    cap = cv2.VideoCapture(a.video)
    ok, f0 = cap.read()
    cv2.imwrite(os.path.join(a.out, "first.png"), f0)
    cap.set(cv2.CAP_PROP_POS_FRAMES, n - 1)
    ok, fl = cap.read()
    if ok:
        cv2.imwrite(os.path.join(a.out, "last.png"), fl)
    e0 = empty_fraction(f0)
    lines.append(f"frame0 empty fraction: {e0:.3f}")
    if e0 > 0.02 and a.frame0_dark_is_product:
        lines.append("frame0: dark edge area declared as real product - QA must confirm on first.png")
    elif e0 > 0.02:
        fails.append(f"FRAME 0 NOT COMPLETE: {e0*100:.1f}% empty/dark-flat")

    # black / empty frames
    dark_ok = [tuple(map(float, w.split("-"))) for w in a.dark_ok.split(",") if w.strip()]
    for i, f in enumerate(frames):
        e = empty_fraction(f)
        if e > 0.35:
            t = i / fps
            if any(lo <= t <= hi for lo, hi in dark_ok):
                continue
            if t < rest:
                fails.append(f"empty/black frame at {t:.2f}s ({e*100:.0f}%)")
                break

    # motion magnitude per frame and scene changes
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) for f in frames]
    diff = np.array([0.0] + [float(np.abs(gray[i] - gray[i - 1]).mean()) for i in range(1, n)])
    cuts = [i / fps for i in range(1, n) if diff[i] > 18]
    lines.append("hard changes (s): " + ", ".join(f"{c:.2f}" for c in cuts))
    planned = [float(x) for x in a.planned_cuts.split(",") if x.strip()]
    if planned:
        for c in cuts:
            if not any(abs(c - p) <= 0.2 for p in planned):
                fails.append(f"unplanned hard change at {c:.2f}s")
    # hitches: runs of near-static frames inside the motion part
    static = diff < 0.15
    run = 0
    for i in range(1, n):
        t = i / fps
        if static[i] and 0.2 < t < rest:
            run += 1
            if run == 3:
                fails.append(f"hitch (motion stops) around {t:.2f}s")
        else:
            run = 0
    # speed jumps at cuts
    for c in cuts:
        i = int(round(c * fps))
        before = diff[max(1, i - 6):i - 1].mean() if i > 7 else None
        after = diff[i + 2:i + 8].mean() if i + 8 < n else None
        if before and after and before > 0.3:
            r = after / before
            if r < 0.4 or r > 2.5:
                warns.append(f"speed jump at cut {c:.2f}s (x{r:.2f})")

    # contact sheet at 6 fps
    step = max(1, int(round(fps / 6)))
    sel = frames[::step]
    cols = 8
    while len(sel) % cols:
        sel.append(np.zeros_like(frames[0]))
    rows = [np.hstack(sel[i:i + cols]) for i in range(0, len(sel), cols)]
    cv2.imwrite(os.path.join(a.out, "sheet.jpg"), cv2.resize(np.vstack(rows), None, fx=0.5, fy=0.5))

    status = "PASS" if not fails else "FAIL"
    rep = [f"{os.path.basename(a.video)}: {status}  ({dur:.1f}s, {fps:.0f}fps)"] + lines
    rep += ["FAIL: " + x for x in fails] + ["WARN: " + x for x in warns]
    open(os.path.join(a.out, "report.txt"), "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


if __name__ == "__main__":
    main()
