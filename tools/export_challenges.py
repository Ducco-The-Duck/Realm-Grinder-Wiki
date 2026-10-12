"""Export the faction challenges and their spell upgrades to data/challenges.json.

Texts are the game's own: each challenge object's description is evaluated in the engine with the
challenge marked as completed (which makes it print its reward), live-value readouts are dropped by
comparing three game states, and the formulas are converted from the static getters the description reads.

    python -I tools/export_challenges.py
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'pylib'))
import quickjs
from as3parse import parse_all, resolve
from chance_latex import convert, FACTION

FACTION = dict(FACTION)
FACTION.update({1: 'Elven', 9: 'Dwarven', 14: 'Djinn', 15: 'Makers'})   # the game's own challenge-header names
names = json.load(open(os.path.join(ROOT, 'data', 'engine_names.json'), encoding='utf8'))['names']
sprites = json.load(open(os.path.join(ROOT, 'data', 'sprites.json')))
J = lambda t: names[t]
g = J('§8G§')
ENGINE = open(os.path.join(ROOT, 'data', 'engine.js'), encoding='utf8').read()
PRESTIGE = {9, 10, 12}
THIRD = {13, 14, 15}      # affiliated through a Trade Treaty


def boot():
    ctx = quickjs.Context(); ctx.eval(ENGINE); ctx.eval('__boot()'); return ctx


MUT = f"""
  var G = {g}, v = __V;
  [G.{J('§5!V§')}, G.{J('§=y§')}, G.{J('§@w§')}, G.{J('§1!#§')}].forEach(function (a) {{ for (var i = 0; i < a.length; i++) a[i] = v; }});
  G.{J('§%<§')}.forEach(function (b) {{ b.{J('§!a§')} = v; }});
  G.{J('§0!A§')}.forEach(function (s) {{ s.{J('§2-§')} = v; s.{J('§?j§')} = v; s.{J('§<q§')} = v; s.{J('§<!G§')} = v; }});
