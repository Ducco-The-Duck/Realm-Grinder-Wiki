"""Generate the four upgrade pages (Allegiance, Magic, Secret, Miscellaneous) from data/upgrade_pages.json.

    python -I tools/pages/build_upgrades_page.py
"""
import json, os, re, shutil, sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('extract', 'export', 'manual', 'pages', 'checks')]
import tmpl
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
pages = json.load(open(os.path.join(ROOT, 'data', 'generated/upgrade_pages.json'), encoding='utf8'))
meta = json.load(open(os.path.join(ROOT, 'data', 'generated/research_meta.json'), encoding='utf8'))
icons = json.load(open(os.path.join(ROOT, 'data', 'generated/icons.json')))
sprites = json.load(open(os.path.join(ROOT, 'data', 'derived/sprites.json')))
icon_dir = os.path.join(ROOT, 'docs', 'assets', 'icons')
os.makedirs(icon_dir, exist_ok=True)


def icon_file(n):
    if not n or n not in sprites: return None
    dst = os.path.basename(sprites[n][0]['file'])
    path = os.path.join(icon_dir, dst)
    if not os.path.exists(path):
        src = os.path.join(ROOT, sprites[n][0]['file'])
        if os.path.exists(src): shutil.copy(src, path)
    if not os.path.exists(path): return None
    icons[n] = dst
    return dst


def effect_label(text):
    """short noun phrase naming what a paragraph's formula gives"""
    prefix = ''
    m = re.match(r'^([^:.]{1,20}): (.*)$', text)
    if m: prefix, text = m.group(1) + ': ', m.group(2)
    t = re.split(r' based on | for each |\. ', text)[0].rstrip('.')
    t = re.sub(r'^(?:[Mm]ultiplicatively )?(?:[Ii]ncreases?|[Gg]ain|[Gg]ive|[Rr]educe|[Ll]ower) ', '', t)
    t = re.sub(r'^the ', '', t)
    return prefix + t[:1].upper() + t[1:]


_SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
from factions import FNAME, FSEARCH, FACTIONS      # the factions table is shared with the Buildings page
FORDER = [f['i'] for f in FACTIONS]


def fmt_num(n):
    n = float(n)
    if n < 1e6: return f'{int(round(n)):,}' if n == int(n) else f'{n:g}'
    m_, e_ = f'{n:.9e}'.split('e')
    mant, e = float(m_), int(e_)
    if abs(mant - round(mant)) < 1e-6: mant = round(mant)
    sup = str(e).translate(_SUP)
    return f'{mant:g}e{e}'


UNION_ICON = {9: 'DwarvenUnion', 10: 'DrowUnion', 12: 'DragonUnion'}     # their icons exist per path (Order / Chaos / Balance)


PROOF_OF = {'Proof of Good Deed': {'al': 1}, 'Proof of Evil Deed': {'al': 2}, 'Proof of Neutrality': {'al': 3},
            'Proof of Order': {'ax': 4}, 'Proof of Chaos': {'ax': 5}, 'Proof of Balance': {'ax': 6}}
KIND_ORDER = {'proof': 0, 'bloodline_c': 1, 'lineage_c': 1.2, 'set_c': 1.3, 'combo_c': 1.35, 'set': 9, 'lineage': 9, 'lineage_perk': 9, 'quest': 1.5, 'bloodline': 9, 'tier': 2, 'perk': 3, 'heritage': 4, 'spell': 6, 'unique': 7}


# notes shown (faded) right under the sentence of the description that matches the pattern: name -> (note, pattern)
TIER_COST = ('See the Spells page for more on tier cost scaling.', 'cost scaling')      # the upgrades that lower spell tier cost scaling
ASC_MULT = ('See the Royal Exchanges page for more on the Ascension multiplier.', 'Ascension multiplier')
BUILD_MULT = ('See the Buildings page for more on the building cost multiplier.', 'cost multiplier')
EXCAV_MULT = ('See the Excavations page for more on the excavation cost multiplier.', 'cost multiplier')
EXCH_MULT = ('See the Royal Exchanges page for more on the Royal Exchange cost multiplier.', 'cost multiplier')
NOTES = {'Iron Flight': TIER_COST, 'Dragon Set': TIER_COST, 'Angel Perk 1': TIER_COST,
         'Goblin Bloodline': ('See the Buildings page for more on the building cost multiplier.', 'cost multiplier'),
         'Elven Perk 1': ('Elven Luck is affected by Ascension penalties.', 'Faction Coins based on'),
         'Titan Perk 1': ('See the Buildings page for more on the building cost multiplier.', 'cost multiplier'),
         "Wyrm's Rest": ASC_MULT, 'Drow Set': ASC_MULT, 'Makers Perk 6': ASC_MULT,
         'Pixie Dust Fertilizer': BUILD_MULT, 'Lousy Architecture': BUILD_MULT, 'Oversized Legends': BUILD_MULT, 'Expert Masonry': BUILD_MULT,
         'Magic Resistance': EXCAV_MULT, 'Reality Crater': EXCAV_MULT, 'Heavy Coins': EXCH_MULT, 'Blackmail': EXCH_MULT}


