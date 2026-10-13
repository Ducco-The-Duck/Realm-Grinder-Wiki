"""Export the Secret upgrades (upgrade category 4) to data/upgrades_secret.json.

Per upgrade: name, icon, the game's description with formulas where the text shows a computed value, and how it
is unlocked: the trophy / artifact (or upgrade) its availability check reads, plus the other conditions the check
has (faction, alignment, Ascension).  Conditions that cannot be put into words are listed under `undecoded`.

    python -I tools/export_upgrades.py
"""
import json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'pylib'))
import quickjs
from as3parse import parse_all, resolve
import desc_tools as D
from numtext import pow10_text
from chance_latex import convert

names = json.load(open(os.path.join(ROOT, 'data', 'engine_names.json'), encoding='utf8'))['names']
sprites = json.load(open(os.path.join(ROOT, 'data', 'sprites.json')))
J = lambda t: names[t]
g = J('§8G§')
ENGINE = open(os.path.join(ROOT, 'data', 'engine.js'), encoding='utf8').read()
SECRET = 4          # the game's category index of "Secret Upgrades"

MUT = f"""
  var G = {g}, v = __V;
  [G.{J('§5!V§')}, G.{J('§=y§')}, G.{J('§@w§')}, G.{J('§1!#§')}].forEach(function (a) {{ for (var i = 0; i < a.length; i++) a[i] = v; }});
  G.{J('§%<§')}.forEach(function (b) {{ b.{J('§!a§')} = v; }});
  G.{J('§0!A§')}.forEach(function (s) {{ s.{J('§2-§')} = v; s.{J('§?j§')} = v; s.{J('§<q§')} = v; s.{J('§<!G§')} = v; }});
"""
PROBE = f"""(function () {{ __MUT
  var U = {g}.{J('§-!4§')}, out = [], named = {{}};
  var qOf = function (o) {{ for (var c = 0; c < __classes.length; c++) if (__classes[c].K === o.constructor) return __classes[c].q; return null; }};
  var lists = {{ upgrade: U, trophy: {g}.{J('§0Q§')}, spell: {g}.{J('§0!A§')}, building: {g}.{J('§%<§')} }};
  for (var k in lists) for (var i = 0; i < lists[k].length; i++) {{ var q = qOf(lists[k][i]); if (q !== null) named[q] = [k, lists[k][i].{J('§1i§')}, !!lists[k][i].{J('§@!R§')}]; }}
  for (var i = 0; i < U.length; i++) {{ var o = U[i];
    if (o.{J('§,!B§')} !== {SECRET}) continue;
    var r = {{ q: qOf(o), n: o.{J('§1i§')}, icon: o.{J('§^!#§')}, id: o.id, i: i }};
    try {{ r.d = o.{J('§@"§')}(); }} catch (e) {{ r.d = 'ERR ' + e; }}
    out.push(r); }}
  return JSON.stringify({{ rows: out, named: named }}); }})()"""


def probe(v=None):
    ctx = quickjs.Context(); ctx.eval(ENGINE); ctx.eval('__boot()')
    pre = MUT.replace('__V', str(v)) if v is not None else ''
    return json.loads(ctx.eval(PROBE.replace('__MUT', pre)))


runs = [probe(), probe(1000), probe(98765)]
rows, named = runs[0]['rows'], runs[0]['named']
cl = parse_all()
D.init(cl, named, pow10_text)

FACTION = {0: 'Fairy', 1: 'Elf', 2: 'Angel', 3: 'Goblin', 4: 'Undead', 5: 'Demon', 6: 'Titan', 7: 'Druid', 8: 'Faceless',
           9: 'Dwarf', 10: 'Drow', 11: 'Mercenary', 12: 'Dragon', 13: 'Archon', 14: 'Djinn', 15: 'Makers'}
ALIGN = {1: 'Good', 2: 'Evil', 3: 'Neutral'}

tro = json.load(open(os.path.join(ROOT, 'data', 'trophies.json'), encoding='utf8'))
art = json.load(open(os.path.join(ROOT, 'data', 'artifacts.json'), encoding='utf8'))
TROPHY = collections.defaultdict(list)
for t in tro: TROPHY[t['name']].append(t)
ARTIFACT = {a['name']: a for a in art}


def split_and(expr):
    out, depth, cur = [], 0, ''
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if depth == 0 and expr.startswith(' && ', i):
            out.append(cur.strip()); cur = ''; i += 4; continue
        cur += ch; i += 1
    if cur.strip(): out.append(cur.strip())
    return out


