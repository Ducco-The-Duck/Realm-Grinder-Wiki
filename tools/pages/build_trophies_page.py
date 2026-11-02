"""Generate docs/trophies.html (self-contained, data embedded) from data/trophies.json.

Layout mirrors the in-game trophy screen: sections by category, 7-column icon grid, tiers of the
same trophy type collapsed into one cell (click for a popup of every tier), tooltips on hover.

    python -I tools/pages/build_trophies_page.py
"""
import json, os, re, sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('extract', 'export', 'manual', 'pages', 'checks')]
import tmpl
ROOT =os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
trophies = json.load(open(os.path.join(ROOT, 'data', 'generated/trophies.json'), encoding='utf8'))
icons = json.load(open(os.path.join(ROOT, 'data', 'generated/icons.json')))

CATEGORIES = {0: 'Allegiances', 1: 'Miscellaneous', 2: 'Magic', 3: 'Building', 4: 'Secret'}
# 'special' entries (56) are internal: 53 have no icon and mirror upgrades, so they are not shown. Event trophies
# ('seasonal') are left out on purpose; so are the excavation finds, which live on the Archaeology page.


def pretty(t):
    t = re.sub(r'\d+$', '', t or '')
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', t)


_BLD = {re.sub(r"[^a-z]", '', b['name'].lower()): b.get('name_plural') or b['name']
        for b in json.load(open(os.path.join(ROOT, 'data', 'derived/buildings.json'), encoding='utf8'))}
STACK_TITLES = {'Gain Coin': 'Coins', 'Gain Coin Clicking': 'Coins from Clicks', 'Click Treasure': 'Clicks',
                'Find Faction Coin': 'Faction Coins', 'Have Assistants': 'Assistants', 'Find Artifact': 'Artifacts',
                'Gain Gem': 'Gems', 'Gain Ruby': 'Rubies', 'Purchase Upgrade': 'Upgrades', 'Gain Reincarnate': 'Reincarnations',
                'Spend Mana': 'Mana', 'Cast Spell': 'Spells', 'Unlock Spell Tier': 'Arcane Brilliance',
                'Build Building': 'Buildings'}


def stack_title(t):
    """the name shown for a stack of tiers: what the trophies count, e.g. Coins, Spells, Farms"""
    p = pretty(t)
    if p in STACK_TITLES: return STACK_TITLES[p]
    if p.startswith('Build '):
        return _BLD.get(re.sub(r"[^a-z]", '', p[6:].lower()), p[6:] + 's')
    return p


def item(t):
    return {'n': t['name'], 'r': t['requirement'], 'i': icons.get(t['icon']) if t['icon'] else None}


def cells(items):
    """Group by trophy type (non-empty), keeping first-appearance order; tiers by registry order."""
    out, by_type = [], {}
    for t in sorted(items, key=lambda t: t['order']):
        if t['type']:
            if t['type'] not in by_type:
                by_type[t['type']] = {'title': stack_title(t['type']), 'items': []}
                out.append(by_type[t['type']])
            by_type[t['type']]['items'].append(item(t))
        else:
            out.append({'items': [item(t)]})
    return out


sections = []
listed = [t for t in trophies if t['listed']]
for cat, title in CATEGORIES.items():
    its = [t for t in listed if t['category'] == cat]
    sections.append({'title': f'{title} Trophies', 'n': len(its), 'cells': cells(its)})
assert sum(sum(len(c['items']) for c in s['cells']) for s in sections) == len(listed)
data = json.dumps(sections, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

html = tmpl.load('trophies.html')
import search_snippet
html = search_snippet.apply(html.replace('__DATA__', data).replace('__TOTAL__', str(len(listed))),
                            'Search trophy names and requirements')
os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
open(os.path.join(ROOT, 'docs', 'trophies.html'), 'w', encoding='utf8').write(html)
print('docs/trophies.html', len(html) // 1024, 'KB')
for s in sections:
    subs_ = s.get('subs') or [s]
    print(' ', s['title'], '->', sum(len(x['cells']) for x in subs_), 'cells')