import verify_formulas as _V
_spell_cls = {x['name']: x['class'] for x in json.load(open(os.path.join(ROOT, 'data', 'derived/spells.json'), encoding='utf8')) if x.get('class')}
_start = {}


def spell_start(name):
    """the Ascension a spell can first be had at: its availability check opens with `Ascension >= n &&` (the six Order, Chaos, Balance and astral spells: 2)"""
    if name not in _start:
        m = re.search(r'function get §-6§\(\) : Boolean\s*\{\s*return (.*?);\s*\}', _V.read(_V.path_of(_spell_cls[name])), re.S) if name in _spell_cls else None
        n = re.match(r'§8G§\.§,P§ >= (\d) &&', m.group(1)) if m else None
        _start[name] = int(n.group(1)) if n else 0
    return _start[name]


def lo_of(u):
    """the first Ascension an upgrade can be had at: its own (the page's data), the first Ascension it has a cost for, and the one its spell starts at"""
    lo = u['asc_min'] or 0
    if '_cost' in u: lo = max(lo, next(a for a, x in enumerate(u['_cost']) if x is not None))
    if u.get('spell'): lo = max(lo, spell_start(u['spell']))
    return lo or None


def item(u):
    forms = []
    for p in u['description']:
        for f in p['formulas']:
            forms.append({'l': f['latex'], 'v': f['vars'], 'lb': f.get('label') or effect_label(p['text']), 's': p['s'],
                          **({'np': 1} if p.get('np') else {})})
    if len(forms) == 1: forms[0]['lb'] = None
    return {
        'n': u['name'], 'i': icon_file(u['icon']),
        'd': [{'t': p['text'], 's': p['s'], **({'np': 1} if p.get('np') else {})} for p in u['description']], 'f': forms,
        's': [f"{s['kind']}: {s['name']}" for s in u['sources']] + u['requirements'],
        'o': u['conditions'], 'lo': lo_of(u), 'hi': u['asc_max'],
        **({'an': u['asc_not']} if u.get('asc_not') else {}), **({'ns': 1} if u.get('asc_not_say') else {}),
        'm': [{'t': b['text'], 's': b['s'], 'f': [{'l': f['latex'], 'v': f['vars']} for f in b['formulas']]}
              for b in u['more']] if u.get('more') else None,
        'mn': u.get('more_note'),
        **({'c': u['_cost']} if '_cost' in u else {}),
        **({'cb': [dict(item({'name': c['name'], 'icon': c['icon'], 'description': [dict(q, s=q.get('s')) for q in c['description']], 'sources': [], 'requirements': [],
                                'conditions': [], 'asc_min': 4, 'asc_max': None, **({'_cost': c['_cost']} if '_cost' in c else {})}), sub=c['note']) for c in u['combos']]} if u.get('combos') else {}),
        **({'nt': NOTES[u['name']][0], 'nr': NOTES[u['name']][1]} if u['name'] in NOTES else {}),
        **({'ra': u['unlock_by_asc'], 'sp': u['spell']} if u.get('unlock_by_asc') else {}),
        **({'fa': u['faction'], 'fn': FSEARCH.get(u['faction']), 'ak': u['akind']} if 'faction' in u else {}),
        **({'pr': PROOF_OF[u['name']]} if u.get('akind') == 'proof' else {}),
        **({'ia': {str(ax): icon_file(f"{UNION_ICON[u['faction']]}{nm}") for ax, nm in ((4, 'Order'), (5, 'Chaos'), (6, 'Balance'))}}
           if u.get('tier_no') == 4 and u.get('faction') in UNION_ICON else {}),
    }


