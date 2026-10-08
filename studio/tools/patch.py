"""Remove small marks (Instagram UI badges, old watermarks) by Poisson-blending a nearby REAL patch.

Usage:
  python3 -I studio/tools/patch.py IN OUT  "sx,sy,dx,dy,w,h" ["sx,sy,dx,dy,w,h" ...]

Each spec copies the w x h region at (sx,sy) onto (dx,dy) with cv2.seamlessClone, so lighting
and gradients match the surroundings. Pick sources with the same structure:
  - flat door surfaces: copy from above/below on the same door
  - shelves/horizontal structures: copy sideways inside the same bay
  - vertical panels: copy from above/below
The destination boundary must not cross the mark itself (marks bleed into the blend).
Plain inpainting was tried and rejected (visible smudges). Always check the result at 100%.
"""
import sys
import cv2
import numpy as np


def clone(img, sx, sy, dx, dy, w, h):
    patch = img[sy:sy + h, sx:sx + w].copy()
    mask = np.full((h, w), 255, np.uint8)
    mask[:2, :] = mask[-2:, :] = 0
    mask[:, :2] = mask[:, -2:] = 0
    return cv2.seamlessClone(patch, img, mask, (dx + w // 2, dy + h // 2), cv2.NORMAL_CLONE)


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    img = cv2.imread(sys.argv[1])
    for spec in sys.argv[3:]:
        img = clone(img, *map(int, spec.split(",")))
    cv2.imwrite(sys.argv[2], img, [cv2.IMWRITE_JPEG_QUALITY, 97])


if __name__ == "__main__":
    main()