"""
N_E, N_P, N_T, N_RE, N_RP, N_RT = [J(x) for x in ('§ e§', '§ "+§', '§-"0§', '§^!m§', '§,!l§', '§`"\'§')]
PROBE = f"""(function () {{ __MUT
  var K1 = {J('§]<§')}, K2 = {J('§[!a§')}, U = {g}.{J('§-!4§')}, out = [], named = {{}};
  var qOf = function (o) {{ for (var c = 0; c < __classes.length; c++) if (__classes[c].K === o.constructor) return __classes[c].q; return null; }};
  var lists = {{ upgrade: U, trophy: {g}.{J('§0Q§')}, spell: {g}.{J('§0!A§')}, building: {g}.{J('§%<§')} }};
  for (var k in lists) for (var i = 0; i < lists[k].length; i++) {{ var q = qOf(lists[k][i]); if (q !== null) named[q] = [k, lists[k][i].{J('§1i§')}]; }}
  for (var i = 0; i < U.length; i++) if (U[i] instanceof K1 || U[i] instanceof K2) U[i].{J('§?!6§')} = true;
  for (var i = 0; i < U.length; i++) {{ var o = U[i]; if (!(o instanceof K1) && !(o instanceof K2)) continue;
    var r = {{ q: qOf(o), n: o.{J('§1i§')}, icon: o.{J('§^!#§')}, grp: o.{J('§?!=§')}, f: o.{J('§-!^§')}, spell: o instanceof K2,
              base: o.{N_E}, pre: o.{N_P}, third: o.{N_T}, rbase: o.{N_RE}, rpre: o.{N_RP}, rthird: o.{N_RT} }};
    if (r.spell) {{ r.reward = o.{J('§<_§')}; r.count = o.{J('§]!Y§')}; }}
    try {{ r.desc = o.{J('§@"§')}(); }} catch (e) {{ r.desc = 'ERR ' + e; }}
    out.push(r); }}
  return JSON.stringify({{ rows: out, named: named }}); }})()"""


def probe(asc, v=None, extra=''):
    pre = f"{g}.{J('§,P§')} = {asc};" + (MUT.replace('__V', str(v)) if v is not None else '') + extra
    return json.loads(boot().eval(PROBE.replace('__MUT', pre)))


ALIGN1 = {1: 'Good', 2: 'Evil', 3: 'Neutral'}
ALIGN2 = {4: 'Order', 5: 'Chaos', 6: 'Balance'}
base = [probe(0), probe(0, 1000), probe(0, 98765)]
rows, named = base[0]['rows'], base[0]['named']
asc_runs = {a: probe(a)['rows'] for a in range(1, 5)}
al_runs = {}
for k in ALIGN1: al_runs[k] = probe(0, None, f"{g}.{J('§,!Y§')} = {k};")['rows']
for k in ALIGN2: al_runs[k] = probe(0, None, f"{g}.{J('§9!m§')} = {k};")['rows']
print('challenge objects:', len(rows))

cl = parse_all()
NUM = re.compile(r'INF|NaN|[+-]?\d[\d,.]*(?:[eE][+-]?\d+)?(?: ?[KMBTkmbt]\b|(?: [A-Z][a-z]{0,2}\b))?')
_dsrc = open(os.path.join(ROOT, 'out', 'script', 'scripts', '§-D§.as'), encoding='utf8').read()
_suffixes = [x.strip() for x in re.findall(r'"( [A-Za-z]+)"', re.search(r'§1X§:Array = \[(.*?)\];', _dsrc).group(1))]
SUFFIX_EXP = {sfx: 6 + 3 * i for i, sfx in enumerate(_suffixes)}
SUFFIX_RE = re.compile(r'(?<![\w.])(\d+(?:\.\d+)?) ?(' + '|'.join(sorted(map(re.escape, SUFFIX_EXP), key=len, reverse=True)) + r')(?![A-Za-z])')
_SUP = str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻')


def pow10_text(text):
    def rep(m):
        mant, e = float(m.group(1)), SUFFIX_EXP[m.group(2)]
        while mant >= 10: mant /= 10; e += 1
        while 0 < mant < 1: mant *= 10; e -= 1
        mant = round(mant, 6)
        pw = '10' + str(e).translate(_SUP)
        return pw if mant == 1 else f'{mant:g} × {pw}'
    return SUFFIX_RE.sub(rep, text)


def dyn_flags(paras):
    """paras: list of (text in state 0, 1, 2).  True where the paragraph's numbers differ between states."""
    return [not (a == b == c) for a, b, c in paras]


def split_desc(t):
    """-> (flavor, [paragraphs], [requirement lines])"""
    parts = t.replace('\r', '').split('\n\n')
    flavor = ''
    if parts and parts[0].startswith('"'): flavor = parts.pop(0).strip().strip('"')
    reqs = []
    body = []
    for p in parts:
        if p.startswith('Requirements:'):
            reqs = [x.strip() for x in p.split('\n')[1:] if x.strip()]
        else:
            body.extend(x.strip() for x in p.split('\n') if x.strip())
    return flavor, body, reqs


def class_of(r):
    tok = r['q'].split('.')[-1]
    return next((k for k in cl.values() if k.name == tok), None)


def name_of_for(c):
    def f(tok):
        q = resolve(c, tok, cl)
        return named.get(q) if q else None
    return f


def source_templates(c):
    """-> {method name: body} for the description method and the string-returning helpers it calls"""
    meths = {m.name: m for m in c.methods}
    desc = meths.get('§@"§')
    bodies = [desc.body] if desc else []
    for n in re.findall(r'(§[^§]*§)\(\)', desc.body if desc else ''):
        m = meths.get(n)
        if m is not None and n != '§@"§' and '_("' in m.body: bodies.append(m.body)
    return meths, '\n'.join(bodies)