GROUP_TITLES = {
    'HallOfLegendsProduction': 'Hall of Legends production upgrades',
    'HallOfLegendsPrestige': 'Hall of Legends base production upgrades',
    'NeutralProduction': 'Neutral buildings production upgrades',
    'GoodProduction': 'Good buildings production upgrades',
    'EvilProduction': 'Evil buildings production upgrades',
    'TrophyUpgrade': 'Trophy upgrades',
    'ManaProduction': 'Mana Regeneration upgrades',
    'RubyUpgrade': 'Ruby Power tiers',
    'ClickingBase': 'Base clicking reward upgrades',
    'ClickingProduction': 'Clicking reward and production upgrades',
    'ClickingTotalProduction': 'Production added to base clicking reward upgrades',
    'OfflineUpgrade': 'Offline production upgrades',
    'AssistantUpgrade': 'Production per assistant upgrades',
}
NOT_CONSOLIDATED = {'Autocast', 'ReincarnationPowerUpgrade', 'GemUpgrade'}      # listed one by one


def entries(items):
    """the game's grouping: upgrades of one group become one stacked icon (at the first member's position)"""
    out, pos = [], {}
    for u in sorted(items, key=lambda u: u['order']):
        g = u['group']
        if not g or g in NOT_CONSOLIDATED or u['name'] == 'Ruby Power':
            out.append({'g': None, 'items': [item(u)]}); continue
        if g not in pos:
            pos[g] = len(out)
            title = GROUP_TITLES.get(g) or (f"{u['building']} production upgrades" if u.get('building') else
                                            f"{u['spell']} spell tiers" if u.get('spell') else g)
            out.append({'g': title, 'items': []})
        out[pos[g]]['items'].append(item(u))
    for e in out:
        if e['g'] and len(e['items']) == 1: e['g'] = None
        elif e['g']: e['g'] = re.sub(r'\s*\bupgrades?\b', '', e['g'])      # a stack is named for what it is, not "... upgrades"
    return out


def section(sid, name, items):
    es = entries(items) if items is not None else None
    return {'id': sid, 'name': name, 'entries': es, 'count': sum(len(e['items']) for e in es) if es else 0}


def alleg_section():
    pair_asc = {}
    for u in pages['allegiances']:
        if u['akind'] == 'unique':
            b_ = u['name'][:-6] if u['name'].endswith(' Quest') else u['name']
            pair_asc[b_] = max(pair_asc.get(b_, 0), u['asc_min'] or 0)
    def key(u):
        sub = u['tier_no'] or u['perk'] or 0
        if u['akind'] == 'proof': sub = list(PROOF_OF).index(u['name'])      # Good, Evil, Neutrality, then Order, Chaos, Balance
        if u['akind'] == 'heritage': sub = (1 if u['name'].startswith('Advanced') else 0, FORDER.index(u['faction']))
        if u['akind'] == 'unique':
            base = u['name'][:-6] if u['name'].endswith(' Quest') else u['name']
            sub = (pair_asc.get(base, 0), base, 0 if u['name'].endswith(' Quest') else 1)      # the Research one first, then the Ascension 2 one
        general = u['faction'] == -1 or u['akind'] == 'heritage'      # the heritages are not tied to the faction you play
        return (-1 if general else FORDER.index(u['faction']), KIND_ORDER[u['akind']], sub, u['name'])
    allu = sorted(pages['allegiances'], key=key)
    bl_by = {u['faction']: item(u) for u in allu if u['akind'] == 'bloodline'}
    blood = [bl_by[i] for i in range(16) if i in bl_by]          # the game's grid: three columns in faction order (Mercenaries have none)
    perks = {}
    for u in allu:
        if u['akind'] == 'lineage_perk':
            perks[(u['faction'], int(u['name'].rsplit(' ', 1)[1]))] = item(u)
    lin_by = {}
    for u in allu:
        if u['akind'] != 'lineage': continue
        it = item(u)
        it['lp'] = [dict(p, it=perks.get((u['faction'], p['n']))) for p in u['perks']]
        lin_by[u['faction']] = it
    lineages = [lin_by[i] for i in range(16) if i in lin_by]
    set_by = {u['faction']: item(u) for u in allu if u['akind'] == 'set'}
    sets = [set_by[i] for i in range(16) if i in set_by]
    es = []
    for u in allu:
        if u['akind'] in ('bloodline', 'quest', 'lineage', 'lineage_perk', 'set') or (u['akind'] == 'unique' and u['name'].endswith(' Quest')): continue
        it = item(u)
        if u['akind'] == 'heritage': it['fa'] = -1
        if u['akind'] == 'bloodline_c': it['bl'] = blood
        if u['akind'] == 'lineage_c': it['lg'] = lineages; it['lc'] = costs.lineage_spec()      # the cost formula sits in the tooltip of the Lineages
        if u['akind'] == 'set_c': it['st'] = sets
        es.append({'g': None, 'items': [it]})
    return {'id': 'allegiances', 'name': 'Allegiances Upgrades', 'entries': es, 'count': len(es), 'alleg': True}


