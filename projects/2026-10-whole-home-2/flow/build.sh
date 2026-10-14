#!/usr/bin/env bash
# inline the rig JSON into the composition (no fetch at render time)
cd "$(dirname "$0")/.." && python3 -I - "${1:-flow/index.tpl.html}" <<'PY'

import json
import sys
src=sys.argv[1] if len(sys.argv)>1 else 'flow/index.tpl.html'
t=open(src).read()
t=t.replace('__WHITE__', json.dumps(json.load(open('reel/assets/white/rig.json')), separators=(',',':')))
open('reel/index.html','w').write(t)
PY
