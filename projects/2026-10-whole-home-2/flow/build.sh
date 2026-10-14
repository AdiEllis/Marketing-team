#!/usr/bin/env bash
# inline the rig JSON into the composition (no fetch at render time)
cd "$(dirname "$0")/.." && python3 -I -c "
import json
t=open('flow/index.tpl.html').read()
t=t.replace('__WHITE__', json.dumps(json.load(open('reel/assets/white/rig.json')), separators=(',',':')))
open('reel/index.html','w').write(t)"
