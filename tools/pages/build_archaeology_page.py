"""Generate docs/archaeology.html from data/artifacts.json.

    python -I tools/pages/build_archaeology_page.py
"""
import json, os, sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('extract', 'export', 'manual', 'pages', 'checks')]
import tmpl
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
artifacts = json.load(open(os.path.join(ROOT, 'data', 'generated/artifacts.json'), encoding='utf8'))
icons = json.load(open(os.path.join(ROOT, 'data', 'generated/icons.json')))

# artifact icons are not referenced by entity data, so make sure they are exported
import shutil
sprites = json.load(open(os.path.join(ROOT, 'data', 'derived/sprites.json')))
icon_dir = os.path.join(ROOT, 'docs', 'assets', 'icons')
os.makedirs(icon_dir, exist_ok=True)


def icon_file(a):
    n = a['icon']
    if not n: return None
    dst = os.path.basename(sprites[n][0]['file'])
    path = os.path.join(icon_dir, dst)
    if not os.path.exists(path):
        src = os.path.join(ROOT, sprites[n][0]['file'])
        if os.path.exists(src): shutil.copy(src, path)
    if not os.path.exists(path): return None
    icons[n] = dst
    return dst


def item(a):
    ch = a.get('chance', {})
    return {'n': a['name'], 'f': a['flavor'], 'h': a['hint'], 'q': a['requirements'],
            'x': a['undecoded_conditions'], 'i': icon_file(a),
            'c': ch.get('mode'), 'p': ch.get('percent'), 'l': ch.get('latex'), 'v': ch.get('vars')}


sections = []
for kind, label in (('quest', 'Quest Artifacts'), ('lore', 'Lore Artifacts')):
    its = sorted((a for a in artifacts if a['kind'] == kind), key=lambda a: a['order'])
    sections.append({'title': label, 'n': len(its), 'items': [item(a) for a in its]})

json.dump(icons, open(os.path.join(ROOT, 'data', 'generated/icons.json'), 'w'), indent=0, sort_keys=True)
data = json.dumps(sections, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
total = sum(len(s['items']) for s in sections)

html = tmpl.load('archaeology.html')
import search_snippet
html = search_snippet.apply(html.replace('__DATA__', data).replace('__TOTAL__', str(total)),
                            'Search artifact names, hints and flavor text')
open(os.path.join(ROOT, 'docs', 'archaeology.html'), 'w', encoding='utf8').write(html)
print('docs/archaeology.html', len(html) // 1024, 'KB;', [s['title'] for s in sections])