G = r'§8G§\.'
FAC, PRE, AST, AL = G + r'§-!\^§', G + r'§#3§', G + r'§-!x§', G + r'§,!Y§'
ASC = G + r'§,P§'


def faction_range(a, b):
    if (a, b) == (0, 5): return 'playing as a Vanilla faction (Fairy, Elf, Angel, Goblin, Undead or Demon)'
    if (a, b) == (6, 8): return 'playing as a Neutral faction (Titan, Druid or Faceless)'
    return None


def asc_text(lo, hi):
    """lo inclusive, hi exclusive (None = no bound)"""
    if lo is None and hi is not None: return f'Ascension {hi - 1} or lower' if hi > 1 else 'No Ascension yet'
    if hi is None: return f'Ascension {lo} or higher'
    return f'Ascension {lo} to {hi - 1}' if hi - 1 > lo else f'Ascension {lo}'


def decode(body, c):
    """-> (sources [{kind, name}], conditions [str], undecoded [str])"""
    nm = D.name_of_for(c)
    src, cond, bad = [], [], []
    m = re.fullmatch(r'return (.+);', body)
    if not m: return src, cond, [body], (None, None)
    asc_lo = asc_hi = fac_lo = fac_hi = None
    for cl_ in split_and(m.group(1)):
        t = cl_
        mm = re.fullmatch(r'§8G§\.§<P§\((§[^§]*§)\.id\)', t)
        if mm:
            n = nm(mm.group(1)); src.append({'kind': 'artifact' if n and n[2] else 'trophy', 'name': n[1]} if n else {'kind': '?', 'name': mm.group(1)}); continue
        mm = re.fullmatch(r'§8G§\.§7d§\((§[^§]*§)\.id\)', t)
        if mm:
            n = nm(mm.group(1)); src.append({'kind': 'upgrade', 'name': n[1]}); continue
        mm = re.fullmatch(r'§8G§\.§,#§\(_\("([^"]+)"\)\)', t)
        if mm: src.append({'kind': 'trophy', 'name': mm.group(1)}); continue
        mm = re.fullmatch(ASC + r' (<|>=|>|<=) (\d)', t)
        if mm:
            op, n = mm.group(1), int(mm.group(2))
            if op == '<': asc_hi = n if asc_hi is None else min(asc_hi, n)
            elif op == '<=': asc_hi = n + 1
            elif op == '>=': asc_lo = n
            else: asc_lo = n + 1
            continue
        mm = re.fullmatch(r'\(?' + FAC + r' >= (\d+) && ' + FAC + r' <= (\d+)\)?', t)
        if mm:
            r = faction_range(int(mm.group(1)), int(mm.group(2)))
            if r: cond.append(r); continue
        mm = re.fullmatch(FAC + r' == (\d+)', t)
        if mm: cond.append(f'playing as {FACTION[int(mm.group(1))]}'); continue
        mm = re.fullmatch(r'\(' + FAC + r' == 6 \|\| ' + FAC + r' == 7 \|\| ' + FAC + r' == 8\)', t)
        if mm: cond.append('playing as a Neutral faction (Titan, Druid or Faceless)'); continue
        mm = re.fullmatch(r'\(' + PRE + r' == 9 \|\| ' + PRE + r' == 10 \|\| ' + PRE + r' == 12\)', t)
        if mm: cond.append('having a Prestige faction (Dwarf, Drow or Dragon)'); continue
        mm = re.fullmatch(PRE + r' == (\d+)', t)
        if mm: cond.append(f'having {FACTION[int(mm.group(1))]} as your prestige faction'); continue
        mm = re.fullmatch(r'\(' + AST + r' == 13 \|\| ' + AST + r' == 14 \|\| ' + AST + r' == 15\)', t)
        if mm: cond.append('having an Astral faction (Archon, Djinn or Makers)'); continue
        mm = re.fullmatch(AL + r' == (\d)', t)
        if mm: cond.append(f'having {ALIGN[int(mm.group(1))]} alignment'); continue
        if re.fullmatch(AL + r' != 0', t) or re.fullmatch(G + r'§9!m§ != 0', t) or re.fullmatch(FAC + r' != -1', t):
            continue        # "an alignment / faction is set": always true while playing
        if re.fullmatch(AL + r' != 3', t):
            cond.append('having a Good or Evil alignment'); continue
        if re.fullmatch(r'\(' + AL + r' == 1 \|\| ' + AL + r' == 2\)', t):
            cond.append('having a Good or Evil alignment'); continue
        mm = re.fullmatch(FAC + r' (>=|<=) (\d+)', t)
        if mm:
            if mm.group(1) == '>=': fac_lo = int(mm.group(2))
            else: fac_hi = int(mm.group(2))
            continue
        if t == '§#!!§.§`Q§ != -1':
            cond.append('using a bloodline'); continue
        if t == '§&c§.§9X§()':
            cond.append('being able to access Research'); continue
        if t.startswith('(§#!!§.§6!r§ != -1 && ') and '§1"0§' in t:
            cond.append('having a Set faction (or Astral Set faction) with the same alignment as your faction'); continue
        mm = re.fullmatch(r'§-"3§\.§\+"8§\((\d+)\)', t)
        if mm:
            cond.append(f'having bought upgrades from at least {mm.group(1)} different factions other than Mercenary'); continue
        bad.append(t)
    if fac_lo is not None and fac_hi is not None:
        r = faction_range(fac_lo, fac_hi)
        if r: cond.append(r)
        else: bad.append(f'faction {fac_lo}..{fac_hi}')
    return src, cond, bad, (asc_lo, asc_hi)