def inline_helpers(c, expr):
    """Replace calls to one-expression methods that only wrap param1, and zero-argument static getters of other
    classes (e.g. the Hive Mind bonus), by their expression."""
    meths = {m.name: m for m in c.methods}
    for _ in range(4):
        def rep(m):
            mm = meths.get(m.group(1))
            if mm is None: return m.group(0)
            b = re.fullmatch(r'return (.+);', re.sub(r'\s+', ' ', mm.body.strip()))
            if not b or 'param1' not in b.group(1) or 'param2' in b.group(1): return m.group(0)
            return '(' + b.group(1).replace('param1', '(' + m.group(2) + ')') + ')'
        new = re.sub(r'(?<![.\w§])(§[^§]*§)\(((?:[^()]|\([^()]*(?:\([^()]*\))?[^()]*\))*)\)', rep, expr)
        def rep2(m):
            if m.group(1) in ('§&c§', '§#!!§', '§8G§'): return m.group(0)
            q = resolve(c, m.group(1), cl)
            oc = cl.get(q) if q else None
            if oc is None: return m.group(0)
            mm = next((x for x in oc.methods if x.name == m.group(2)), None)
            if mm is None: return m.group(0)
            b = re.fullmatch(r'return (.+);', re.sub(r'\s+', ' ', mm.body.strip()))
            return '(' + b.group(1) + ')' if b and 'param' not in b.group(1) else m.group(0)
        new = re.sub(r'(§[^§]*§)\.(§[^§]*§)\(\)', rep2, new)
        if new == expr: break
        expr = new
    return expr


def split_args(a):
    out, depth, cur = [], 0, ''
    for ch in a:
        if ch in '([': depth += 1
        elif ch in ')]': depth -= 1
        if ch == ',' and depth == 0: out.append(cur); cur = ''
        else: cur += ch
    if cur.strip() or out: out.append(cur)
    return [x.strip() for x in out]


unconv = {}


def formulas_for(c, gname=''):
    """-> [(template, {placeholder index: ('const'|'f'|'raw', value)}, is_readout)] for each `_("template", args)`
    of the description (and of the string helpers it calls) whose arguments call getters of the class."""
    meths, body = source_templates(c)
    out = []
    for m in re.finditer(r'_\("((?:[^"\\]|\\.)*)"((?:[^;]|\n)*?)\)\s*[;+]', body):
        tmpl = m.group(1).replace("\\'", "'").replace('\\"', '"').replace('\\n', '\n').strip()
        args = m.group(2).lstrip(',').replace(c.name + '.', '')
        if '§%`§' in args: continue
        forms, readout = {}, bool(re.search(r'§8G§\.|§#!!§\.', args))
        for i, a in enumerate(split_args(args)):
            keys = re.findall(r'(?<![.\w§])(§[^§]*§)\(\)', a)
            if not keys: continue
            mt = meths.get(keys[0])
            if mt is None: continue
            b = re.sub(r'\s+', ' ', mt.body.strip())
            mm = re.fullmatch(r'return (.+);', b)
            man = MANUAL.get((gname, keys[0]))
            if man: forms[i] = ('f', man); readout = True; continue
            if not mm: forms[i] = ('raw', b); readout = True; continue
            e = mm.group(1).strip()
            if re.fullmatch(r'-?[\d.]+', e): forms[i] = ('const', e); continue
            readout = True
            e = inline_helpers(c, e)
            # a single read of a this-Era stat array entry -> the game's helper call for the same value
            e = re.sub(r'§8G§\.§5!V§\[(\d+)\]', lambda mt_: '§&c§.§"!B§(' + mt_.group(1) + ',false,true)', e)
            cv = convert(e, name_of_for(c))
            if cv: forms[i] = ('f', {'latex': cv['latex'].replace('p = ', 'v = ', 1), 'vars': cv['vars']})
            else: forms[i] = ('raw', e)
        out.append((tmpl, forms, readout))
    return out


def tmpl_re(tmpl):
    parts = re.split(r'%\d', tmpl)
    return re.compile(r'^' + '(.*?)'.join(re.escape(p) for p in parts) + r'$', re.S)


APPLIES = re.compile(r'This reward can be used (?:only )?while playing with (?:the (.+?) faction|any (.+?))\.$')
TAIL_GROUP = re.compile(r'\s*\(([^()]*)\)\.?$')

# formulas the converter cannot express (loops, several game systems); filled in below
def _getter(c, key, tail='', more=()):
    """formula of a static getter that the description text does not call (the game applies it elsewhere)"""
    m = next(x for x in c.methods if x.name == key)
    e = re.fullmatch(r'return (.+);', re.sub(r'\s+', ' ', m.body.strip())).group(1)
    cv = convert(inline_helpers(c, e), name_of_for(c))
    assert cv, (c.name, key)
    return {'latex': cv['latex'].replace('p = ', 'v = ', 1) + tail,
            'vars': cv['vars'] + [{'symbol': a, 'text': b} for a, b in more]}


