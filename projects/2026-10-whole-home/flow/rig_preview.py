"""Draw the rig's doors at their open angle over the (fitted) real open photo: cmp_open check."""
import sys, json, numpy as np, cv2
name = sys.argv[1]; A = f"reel/assets/{name}/"; R = json.load(open(A + "rig.json"))
K = np.array(R["K"]); O, rx, ry, rz = map(np.array, (R["O"], R["rx"], R["ry"], R["rz"]))
def proj(P): c = O + P[0] * rx + P[1] * ry + P[2] * rz; p = K @ c; return p[:2] / p[2]
im = cv2.imread(A + "open_fit.png")
over = dict(a.split("=") for a in sys.argv[2:])
for n, d in R["doors"].items():
    P = np.array(d["P"]); hx = P[1][0]; phi = np.radians(float(over.get(n, d["open"])))
    Q = [proj([hx + (p[0] - hx) * np.cos(phi), p[1], abs(p[0] - hx) * np.sin(phi)]) for p in P]
    cv2.polylines(im, [np.int32(np.round(Q))], True, (0, 0, 255), 2)
cv2.imwrite(f"work/cmp_open_{name}.png", im)
