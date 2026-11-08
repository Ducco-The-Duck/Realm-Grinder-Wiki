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

data = json.dumps({'buildings': slots, 'production': hand['production'], 'hall': hand['hall'], 'cost': hand['cost']},
                  ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
import html as _html
_mech = next(m for m in json.load(open(os.path.join(ROOT, 'data', 'handwritten/unlocks.json'), encoding='utf8'))['mechanics'] if m['name'] == 'Buildings')
BLURB = _html.escape(next(s for s in _mech['sections'] if s['title'] == 'What they are')['text'])      # the same text as on the Mechanics page
page = search_snippet.apply(tmpl.load('buildings.html').replace('__DATA__', data).replace('__BLURB__', BLURB), '', 'buildings.html')
open(os.path.join(ROOT, 'docs', 'buildings.html'), 'w', encoding='utf8').write(page)
print('docs/buildings.html', len(page) // 1024, 'KB;', len(slots), 'buildings')
