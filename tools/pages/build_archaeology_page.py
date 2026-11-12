"""Generate docs/archaeology.html from data/artifacts.json.

    python -I tools/pages/build_archaeology_page.py
"""
import json, os, sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('extract', 'export', 'manual', 'pages', 'checks')]
import tmpl
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
import artifact_items
from artifact_items import artifacts, icons, item      # the artifact as the pages show it (shared with the pages that show one beside a text)


sections = []
for kind, label in (('quest', 'Quest Artifacts'), ('lore', 'Lore Artifacts')):
    its = sorted((a for a in artifacts if a['kind'] == kind), key=lambda a: a['order'])
    sections.append({'title': label, 'n': len(its), 'items': [item(a) for a in its]})

json.dump(icons, open(os.path.join(ROOT, 'data', 'generated/icons.json'), 'w'), indent=0, sort_keys=True)
data = json.dumps(sections, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
total = sum(len(s['items']) for s in sections)
import catalog
catalog.write('artifact', {'items': catalog.unique('artifact', [(it['n'], it) for s in sections for it in s['items']])})      # for the tray

html = tmpl.load('archaeology.html')
import search_snippet
html = search_snippet.apply(html.replace('__DATA__', data).replace('__TOTAL__', str(total)),
                            'Search artifact names, hints and flavor text')
open(os.path.join(ROOT, 'docs', 'archaeology.html'), 'w', encoding='utf8').write(html)
print('docs/archaeology.html', len(html) // 1024, 'KB;', [s['title'] for s in sections])
