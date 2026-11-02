"""Generate docs/research.html from data/generated/research.json (+ data/generated/research_meta.json).

    python -I tools/pages/build_research_page.py
"""
import json, os, re, shutil, sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('extract', 'export', 'manual', 'pages', 'checks')]
import tmpl
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
research = json.load(open(os.path.join(ROOT, 'data', 'generated/research.json'), encoding='utf8'))
meta = json.load(open(os.path.join(ROOT, 'data', 'generated/research_meta.json')))
sprites = json.load(open(os.path.join(ROOT, 'data', 'derived/sprites.json')))
icons = json.load(open(os.path.join(ROOT, 'data', 'generated/icons.json')))
icon_dir = os.path.join(ROOT, 'docs', 'assets', 'icons')
os.makedirs(icon_dir, exist_ok=True)


def icon_file(name):
    """Copy the sprite into docs/assets/icons if needed and return its file name."""
    if name not in sprites: return None
    dst = os.path.basename(sprites[name][0]['file'])
    path = os.path.join(icon_dir, dst)
    if not os.path.exists(path):
        src = os.path.join(ROOT, sprites[name][0]['file'])
        if os.path.exists(src): shutil.copy(src, path)
    if not os.path.exists(path): return None
    icons[name] = dst
    return dst


# where extra research slots come from (read from the game's slot function); branch index -> data
SLOT_UPGRADE = {0: 'Magician', 1: 'Artisan', 2: 'Demigod', 3: 'Businessman', 4: 'Apothecary', 5: 'Warlord'}
MERC_ALIGN = {0: 'Good', 2: 'Good', 3: 'Evil', 5: 'Evil', 1: 'Neutral', 4: 'Neutral'}
NEUTRAL_AFFINITY = {0: 'Faceless', 1: 'Titan', 2: 'Faceless', 3: 'Druid', 4: 'Druid', 5: 'Titan'}
BASE_FACTION = {0: 'Fairy', 1: 'Elf', 2: 'Angel', 3: 'Goblin', 4: 'Undead', 5: 'Demon'}


def slot_sources(b):
    """[delta, text, from Ascension, until Ascension (exclusive)]; the page keeps the rows of the chosen Ascension"""
    rows = [
        ['-1', 'Mercenary', 1, 2],
        ['+1', f'Secret Trophy: {SLOT_UPGRADE[b]}', 0, 2],
        ['+1', 'Reincarnation Power, from Reincarnation 90', 1, 2],
        ['+1', f'Reincarnation Power, from Reincarnation 75 ({MERC_ALIGN[b]} Mercenary)', 1, 2],
        ['+1', f'Ancient Device Power ({NEUTRAL_AFFINITY[b]})', 0, 2],
    ]
    if b == 1:
        rows.append(['+2', 'Legacy of the Dwarven Kings', 0, 2])
    if b == 5:
        rows.append(['+2', 'Dark Light of Bondelnar', 0, 2])
    # Dwarf is the prestige faction of the Good base factions, Drow of the Evil ones, so only one of the two applies
    rows.append(['+1', f"{'Legacy of the Dwarven Kings' if b < 3 else 'Dark Light of Bondelnar'} ({BASE_FACTION[b]})", 0, 2])
    rows.append(['+1 or more', 'Archon Bloodline', 2, 3])
    return rows