CATEGORY = {0: 'Allegiances', 1: 'Miscellaneous', 2: 'Magic', 3: 'Building', 4: 'Secret'}   # the Trophies page sections
amb = []


def describe_source(s):
    """what the availability check reads, named by the page the user finds it on"""
    if s['kind'] == 'upgrade': return {'kind': 'Upgrade', 'name': s['name']}
    if s['kind'] == 'artifact':
        a = ARTIFACT.get(s['name'])
        return {'kind': 'Lore artifact' if (a or {}).get('kind') == 'lore' else 'Quest artifact', 'name': s['name']}
    ts = TROPHY.get(s['name'], [])
    cats = {t['category'] for t in ts}
    if len(cats) != 1: amb.append((s['name'], cats))
    return {'kind': f"{CATEGORY.get(min(cats), '?')} trophy" if cats else 'Trophy', 'name': s['name']}


# live readouts: numbers that differ between the three game states
def clean_lines(r0, r1, r2):
    a, b, c = (x.split('\n') for x in (r0, r1, r2))
    return a, (b if len(b) == len(a) else a), (c if len(c) == len(a) else a)


def _m(latex, *vs):
    return {'latex': latex, 'vars': [{'symbol': a, 'text': b} for a, b in vs]}


# formulas the converter cannot read (multi-statement getters, time-of-day or alignment switches); in order of the
# unconverted ones of each upgrade, None = an intermediate value that is not shown as a formula
MANUAL_RAW = {
    'Bloodstream': [None, _m(
        r'v = 0.1 \cdot \left(t_{1} + t_{2} + t_{3}\right)^{0.65}',
        ('t_{1}', 'Your all-time time with the bloodline faction (seconds)'),
        ('t_{2}', 'Your all-time time with your current (prestige, if applicable) faction, if you have Bloodspring (A400) '
                  '(seconds)'),
        ('t_{3}', '1/12 of your all-time time with Mercenaries per bloodline faction upgrade bought, if you are playing '
                  'Mercenaries (seconds)'))],
    'Holy Frenzy': [_m(
        r'v = 250 \cdot j^{2}',
        ('j', 'The higher of the tiers Blood Frenzy and Holy Light are cast at (1 is the base tier, also while neither is active)'))],
    'Lantern of Guidance': [_m(
        r'v = \left(4 \cdot M^{0.2}\right)^{p}',
        ('M', 'Your mana regeneration per second'), ('p', '1.5 while playing as an Order faction, otherwise 1'))],
    'Oil Lamp': [_m(
        r'v = \left(9 \cdot M_{\max}^{0.2}\right)^{p}',
        (r'M_{\max}', 'Your Maximum Mana'), ('p', '1.5 while playing as a Chaos faction, otherwise 1'))],
    'Spark of Life': [_m(
        r'v = \left(Q^{0.2}\right)^{p}',
        ('Q', 'Your Faction Coin find chance (%)'), ('p', '1.5 while playing as a Balance faction, otherwise 1'))],
    'MAD Masks': [_m(
        r'v = 1.5 \cdot D^{0.6}', ('D', 'Deepest excavation depth you have reached in this Reincarnation'))],
    'Future Linkin': [_m(r'v = 214 + 0.03 \cdot t^{0.7}', ('t', 'Length of your last Era (seconds)'))],
    "God's Fingers": [None],
}


READOUT = re.compile(r'\s*\((?:v[₁₂₃₄₅₆₇₈₉]?%?|\+?-?(?:[\d.,]+|INF|NaN)%?)\)(?=\.?$|\s+[A-Z])')


