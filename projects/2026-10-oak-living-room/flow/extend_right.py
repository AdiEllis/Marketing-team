# Evening niche wall: extend the plain dark wall/floor to the RIGHT of the vitrine (environment only, R8) so the camera
# can tilt down the lit vitrine shelves with them near the centre of the frame. Carpentry pixels untouched.
import cv2, numpy as np
im = cv2.imread('work/hq/02_niche_wall_angle_night.png').astype(np.float32)
H, W = im.shape[:2]; E = 320
edge = im[:, W-70:W-45].mean(1)                                       # (H,3) plain-wall column right of the vitrine
k = 61; pad = np.pad(edge, ((k//2, k//2), (0, 0)), mode='edge')
edge = np.stack([np.median(pad[y:y+k], 0) for y in range(H)])         # vertical median kills the thin warm streak
edge = cv2.GaussianBlur(edge[:, None, :], (1, 0), sigmaX=1, sigmaY=8)
ext = np.repeat(edge, E, 1)
fade = np.linspace(1.0, 0.82, E)[None, :, None]                      # wall falls off slightly away from the light
ext = ext * fade
rng = np.random.default_rng(5); ext += rng.normal(0, 1.4, ext.shape)
C = W - 44                                                            # drop the photo's last columns (wall-corner line)
out = np.concatenate([im[:, :C], np.repeat(edge, W - C, 1), ext], 1)
a = np.clip((np.arange(out.shape[1]) - (C - 30)) / 30, 0, 1)[None, :, None]   # 30px cross-fade photo -> plain wall
flat = np.concatenate([np.repeat(edge, C, 1), np.repeat(edge, W - C, 1), ext], 1)
out = out * (1 - a) + flat * a
cv2.imwrite('reel/assets/niche_n.png', np.clip(out, 0, 255).astype(np.uint8)); print(out.shape)
