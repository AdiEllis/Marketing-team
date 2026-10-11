#!/usr/bin/env bash
# Render slides.html -> all.png -> draft_N.png/jpg (JPEG 95, 4:4:4). Run from carousel/.
set -e
HS=$(ls /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell | head -1)
$HS --no-sandbox --allow-file-access-from-files --virtual-time-budget=3000 --hide-scrollbars --window-size=1080,5400 --screenshot=all.png "file://$PWD/slides.html" 2>/dev/null
python3 -I -c "
from PIL import Image
a=Image.open('all.png').convert('RGB')
for i in range(4):
  s=a.crop((0,i*1350,1080,(i+1)*1350)); s.save(f'draft_{i+1}.png'); s.save(f'draft_{i+1}.jpg',quality=95,subsampling=0)
s=a.resize((540,2700)); s.save('../work/post_sheet.jpg',quality=88)"