# ---- research budget (Ascension 3 and 4): the slots are replaced by a budget per branch ----------------------------------
BUDGET_COMMON = [
    {'n': 'Reincarnation Power', 'q': 'From Reincarnation 170',
     'l': r'v = 150 \cdot A + 3.5 \cdot \left(R - 159\right)',
     'v': [['A', 'Your Ascension number'],
           ['R', 'Reincarnations made, counting the effects that make Reincarnations count more (for example Prismatic Breath from the Dragon Challenge)']],},
    {'n': 'Archon Bloodline',
     'l': r'v = \left(\ln\left(1 + t\right)\right)^{3}', 'v': [['t', 'Time played in this Era (seconds)']],},
    {'n': 'Faceless Set, Set Bonus 2',
     'l': r'v = \min\left(3000,\; \left(\ln\left(1 + F\right)\right)^{1.5}\right)',
     'v': [['F', 'Faction Coins found in this Era']],},
    {'n': 'Goblin Perk 6',
     'l': r'v = \min\left(3000,\; 4 \cdot W^{0.5}\right)', 'v': [['W', "Tax Collection's worth"]],},
    {'n': 'Dwarven Perk 6',
     'l': r'v = \min\left(3000,\; 0.6 \cdot D^{0.6}\right)', 'v': [['D', 'Excavation depth']],},
]
BUDGET_MERC = [
    {'n': 'Mercenary First Contract', 'l': r'v = 500', 'v': [],},
    {'n': 'Mercenary Fourth Contract', 'l': r'v = 1000', 'v': [],},
    {'n': 'Mercenary Magic Contract and Sorcery Contract',
     'l': r'v = w \cdot \min\left(5000,\; 1000 + 5 \cdot \sqrt{t}\right)',
     'v': [['t', 'Activity time of the spell you tied the contract to'], ['w', 'The weight of that spell\'s faction in this branch (listed below)']],},
    {'n': 'Mercenary Union Contracts',
     'l': r'v = w \cdot 400 \cdot n', 'v': [['n', 'Upgrades you have bought from that faction'], ['w', 'The weight of that faction in this branch (listed below)']],},
]
BUDGET_A4 = [
    {'n': 'Homunculus Lab', 'q': 'Goblin/Undead legacy combo', 'a': 4,
     'l': r'v = \min\left(3000,\; 50 + 1.15 \cdot \left(\ln\left(1 + \min\left(T_{O}, T_{B}\right)\right)\right)^{3.15}\right)',
     'v': [['T_{O}', 'Time spent with Order alignment in this Reincarnation (seconds)'], ['T_{B}', 'Time spent with Balance alignment in this Reincarnation (seconds)']],},
    {'n': 'Trade Treaty', 'l': r'v = 5000', 'v': [], 'a': 4},
    {'n': 'Union', 'l': r'v = 5000', 'v': [], 'a': 4},
]
# the research facility upgrade of each branch: name, alignment, axis (stat indexes 2/3 = Good/Evil time, 48/36/14 = Order/Chaos/Balance time)
FACILITY = {0: ('Mana Loom', 'Good', 'Chaos'), 1: ('Factory', 'Good', 'Balance'), 2: ('Mythos', 'Good', 'Order'),
            3: ('Vault', 'Evil', 'Balance'), 4: ('Athanor', 'Evil', 'Order'), 5: ('Battlefield', 'Evil', 'Chaos'), 6: ('Apeiron', None, None)}
FAC_NAME = {0: 'Fairy', 1: 'Elf', 2: 'Angel', 3: 'Goblin', 4: 'Undead', 5: 'Demon', 6: 'Titan', 7: 'Druid', 8: 'Faceless', 9: 'Dwarf', 10: 'Drow',
            12: 'Dragon', 13: 'Archon', 14: 'Djinn', 15: 'Makers'}


def merc_weight(branch, fac):
    """how much of a Mercenary contract's value a faction's branch gets (the game's weighting function, in its own order)"""
    if fac == 12 and branch != 6: return 0.15
    if branch == 6: return 0.2
    if fac == branch and fac <= 5: return 1
    for f, bs, w in ((6, (2, 3), .5), (7, (1, 5), .5), (8, (0, 4), .5), (9, (0, 1, 2), .35), (10, (3, 4, 5), .35),
                     (13, (2, 4), .5), (14, (0, 5), .5), (15, (1, 3), .5)):
        if fac == f and branch in bs: return w
    return 0


def budget_for(b):
    name, a, x = FACILITY[b]
    if a:
        ent = {'n': f'{name} (research facility upgrade)',
               'l': r'v = 500 + \left(\ln\left(1 + \sqrt{a \cdot b}\right)\right)^{3}',
               'v': [['a', f'Time spent with {a} alignment in this Reincarnation (seconds)'], ['b', f'Time spent with {x} alignment in this Reincarnation (seconds)']],}
    else:
        ent = {'n': 'Apeiron (research facility upgrade)',
               'l': r'v = 500 + 0.75 \cdot \left(\ln\left(1 + \max_{i} \sqrt{a_{i} \cdot b_{i}}\right)\right)^{3}',
               'v': [['a_{i} \\cdot b_{i}', 'The six products of the time spent with an alignment (Good or Evil) and the time spent with an axis (Order, Chaos or Balance) in this Reincarnation (seconds); the largest counts']],}
    weights = [[FAC_NAME[f], merc_weight(b, f)] for f in sorted(FAC_NAME) if merc_weight(b, f)]
    if len({w for _, w in weights}) == 1 and len(weights) > 3: weights = [['Every faction', weights[0][1]]]      # the Forbidden branch weighs them all the same
    return {'fac': ent, 'w': weights}


