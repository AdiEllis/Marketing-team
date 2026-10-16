"""Every K.path in reel/index.html keeps the 1080x1920 window inside its photo (Catmull-Rom sampled every 0.05 s)."""
import re
html = open("reel/index.html").read()
size = {"sA": (1178, 1210), "sA2": (1178, 1210), "sB": (1166, 1245), "sB2": (1166, 1245), "sC": (977, 1110), "sD": (934, 1348)}
def cr(keys, t):
    i = 0
    while i < len(keys) - 2 and t > keys[i + 1][0]: i += 1
    k0 = keys[max(i - 1, 0)]; k1 = keys[i]; k2 = keys[i + 1]; k3 = keys[min(i + 2, len(keys) - 1)]
    u = min(1, max(0, (t - k1[0]) / (k2[0] - k1[0]))); out = []
    for j in (1, 2, 3):
        m1 = (k2[j] - k0[j]) / ((k2[0] - k0[0]) or 1) * (k2[0] - k1[0]); m2 = (k3[j] - k1[j]) / ((k3[0] - k1[0]) or 1) * (k2[0] - k1[0])
        u2 = u * u; u3 = u2 * u
        out.append((2*u3-3*u2+1)*k1[j] + (u3-2*u2+u)*m1 + (-2*u3+3*u2)*k2[j] + (u3-u2)*m2)
    return out
for m in re.finditer(r'K\.path\("#(\w+)", (\[\[.*?\]\])\);', html):
    st = m.group(1); keys = eval(m.group(2)); W, H = size[st]; bad = []; t = keys[0][0]
    while t <= keys[-1][0] + 1e-9:
        cx, cy, s = cr(keys, t); w = 1080 / s; h = 1920 / s
        e = [cx - w/2, W - (cx + w/2), cy - h/2, H - (cy + h/2)]
        if min(e) < -0.5: bad.append((round(t, 2), [round(v) for v in e]))
        t += 0.05
    print(st, "OK" if not bad else bad[:4])
