"""Generate docs/challenges.html from data/challenges.json.

    python -I tools/pages/build_challenges_page.py
"""
import json, os, shutil, sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('extract', 'export', 'manual', 'pages', 'checks')]
import tmpl
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
import challenge_items
from challenge_items import factions, icons, item      # the challenge as the pages show it (shared with the Factions page)


sections = [{'id': f['id'], 'name': f['name'], 'kind': f['kind'], 'items': [item(f, it) for it in f['items']]}
            for f in sorted(factions, key=lambda f: f['name'] == 'Mercenary')]      # the Mercenaries go last
json.dump(icons, open(os.path.join(ROOT, 'data', 'generated/icons.json'), 'w'), indent=0, sort_keys=True)
data = json.dumps(sections, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
import catalog
catalog.write('challenge', {'sections': {s['name']: {'name': s['name'], 'items': catalog.unique('challenge', [(it['n'], it) for it in s['items']])} for s in sections}})      # for the tray, by faction name
import html as _html
bugs = [(it['name'], it['bug']) for f in factions for it in f['items'] if it.get('bug')]
bug_html = ''.join(f'<p><b>Known bug, {_html.escape(n)}:</b> {_html.escape(t)}</p>' for n, t in bugs)
n_ch = sum(1 for f in factions for it in f['items'] if not it['spell_upgrade'])

# the blurb and the line about the Veteran Figurine: the same text as in the Challenges section of the Mechanics page (data/handwritten/unlocks.json)
import artifact_items
_sec = next(m for m in json.load(open(os.path.join(ROOT, 'data', 'handwritten/unlocks.json'), encoding='utf8'))['mechanics'] if m['name'] == 'Challenges')['sections'][0]
BLURB = _html.escape(_sec['text'])
VLINE = _html.escape(_sec['lines'][0]['text'])
VART = json.dumps(artifact_items.by_name(_sec['lines'][0]['artifacts'])[_sec['lines'][0]['artifacts'][0]], ensure_ascii=False, separators=(',', ':')).replace('</', '<\/')

html = tmpl.load('challenges.html')
import search_snippet
html = html.replace('__BLURB__', BLURB).replace('__VLINE__', VLINE).replace('__VART__', VART).replace('__BUGS__', bug_html).replace('__DATA__', data).replace('__TOTAL__', str(n_ch))
html = search_snippet.apply(html, 'Search challenge names, flavor text, challenge and reward descriptions')
open(os.path.join(ROOT, 'docs', 'challenges.html'), 'w', encoding='utf8').write(html)
print('docs/challenges.html', len(html) // 1024, 'KB;', [s['name'] for s in sections])
