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

# Official HyperFrames skills (hyperframes-animation, hyperframes-creative, ...): required for every reel (CLAUDE.md #7)
if [ ! -d "$HOME/.claude/skills/hyperframes-animation" ] && command -v npx >/dev/null 2>&1; then
  (cd /tmp && timeout 180 npx --yes hyperframes@0.8.141 skills update hyperframes-animation >/dev/null 2>&1) || log "WARN: hyperframes skills install failed"
fi

# CLAUDE.md #9: every session starts in sync with main, so notes recorded in other sessions are never missed (lesson 11.10).
# Safe: only when the working tree is clean; a conflicting merge is aborted and reported, never left half-done.
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/..}" 2>/dev/null && if git rev-parse --git-dir >/dev/null 2>&1; then
  if timeout 60 git fetch -q origin main 2>/dev/null; then
    if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
      log "WARN: local changes present - merge origin/main by hand before reading the rules"
    elif git merge-base --is-ancestor origin/main HEAD 2>/dev/null; then
      log "synced main (already up to date)"
    elif git merge -q --no-edit origin/main >/dev/null 2>&1; then
      log "synced main (merged origin/main)"
    else
      git merge --abort >/dev/null 2>&1
      log "WARN: merging origin/main conflicts - resolve by hand before reading the rules"
    fi
  else
    log "WARN: could not fetch origin/main - run: git fetch origin main && git merge origin/main"
  fi
fi

command -v ffmpeg >/dev/null 2>&1 || log "WARN: ffmpeg missing"
ls /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell >/dev/null 2>&1 || log "WARN: headless Chromium not found (needed for carousel PNGs)"
log "ready"
exit 0
