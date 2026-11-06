"""Generate docs/spells.html from data/derived/spells.json and data/handwritten/spells_overview.json (descriptions, tags): every spell as an icon with a hover tooltip.

    python -I tools/pages/build_spells_page.py
"""
import json, os, sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('extract', 'export', 'manual', 'pages', 'checks')]
import tmpl
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
spells = json.load(open(os.path.join(ROOT, 'data', 'derived/spells.json'), encoding='utf8'))
ov = json.load(open(os.path.join(ROOT, 'data', 'handwritten/spells_overview.json'), encoding='utf8'))['spells']
tier_up = {}      # spell -> its tier upgrades (Magic upgrades), from the upgrade pages' data
for u in json.load(open(os.path.join(ROOT, 'data', 'generated/upgrade_pages.json'), encoding='utf8'))['magic']:
    if u.get('spell'): tier_up.setdefault(u['spell'], []).append(u)

# formulas shared by all spells ("@name" in data/handwritten/spells_overview.json)
SHARED = {
    'penalty': [
        {'latex': r'p = 1 \quad (A = 0)'},
        {'latex': r'p = \dfrac{0.1}{A} \quad (A \ge 1,\ \text{no tier unlocked})'},
        {'latex': r'p = \dfrac{0.5}{A} \cdot 0.5^{\,w\,(A - T + 1)} \quad (A \ge 1,\ \text{tiers unlocked})',
         'vars': [['A', 'your Ascension number'], ['T', 'the tier the spell is cast at (1 for a spell cast once)'],
                  ['w', '$1$ if T - 1 is not above A, otherwise $1/2$']]}],
}

SHARED['penalty_tiers'] = SHARED['penalty'][2:]      # only the case of a spell with tiers unlocked

import re as _re


def _num(t):
    """'2h cumulative evil spells activity ...' -> (7200, 'cumulative evil spells activity ...', True): the amount (seconds for a time), the label, whether it is a time"""
    m = _re.match(r'^(\d+(?:\.\d+)?(?:e\+?\d+)?)(%)?\s*(h|m|s)?\s+(?:of\s+)?(.*)$', t)
    if not m: return None
    v, pct, u, lab = float(m.group(1)), bool(m.group(2)), m.group(3), m.group(4)
    lab = lab.replace(' in this Reincarnation', ' (this Reincarnation)')
    if 'activity' in lab and 'activity time' not in lab: lab = lab.replace('activity', 'activity time', 1)
    return v * {'h': 3600, 'm': 60, 's': 1}.get(u, 1), lab, bool(u), pct


def _fit(vals):
    """vals: {tier: amount}; the amount as a formula in n: k(n-1) or a + bn, else None"""
    ns = sorted(vals)
    k = vals[ns[0]] / (ns[0] - 1)
    if all(abs(vals[n] - k * (n - 1)) < 1e-9 for n in ns): return ('prop', k)
    b = (vals[ns[1]] - vals[ns[0]]) / (ns[1] - ns[0]); a = vals[ns[0]] - b * ns[0]
    if all(abs(vals[n] - (a + b * n)) < 1e-9 for n in ns): return ('lin', a, b)
    r = vals[ns[1]] / vals[ns[0]]      # a geometric series: a r^(n-1)
    if all(abs(vals[n] / vals[ns[0]] / r ** (n - ns[0]) - 1) < 1e-3 for n in ns): return ('geo', vals[ns[0]] / r ** (ns[0] - 1), r)
    return None


def _g(x):
    """a number for a formula: digits, or a power of ten when it is a large one"""
    import math
    if x < 1e6 or (x < 1e9 and x != 10 ** round(math.log10(x))): return str(int(x)) if x == int(x) else f'{x:g}'
    e = round(math.log10(x))
    if abs(x - 10 ** e) < 1e-6 * x: return f'10^{{{e}}}'
    e = math.floor(math.log10(x))
    return f'{x / 10 ** e:g} \cdot 10^{{{e}}}'


