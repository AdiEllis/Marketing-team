# Quality pass (her notes 13.10: "אם אתה יכול לשפר איכות" / "תשפר את רזולוציית התמונות"):
# AI x4 super-resolution (UpscalerJS ESRGAN-thick on tfjs-node, flow/upscale_ai.js -> work/ai/) then area-downscale to x2
# (work/hq/), which keeps the recovered edges/grain without the x4 artefacts. Colour checked against the source (P15).
import cv2, os, glob, numpy as np
os.makedirs('work/hq', exist_ok=True)
for f in sorted(glob.glob('input/0*.jpg')):
    n = os.path.basename(f)[:-4]; src = cv2.imread(f); ai = cv2.imread(f'work/ai/{n}.png')
    out = cv2.resize(ai, (src.shape[1]*2, src.shape[0]*2), interpolation=cv2.INTER_AREA)
    a = cv2.cvtColor(cv2.resize(out, src.shape[1::-1], interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2LAB).astype(float).mean((0, 1))
    b = cv2.cvtColor(src, cv2.COLOR_BGR2LAB).astype(float).mean((0, 1))
    cv2.imwrite(f'work/hq/{n}.png', out); print(n, out.shape[:2], 'mean Lab shift', np.round(a - b, 2))
