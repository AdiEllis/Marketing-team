#!/usr/bin/env bash
# Scaffold a project: projects/<YYYY-MM-name>/{input,work,reel/assets,carousel,output} + PROJECT.md,
# with the reel kit, fonts, GSAP, logos and post template already in place (no copying by hand, no CDN).
# Usage: bash studio/tools/new_project.sh 2026-11-oak-kitchen
set -euo pipefail
name="${1:?usage: new_project.sh <YYYY-MM-name>}"
root="$(cd "$(dirname "$0")/../.." && pwd)"
p="$root/projects/$name"
[ -e "$p" ] && { echo "exists: $p"; exit 1; }
mkdir -p "$p"/{input,work,reel/assets,carousel,output}
A="$root/studio/assets"; L="$root/studio/lib"
cp "$A/gsap.min.js" "$A/heebo.ttf" "$A/plex-Light.ttf" "$A/logo_light.png" "$L/reel-kit.js" "$L/reel-kit.css" "$p/reel/assets/"
cp "$L/reel-template.html" "$p/reel/index.html"
cp "$L/hyperframes.json" "$p/reel/hyperframes.json"
cp "$A"/plex-*.ttf "$A/Karantina-300-hebrew.woff2" "$A/heebo.ttf" "$A/logo_light.png" "$A/logo_alpha.png" "$p/carousel/"
cp "$L/post-template.html" "$p/carousel/slides.html"
cat > "$p/PROJECT.md" <<EOF
# $name

**הבריף שלה (מילה במילה):**
**מצב:** חסכוני / "בלי אישור" / "הפקה מלאה"

## הרעיון (כפי שאושר בכרטיס)
- רילס:
- פוסט: תמונות בלבד (P16): אילו תמונות נבחרו ולמה, ומה תוקן בכל אחת

## כיסוי בריף
| פרט | רילס | פוסט |
|---|---|---|

## סטטוס וסבבים
EOF
echo "created $p"
