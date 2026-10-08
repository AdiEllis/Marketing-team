#!/usr/bin/env bash
# Installs the studio's production tools in a fresh cloud session. Idempotent and quiet.
# Run automatically by the SessionStart hook in .claude/settings.json.
set -u
log() { echo "[studio-setup] $*"; }

if ! python3 -c "import cv2" 2>/dev/null; then
  log "installing opencv (image alignment / patching)…"
  pip install -q opencv-python-headless >/dev/null 2>&1 || log "WARN: opencv install failed"
fi
python3 -c "import PIL, numpy" 2>/dev/null || pip install -q pillow numpy >/dev/null 2>&1

# Warm the HyperFrames CLI (video renderer) so the first render does not wait on npm.
if command -v npx >/dev/null 2>&1; then
  timeout 240 npx --yes hyperframes@0.8.141 --version >/dev/null 2>&1 || log "WARN: hyperframes prefetch failed (will retry on first render)"
fi

command -v ffmpeg >/dev/null 2>&1 || log "WARN: ffmpeg missing"
ls /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell >/dev/null 2>&1 || log "WARN: headless Chromium not found (needed for carousel PNGs)"
log "ready"
exit 0
