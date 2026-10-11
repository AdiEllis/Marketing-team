#!/usr/bin/env bash
# Render a carousel HTML (N stacked 1080x1350 <section class="slide">) to slide PNGs + JPEG 95 (4:4:4) + one review sheet.
# Usage: bash studio/tools/render_post.sh projects/X/carousel/slides.html N [out_prefix]
#   -> carousel/all.png, carousel/slide_1..N.png, output/<prefix>_1..N.jpg, work/post_sheet.jpg (all slides, small)
set -euo pipefail
html="$(realpath "${1:?html}")"; n="${2:?slide count}"; dir="$(dirname "$html")"; proj="$(dirname "$dir")"
prefix="${3:-post}"
shell=$(ls /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell | head -1)
"$shell" --no-sandbox --allow-file-access-from-files --hide-scrollbars --virtual-time-budget=3000 \
  --window-size=1080,$((1350*n)) --screenshot="$dir/all.png" "file://$html" >/dev/null 2>&1
mkdir -p "$proj/output" "$proj/work"
python3 -I - "$dir" "$proj" "$n" "$prefix" <<'PY'
import sys
from PIL import Image
d, proj, n, pre = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
im = Image.open(f"{d}/all.png").convert("RGB")
thumbs = []
for i in range(n):
    s = im.crop((0, 1350 * i, 1080, 1350 * (i + 1)))
    s.save(f"{d}/slide_{i+1}.png")
    s.save(f"{proj}/output/{pre}_{i+1}.jpg", quality=95, subsampling=0)
    thumbs.append(s.resize((360, 450), Image.LANCZOS))
cols = min(n, 4); rows = (n + cols - 1) // cols
sheet = Image.new("RGB", (cols * 370 + 10, rows * 460 + 10), (40, 36, 33))
for i, t in enumerate(thumbs):
    sheet.paste(t, (10 + (i % cols) * 370, 10 + (i // cols) * 460))
sheet.save(f"{proj}/work/post_sheet.jpg", quality=88)
print(f"{n} slides -> {proj}/output/{pre}_1..{n}.jpg ; review: {proj}/work/post_sheet.jpg")
PY