def _extra_overflowing(paras, c):
    paras[0]['formulas'].append(_getter(
        c, "§'!b§", r' \cdot \left(12 - k\right)',
        [('k', 'Tier number of the building (the first building is tier 1); each Non-Unique building gets +v %')]))


def _extra_art_of_war(paras, c):
    paras[0]['formulas'].append(_m(
        r'v = t^{0.7}',
        ('t', 'Time spent as that faction in this Reincarnation (seconds). A Unique Building gets +v % for each of your '
              'Lineage and Set factions that is its faction, and +v/2 % for each that is tied to its faction')))


def _extra_altar(paras, c):
    paras[0]['formulas'].append(_m(
        r'v = 45^{\,1 + n/4}', ('n', 'Number of your available faction spells tied to that alignment')))
    paras[0]['formulas'][-1]['shown'] = True
    for t in ('Good: Increase Assistants.', 'Evil: Increase trophy count.', 'Neutral: Increase production bonus from Gems.',
              'Order: Increase Mana Regeneration.', 'Chaos: Increase Maximum Mana.', 'Balance: Increase Faction Coin find chance.'):
        paras.append({'text': t, 'formulas': []})


EXTRA = {'Overflowing Magic': [_extra_overflowing], 'The Art of War': [_extra_art_of_war],
         'Altar of Wishes': [_extra_altar]}


def _m(latex, *vs):
    return {'latex': latex, 'vars': [{'symbol': s, 'text': t} for s, t in vs]}


# Getters with loops or several game systems, written out by hand from the game code (see INFERENCES.md).
MANUAL = {
    ('Titan Challenge', '§ "D§'): _m(
        r'v = 20 \cdot \left(T + 11\,R + P\,\Sigma\right)',
        ('T', 'Tier number of the building the random target of Lightning Strike was (the first building is tier 1)'),
        ('R', '1 if you have the research Lightning Rod (C375); otherwise 0'),
        ('P', '1 if you have the Titan lineage perk 4; otherwise 0'),
        (r'\Sigma', 'Sum of the tier numbers of your owned Unique Buildings')),
    ('Druid Challenge', '§&s§'): _m(
        r'v = 3 \cdot \max\left(0, v_{1} - 10\right)^{1.5}',
        ('v_{1}', 'Extra buildings Grand Balance affects (the first formula). Grand Balance has 1 + v₁ targets in '
                  'total and the bonus starts at 12 targets, so the amount above 11 is v₁ − 10')),
    ('Drow Challenge', '§^"I§'): _m(
        r'v = N - N_{\mathrm{CS}}',
        ('N', 'Spells you have cast in this Era, not counting Tax Collection'),
        (r'N_{\mathrm{CS}}', 'Times you have cast "Combo Strike" in this Era (it is part of N and is taken out again)')),
    ('Dragon Challenge', '§,!G§'): _m(
        r"v = \begin{cases} 5\,j & \text{if Dragon's Breath is active} \\ 0 & \text{otherwise} \end{cases}",
        ('j', 'Tier "Dragon\'s Breath" is cast at (1 is the base tier)')),
    ('Miniature Lamps', '§9"I§'): _m(
        r'v = 200 \cdot \left(12 - i\right)',
        ('i', 'Position of the lowest-tier building that "Maelstrom" is targeting (0 for the first building, 1 for the second, and so on). '
              'Only counts while "Maelstrom" is active')),
}
# what the values of a paragraph with several formulas are, when its readout does not say
LABELS = {}


SUBS = '₁₂₃₄₅₆₇₈₉'