COST_PAGES = ('secret', 'magic', 'misc', 'buildings', 'allegiances')      # the pages that show costs
NO_COST_KINDS = {'bloodline', 'bloodline_c', 'set', 'set_c', 'lineage', 'lineage_c', 'lineage_perk', 'combo_c'}      # chosen, not bought: no cost line
import costs
_todo = [_u for _pg in COST_PAGES for _u in pages[_pg] if _u.get('akind') not in NO_COST_KINDS]
_ec = costs.engine_costs([_u['order'] for _u in _todo])      # the game's own code, asked for the cost of each upgrade
for _u in _todo:
    if _u['order'] not in _ec: continue      # not an upgrade of the game (the "Legacy Combos" heading)
    _n, _c = _ec[_u['order']]
    assert _n == _u['name'], (_n, _u['name'])
    _inf = [a for a, x in enumerate(_c) if x is not None and x[0] == float('inf')]
    _odd = [a for a in _inf if not (a < (_u['asc_min'] or 0) or (_u['asc_max'] is not None and a >= _u['asc_max']))]
    assert not _odd, ('infinite cost at an Ascension the page says it can be had at', _u['name'], _odd)
    _c = [None if (x is not None and x[0] == float('inf')) else x for x in _c]
    _u['_cost'] = [None if x is None else [int(x[0]) if x[0] < 1e15 and x[0] == int(x[0]) else x[0], [[i, int(v)] for i, v in x[1]]] for x in _c]      # per Ascension: coins, then [faction, amount] pairs (null: the upgrade does not exist yet)
_combo = next(_u for _u in pages['allegiances'] if _u.get('akind') == 'combo_c')      # the Legacy Combos: upgrades of the game that the page holds inside the heading
_ix = costs.engine_find([_c['name'] for _c in _combo['combos']])
_cc = costs.engine_costs(list(_ix.values()))
for _c in _combo['combos']:
    _c['_cost'] = [None if x is None else [int(x[0]) if x[0] < 1e15 and x[0] == int(x[0]) else x[0], [[i, int(v)] for i, v in x[1]]] for x in _cc[_ix[_c['name']]][1]]
COIN_NAMES = costs.names()      # the game's names: the main currency of each Ascension, the Faction Coin of each faction

UNION_PICK = {9: 4, 10: 5, 12: 6}      # Dwarf: Order, Drow: Chaos, Dragon: Balance


def faction_upgrades():
    """for the Factions page: each faction's upgrades arranged as the page shows them. {'items': {name: item}, 'f': {faction: {rows: [[names]] (a treaty tier and the upgrades it opens), heritage, bloodline, lineage, set, combos, spell, uniques}}}"""
    al = pages['allegiances']
    items, out = {}, {}
    cb = item(next(u for u in al if u['akind'] == 'combo_c'))['cb']
    for f in FACTIONS:
        fi, nm = f['i'], f['n']
        mine = sorted((u for u in al if u['faction'] == fi), key=lambda u: u['order'])
        tiers = [u for u in mine if u['akind'] == 'tier']
        rows = [[u['name']] for u in tiers]
        for u in mine:
            if u['akind'] != 'perk': continue
            r = (u['perk'] - 1) // 3 if u['perk'] else next(i for i, t in enumerate(tiers) if u['sources'] and u['sources'][0]['name'] == t['name'])      # the perks come three to a tier (the Mercenary ones name their contract)
            rows[r].append(u['name'])
        one = lambda k: next((u['name'] for u in mine if u['akind'] == k), None)
        sp = next((re.sub('^having the spell ', '', c) for u in mine if u['akind'] == 'spell' for c in u['conditions']), None)      # the spell the faction's spell upgrade belongs to
        mc = [c['n'] for c in cb if f['role'] == 'base' and (c['sub'].startswith(nm + '/') or ('/' + nm + ' ') in c['sub'])]
        out[str(fi)] = {'rows': rows, 'heritage': [u['name'] for u in mine if u['akind'] == 'heritage'], 'bloodline': one('bloodline'), 'lineage': one('lineage'), 'set': one('set'),
                        'combos': mc, 'spell': sp, 'uniques': [u['name'] for u in mine if u['akind'] == 'unique' and not u['name'].endswith(' Quest')]}
        for u in mine:
            if u['akind'] in ('tier', 'perk', 'heritage', 'bloodline', 'lineage', 'set') and u['name'] not in items: items[u['name']] = item(u)
            if u.get('tier_no') == 4 and u['faction'] in UNION_PICK and not items[u['name']]['i']: items[u['name']]['i'] = items[u['name']]['ia'][str(UNION_PICK[u['faction']])]      # the Union of a prestige faction has one icon per path: one each, none twice
    perk_items = {(u['faction'], int(u['name'].rsplit(' ', 1)[1])): item(u) for u in al if u['akind'] == 'lineage_perk'}
    for u in al:      # a Lineage opens its perks when clicked
        if u['akind'] == 'lineage' and u['name'] in items: items[u['name']]['lp'] = [dict(p, it=perk_items.get((u['faction'], p['n']))) for p in u['perks']]
    for c in cb: items[c['n']] = c
    return {'items': items, 'f': out}


