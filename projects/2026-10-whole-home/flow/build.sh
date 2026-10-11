#!/usr/bin/env bash
# inline the rig JSON into the composition (no fetch at render time)
cd "$(dirname "$0")/.." && python3 -I -c "
import json
t=open('flow/index.tpl.html').read()
for n in ('oak','white'):
    t=t.replace('__%s__'%n.upper(), json.dumps(json.load(open('reel/assets/%s/rig.json'%n)), separators=(',',':')))
open('reel/index.html','w').write(t)"
