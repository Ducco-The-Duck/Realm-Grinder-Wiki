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
for m in d['mechanics']:
    m['id'] = search_snippet.mech_slug(m['name'])
    m['href'] = m.get('page') or 'mechanics.html#' + m['id']


def upgrade_cards():
    """the upgrades that the written Unlocks pages name ("upgrades" of a section): {name: card} with the icon, the game's description and the cost at each Ascension"""
    import shutil, costs
    want = []
    for pg in d.get('ascension_pages', {}).values():
        for e in pg['entries']:
            for sec in e.get('sections', []):      # the upgrades of a section: in a row ("upgrades"), at its right ("side"), or at the right of each item of a list (the "upgrades" of the list)
                want += sec.get('upgrades', []) + sec.get('side', []) + [u for l in sec.get('lists', []) for u in l.get('upgrades', []) + l.get('side', [])]
    want = list(dict.fromkeys(want))
    pages = json.load(open(os.path.join(ROOT, 'data', 'generated/upgrade_pages.json'), encoding='utf8'))
    page_items = {u['name']: u for lst in pages.values() if isinstance(lst, list) for u in lst if isinstance(u, dict) and u.get('name') in want}
    derived = {u['name']: u for u in json.load(open(os.path.join(ROOT, 'data', 'derived/upgrades.json'), encoding='utf8')) if u.get('name') in want and u.get('class')}
    sprites = json.load(open(os.path.join(ROOT, 'data', 'derived/sprites.json')))
    ix = costs.engine_find(want)
    ec = costs.engine_costs([ix[n] for n in want if n not in costs.NO_COST])
    out = {}
    for n in want:
        assert n in ix and (n in page_items or n in derived), ('upgrade not found in the game data', n)
        if n in page_items: icon, desc = page_items[n]['icon'], [p['text'] for p in page_items[n]['description']]
        else: icon, desc = derived[n]['icon'], [derived[n]['description']]
        dst = os.path.basename(sprites[icon][0]['file'])      # the icon is copied from the game assets to docs/assets/icons
        path = os.path.join(ROOT, 'docs', 'assets', 'icons', dst)
        if not os.path.exists(path): shutil.copy(os.path.join(ROOT, sprites[icon][0]['file']), path)
        gn, cs = (n, [None] * (costs.MAXA + 1)) if n in costs.NO_COST else ec[ix[n]]
        assert gn == n, (gn, n)
        out[n] = {'n': n, 'i': dst, 'd': desc, 's': [f"{x['kind']}: {x['name']}" for x in page_items[n]['sources']] + page_items[n]['requirements'] if n in page_items else [], 'c': [None if x is None else [int(x[0]) if x[0] < 1e15 and x[0] == int(x[0]) else x[0], [[i, int(v)] for i, v in x[1]]] for x in cs]}
    return out


UPS = upgrade_cards()
import artifact_items
_FU = json.load(open(os.path.join(ROOT, 'data', 'derived/faction_upgrades.json'), encoding='utf8'))
FU_ITEMS = {**_FU['items'], **_FU['umbrella']}      # the upgrades as the Upgrades pages show them (written by build_upgrades_page.py)
ITEMS = {n: FU_ITEMS[n] for n in dict.fromkeys(n for m in d['mechanics'] for s in m.get('sections', []) for n in s.get('side', []))}      # the upgrades shown beside a text of a mechanic ("side")
ARTS = artifact_items.by_name(list(dict.fromkeys(a for m in d['mechanics'] for s in m.get('sections', []) for l in s.get('lines', []) for a in l.get('artifacts', []))))      # the artifacts shown beside a line of a mechanic
COINS = __import__('costs').names()      # the game's names of the coins
RUNLOCKS = d['reincarnation_unlocks']      # the table on the overall Unlocks page (hand-written)


def write(fn, title, sub, mode, asc, mechs):
    data = json.dumps({'mechanics': mechs, 'rows': RUNLOCKS, 'page': d.get('ascension_pages', {}).get(str(asc)) if mode == 'unlocks' else None, 'ups': UPS if mode == 'unlocks' else {}, 'arts': ARTS, 'items': ITEMS, 'coins': COINS},ensure_ascii=False, separators=(',', ':')).replace('</', '<\/')
    page = html.replace('__DATA__', data).replace('__TITLE__', title).replace('__SUB__', sub).replace('__UC__', search_snippet.UNDER_CONSTRUCTION).replace('__FILE__', fn).replace('__MODE__', mode).replace('__ASC__', str(asc))
    page = search_snippet.apply(page, '', fn).replace('<title>' + title + '</title>', '<title>Realm Grinder ' + title + '</title>')
    open(os.path.join(ROOT, 'docs', fn), 'w', encoding='utf8').write(page)


write('mechanics.html', 'Mechanics', 'How the game mechanics work.', 'mechanics', 0, d['mechanics'])
for a in range(MAXA + 1):
    write(f'unlocks-a{a}.html', f'Unlocks (Ascension {a})', f'What is unlocked at Ascension {a}.', 'unlocks', a, [m for m in d['mechanics'] if m.get('unlockable')])      # only what needs unlocking ("unlockable": true)
write('unlocks.html', 'Unlocks', 'What is unlocked at each Ascension.', 'all', MAXA, [m for m in d['mechanics'] if m.get('unlockable')])      # the overall page: every Ascension
print(f'docs/mechanics.html, docs/unlocks.html, docs/unlocks-a0..a{MAXA}.html;', len(d['mechanics']), 'mechanics')