json.dump(faction_upgrades(), open(os.path.join(ROOT, 'data', 'derived/faction_upgrades.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))


sections = [
    alleg_section(),
    section('misc', 'Misc Upgrades', pages['misc']),
    section('magic', 'Magic Upgrades', pages['magic']),
    section('buildings', 'Buildings Upgrades', pages['buildings']),
    section('secret', 'Secret Upgrades', pages['secret']),
]
json.dump(icons, open(os.path.join(ROOT, 'data', 'generated/icons.json'), 'w'), indent=0, sort_keys=True)
data = json.dumps({'max': meta['max_ascension'], 'sections': sections, 'factions': FACTIONS, 'coins': COIN_NAMES}, ensure_ascii=False,
                  separators=(',', ':')).replace('</', '<\\/')

html = tmpl.load('upgrades.html')
import search_snippet
import re as _re
SPLIT = [
    ('upgrades-allegiance.html', 'Allegiance Upgrades', ['allegiances'],
     'The treaty tiers and the twelve faction upgrades of every faction, the Proofs, Heritages, unique buildings, Bloodlines and '
     'Lineages. Pick a base faction to see its upgrades together with those of a prestige and an astral faction.'),
    ('upgrades-magic.html', 'Magic Upgrades', ['magic'],
     'The Magic upgrades, including the spell tiers: one stack per spell with its tiers 2 to 5 and what unlocks each.'),
    ('upgrades-secret.html', 'Secret Upgrades', ['secret'],
     'The Secret upgrades: the ones that appear once you own a trophy or an artifact.'),
    ('upgrades-misc.html', 'Miscellaneous Upgrades', ['misc', 'buildings'],
     'The Misc upgrades (the Gem, Reincarnation, Ruby and Challenge powers and the clicking, offline and assistant series) and '
     'the Building upgrades.'),
]
# known bugs in the game's own texts, shown at the top of the page (all of them are listed in data/docs/KNOWN_BUGS.md)
BUGS = {'upgrades-secret.html': '<div class="bugs"><p><b>Known bug, Art of the Crow:</b> the first paragraph of the upgrade&#39;s text says that for Evil '
         'Faction and Set the amount is based on the production bonus from Gems, but the line for Evil below it, and the game itself, use the mana produced in '
         'this Reincarnation. This page shows the latter.</p></div>'}
total = 0
for fname, title, ids, sub in SPLIT:
    secs = [x for x in sections if x['id'] in ids]
    secs.sort(key=lambda x: ids.index(x['id']))
    pdata = json.dumps({'max': meta['max_ascension'], 'sections': secs, 'factions': FACTIONS, 'coins': COIN_NAMES}, ensure_ascii=False,
                       separators=(',', ':')).replace('</', '<\\/')
    h = html.replace('__BUGS__', BUGS.get(fname, '')).replace('__DATA__', pdata).replace('__TITLE__', 'Realm Grinder ' + title).replace('__H1__', title).replace('__SUB__', sub)
    if 'allegiances' not in ids:      # no faction picker on the other pages
        h = _re.sub(r'  <div class="row" id="alleg-row">.*?</div>\n', '', h, flags=_re.S)
    if fname == 'upgrades-allegiance.html': h = h.replace('<body>', '<body class="steel">', 1)      # the game's tooltip borders, tried on one page
    h = search_snippet.apply(h, 'Search upgrade names and descriptions', fname)
    open(os.path.join(ROOT, 'docs', fname), 'w', encoding='utf8').write(h)
    print('docs/' + fname, len(h) // 1024, 'KB;', [(x['id'], x['count']) for x in secs])
    total += len(h)