def para(c, templates, raw, ctx):
    """-> {'text', 'formulas'} for one reward paragraph of the game text.  Values the game computes are replaced by
    v (or v1, v2 ...) in the text, and the trailing live readout "(+x%)" is dropped."""
    tmpl = forms = None
    readout = False
    for t, f, ro in templates:
        if tmpl_re(t).match(raw):
            tmpl, forms, readout = t, f, ro
            break
    if tmpl is None:
        return {'text': pow10_text(raw.strip()), 'formulas': []}
    vals = tmpl_re(tmpl).match(raw).groups()
    tg = TAIL_GROUP.search(tmpl)
    labels, cut = {}, None
    if readout and tg and '%' in tg.group(1):
        cut = tg.start()
        for lab, i in re.findall(r'([A-Za-z][A-Za-z ]*?): ?[+x]?%(\d)', tg.group(1)): labels[int(i)] = lab.strip()
    fkeys = sorted(i for i, (k, _) in forms.items() if k == 'f')
    multi = len(fkeys) > 1
    # several values with identical formulas (both bonuses equal the same number)
    same = multi and len({json.dumps(forms[i][1], sort_keys=True) for i in fkeys}) == 1
    sym = lambda i: 'v' if (not multi or same) else 'v' + SUBS[fkeys.index(i)]
    text, last = '', 0
    for k, m in enumerate(re.finditer(r'%(\d)', tmpl)):
        if cut is not None and m.start() >= cut: break
        text += tmpl[last:m.start()]
        i = int(m.group(1))
        text += sym(i) if forms.get(i, ('',))[0] == 'f' else vals[k]
        last = m.end()
    if cut is not None:
        text += tmpl[last:cut]
        rest = tmpl[tg.end():]
        text += '.' if tg.group(0).endswith('.') and not text.rstrip().endswith('.') else ''
    else:
        text += tmpl[last:]
    text = text.replace("\'", "'").strip()
    fl = []
    use = fkeys[:1] if same else fkeys
    for i in use:
        f = dict(forms[i][1])
        if multi and not same:
            f['latex'] = f['latex'].replace('v = ', 'v_{' + str(fkeys.index(i) + 1) + '} = ', 1)
        if i in labels: f['label'] = labels[i]
        f['shown'] = cut is not None or sym(i) in text
        fl.append(f)
    for i in sorted(forms):
        if forms[i][0] == 'raw': fl.append({'raw': forms[i][1], 'label': labels.get(i)})
    return {'text': pow10_text(text), 'formulas': fl}


def reward_text(desc_text):
    flavor, body, reqs = split_desc(desc_text)
    return flavor, body, reqs


def asc_name(i): return {0: 'Neutral'}.get(i)


entries = []
for idx, r in enumerate(rows):
    c = class_of(r)
    templates = formulas_for(c, r['n'])
    flavor, body, reqs = split_desc(r['desc'])
    paras, applies = [], None
    for raw in body:
        m = APPLIES.match(raw)
        if m: applies = m.group(1) or ('any ' + m.group(2)); continue
        paras.append(para(c, templates, raw, r['n']))
    for ex in EXTRA.get(r['n'], []): ex(paras, c)
    # reward text that depends on the alignment (the Mercenary spell upgrade)
    variants = {}
    base_set = set(body)
    for k, aname in {**ALIGN1, **ALIGN2}.items():
        _, bk, _ = split_desc(al_runs[k][idx]['desc'])
        extra = [x for x in bk if x not in base_set and not APPLIES.match(x)]
        if extra: variants[aname] = [para(c, templates, x, r['n']) for x in extra]
    by_asc = {}
    for a, rr in asc_runs.items():
        f2, b2, q2 = split_desc(rr[idx]['desc'])
        if q2 != reqs or b2 != body: by_asc[a] = {'requirements': q2, 'body': b2}
    num = re.search(r'(\d+)$', r['icon'])
    unlock = []
    if r['spell']:
        avail = next((m for m in c.methods if m.name == '§9!%§'), None)
        if avail is not None:
            nm = name_of_for(c)
            for tok in dict.fromkeys(re.findall(r'(§[^§]*§)\.id', avail.body)):
                n = nm(tok)
                if n: unlock.append(n)
    entries.append({
        'faction': r['f'], 'spell_upgrade': r['spell'], 'name': r['reward'] if r['spell'] else r['n'], 'game_name': r['n'],
        'number': int(num.group(1)) if num and not r['spell'] else 0, 'icon_name': r['icon'],
        'icon': r['icon'] if r['icon'] in sprites else None, 'flavor': flavor,
        'requirements': [pow10_text(x) for x in reqs], 'rewards': paras, 'applies_to': applies,
        'alignment_variants': variants, 'by_ascension': by_asc, 'count': r.get('count'), 'unlock': unlock,
        'group': r['grp'],
    })