BRANCHES = []
for b in range(7):
    its = sorted((r for r in research if r['branch'] == b), key=lambda r: (r['number'], r['index']))
    if not its: continue
    name = its[0]['branch_name']
    bicon = icon_file('Research' + name)
    items = []
    tight = lambda t: re.sub(r'\n{2,}', '\n', t) if t else t      # no blank line between the lines of a description
    TIER_COST_NOTE = 'See the Spells page for more on tier cost scaling.'
    BUILDING_COST = 'See the Buildings page for more on the building cost multiplier.'
    EXCAVATION_COST = 'See the Excavations page for more on the excavation cost multiplier.'
    EXCHANGE_COST = 'See the Royal Exchanges page for more on the Royal Exchange cost multiplier.'
    EXCHANGE_ASC = 'See the Royal Exchanges page for more on the Ascension multiplier.'
    NOTES = {'S1275': [TIER_COST_NOTE], 'E50': [BUILDING_COST], 'E135': [BUILDING_COST], 'E270': [EXCAVATION_COST], 'E1325': [EXCHANGE_COST],
             'E13125': [EXCHANGE_COST, EXCAVATION_COST, BUILDING_COST], 'E11125': [BUILDING_COST], 'E1225': [EXCHANGE_ASC]}      # faded notes pointing to the pages that explain the cost multipliers
    for r in its:
        items.append({
            'n': r['name'], 'k': f"{r['code']} · {name} {r['number']:,}", 'i': icon_file(f"Research{r['number']}"), 'b': bicon,
            'd': tight(r['description']), 'q': r['requirements'], 'h': r['hint'],
            'u': r['unavailable_from'], 'm': r['mercenary_exception'], 'nm': r['number'],
            'nt': NOTES.get(r['code']),
            'fn': r['faction_name'], 'fk': r['faction_kind'], 'fc': meta['faction_colors'].get(str(r['faction'])),
            'mn': r['mercenary_note'], 'al': r['alignment_lock'], 'an': r['alignment_not'],
            'ac': meta['alignment_colors'].get(r['alignment_lock'] or ''),
            'a': {k: {'d': tight(v['description']), 'q': v['requirements']} for k, v in r['by_ascension'].items()},
            'ps': r.get('pen'),
            'f': [{'l': f['latex'], 'v': f['vars'], 's': f.get('scale'), 'lb': f.get('label')} for f in r['formulas']],
        })
    BRANCHES.append({'name': name, 'icon': bicon, 'items': items, 'sl': slot_sources(b) if b in SLOT_UPGRADE else None, 'bud': budget_for(b)})

json.dump(icons, open(os.path.join(ROOT, 'data', 'generated/icons.json'), 'w'), indent=0, sort_keys=True)
payload = {'max': meta['max_ascension'], 'branches': BRANCHES,
           'budget': {'common': BUDGET_COMMON, 'a4': BUDGET_A4, 'merc': BUDGET_MERC}}
data = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
total = sum(len(b['items']) for b in BRANCHES)

html = tmpl.load('research.html')
import search_snippet, availability
html = html.replace('__MAXNUM__', json.dumps(availability.MAXNUM)).replace('__DATA__', data).replace('__TOTAL__', str(total)).replace('__BRANCHES__', str(len(BRANCHES)))
html = search_snippet.apply(html, 'Search research names, hints and descriptions')
open(os.path.join(ROOT, 'docs', 'research.html'), 'w', encoding='utf8').write(html)
print('docs/research.html', len(html) // 1024, 'KB;', [(b['name'], len(b['items'])) for b in BRANCHES],
      'no icon:', sum(1 for b in BRANCHES for it in b['items'] if not it['i']), '| max Ascension', meta['max_ascension'])
