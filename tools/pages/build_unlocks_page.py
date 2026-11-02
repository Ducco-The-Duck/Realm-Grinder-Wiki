"""Generate docs/mechanics.html (every mechanic, one section each) and docs/unlocks-a0.html ... unlocks-a4.html (what is unlocked at each Ascension)
from data/handwritten/unlocks.json (hand-written).

    python -I tools/pages/build_unlocks_page.py
"""
import json, os, sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('extract', 'export', 'manual', 'pages', 'checks')]
import tmpl
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
d = json.load(open(os.path.join(ROOT, 'data', 'handwritten/unlocks.json'), encoding='utf8'))
MAXA = d['max_ascension']

html = tmpl.load('unlocks.html')
import search_snippet
hrefs = dict(search_snippet.mechanics_list())
for m in d['mechanics']:
    m['id'] = search_snippet.mech_slug(m['name'])
    m['href'] = hrefs[m['name']]


def write(fn, title, sub, mode, asc, mechs):
    data = json.dumps({'mechanics': mechs}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\/')
    page = html.replace('__DATA__', data).replace('__TITLE__', title).replace('__SUB__', sub).replace('__UC__', search_snippet.UNDER_CONSTRUCTION).replace('__FILE__', fn).replace('__MODE__', mode).replace('__ASC__', str(asc))
    page = search_snippet.apply(page, '', fn).replace('<title>' + title + '</title>', '<title>Realm Grinder ' + title + '</title>')
    open(os.path.join(ROOT, 'docs', fn), 'w', encoding='utf8').write(page)


write('mechanics.html', 'Mechanics', 'How the game mechanics work. Under each name is when it becomes available.', 'mechanics', 0, d['mechanics'])
for a in range(MAXA + 1):
    write(f'unlocks-a{a}.html', f'Unlocks (Ascension {a})', f'What is unlocked at Ascension {a}.', 'unlocks', a, [m for m in d['mechanics'] if m.get('unlockable')])      # only what needs unlocking ("unlockable": true)
print(f'docs/mechanics.html, docs/unlocks-a0..a{MAXA}.html;', len(d['mechanics']), 'mechanics')