# ---- final shape ---------------------------------------------------------------------------------
KIND = {9: 'Prestige faction', 10: 'Prestige faction', 12: 'Prestige faction', 6: 'Neutral faction', 7: 'Neutral faction',
        8: 'Neutral faction', 11: 'Mercenary', 13: 'Trade Treaty faction', 14: 'Trade Treaty faction',
        15: 'Trade Treaty faction'}
PENALIZED = 'the game shows this percentage reduced by the Ascension penalty'


def requirement_lines(e):
    """eligibility lines and the challenge line; numbers that change with the Ascension get a note"""
    reqs = list(e['requirements'])
    asc = e['by_ascension']
    if asc:
        a1 = [pow10_text(x) for x in asc[1]['requirements']]
        later = [[pow10_text(x) for x in v['requirements']] for k, v in asc.items() if k != 1]
        for i, ln in enumerate(reqs):
            if i >= len(a1) or a1[i] == ln: continue
            if any(L[i] != a1[i] for L in later if i < len(L)):
                shown = re.search(r'at least ([\d.]+%)', a1[i]).group(1)
                reqs[i] = f'{ln} This requirement is affected by the Ascension penalty. For example, it is {shown} at Ascension 1.'
            else:
                old_toks = ln.split()
                new = ' '.join(t for t in a1[i].split() if t not in old_toks).rstrip('.')
                reqs[i] = f'{ln.rstrip(".")} (after your first Ascension: {new}).'
    return reqs[:-1], reqs[-1]


LABEL_FIX = {'Max': 'Maximum Mana', 'Regen': 'Mana Regeneration'}
# values of a paragraph with two formulas whose readout does not name them (additive first, then multiplicative)
PARA_LABELS = {"God's Plan": ['Mana Regeneration, additive', 'Mana Regeneration, multiplicative (%)']}
# names of the values of multi-effect rewards, in the order of their formulas (the paragraph text is too long for a label)
FORM_LABELS = {
    'Druid Challenge': ['Extra buildings Grand Balance affects', 'Production of all targeted buildings, once there are more than 11 (%)'],
    'Mercenary Challenge': ["Good: Tax Collection casts added to the base of Call to Arms' bonus", 'Evil: Tax Collection worth',
                            'Neutral: Faction Coin find chance', 'Order: Autoclicks per second',
                            'Chaos: Assistants, temporarily', 'Balance: Royal Exchange bonus'],
    'Draconstellation': ['Faction Coins from excavations', 'Production of all buildings'],
    'Time Merge': ['Time added to this Era (seconds)', 'Production of Unique buildings'],
    'Miniature Lamps': ['Assistants, temporarily (while Maelstrom is active)',
                        'Limited Wish casts per second (while Fairy Chanting is active)'],
    'Ifrit Ignition': ['Maximum Mana', 'Additional casts per Evil or Chaos spell'],
    'Artificial Currency': ['Increase of triggered Tax Collections', 'Production bonus from Gems'],
    'Drow Challenge': ['Combo Strike counter', 'Offline spells cast amount (%)'],
}
DROP_FORMULAS = {'Recruitment'}      # the text says everything
TEXT_FIX = {
    'Increase the production of all Buildings and Faction Coin find chance based on upgrades purchased.':
        'Increase the production of all buildings by v% and the Faction Coin find chance by +v%, based on upgrades purchased.',
}
NOTES = {'Faceless Challenge': 'v is in seconds. The game shows it as minutes, hours or days as appropriate.'}
BUGS = {'Mystic Maze': 'The reward text says "the highest amount of buildings you had in this Reincarnation", but the game '
                       'uses the highest number you currently own of any single building type (including bonuses that '
                       'make buildings count as more), which starts over every Era.'}
