"""Find the real tile-grout lines around the removed-logo patch (open photo) with Hough, outside the patch."""
import cv2, numpy as np
S = "/tmp/claude-0/-home-user-Marketing-team/7f9a15bc-27ce-5d25-99d6-2dc96cdb74ce/scratchpad/latte"
orig = cv2.imread("../input/angle_open.jpg"); cl = cv2.imread("open_clean_v4b.png")
diff = (np.abs(orig.astype(int) - cl.astype(int)).sum(2) > 6).astype(np.uint8)
diff[:1150] = 0; diff[:, 500:] = 0
mask = cv2.dilate(diff, np.ones((9, 9), np.uint8))
g = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
bh = cv2.morphologyEx(g, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
roi = np.zeros_like(g); roi[1120:1469, 70:560] = 1
edges = ((bh > 7) & (roi > 0) & (cv2.dilate(mask, np.ones((15, 15), np.uint8)) == 0)).astype(np.uint8) * 255
lines = cv2.HoughLinesP(edges, 1, np.pi / 360, 40, minLineLength=45, maxLineGap=8)
lines = [] if lines is None else lines.reshape(-1, 4)
vis = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
for x1, y1, x2, y2 in lines:
    print(x1, y1, x2, y2, round(float(np.degrees(np.arctan2(y2 - y1, x2 - x1))), 1))
    cv2.line(vis, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 1)
vis[mask > 0] = (vis[mask > 0] * 0.5 + np.array([255, 0, 0]) * 0.5).astype(np.uint8)
cv2.imwrite(f"{S}/hough.png", cv2.resize(vis[1100:1469, 60:560], None, fx=1.3, fy=1.3))
np.save(f"{S}/floormask.npy", mask)
