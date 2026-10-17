"""Export the researches to data/research.json.

Per research: branch, research number (points of its branch required), name, icon, description with the
live-value readouts removed, formulas as LaTeX with named inputs, and the unlock requirements.

Requirement text is the game's own (the research's requirement-text method evaluated in the engine with
the research marked as owned, which makes it print the plain target instead of "Progress: x/y").
Descriptions are the game's own text evaluated at a fresh game state; the "(+x%)" style readouts of the
current value are dropped.  Formulas come from the getters that the description reads.

    python -I tools/export_research.py
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'pylib'))
import quickjs
from as3parse import parse_all, resolve
from chance_latex import convert, FACTION

names = json.load(open(os.path.join(ROOT, 'data', 'engine_names.json'), encoding='utf8'))['names']
sprites = json.load(open(os.path.join(ROOT, 'data', 'sprites.json')))
J = lambda t: names[t]
g = J('§8G§')
ENGINE = open(os.path.join(ROOT, 'data', 'engine.js'), encoding='utf8').read()


def boot():
    ctx = quickjs.Context(); ctx.eval(ENGINE); ctx.eval('__boot()'); return ctx


MUT = f"""
  var G = {g}, v = __V;
  [G.{J('§5!V§')}, G.{J('§=y§')}, G.{J('§@w§')}, G.{J('§1!#§')}].forEach(function (a) {{ for (var i = 0; i < a.length; i++) a[i] = v; }});
  G.{J('§%<§')}.forEach(function (b) {{ b.{J('§!a§')} = v; }});
  G.{J('§0!A§')}.forEach(function (s) {{ s.{J('§2-§')} = v; s.{J('§?j§')} = v; s.{J('§<q§')} = v; s.{J('§<!G§')} = v; }});