_PH = re.compile(r'(?<![A-Za-z])v([₁₂₃₄₅₆₇₈₉])?(?![A-Za-z])')


def effect_label(text):
    """short noun phrase naming what a paragraph's formula gives"""
    t = re.split(r' based on |\. ', text)[0].rstrip('.')
    t = re.sub(r'^Also ', '', t)
    m = re.match(r'^While (.+?) is active, (.*)$', t)
    if m: t = f'{m.group(2)} (while {m.group(1)} is active)'
    t = re.sub(r'^(?:[Mm]ultiplicatively )?(?:[Ii]ncreases?|[Gg]ain|[Gg]ive) ', '', t)
    t = re.sub(r'^the ', '', t)
    return t[:1].upper() + t[1:]


def flatten(e):
    """-> (reward paragraphs with v / v1.. placeholders numbered over the whole reward, [formula dicts])"""
    if e['game_name'] in DROP_FORMULAS:
        return [p['text'] for p in e['rewards']], []
    paras = [(p, None) for p in e['rewards']]
    for al, ps in e['alignment_variants'].items():
        paras += [(p, al) for p in ps]
    total = sum(len(p['formulas']) for p, _ in paras)
    out, forms, k = [], [], 0
    for p, al in paras:
        fl = p['formulas']
        text = p['text']
        base = k
        if al: text = f'{al}: {text}'
        names = PARA_LABELS.get(e['game_name'] if not al else '', [])
        for j, f in enumerate(fl):
            k += 1
            lab = f.get('label')
            lab = LABEL_FIX.get(lab, lab) if lab else (names[j] if j < len(names) else effect_label(p['text']))
            if al and lab: lab = f'{al}: {lab}'
            if e['game_name'] in FORM_LABELS: lab = FORM_LABELS[e['game_name']][k - 1]
            g = {'latex': f['latex'], 'vars': f['vars'], 'label': lab if total > 1 else None, 'shown': f.get('shown', False)}
            if total > 1:
                g['latex'] = re.sub(r'^v(?:_\{\d+\})? = ', f'v_{{{k}}} = ', g['latex'])
            forms.append(g)
        if total > 1 and fl:
            # local placeholder v / v1.. -> global number (identical formulas share the first one)
            def sub(m):
                loc = ('₁₂₃₄₅₆₇₈₉'.index(m.group(1)) if m.group(1) else 0)
                return 'v' + SUBS[base + min(loc, len(fl) - 1)]
            text = _PH.sub(sub, text)
        out.append(TEXT_FIX.get(text, text))
    return out, forms


facs = {}
for e in entries:
    elig, chal = ([], '') if e['spell_upgrade'] else requirement_lines(e)
    item = {
        'name': e['name'], 'number': e['number'], 'spell_upgrade': e['spell_upgrade'], 'icon': e['icon_name'] if e['icon'] else None,
        'flavor': e['flavor'], 'requirements': elig, 'challenge': chal,
        'rewards': flatten(e)[0], 'formulas': flatten(e)[1], 'applies_to': e['applies_to'],
        'game_name': e['game_name'], 'note': NOTES.get(e['game_name']), 'bug': BUGS.get(e['game_name']),
    }
    if e['spell_upgrade']:
        item['count'] = e['count']
        item['unlock'] = [{'kind': k, 'name': n} for k, n in e['unlock']]
    facs.setdefault(e['faction'], []).append(item)
result = []
for fid in sorted(facs):
    its = sorted(facs[fid], key=lambda x: (not x['spell_upgrade'], x['number']))
    result.append({'id': fid, 'name': FACTION.get(fid, str(fid)), 'kind': KIND.get(fid, 'Base faction'), 'items': its})
for f in result:
    n = len([i for i in f['items'] if not i['spell_upgrade']])
    su = next((i for i in f['items'] if i['spell_upgrade']), None)
    assert su and su['count'] == n, (f['name'], n, su and su['count'])
    assert [i['number'] for i in f['items'] if not i['spell_upgrade']] == list(range(1, n + 1)), f['name']
json.dump(result, open(os.path.join(ROOT, 'data', 'challenges.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
print('data/challenges.json:', [(f['name'], len(f['items']) - 1) for f in result])

