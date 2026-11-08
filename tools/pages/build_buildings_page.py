"""Generate docs/buildings.html: the 11 base buildings as a list; clicking one shows its base production and the cost of buying more of it.

    python -I tools/pages/build_buildings_page.py

The names, first prices and base productions come from data/derived/buildings.json (read from the game code); the explaining texts, the cost
formula and the list of cost reductions are hand-written in data/handwritten/buildings.json (their numbers are checked against the code by
tools/checks/verify_formulas.py --buildings).
"""
import json, os, sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('extract', 'export', 'manual', 'pages', 'checks')]
import tmpl, search_snippet
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
TICKS = 30      # the code gives the production per tick; the game runs 30 ticks a second (the production code divides the per-second amounts by 30)
ALIGN = (1, 2, 3)      # Good, Evil, Neutral: the order the game lists the three lines in

derived = json.load(open(os.path.join(ROOT, 'data', 'derived/buildings.json'), encoding='utf8'))
hand = json.load(open(os.path.join(ROOT, 'data', 'handwritten/buildings.json'), encoding='utf8'))

slots = []
for i in range(1, 12):
    row = [b for b in derived if b['building_index'] == i]
    row.sort(key=lambda b: ALIGN.index(b['alignment']) if b.get('alignment') in ALIGN else 0)
    assert len({b['cost'] for b in row}) == 1 and len({b.get('base_production') for b in row}) == 1, i      # one price and production for every line of a tier
    names = [b['name'] for b in row]
    slots.append({'i': i, 'id': names[0].lower().replace(' ', '-'), 'names': names, 'cost': row[0]['cost'],
                  'prod': None if row[0].get('base_production') is None else round(row[0]['base_production'] * TICKS, 6)})
assert len(slots) == 11

# the game's building buttons (130 x 57; one set per alignment) for the list
import shutil
SRC = os.path.join(ROOT, 'assets', 'sprites', 'realmgrinderui_new')
DST = os.path.join(ROOT, 'docs', 'assets', 'ui', 'buildings')
os.makedirs(DST, exist_ok=True)
for al in ('good', 'evil', 'neutral'):
    for st in ('Up', 'Hover', 'Down'):
        f = f'{al}Building_{st}.png'
        if os.path.exists(os.path.join(SRC, f)): shutil.copyfile(os.path.join(SRC, f), os.path.join(DST, f))
        elif not os.path.exists(os.path.join(DST, f)): sys.exit('missing sprite ' + f + ' (run tools/extract/slice_atlases.py)')

# the building icons (50 x 50), one per building
sprites = json.load(open(os.path.join(ROOT, 'data', 'derived/sprites.json'), encoding='utf8'))
ICONS = os.path.join(DST, 'icons')
os.makedirs(ICONS, exist_ok=True)
for b in derived:
    f = b['internal_name'] + '.png'
    src = os.path.join(ROOT, sprites['Building' + b['internal_name']][0]['file'])
    if os.path.exists(src): shutil.copyfile(src, os.path.join(ICONS, f))
    elif not os.path.exists(os.path.join(ICONS, f)): sys.exit('missing icon ' + f)
for sl in slots:
    sl['icons'] = ['assets/ui/buildings/icons/' + b['internal_name'] + '.png' for b in sorted((b for b in derived if b['building_index'] == sl['i']), key=lambda b: ALIGN.index(b['alignment']) if b.get('alignment') in ALIGN else 0)]

# the unique buildings: every unique building upgrade of the Upgrades data (faction, first Ascension, Ascensions without it, formula), and the slot it replaces
from factions import FSEARCH, FNAME
pages = json.load(open(os.path.join(ROOT, 'data', 'generated/upgrade_pages.json'), encoding='utf8'))
ups = {u['name']: u for lst in pages.values() if isinstance(lst, list) for u in lst if isinstance(u, dict) and u.get('akind') == 'unique' and not u['name'].endswith(' Quest')}
import re
import verify_formulas      # path_of / read: the game's class files
upname = {u['class']: u.get('name') for u in json.load(open(os.path.join(ROOT, 'data', 'derived/upgrades.json'), encoding='utf8')) if u.get('class')}
places = {}      # unique name -> (slot, the alignments of the building lines that carry it)
for b in derived:      # the unique building upgrades a building class lists (read from the class: `§9;§[n] = Upgrade.id`)
    text = verify_formulas.read(verify_formulas.path_of(b['class']))
    imports = {m.group(1).rsplit('.', 1)[-1]: m.group(1) for m in re.finditer(r'^\s*import (.+);\s*$', text, re.M)}
    for m in re.finditer(r'§9;§\[\d\] = (§[^§]*§)\.id', text):
        nm = upname[imports[m.group(1)]]
        sl, al = places.setdefault(nm, (b['building_index'], []))
        assert sl == b['building_index'], nm
        al.append(b.get('alignment'))