"""

PROBE = f"""(function () {{ __MUT
  var qOf = function (o) {{ for (var c = 0; c < __classes.length; c++) if (__classes[c].K === o.constructor) return __classes[c].q; return null; }};
  var K = {J('§&!_§')}, U = {g}.{J('§-!4§')}, out = [], named = {{}};
  var lists = {{ upgrade: U, trophy: {g}.{J('§0Q§')}, spell: {g}.{J('§0!A§')}, building: {g}.{J('§%<§')} }};
  for (var k in lists) for (var i = 0; i < lists[k].length; i++) {{ var q = qOf(lists[k][i]); if (q !== null) named[q] = [k, lists[k][i].{J('§1i§')}]; }}
  for (var i = 0; i < U.length; i++) {{ var o = U[i]; if (!(o instanceof K)) continue;
    var r = {{ q: qOf(o), n: o.{J('§1i§')}, w: o.{J('§%w§')}, b: o.{J('§!G§')}, f: o.{J('§^!C§')}, h: o.{J('§-!^§')}, al: o.{J('§,!Y§')}, ax: o.{J('§9!m§')}, u: o.{J('§"!U§')},
              id: o.id, icon: o.{J('§^!#§')}, hint: '' }};
    try {{ r.desc = o.{J('§@"§')}(); }} catch (e) {{ r.desc = 'ERR ' + e; }}
    try {{ r.hint = o.{J('§8!s§')}(); }} catch (e) {{ }}
    var was = o.{J('§?!6§')}; o.{J('§?!6§')} = true;
    try {{ r.req = o.{J('§8[§')}(); }} catch (e) {{ r.req = ''; }}
    o.{J('§?!6§')} = was;
    out.push(r); }}
  return JSON.stringify({{ rows: out, named: named }}); }})()"""

def probe(asc, v=None):
    pre = f"{g}.{J('§,P§')} = {asc};"
    if v is not None: pre += MUT.replace('__V', str(v))
    return json.loads(boot().eval(PROBE.replace('__MUT', pre)))


# highest Ascension: the Ascend rule has one "Ascension == k && Reincarnation >= n" step per Ascension
_asc_src = open(os.path.join(ROOT, 'out', 'script', 'scripts', '§8G§.as'), encoding='utf8').read()
_m = re.search(r'if\(§8G§\.§,P§ == 0 && §8G§\.§8!H§ >= \d+(?: \|\| §8G§\.§,P§ == \d && §8G§\.§8!H§ >= \d+)*', _asc_src)
MAX_ASC = max(int(x) for x in re.findall(r'§,P§ == (\d)', _m.group(0))) + 1
print('max Ascension:', MAX_ASC)
runs = {a: [probe(a), probe(a, 1000), probe(a, 98765)] for a in range(MAX_ASC + 1)}
base = runs[0][0]
rows, named = base['rows'], base['named']
mut = [runs[0][1]['rows'], runs[0][2]['rows']]
# branch names
BR = json.loads(boot().eval(f"JSON.stringify({J('§-D§')}.{J('§?+§')})"))
print('research objects:', len(rows), 'branches:', BR)

cl = parse_all()
NUM = re.compile(r'INF|NaN|[+-]?\d[\d,.]*(?:[eE][+-]?\d+)?(?: ?[KMBTkmbt]\b|(?: [A-Z][a-z]{0,2}\b))?')
LABEL_WORDS = r'and|Additive|Multiplicative|Max Mana|Mana Regen|Duration bonus|Production|Faction Coin Chance|Combo bonus|Overall bonus|Max|Current'


def clean_desc(texts):
    """texts: description in the three states."""
    t = texts[0]
    # numbers that differ between states are live values
    toks = [NUM.findall(x) for x in texts]
    if len({len(a) for a in toks}) == 1 and len(toks[0]):
        dyn = {i for i in range(len(toks[0])) if not (toks[0][i] == toks[1][i] == toks[2][i])}
        if dyn:
            it = iter(range(10 ** 6)); idx = [0]
            def rep(m):
                i = idx[0]; idx[0] += 1
                return 'X' if i in dyn else m.group(0)
            t = NUM.sub(rep, t)
    def strip_paren(m):
        inner = m.group(1)
        if not re.search(r'\d|INF|NaN|\bX\b', inner): return m.group(0)
        rest = re.sub(LABEL_WORDS, '', inner)
        rest = NUM.sub('', rest)
        rest = re.sub(r'[Xx,:%+\-s ]', '', rest)
        return '' if not re.search(r'[A-Za-z]', rest) else m.group(0)
    t = re.sub(r' ?\(([^()]*)\)', strip_paren, t)
    lines = []
    for ln in t.split('\n'):
        if re.fullmatch(r'[A-Z][^:]*: ?[+x]?(?:X|[\d.,]+|INF)[%.]*\.?', ln.strip()): continue  # readout lines
        lines.append(ln.rstrip())
    t = '\n'.join(lines).strip()
    return re.sub(r'\n{3,}', '\n\n', t)


# The game prints big numbers with its suffix table (" M"," B"," T"," Qa",...): index i means 10^(6+3i).
_dsrc = open(os.path.join(ROOT, 'out', 'script', 'scripts', '§-D§.as'), encoding='utf8').read()
_suffixes = [x.strip() for x in re.findall(r'"( [A-Za-z]+)"', re.search(r'§1X§:Array = \[(.*?)\];', _dsrc).group(1))]
SUFFIX_EXP = {sfx: 6 + 3 * i for i, sfx in enumerate(_suffixes)}
SUFFIX_RE = re.compile(r'(?<![\w.])(\d+(?:\.\d+)?) ?(' + '|'.join(sorted(map(re.escape, SUFFIX_EXP), key=len, reverse=True)) + r')(?![A-Za-z])')
_SUP = str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻')


def pow10_text(text):
    """'10 M' -> '1e7', '1.5 B' -> '1.5e9' (plain numbers and times are left alone)."""
    def rep(m):
        mant, e = float(m.group(1)), SUFFIX_EXP[m.group(2)]
        while mant >= 10: mant /= 10; e += 1
        while 0 < mant < 1: mant *= 10; e -= 1
        mant = round(mant, 6)
        return f'{mant:g}e{e}'
    return SUFFIX_RE.sub(rep, text)


def clean_req(req, row):
    out, res = [], []
    for ln in req.replace('\r', '').split('\n'):
        ln = ln.strip()
        if not ln or ln == 'Progress:': continue
        m = re.match(r'^Research \d: (.+)$', ln)
        if m: res.append(m.group(1)); continue
        ln = re.sub(r'^Progress: ?', '', ln)
        if ln: out.append('Reach ' + pow10_text(ln))
    if res: out.append('Have bought the researches ' + ' and '.join(res))
    return out


# ---- formulas ----------------------------------------------------------------------------------
def formulas_for(c, q):
    """Single-expression getters/methods of the research class that its description text reads."""
    meths = {m.name: m for m in c.methods}
    desc = meths.get('§@"§')
    used = []
    if desc is not None:
        body = desc.body
        used = [n for n in re.findall(r'(§[^§]*§)\(\)', body) if n in meths and n != '§@"§']
    out = []
    for n in dict.fromkeys(used):
        b = re.sub(r'\s+', ' ', meths[n].body.strip())
        m = re.fullmatch(r'return (.+);', b)
        if not m: out.append((n, None, b)); continue
        out.append((n, m.group(1).strip(), b))
    return out, desc


def name_of_for(c):
    def f(tok):
        q = resolve(c, tok, cl)
        return named.get(q) if q else None
    return f


def sym_desc(c, desc, key):
    """Label for a formula: the line of the description that shows it."""
    if desc is None: return None
    body = desc.body
    m = re.search(r'_\("((?:[^"\\]|\\.)*)"[^;]*' + re.escape(key) + r'\(\)', body, re.S)
    if not m: return None
    tmpl = m.group(1).replace("\\'", "'")
    return tmpl


_base = next((k for k in cl.values() if k.name == '§&!_§'), None)
_cap_q = resolve(_base, '§#"3§', cl) if _base else None
CAP_ARTIFACT = (named.get(_cap_q) or [None, None])[1] if _cap_q else None
print('research cap artifact:', CAP_ARTIFACT)
KEEP_TEXT_VARIANTS = {'Estates'}
# production effects the Ascension penalty hits that the description does not show: name -> (first Ascension, no penalty at Ascension 4)
PEN_FIX = {'Journeymen': (1, False), 'Hierarchy': (1, False), 'Solemnity': (2, False),
           'Upheaval': (2, False), 'Decentralization': (4, False)}
# Weighting's first value is 2000^tier (%), the targeted building's own bonus; the user judged it self-evident from the text
DROP_FORMULAS = {'Weighting': {0}}

# values read from the production / spell code (the research's own text shows no number)
def _F(latex, *vs, label=None):
    f = {'latex': latex, 'vars': [{'symbol': a, 'text': b} for a, b in vs], 'scale': None}
    if label: f['label'] = label
    return f


_T = ('T', "The building's tier (1 for the first building in the list)")
_J = ('j', 'Tier Brainwave is cast at, minus 1 (0 for the base tier)')
_BW = ('t', 'Seconds since Brainwave was cast (while it is active)')
MANUAL_FORMULAS = {
    'Illusion': [_F(r'v = 1 + 0.25 \cdot \left(t + 600 \cdot j\right)^{1.5}', _BW, _J)],
    'Compression': [_F(r'v = 1.5 \cdot \left(\frac{t + 600 \cdot j}{60}\right)^{2.25}', _BW, _J)],
    'Hierarchy': [_F(r'v = 0.1 \cdot W^{0.45} \cdot \left(12 - T\right)^{2}', ('W', 'Mana produced in this Era'), _T,
                     label='Production of each building (%)')],
    'Journeymen': [_F(r'v = 25 + 1.25 \cdot t^{0.75}',
                      ('t', "Time spent with the building's alignment in this Reincarnation (seconds)"),
                      label='Production of each Unique Building (%)')],
    'Distribution': [_F(r'v = 0.4 \cdot t^{0.6}',
                        ('t', 'Time spent with alignments other than your current one in this Reincarnation (seconds)'))],
    'Installation': [_F(r'v = 1.3 \cdot N^{0.7}', ('N', 'Number of buildings of that type you own'), label='Production of each building (%)')],
    'Scriptures': [_F(r'v = 0.3 \cdot t^{0.7}',
                      ('t', "Time spent with the spell's requirement (its faction or alignment) in this Reincarnation (seconds)"),
                      label='Duration of each spell (%)')],
    'Asceticism': [_F(r'v = 10', label='Share of the time you spend with a faction that you also gain with every other faction (%)')],
    'Decentralization': [_F(r'v = \left(3 - 0.25 \cdot T\right)^{4} \cdot B^{0.6}', _T, ('B', 'Buildings you have built'),
                            label='Production of each building (%)')],
    'Reduction': [_F(r'v = \max\left(10, \min\left(90, \left(\ln\left(1 + \frac{D}{D_{0}}\right)\right)^{2}\right)\right)',
                     ('D', "The spell's duration (seconds)"), (r'D_{0}', "The spell's base duration (seconds)"), label='Spell cost reduction (%)')],
    'Upheaval': [_F(r'v = 0.5 \cdot \left(60 + t\right)^{0.75} \cdot \left(12 - T\right)^{2.15}',
                    ('t', 'Time spent with your least used alignment in this Reincarnation (seconds)'), _T,
                    label='Production of each building (%)')],
}
# factions that can be a prestige faction (the research condition is "faction == X or prestige faction == X")
PRESTIGE = {9, 10, 12}
TRIM = {0: 'Fairy', 1: 'Elven', 2: 'Angel', 3: 'Goblin', 4: 'Undead', 5: 'Demon', 6: 'Titan', 7: 'Druid', 8: 'Faceless',
        9: 'Dwarven', 10: 'Drow', 11: 'Mercenary', 12: 'Dragon'}
# What each value of a two-value research is, in the order the game's text lists them (its readout lines
# "Max Mana: +%0." / "(Additive: +%0, Multiplicative: %1%)" or the order of its %n placeholders).
FORMULA_LABELS = {
    'Diplomacy': ['Faction Coin find chance (%)', 'Royal Exchange bonus (%)'],
    'Vacuumancy': ['Maximum Mana', 'Mana Regeneration'],
    'Heirlooms': ['Maximum Mana', 'Mana Regeneration'],
    'Transubstantiation': ['Maximum Mana, additive', 'Maximum Mana, multiplicative (%)'],
    'Invocation': ['Maximum Mana, additive', 'Maximum Mana, multiplicative (%)'],
    'Spellbinding': ['Call to Arms counts more buildings', 'Offline production (%)'],
    'Vampirism': ['Assistants, additive', 'Assistants, multiplicative (%)'],
    'Manufacture': ['Faction Coin find chance, additive (%)', 'Faction Coin find chance, multiplicative (%)'],
    'Whipround': ['Royal Exchange bonus, additive (%)', 'Royal Exchange bonus, multiplicative (%)'],
}
CODE_LETTER = {0: 'S', 1: 'C', 2: 'D', 3: 'E', 4: 'A', 5: 'W', 6: 'F'}   # F (Forbidden) is an assumption
def inline_helpers(c, expr):
    """Replace calls to one-expression methods of the research class that only wrap param1 (e.g. Backfire's 0.75*x^0.75)."""
    meths = {m.name: m for m in c.methods}
    for _ in range(4):
        def rep(m):
            mm = meths.get(m.group(1))
            if mm is None: return m.group(0)
            b = re.fullmatch(r'return (.+);', re.sub(r'\s+', ' ', mm.body.strip()))
            if not b or 'param1' not in b.group(1) or 'param2' in b.group(1): return m.group(0)
            return '(' + b.group(1).replace('param1', '(' + m.group(2) + ')') + ')'
        new = re.sub(r'(§[^§]*§)\(((?:[^()]|\([^()]*(?:\([^()]*\))?[^()]*\))*)\)', rep, expr)
        if new == expr: break
        expr = new
    return expr


def merge_same(forms, name=''):
    """Backfire shows six values that all use 0.75 * x^0.75; list the six inputs in the order of its text."""
    if name != 'Backfire': return forms
    T = lambda what: f'Time spent with {what} alignment in this Reincarnation (seconds)'
    P = lambda a, b: f'Time spent with {a} alignment plus time spent with {b} alignment, both in this Reincarnation (seconds)'
    xs = [T('Good'), T('Order'), P('Good', 'Order'), T('Evil'), T('Chaos'), P('Evil', 'Chaos')]
    sc = forms[0].get('scale') if forms else 5
    return [{'latex': 'v = 0.75 \cdot x^{0.75}', 'scale': sc,
             'vars': [{'symbol': f'x_{{{i + 1}}}', 'text': t} for i, t in enumerate(xs)]}]


out = []
unconv = {}
for idx, (r, a, b) in enumerate(zip(rows, mut[0], mut[1])):
    c = cl.get(r['q'])
    texts = [r['desc'], a['desc'], b['desc']]
    desc = clean_desc(texts) if not r['desc'].startswith('ERR') else ''
    if not desc and r['n'] == 'Paradox':   # its description reads a set bonus that needs a live game state
        desc = 'Gain the Primary Set bonus of the base faction of your opposite alignments.'
    if r['n'] == 'Patience': desc = re.sub(r' \([A-Z][a-z]+\)', '', desc)      # a live readout: the faction that is least used right now
    fs, dm = formulas_for(c, r['q']) if c else ([], None)
    forms = []
    for key, expr, body in fs:
        if expr is None or re.fullmatch(r'-?[\d.]+', expr or ''): continue
        expr = inline_helpers(c, expr)
        # offline-progress terms: non-zero only while the game simulates offline time (see INFERENCES.md)
        expr = re.sub(r'§#!!§\.(?:§2!P§|§ !O§) / 2 \+ ', '', expr)
        cv = convert(expr, name_of_for(c))
        # the description shows percentages through §&c§.§6!T§(value[, from-Ascension]), which applies the
        # Ascension reduction (x -> x^(0.1^(A - a + 1)) on 1 + v/100 from Ascension a)
        sm = re.search(r'§&c§\.§6!T§\(' + re.escape(key) + r'\(\)(?:,(\d+))?\)', dm.body) if dm is not None else None
        scale = (int(sm.group(1)) if sm.group(1) else 1) if sm else None
        if cv: forms.append({'latex': cv['latex'].replace('p = ', 'v = ', 1), 'vars': cv['vars'], 'scale': scale})
        else: unconv[(r['n'], key)] = expr
    forms = merge_same(forms, r['n'])
    if r['n'] in MANUAL_FORMULAS and not forms:
        forms = [dict(f, vars=list(f['vars'])) for f in MANUAL_FORMULAS[r['n']]]
    if r['n'] in DROP_FORMULAS:
        forms = [f for i, f in enumerate(forms) if i not in DROP_FORMULAS[r['n']]]
    if len(forms) > 1:
        lab = FORMULA_LABELS.get(r['n'])
        assert lab and len(lab) == len(forms), f"label the values of {r['n']} ({len(forms)} formulas)"
        for f, t in zip(forms, lab): f['label'] = t
    branch = BR[r['b']] if 0 <= r['b'] < len(BR) else '?'
    def make_reqs(game_text):
        reqs = []
        if r['f'] != -1 and r['f'] != r['h']:
            fn = FACTION.get(r['f'], f'faction {r["f"]}')
            reqs.append(f'Have {fn} as prestige faction' if r['f'] in PRESTIGE else f'Play as {fn}')
        reqs += clean_req(game_text, r)
        if r['w'] >= 5000:
            reqs.append(f'Reincarnation 180 or higher, and the artifact {CAP_ARTIFACT}' if CAP_ARTIFACT
                        else 'Reincarnation 180 or higher')
        return reqs
    reqs = make_reqs(r['req'])
    # first Ascension in which the game stops offering it (availability getter of the research base class)
    unavail = 3 if r['w'] < 405 else (4 if r['w'] < 5000 else None)
    avail = next((m for m in c.methods if m.name == '§9!%§'), None) if c else None
    merc = bool(avail is not None and re.search(r'§-!\^§ == 11', avail.body))
    # alignment lock: the research's own alignment must equal yours (`9!%` compares them); Common Business excludes Neutral
    ALN = {1: 'Good', 2: 'Evil', 3: 'Neutral', 4: 'Order', 5: 'Chaos', 6: 'Balance'}
    al_lock = al_not = None
    if avail is not None and r['h'] == -1:
        if re.search(r'§8G§\.§,!Y§ == §,!Y§', avail.body) and r['al'] in ALN: al_lock = ALN[r['al']]
        elif re.search(r'§8G§\.§9!m§ == §9!m§', avail.body) and r['ax'] in ALN: al_lock = ALN[r['ax']]
        elif re.search(r'§8G§\.§,!Y§ != 3', avail.body): al_not = 'Neutral'
    # what a Mercenary needs: the faction lock does not apply to them unless the research has its own rule
    merc_note = ''
    if r['h'] not in (-1, 11):
        body = avail.body if avail is not None else ''
        if re.search(r'§-!\^§ != 11', body):
            merc_note = 'Mercenaries cannot buy it.'
        else:
            items = []
            for tok in dict.fromkeys(re.findall(r'(§[^§]*§)\.id', body)):
                n = name_of_for(c)(tok)
                if n and n[0] in ('upgrade', 'spell'): items.append(n)
            if items:
                bits = [f'the spell {v} unlocked' if k == 'spell' else f'the upgrade {v}' for k, v in items]
                merc_note = 'Mercenaries can also buy it once they have ' + ' and '.join(bits) + '.'
            else:
                merc_note = 'Mercenaries can also buy it.'
    # text that changes with the Ascension
    by_asc, prev = {}, (desc, reqs)
    for A in range(1, MAX_ASC + 1):
        rr = runs[A][0]['rows'][idx]
        dd = clean_desc([runs[A][k]['rows'][idx]['desc'] for k in range(3)]) if not rr['desc'].startswith('ERR') else desc
        if not dd and desc: dd = desc
        cur = (dd, make_reqs(rr['req']))
        if cur != prev:
            by_asc[A] = {'description': cur[0], 'requirements': cur[1]}
            prev = cur
    # The other per-Ascension differences ("by 160% per Gate" vs "based on Gates", values already reduced, a Gems
    # readout) are the Ascension penalty showing through; the page covers them with the A marks.  Estates really
    # changes what it does from Ascension 3, so its text variant is kept.
    by_asc = {k: v for k, v in by_asc.items() if r['n'] in KEEP_TEXT_VARIANTS}
    out.append({
        'branch': r['b'], 'branch_name': branch, 'number': r['w'], 'index': r['u'], 'name': r['n'],
        'code': CODE_LETTER.get(r['b'], '?') + str(r['w']),
        'icon': r['icon'] if r['icon'] in sprites else None, 'icon_name': r['icon'],
        'pen': PEN_FIX.get(r['n']), 'description': desc, 'formulas': forms, 'requirements': reqs, 'hint': (r['hint'] or '').strip(),
        'faction': r['h'], 'faction_name': FACTION.get(r['h']) if r['h'] != -1 else None,
        'faction_kind': None if r['h'] == -1 else ('prestige' if r['h'] in PRESTIGE else 'base'),
        'unlock_faction': r['f'], 'unlock_faction_name': FACTION.get(r['f']) if r['f'] != -1 else None,
        'mercenary_note': merc_note, 'alignment_lock': al_lock, 'alignment_not': al_not,
        'unavailable_from': unavail, 'mercenary_exception': merc, 'by_ascension': by_asc,
    })
# cell background per faction: the game draws each faction's "<Name>Trim" texture; use its fill colour
from PIL import Image
FACTION_COLORS = {}
for fid, nm in TRIM.items():
    im = Image.open(os.path.join(ROOT, sprites[nm + 'Trim'][0]['file'])).convert('RGBA')
    FACTION_COLORS[str(fid)] = '#%02x%02x%02x' % im.getpixel((im.width // 2, im.height // 2))[:3]
ALIGN_COLORS = {}
for nm in ('Good', 'Evil', 'Order', 'Chaos', 'Balance'):
    im = Image.open(os.path.join(ROOT, sprites[nm + 'Trim'][0]['file'])).convert('RGBA')
    ALIGN_COLORS[nm] = '#%02x%02x%02x' % im.getpixel((im.width // 2, im.height // 2))[:3]
json.dump({'max_ascension': MAX_ASC, 'faction_colors': FACTION_COLORS, 'alignment_colors': ALIGN_COLORS}, open(os.path.join(ROOT, 'data', 'research_meta.json'), 'w'))
out.sort(key=lambda x: (x['branch'], x['number'], x['index']))
json.dump(out, open(os.path.join(ROOT, 'data', 'research.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
json.dump({f'{k[0]}::{k[1]}': v for k, v in unconv.items()},
          open(os.path.join(HERE, '_res_unconv.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
print(len(out), 'researches |', sum(1 for x in out if x['formulas']), 'with formulas |', len(unconv), 'formulas not converted |',
      sum(1 for x in out if not x['description']), 'without description |',
      sum(1 for x in out if 'X' in re.findall(r'\bX\b', x['description'])), 'with a live value left')