def tier_requirement_list(ups, name=''):
    """the unlock requirements of the tier upgrades as lines in the tier n ($...$ is set as a formula), and a note naming amounts that depend on the Ascension"""
    out, note, extra = [], '', []
    out.append('Ascension $n - 1$' if all(u['asc_min'] == u['spell_tier'] - 1 for u in ups) else 'Ascension $1$')
    parts = {}      # part index -> tier -> Ascension -> text
    for u in ups:
        for a, t in u['unlock_by_asc'].items():
            ps = t.removeprefix('To unlock, you need to have at least ').rstrip('.').split(' and have at least ')
            for i, x in enumerate(ps): parts.setdefault(i, {}).setdefault(u['spell_tier'], {})[a] = x
    for i in sorted(parts):
        tiers = parts[i]
        asc = sorted(next(iter(tiers.values())))
        parsed = {n: {a: _num(x) for a, x in v.items()} for n, v in tiers.items()}
        first = next(iter(next(iter(parsed.values())).values()))
        if any(q is None for v in parsed.values() for q in v.values()):
            out.append(next(iter(tiers.values()))[asc[0]]); continue
        lab = (' seconds ' if first[2] else ' ') + first[1]
        same = all(len({parsed[n][a][0] for a in asc}) == 1 for n in parsed)
        if same:
            f = _fit({n: parsed[n][asc[0]][0] for n in parsed})
            if f is None: out.append(first[1]); continue
            if f[0] == 'prop': rhs = _g(f[1]) + r'\,(n - 1)'
            elif f[0] == 'lin': rhs = _g(f[2]) + r'\,n + ' + _g(f[1])
            else:
                import math
                ea, er = round(math.log10(f[1]), 2), round(math.log10(f[2]), 2)
                rhs = f'10^{{{_g(er)}\,n}}' if ea == er else f'10^{{{_g(ea)}}} \cdot 10^{{{_g(er)}\,(n - 1)}}'
            out.append('$' + rhs + (r'\%' if first[3] else '') + '$' + lab)
        elif name == 'Call to Arms':      # k (n - 1) / A, k read from the game's own formula
            out.append(r'$k\,(n - 1) / A$' + lab)
            note = '$k$ is $10000$ at Ascension 4, $60000$ otherwise, and $A$ is your Ascension number.'
        else:      # the amount depends on the Ascension: each tier on its own, with its value at each Ascension
            lines = []
            for n in sorted(parsed):
                vals = ', '.join(f'${_g(parsed[n][a][0])}$ at Ascension {a}' for a in asc if int(a) >= n - 1)
                lines.append(f'Tier ${n}$: ' + vals)
            extra.append({'title': first[1][0].upper() + first[1][1:] + ' needed per tier and Ascension:', 'items': lines})
    return out, note, extra


def tier_sections(name, hand):
    """the generated sections of a spell with tiers: the tier requirements, the cost of higher tiers, the bonus at higher tiers and the offline bonus"""
    ups = sorted(tier_up.get(name, []), key=lambda u: u['spell_tier'])
    if not ups: return [dict(b) for b in hand]      # a spell without tier upgrades: only its hand-written sections (e.g. Twisting Nether's cost)
    req = tier_requirement_list(ups, name)
    out = [{'title': 'Spell tiers',
            'text': 'Casting the spell again while it is active raises its tier by one, up to the highest tier you have unlocked. Higher tiers are unlocked by a magic upgrade with the following requirements:',
            'lists': [{'title': 'Tier $n$:', 'items': req[0]}] + req[2], 'after': req[1]},
           {'title': 'Cost of higher tiers',
            'text': 'The first cast costs the normal mana cost. Casting again at a higher tier costs more:',
            'formulas': [{'latex': r'C = c^{\,1 + (0.6 - R)\,T}',
                          'vars': [['C', 'the mana cost of the cast'], ['c', "the spell's mana cost after all reductions"],
                                   ['R', 'the reduction of the tier cost scaling, for example 0.1 from Sequence (S1275)'],
                                   ['T', "the spell's current tier (1 after the first cast)"]]}]}]
    bonus = [dict(b) for b in hand]
    if any('Offline' in t['text'] for t in ups[0]['description']):      # the offline production bonus every tier adds
        bonus.append({'title': 'Offline production',
                      'text': 'Each unlocked tier also increases offline production:',
                      'formulas': [{'latex': r'v = \left( x^{\frac{2}{\max(3,\,A)}} + y^{\frac{2}{\max(3,\,A)}} \right)^{0.4}',
                                    'vars': [['v', 'the offline production bonus of a tier, in %'], ['x', 'your mana regeneration per second'],
                                             ['y', 'your Maximum Mana'], ['A', 'your Ascension number']]}],
                      'after': 'This bonus is affected by the regular Ascension penalty, which starts at Ascension $N$ for tier $N$.'})
    return out + bonus


def spell_detail(name):
    dt = dict(ov[name].get('detail', {}))
    secs = []
    for sec in dt.get('sections', []):
        sec = dict(sec)
        if 'formulas' in sec:
            fs = []
            for f in sec['formulas']:
                fs += SHARED[f[1:]] if isinstance(f, str) else [f]
            sec['formulas'] = fs
        secs.append(sec)
    secs += tier_sections(name, dt.get('tier_sections', []))
    out = {'sections': secs}
    if 'note' in dt: out['note'] = dt['note']
    return out


data = json.dumps([{'name': s['name'], 'icon': s['icon'] + '.png', 'cost': s.get('cost'), 'ticks': s.get('duration'),
                    'desc': ov[s['name']]['description'], 'tags': ov[s['name']]['tags'], 'order': ov[s['name']].get('order', 99), 'detail': spell_detail(s['name'])} for s in spells],
                  ensure_ascii=False, separators=(',', ':')).replace('</', '<\/')

html = tmpl.load('spells.html')
import search_snippet
page = search_snippet.apply(html.replace('__DATA__', data).replace('__UC__', ''), '', 'spells.html')
open(os.path.join(ROOT, 'docs', 'spells.html'), 'w', encoding='utf8').write(page)
print('docs/spells.html', len(page) // 1024, 'KB;', len(spells), 'spells')