assert set(places) == set(ups), (set(places) ^ set(ups))
UICONS = os.path.join(DST, 'icons')
SINGULAR = {'Stonehenge'}      # the game's only unique building name that has no plural form ("Upgrade Stone Pillars to Stonehenge")


def unique_text(t):
    """the game's "Upgrade A to B, boosting their production ..." as "B boost their production ..." (the unique building is the subject)"""
    head, sep, rest = t.partition(', boosting')
    if not sep or not head.startswith('Upgrade ') or ' to ' not in head: return t
    new = head.rsplit(' to ', 1)[1]
    if new in SINGULAR: return new + ' boosts' + rest.replace(' their ', ' its ', 1)
    return new + ' boost' + rest


uniques = []
for nm, (sl, al) in places.items():
    u = ups[nm]
    src = os.path.join(ROOT, sprites['Building' + nm][0]['file'])
    slug = ''.join(c for c in nm if c.isalnum())
    if os.path.exists(src): shutil.copyfile(src, os.path.join(UICONS, slug + '.png'))
    elif not os.path.exists(os.path.join(UICONS, slug + '.png')): sys.exit('missing icon ' + nm)
    ucls = next(c for c, n in upname.items() if n == nm)
    ral = re.search(r'§,!Y§ = (\d);', verify_formulas.read(verify_formulas.path_of(ucls)))      # the alignment the upgrade needs (the Mercenary buildings: one per alignment)
    main = next(p for p in u['description'] if p.get('formulas'))      # the paragraph that says what the upgrade does
    fl = [{'latex': f['latex'], 'vars': [[v['symbol'], v['text']] for v in f.get('vars', [])]} for p in u['description'] for f in p.get('formulas', [])]
    uniques.append({'n': nm, 'f': u['faction'], 'fn': FSEARCH[u['faction']], 's': sl, 'al': None if (None in al or 0 in al) else al,
                    'ra': int(ral.group(1)) if ral and int(ral.group(1)) else None, 'a0': u.get('asc_min') or 0, 'an': u.get('asc_not') or [], 'ic': 'assets/ui/buildings/icons/' + slug + '.png', 'fm': fl, 'd': unique_text(main['text']), 'ps': main.get('s'), 'pn': bool(main.get('np')), 'fc': FNAME[u['faction']].lower()})
for fc in sorted({u['fc'] for u in uniques}):      # the game's building buttons of the factions (130 x 57), for the unique buildings
    for st in ('Up', 'Hover', 'Down'):
        f = f'{fc}Building_{st}.png'
        if os.path.exists(os.path.join(SRC, f)): shutil.copyfile(os.path.join(SRC, f), os.path.join(DST, f))
        elif not os.path.exists(os.path.join(DST, f)): sys.exit('missing sprite ' + f)
FACCSS = '''#list button.f-FC .pl{background-image:url(assets/ui/buildings/FCBuilding_Up.png)}
#list button.f-FC:hover .pl{background-image:url(assets/ui/buildings/FCBuilding_Hover.png)}
#list button.f-FC[aria-pressed="true"] .pl{background-image:url(assets/ui/buildings/FCBuilding_Down.png)}
'''
faccss = ''.join(FACCSS.replace('FC', fc) for fc in sorted({u['fc'] for u in uniques}))
uniques.sort(key=lambda u: (u['s'], u['n']))

from factions import FACTIONS
data = json.dumps({'buildings': slots, 'uniques': uniques, 'factions': FACTIONS, 'production': hand['production'], 'hall': hand['hall'], 'cost': hand['cost'],
                   'unique': hand['unique'], 'notes': hand['notes']},
                  ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
import html as _html
_mech = next(m for m in json.load(open(os.path.join(ROOT, 'data', 'handwritten/unlocks.json'), encoding='utf8'))['mechanics'] if m['name'] == 'Buildings')
BLURB = _html.escape(next(s for s in _mech['sections'] if s['title'] == 'What they are')['text'])      # the same text as on the Mechanics page
page = search_snippet.apply(tmpl.load('buildings.html').replace('__DATA__', data).replace('__BLURB__', BLURB).replace('/*FACCSS*/', faccss), '', 'buildings.html')
open(os.path.join(ROOT, 'docs', 'buildings.html'), 'w', encoding='utf8').write(page)
print('docs/buildings.html', len(page) // 1024, 'KB;', len(slots), 'buildings')
