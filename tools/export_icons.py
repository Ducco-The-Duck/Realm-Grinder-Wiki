"""Copy the sprites referenced by entity and trophy `icon` fields into docs/assets/icons/ (committed,
served by GitHub Pages).

    python -I tools/export_icons.py      # needs assets/sprites/ from slice_atlases.py
"""
import json, os, shutil
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
idx = json.load(open(os.path.join(ROOT, 'data', 'sprites.json')))
out = os.path.join(ROOT, 'docs', 'assets', 'icons')
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
used = {}
for kind in ['upgrade', 'achievement', 'spell', 'building', 'research']:
    for r in json.load(open(os.path.join(ROOT, 'data', f'{kind}s.json'), encoding='utf8')):
        ic = r.get('icon')
        if ic and ic in idx and ic not in used:
            src = os.path.join(ROOT, idx[ic][0]['file'])
            shutil.copy(src, os.path.join(out, os.path.basename(src)))
            used[ic] = os.path.basename(src)
tp = os.path.join(ROOT, 'data', 'trophies.json')
if os.path.exists(tp):
    for t in json.load(open(tp, encoding='utf8')):
        ic = t.get('icon')
        if ic and ic in idx and ic not in used:
            src = os.path.join(ROOT, idx[ic][0]['file'])
            shutil.copy(src, os.path.join(out, os.path.basename(src)))
            used[ic] = os.path.basename(src)
json.dump(used, open(os.path.join(ROOT, 'data', 'icons.json'), 'w'), indent=0, sort_keys=True)
size = sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out))
print(len(used), 'icons,', size // 1024, 'KB')