def fix_text(name, paras):
    """readouts that stayed in the text, and the few descriptions that need a hand"""
    drop = [p for p in paras if p['text'].startswith('Adjusted time spent for')]
    paras[:] = [p for p in paras if p not in drop]
    for p in drop:
        paras[0]['formulas'] += p['formulas']
        if paras[0].get('s') is None: paras[0]['s'] = p.get('s')
    if name == 'Suggestion Master':
        paras[0]['formulas'] = []
        paras[0]['text'] = 'Increase the production of all buildings based on mysterious events. (43.14%)'
    if name == 'Art of the Crow':
        spec = {
            'Good:': (r'v = 0.1 \cdot D^{0.9}', ('D', 'Your excavation depth (excavations made since your last Excavation Reset)')),
            'Neutral:': (r'v = 1.5 \cdot N^{0.6}', ('N', 'Royal Exchanges made in this Era')),
            'Evil:': (r'v = \left(\ln\left(1 + W\right)\right)^{2}', ('W', 'Mana produced in this Reincarnation')),
        }
        for p in paras:
            for k, (lt, var) in spec.items():
                if p['text'].startswith(k): p['formulas'] = [_m(lt, var)]
    for p in paras:
        p['text'] = READOUT.sub('', p['text']).strip()


def fix_raw(name, c, paras):
    manual = list(MANUAL_RAW.get(name, []))
    for p in paras:
        new = []
        for f in p['formulas']:
            if 'raw' not in f: new.append(f); continue
            e = f['raw']
            m = re.match(r"^.* \? (.+) : 0$", e)
            if m and ("§'!O§" in e or '§8G§.§-!^§ == 11' in e):       # only counts at some time of day / as Mercenary
                cv = convert(D.inline_helpers(c, m.group(1)), D.name_of_for(c))
                if cv:
                    new.append({'latex': cv['latex'].replace('p = ', 'v = ', 1), 'vars': cv['vars']}); continue
            if manual:
                r = manual.pop(0)
                if r is not None: new.append(r)
                continue
            new.append(f)
        p['formulas'] = new


out = []
problems = []
for idx, r in enumerate(rows):
    tok = r['q'].split('.')[-1]
    c = next(k for k in cl.values() if k.name == tok)
    templates = D.formulas_for(c, r['n'])
    texts = [rr['rows'][idx]['d'] for rr in runs]
    lines0, lines1, lines2 = clean_lines(*texts)
    paras = []
    for k, ln in enumerate(lines0):
        if not ln.strip(): continue
        p = D.para(c, templates, ln, r['n'])
        if p['text'] == D.pow10_text(ln.strip()) and not p['formulas']:
            # no template matched: drop a trailing live readout "(x%)" if the numbers change between states
            if not (ln == lines1[k] == lines2[k]):
                p['text'] = pow10_text(re.sub(r'\s*\((?:[^()]*)\)\s*$', '', ln).strip())
        paras.append(p)
    fix_raw(r['n'], c, paras)
    fix_text(r['n'], paras)
    av = next((m for m in c.methods if m.name == '§-6§'), None)
    body = re.sub(r'\s+', ' ', av.body.strip()) if av else ''
    src, cond, bad, (alo, ahi) = decode(body, c)
    if bad: problems.append((r['n'], bad))
    out.append({
        'name': r['n'], 'icon': r['icon'] if r['icon'] in sprites else None, 'order': r['i'], 'id': r['id'],
        'description': paras, 'sources': [describe_source(s) for s in src], 'conditions': cond, 'undecoded': bad, 'asc_min': alo, 'asc_max': ahi,
    })

# value symbols: v, or v1, v2 ... when a description has several computed values
raw = []
for u in out:
    forms = [f for p in u['description'] for f in p['formulas']]
    for f in forms:
        if 'raw' in f: raw.append((u['name'], f['raw']))
    conv = [f for f in forms if 'latex' in f]
    if len(conv) > 1:
        for k, f in enumerate(conv, 1):
            f['latex'] = re.sub(r'^v(?:_\{\d+\})? = ', f'v_{{{k}}} = ', f['latex'])
for n, e in raw: print('RAW', n, '|', e[:200])

json.dump(out, open(os.path.join(ROOT, 'data', 'upgrades_secret.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
print('ambiguous trophy names:', amb)
print('data/upgrades_secret.json:', len(out), 'upgrades;',
      'with formulas:', sum(1 for u in out if any(p['formulas'] for p in u['description'])),
      '| undecoded conditions:', len(problems))
for n, b in problems: print('  ', n, b)
