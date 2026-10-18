"""Export the Secret, Magic and Buildings upgrades (upgrade categories 4, 2, 3) to data/upgrade_pages.json.

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
import misc_manual as MM
import alleg_manual as AM
import alleg_manual_family as AMF  # (also adds the family formulas to AM.FORMULAS)
from numtext import pow10_text
from chance_latex import convert

names = json.load(open(os.path.join(ROOT, 'data', 'engine_names.json'), encoding='utf8'))['names']
sprites = json.load(open(os.path.join(ROOT, 'data', 'sprites.json')))
J = lambda t: names[t]
g = J('§8G§')
ENGINE = open(os.path.join(ROOT, 'data', 'engine.js'), encoding='utf8').read()
CATS = {0: 'allegiances', 4: 'secret', 2: 'magic', 3: 'buildings', 1: 'misc'}      # the game's category indexes of the upgrade sections

MUT = f"""
  var G = {g}, v = __V;
  [G.{J('§5!V§')}, G.{J('§=y§')}, G.{J('§@w§')}, G.{J('§1!#§')}].forEach(function (a) {{ for (var i = 0; i < 200; i++) a[i] = v; }});
  G.{J('§%<§')}.forEach(function (b) {{ b.{J('§!a§')} = v; }});
  G.{J('§0!A§')}.forEach(function (s) {{ s.{J('§2-§')} = v; s.{J('§?j§')} = v; s.{J('§<q§')} = v; s.{J('§<!G§')} = v; }});
"""
PROBE = f"""(function () {{ __MUT
  var U = {g}.{J('§-!4§')}, out = [], named = {{}};
  var qOf = function (o) {{ for (var c = 0; c < __classes.length; c++) if (__classes[c].K === o.constructor) return __classes[c].q; return null; }};
  var lists = {{ upgrade: U, trophy: {g}.{J('§0Q§')}, spell: {g}.{J('§0!A§')}, building: {g}.{J('§%<§')} }};
  for (var k in lists) for (var i = 0; i < lists[k].length; i++) {{ var q = qOf(lists[k][i]); if (q !== null) named[q] = [k, lists[k][i].{J('§1i§')}, !!lists[k][i].{J('§@!R§')}]; }}
  for (var i = 0; i < U.length; i++) {{ var o = U[i];
    var cat = o.{J('§,!B§')}; if (cat !== 0 && cat !== 1 && cat !== 2 && cat !== 3 && cat !== 4) continue;
    var r = {{ q: qOf(o), n: o.{J('§1i§')}, icon: o.{J('§^!#§')}, id: o.id, i: i, cat: cat, f: o.{J('§-!^§')}, grp: o.{J('§@1§')},
              tier: o.{J('§"!U§')}, thr: o.{J('§^!]§')}, idx: o.{J('§!"E§')}, coins: o.{J('§>=§')}, ax: o.{J('§9!m§')},
              sg: o.{J('§`g§')}, sr: o.{J('§`r§')}, sw: o.{J('§2!w§')}, sv: o.{J('§;!v§')}, tg: o.{J('§?!=§')} }};
    try {{ r.bld = o.{J('§%<§')}.{J('§1i§')}; }} catch (e) {{}}
    try {{ r.tid = o.{J('§`!5§')}; }} catch (e) {{}}
    var keepR = {g}.{J('§8!H§')};
    var keepFa = {g}.{J('§-!^§')}, isUnion = /Union$/.test(r.n) && r.f >= 0;
    if (r.grp === 'ReincarnationPowerUpgrade' || isUnion) {g}.{J('§8!H§')} = 9999;      // show every line of the text
    if (isUnion) {g}.{J('§-!^§')} = r.f;      // the Union's text is the one of its own faction
    var keepAl = {g}.{J('§,!Y§')}, ial = o.{J('§,!Y§')};
    r.ial = ial;
    if (ial === 1 || ial === 2 || ial === 3) {g}.{J('§,!Y§')} = ial;      // tier lookups ("the tier 7 building") depend on the alignment
    var isSet = / Set$/.test(r.n) && r.f >= 0, keepT = null;
    if (isSet) {{ keepT = {g}.{J('§0Q§')}.map(function (t) {{ return t.{J('§4!K§')}; }}); {g}.{J('§0Q§')}.forEach(function (t) {{ t.{J('§4!K§')} = true; }}); }}
    try {{ r.d = o.{J('§@"§')}(); }} catch (e) {{ r.d = 'ERR ' + e; }}
    if (isSet) {g}.{J('§0Q§')}.forEach(function (t, i) {{ t.{J('§4!K§')} = keepT[i]; }});
    try {{ if (o.{J('§8!1§')}) r.d2 = o.{J('§8!1§')}(); }} catch (e) {{}}      // lineage perks: the text shown once owned
    {g}.{J('§,!Y§')} = keepAl;
    {g}.{J('§8!H§')} = keepR; {g}.{J('§-!^§')} = keepFa;
    out.push(r); }}
  var tmap = {{}}; {g}.{J('§0Q§')}.forEach(function (t) {{ tmap[t.id] = t.{J('§1i§')}; }});
  var smap = {{}}; {g}.{J('§0!A§')}.forEach(function (sp) {{ smap[sp.id] = sp.{J('§1i§')}; }});
  return JSON.stringify({{ rows: out, named: named, tmap: tmap, smap: smap }}); }})()"""


def probe(v=None, asc=None):
    ctx = quickjs.Context(); ctx.eval(ENGINE); ctx.eval('__boot()')
    pre = (f"{g}.{J('§,P§')} = {asc};" if asc is not None else '') + (MUT.replace('__V', str(v)) if v is not None else '')
    return json.loads(ctx.eval(PROBE.replace('__MUT', pre)))


# availability by Ascension with every other requirement met (counts, trophies, Reincarnation); one item at a time
BB = f"""(function () {{
  var G = {g}, U = G.{J('§-!4§')}, out = {{}}, big = 1e15;
  [G.{J('§5!V§')}, G.{J('§=y§')}, G.{J('§@w§')}].forEach(function (a) {{ for (var i = 0; i < 200; i++) a[i] = big; }});
  G.{J('§%<§')}.forEach(function (b) {{ b.{J('§!a§')} = 2000000000; }});
  G.{J('§8t§')} = 100000;
  G.{J('§0Q§')}.forEach(function (t) {{ t.{J('§4!K§')} = true; }});
  G.{J('§8!H§')} = 9999;
  var idx = __IDX__;
  for (var n = 0; n < idx.length; n++) {{ var o = U[idx[n]], row = [];
    for (var A = 0; A <= 4; A++) {{ G.{J('§,P§')} = A; G.{J('§-!^§')} = o.{J('§-!^§')} === -1 ? 0 : o.{J('§-!^§')}; G.{J('§,!Y§')} = o.{J('§,!Y§')}; G.{J('§9!m§')} = o.{J('§9!m§')};
      var v; try {{ v = !!o.{J('§-6§')}; }} catch (e) {{ v = null; }} row.push(v); }}
    out[idx[n]] = row; }}
  return JSON.stringify(out); }})()"""


COST = f"""(function () {{
  var G = {g}, U = G.{J('§-!4§')}, out = {{}};
  var idx = __IDX__;
  for (var n = 0; n < idx.length; n++) {{ var o = U[idx[n]], row = {{}};
    [[0, 0, 0], [0, 0, 1], [4, 0, 1]].forEach(function (st) {{
      G.{J('§,P§')} = st[0]; G.{J('§"!0§')} = st[1]; G.{J('§8!H§')} = st[2];
      var c = {{}};
      for (var k = 0; k < 16; k++) {{ var v = 0; try {{ v = o.{J('§75§')}(k); }} catch (e) {{}} if (v) c[k] = v; }}
      row['' + st[0] + st[1] + st[2]] = c; }});
    var coins = [];
    for (var A = 0; A <= 4; A++) {{ G.{J('§,P§')} = A; var v = 0; try {{ v = o.{J('§9!U§')}; }} catch (e) {{}} coins.push(v); }}
    row.coins = coins;
    out[idx[n]] = row; }}
  return JSON.stringify(out); }})()"""


def tier_costs(indexes):
    ctx = quickjs.Context(); ctx.eval(ENGINE); ctx.eval('__boot()')
    return {int(k): v for k, v in json.loads(ctx.eval(COST.replace('__IDX__', json.dumps(indexes)))).items()}


def availability(indexes):
    ctx = quickjs.Context(); ctx.eval(ENGINE); ctx.eval('__boot()')
    return {int(k): v for k, v in json.loads(ctx.eval(BB.replace('__IDX__', json.dumps(indexes)))).items()}


FALLBACK_S = []      # items whose Ascension penalty start came from comparing the game's text at Ascension 1 to 4 (no penalty call in the text)
runs = [probe(), probe(1000), probe(98765)]
asc_runs = [probe(None, a) for a in range(1, 5)]
rows, named, TMAP = runs[0]['rows'], runs[0]['named'], runs[0]['tmap']
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


_SUP = str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻')
BLD = {b['name']: b for b in json.load(open(os.path.join(ROOT, 'data', 'buildings.json'), encoding='utf8'))}


def num_text(n):
    n = float(n)
    if n < 1e6: return f'{int(n)}' if n == int(n) else f'{n:g}'
    e = len(str(int(n))) - 1
    mant = n / 10 ** e
    return f'{mant:g}e{e}'


def plural(name):
    return (BLD.get(name) or {}).get('name_plural') or name


STATIC_ARRAY = re.compile(r'static var §&Z§:Array = \[([^\]]*)\]')


def decode_alt(t, c, ctx, nm):
    """one clause that can stand as a requirement line or condition phrase -> ('req'|'cond', text) or None"""
    mm = re.fullmatch(r'§8G§\.§<P§\((§[^§]*§)\.id\)', t)
    if mm:
        n = nm(mm.group(1))
        return ('req', describe_source({'kind': 'artifact' if n and n[2] else 'trophy', 'name': n[1]}) if n else None)
    mm = re.fullmatch(r'§8G§\.§,#§\(§1i§\)', t)
    if mm: return ('req', describe_source({'kind': 'trophy', 'name': ctx['name']}))
    mm = re.fullmatch(r'§&c§\.§3"&§\(false,false,true\) >= (§\^!\]§|[\d.e+]+)', t)
    if mm:
        thr = ctx['thr'] if mm.group(1) == '§^!]§' else float(mm.group(1))
        return ('text', f'Produce at least {num_text(thr)} mana in this Reincarnation (before bonus multipliers)')
    return None


def alleg_perk(body, ctx, nm):
    """availability of a faction upgrade: the tier upgrade of its faction, or the Legacy upgrade that stands in for it"""
    m = re.fullmatch(r'return §8G§\.§\?!2§\("(\w+)"\) >= (\d)(?: && §&c§\.§`!i§\((§[^§]*§)\.id\))?'
                     r'(?: \|\| §8G§\.§7d§\((§[^§]*§)\.id\))?;', body)
    if not m: return None
    tag, n, need, alt = m.group(1), int(m.group(2)), m.group(3), m.group(4)
    line = f"Upgrade: {TIER_ITEM.get((tag, n), f'tier {n} of ' + tag)}"
    if need:
        nn = nm(need)
        if nn: line += f" and Upgrade: {nn[1]}"
    if alt:
        an = nm(alt)
        if an: line += f", or Upgrade: {an[1]} instead" if not need else f", or Upgrade: {an[1]} instead of both"
    return line


def decode(body, c, ctx=None):
    """-> (sources [{kind, name}], conditions [str], undecoded [str], (asc_lo, asc_hi), extra requirement lines [str])"""
    ctx = ctx or {}
    nm = D.name_of_for(c)
    src, cond, bad, extra = [], [], [], []
    rthr = []
    if ctx.get('cat') == 0:
        if ctx.get('kind') == 'lineage_c':
            return src, ['not having a lineage yet', 'being at Reincarnation 60 or higher (230 at Ascension 4)'], bad, (None, None), extra
        if body in ('', 'return false;') or ctx.get('kind') in ('lineage', 'lineage_perk', 'lineage_c'):
            return src, cond, bad, (None, None), extra
        pl = alleg_perk(body, ctx, nm)
        if pl: return src, cond, bad, (None, None), [pl]
        body = body.replace("\\'", "'")
        mc = re.fullmatch(r'if\(§8G§\.§,P§ == 2 \|\| §8G§\.§,P§ == 4\) \{ return false; \} if\(§8G§\.§,P§ == 3\) \{ return '
                          r'§8G§\.§7d§\((§[^§]*§)\.id\) && §8G§\.§,!Y§ != 0 && §8G§\.§9!m§ != 0 && §8G§\.§-!\^§ == -1; \} '
                          r'return §8G§\.§<P§\((§[^§]*§)\.id\) && §8G§\.§,!Y§ != 0 && §8G§\.§-!\^§ == -1 && §8G§\.§#3§ == -1;', body)
        if mc:
            a3, a0 = nm(mc.group(1)), nm(mc.group(2))
            return src, ['not having a faction or a prestige faction yet', 'having an alignment',
                         'Not available at Ascension 2 or 4'], bad, (None, None), \
                [f"Ascension 3: Upgrade: {a3[1]}" if a3 else 'Ascension 3: ?',
                 f"Other Ascensions: {describe_source({'kind': 'artifact' if a0 and a0[2] else 'trophy', 'name': a0[1]})['kind']}: {a0[1]}" if a0 else '?']
        if body.startswith('var ') and '; return ' in body:       # treaties of prestige / astral factions: drop the local declarations
            body = 'return ' + body.split('; return ', 1)[1]
            body = body.replace('§8G§.§7d§(_loc1_[§8G§.§-!^§])', 'ALLIANCE_BASE').replace('§8G§.§7d§(_loc1_[§8G§.§#3§])', 'ALLIANCE_PRESTIGE')
    mq = re.fullmatch(r'if\((.+)\) \{ return true; \} return false;', body)
    if mq and ctx.get('cat') == 0: body = f'return {mq.group(1)};'
    if ctx.get('cat') == 0 and body.startswith('if(§#!!§.§`Q§ != -1) { return false; } return '):
        body = 'return §#!!§.§`Q§ != -1 && ' + body.split('{ return false; } return ', 1)[1]
    mv = re.fullmatch(r'var _loc1_:Boolean = (.+); return _loc1_ && (.+);', body)
    if mv: body = f'return {mv.group(1)} && {mv.group(2)};'
    m = re.fullmatch(r'return (.+);', body)
    if not m: return src, cond, [body], (None, None), extra
    asc_lo = asc_hi = fac_lo = fac_hi = None
    csrc = '\n'.join(x.body for x in c.methods) if hasattr(c, 'methods') else ''
    for cl_ in split_and(m.group(1)):
        t = cl_
        if t == 'super.§-6§' or re.search(r'§"!U§ <=? \d+', t) or t == '§8G§.§,P§ >= §[2§': continue     # base check / tier-dependent Ascension (see availability)
        # building counts
        mm = re.fullmatch(r'§8G§\.§9=§\((§[^§]*§)\.id\)\.§!a§ >= (.+)', t) or \
             re.fullmatch(r'§8G§\.§%Z§\((§[^§]*§)\.id(?:,true)?\) >= (.+)', t)
        if mm:
            tokb, thr = mm.group(1), mm.group(2)
            bn = ctx.get('bld') if tokb == '§%<§' else (nm(tokb) or [None, None])[1]
            if thr == '§^!]§': val = ctx.get('thr')
            else:
                arr = STATIC_ARRAY.search(open(ctx['file'], encoding='utf8').read()) if ctx.get('file') else None
                val = [float(x) for x in arr.group(1).split(',')][int(ctx['tier']) - 1] if arr else None
            if bn and val is not None:
                cond.append(f'having at least {num_text(val)} {plural(bn)}'); continue
        mm = re.fullmatch(r'§&c§\.§0#§\((\d),true\) >= §\^!\]§', t)
        if mm and mm.group(1) in '12':
            cond.append(f"having at least {num_text(ctx['thr'])} {ALIGN[int(mm.group(1))]} buildings"); continue
        if re.fullmatch(r'§&c§\.§0#§\(0,true\) \+ §&c§\.§0#§\(3,true\) >= §\^!\]§', t):
            cond.append(f"having at least {num_text(ctx['thr'])} Neutral buildings"); continue
        if re.fullmatch(r'§8G§\.§8t§ >= §\^!\]§', t):
            cond.append(f"having unlocked at least {num_text(ctx['thr'])} trophies"); continue
        mm = re.fullmatch(r'Math\.floor\(\(§8G§\.§5!V§\[1\] \+ §8G§\.§=y§\[1\] \+ §8G§\.§@w§\[1\]\) / 60 / 60\) >= (\d+)', t)
        if mm: cond.append(f'having played for at least {mm.group(1)} hours (all-time)'); continue
        mm = re.fullmatch(r'Math\.floor\(\(.*\[1\].*\[3\].*\) / 60 / 60\) >= (\d+)', t)
        if mm: cond.append(f'having spent at least {mm.group(1)} hours (all-time) as neither Good nor Evil'); continue
        mm = re.fullmatch(r'§8G§\.§8!H§ >= (\d+)', t)
        if mm: cond.append(f'being at Reincarnation {mm.group(1)} or higher'); continue
        # trophy-or-threshold alternatives
        mm = re.fullmatch(r'\((.+) \|\| (.+)\)', t)
        if mm:
            parts = [decode_alt(x, c, ctx, nm) for x in (mm.group(1), mm.group(2))]
            if all(parts) and parts[0][1] and parts[1][1]:
                def txt(p):
                    return f"{p[1]['kind']}: {p[1]['name']}" if p[0] == 'req' else p[1]
                if ctx.get('group') == 'Autocast':      # buying the upgrade unlocks the trophy: only the amount counts
                    parts = [p for p in parts if p[0] == 'text']
                if ctx.get('group') == 'ManaProduction':    # the trophy is unlocked by reaching the amount: name just the trophy
                    parts = [p for p in parts if p[0] == 'req']
                extra.append(' or '.join(txt(p) for p in parts)); continue
        if t == '§8G§.§,#§(§1i§)' or re.fullmatch(r'§8G§\.§<P§\((§[^§]*§)\.id\)', t):
            pass
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
        if ctx.get('cat') == 0:
            mm = re.fullmatch(r'\(' + ASC + r' < (\d) \|\| ' + G + r'§8!H§ >= (\d+)(?: && ' + G + r'§<P§\((§[^§]*§)\.id\))?\)', t)
            if mm:
                rthr.append((int(mm.group(1)), int(mm.group(2)), mm.group(3))); continue
            mm = re.fullmatch(ASC + r' >= (\d)', t)
            if mm: asc_lo = int(mm.group(1)); continue
            mm = re.fullmatch(G + r'§8!H§ >= (\d+)', t)
            if mm: rthr.append((None, int(mm.group(1)), None)); continue
            mm = re.fullmatch(r'\(' + ASC + r' < 2 \|\| ' + G + r'§9!m§ == (\d)\)', t)
            if mm: cond.append(f'following the {AXIS[int(mm.group(1))]} path (needed from Ascension 2)'); continue
            if re.fullmatch(G + '§9!m§ == §9!m§', t):
                cond.append(f"following the {AXIS.get(ctx.get('ax'), '?')} path"); continue
            if re.fullmatch(FAC + ' == -1', t): cond.append('not having a faction yet'); continue
            if re.fullmatch(FAC + ' != 11', t): cond.append('not playing as Mercenary'); continue
            if re.fullmatch(PRE + ' != -1', t): cond.append('having a prestige faction'); continue
            if re.fullmatch(AST + ' == -1', t): cond.append('not having an astral faction yet'); continue
            mm = re.fullmatch(r"§&c§\.§`!i§\((§[^§]*§)\.id\)", t)
            if mm:
                n_ = nm(mm.group(1))
                if n_: extra.append(f'Upgrade: {n_[1]}'); continue
            if re.fullmatch(G + r'§5!V§\[41\] > 0', t) or re.fullmatch(G + r'§5!V§\[42\] > 0', t):
                if not any('Dwarven Coin' in x for x in cond):
                    cond.append('having found at least one Dwarven Coin and one Drow Coin in this Era')
                continue
            mm = re.fullmatch(AST + r' == (\d+)', t)
            if mm: cond.append(f'having {FACTION[int(mm.group(1))]} as your astral faction'); continue
            if t == 'ALLIANCE_BASE': extra.append('Upgrade: the Alliance of your base faction'); continue
            if t == 'ALLIANCE_PRESTIGE': extra.append('Upgrade: the Alliance of your prestige faction'); continue
            mm = re.fullmatch(r'\(!_loc3_ && _loc2_ == 0 \|\| ' + G + r'§7d§\((§[^§]*§)\.id\)\)', t)
            if mm:
                n_ = nm(mm.group(1))
                cond.append('not having a Research Facility or any research bought' + (f', unless you have the upgrade {n_[1]}' if n_ else '')); continue
            if t == "§&c§.§'!_§()": continue            # Reincarnation 3 or higher (or one upgrade): the Research Facilities access
            if t == 'super.§-6§' or re.fullmatch(r'!' + G + r'§<P§\((§[^§]*§)\.id\)', t): continue   # base check / quest not done yet
            if t == '§9!%§': continue
            mm = re.fullmatch(FAC + r' == §-!\^§', t)
            if mm: cond.append(role_text(ctx['f'])); continue
            if re.fullmatch(PRE + r' == §-!\^§', t): cond.append(role_text(ctx['f'])); continue
            if re.fullmatch(AST + r' == §-!\^§', t): cond.append(role_text(ctx['f'])); continue
            if re.fullmatch(AL + r' == §,!Y§', t): continue
            mm = re.fullmatch(AL + r' == 0', t)
            if mm: cond.append('not having an alignment yet'); continue
            mm = re.fullmatch(G + r'§9!m§ == 0', t)
            if mm: cond.append('not having an Order, Chaos or Balance path yet'); continue
            if t == AL + ' != 0': continue
            if t == '§#!!§.§`Q§ != -1': cond.append('not having a bloodline yet'); continue
            mm = re.fullmatch(r'\(§\?!6§ \|\| ' + G + r'§#N§\((§[^§]*§)\.id\)\.§\?j§ >= (\d+)\)', t)
            if mm:
                n_ = nm(mm.group(1))
                cond.append(f"having used {n_[1] if n_ else 'the faction spell'} for at least {int(mm.group(2)) // 3600} hour of activity time"); continue
            mm = re.fullmatch(G + r'§#N§\((§[^§]*§)\.id\)\.§-6§', t)
            if mm:
                n_ = nm(mm.group(1))
                cond.append(f"having the spell {n_[1] if n_ else '?'}"); continue
            mm = re.fullmatch(r'\((§&c§\.§9"0§\(\)) \|\| ' + G + r'§#N§\((§[^§]*§)\.id\)\.§-6§\)', t)
            if mm:
                n_ = nm(mm.group(2))
                cond.append(f"having the spell {n_[1] if n_ else '?'} (the Djinn Bloodline, or Identity Shaper together with Challenge Power, also counts)"); continue
            mm = re.fullmatch(r'\(' + G + r'§<P§\((§[^§]*§)\.id\) \|\| ' + G + r'§<P§\((§[^§]*§)\.id\) \|\| ' + G + r'§<P§\((§[^§]*§)\.id\)\)', t)
            if mm:
                ns_ = [nm(mm.group(i)) for i in (1, 2, 3)]
                if all(ns_): extra.append(' or '.join(describe_source({'kind': 'trophy', 'name': n[1]})['kind'] + ': ' + n[1] for n in ns_)); continue
            mm = re.fullmatch(r'\(' + PRE + r' == -1 \|\| ' + G + r'§<P§\((§[^§]*§)\.id\)\)', t)
            if mm:
                n_ = nm(mm.group(1))
                cond.append('not having a prestige faction' + (f', unless you have {describe_source({"kind": "trophy", "name": n_[1]})["kind"]}: {n_[1]}' if n_ else '')); continue
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
        if t == '§8G§.§0!,§("UnlockSpellTier") + 1 > §8G§.§,P§':
            cond.append('having unlocked the Arcane Brilliance trophies up to your Ascension number '
                        '(1 at Ascension 1, 1 and 2 at Ascension 2, and so on; each needs the upgrades of that tier of all spells)'); continue
        if t == '§#!!§.§`Q§ != -1':
            cond.append('using a bloodline'); continue
        if t == '§&c§.§9X§()':
            cond.append('being able to access Research'); continue
        if t.startswith('(§#!!§.§6!r§ != -1 && ') and '§1"0§' in t:
            cond.append('having a Set faction (or Astral Set faction) with the same alignment as your faction'); continue
        mm = re.fullmatch(r'§-"3§\.§\+"8§\((\d+)\)', t)
        if mm:
            cond.append(f'having bought upgrades from at least {mm.group(1)} different factions'); continue
        # Misc upgrades
        mm = re.fullmatch(r'§8G§\.§8!H§ > (\d+)', t)
        if mm: cond.append(f'being at Reincarnation {int(mm.group(1)) + 1} or higher'); continue
        if t == '§8G§.§"!0§ > 0':
            cond.append('having at least 1 Gem'); continue
        if t == '§8G§.§"!0§ >= §^!]§' and isinstance(ctx.get('thr'), (int, float)):
            cond.append(f"having at least {num_text(ctx['thr'])} Gems"); continue
        mm = re.fullmatch(r'§&c§\.§ !;§\(102\) >= (§\^!\]§|\d+)', t)
        if mm:
            val = ctx.get('thr') if mm.group(1) == '§^!]§' else int(mm.group(1))
            if isinstance(val, (int, float)):
                cond.append(f"having collected at least {num_text(val)} {'Ruby' if val == 1 else 'Rubies'} (all-time)"); continue
        if re.fullmatch(r"(?:§8G§\.§'!M§\(\"\w+Challenge\"\) > 0(?: \|\| )?)+", t):
            cond.append('having completed at least one challenge of the Fairy, Elven, Angel, Goblin, Undead or Demon factions'); continue
        if t == '§8G§.§<P§(§`!5§)' and ctx.get('tid') is not None and TMAP.get(str(ctx['tid'])):
            src.append({'kind': 'trophy', 'name': TMAP[str(ctx['tid'])]}); continue
        mm = re.fullmatch(r'§8G§\.§5!V§\[(0|5)\] >= §\^!\]§', t)
        if mm and isinstance(ctx.get('thr'), (int, float)):
            what = 'Coins by clicking' if mm.group(1) == '5' else 'Coins'
            cond.append(f"having gained at least {num_text(ctx['thr'])} {what} in this Era"); continue
        if re.fullmatch(r'§8G§\.§5!V§\[45\] \+ §8G§\.§=y§\[45\] \+ §8G§\.§@w§\[45\] >= §\^!\]§', t) and isinstance(ctx.get('thr'), (int, float)):
            cond.append(f"having spent at least {num_text(ctx['thr'] / 3600)} hours offline (all-time)"); continue
        if t == '§8G§.§,#§(§^!]§)' and isinstance(ctx.get('thr'), str):
            src.append({'kind': 'trophy', 'name': ctx['thr']}); continue
        mm = re.fullmatch(r'\(§8G§\.§-!\^§ == 0 \|\| §8G§\.§-!\^§ == 1 \|\| §8G§\.§-!\^§ == 2 \|\| §8G§\.§-!\^§ == 3 \|\| '
                          r'§8G§\.§-!\^§ == 4 \|\| §8G§\.§-!\^§ == 5 \|\| \(§8G§\.§-!\^§ == 6 \|\| §8G§\.§-!\^§ == 7 \|\| '
                          r'§8G§\.§-!\^§ == 8\) && §8G§\.§7d§\((§[^§]*§)\.id\)\)', t)
        if mm and nm(mm.group(1)):
            cond.append('playing as a Fairy, Elf, Angel, Goblin, Undead or Demon, or as a Titan, Druid or Faceless once '
                        f'{nm(mm.group(1))[1]} is bought'); continue
        if t == '§#3§ == -1' or t == '§8G§.§#3§ == -1':
            cond.append('having no prestige faction'); continue
        bad.append(t)
    if rthr:
        parts = []
        for a, rr, tro_ in rthr:
            nmt = nm(tro_) if tro_ else None
            parts.append((f'Ascension {a}: ' if a is not None else '') + f'Reincarnation {rr}+' + (f' and the trophy {nmt[1]}' if nmt else ''))
        cond.append('having reached ' + ('; '.join(parts)))
    if fac_lo is not None and fac_hi is not None:
        r = faction_range(fac_lo, fac_hi)
        if r: cond.append(r)
        else: bad.append(f'faction {fac_lo}..{fac_hi}')
    return src, cond, bad, (asc_lo, asc_hi), extra


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
    if name in MM.MORE:
        paras[:] = [{'text': t, 'formulas': [], 's': sp} for t, sp in MM.MORE[name]['tip']]
        return
    if name in MM.GEM_UPGRADE_NAMES:
        paras.append({'text': MM.GEM_UPGRADE_NOTE, 'formulas': [], 's': None})
        return
    if name in MM.MANUAL_PARAS:
        paras[:] = [{'text': t, 'formulas': [dict(f, vars=list(f['vars'])) for f in fs], 's': sp}
                    for t, fs, sp in MM.MANUAL_PARAS[name]]
        return
    if name in MM.ASSISTANT_NAMES:
        paras[0]['formulas'] = [dict(MM.ASSISTANT_FORMULA, vars=list(MM.ASSISTANT_FORMULA['vars']))]
    drop = [p for p in paras if p['text'].startswith('Adjusted time spent for')]
    paras[:] = [p for p in paras if p not in drop]
    for p in drop:
        paras[0]['formulas'] += p['formulas']
        if paras[0].get('s') is None: paras[0]['s'] = p.get('s')
    if name == 'Djinn Perk 3':
        t_ = re.sub(r'\s*\(Add: .*\)\s*$', '', paras[0]['text'])      # a live readout
        paras[0]['text'] = re.sub(r'by (\d+)% for every', r'by +\1 and \1% for every', t_)      # it adds +N and N% together
    if name == 'Devil Tyrant':      # its text holds two paragraphs in one template, so the penalty call (from Ascension 1, none at 4) was not matched
        paras[0]['s'] = 1; paras[0]['np'] = True
    # marks found by the Ascension penalty audit (production code): name -> (first Ascension or None to keep, no penalty at Ascension 4)
    PEN_AUDIT = {'Scarab of Fortune': (1, False), 'Druidic Vocabulary': (1, True), 'Mabinogion': (1, True), 'Building Jungle': (1, True),
        'Superior Consciousness': (3, True), 'Abyssal Furnace': (3, True), 'Grove Farming': (3, True), 'Lousy Architecture': (3, True),
        'Green Fingers Discount': (1, False), 'Wings of Liberty': (None, True),
        'Unholy Rituals': (None, True), 'Hive Mind': (None, True), 'Hobgoblin Gladiators': (None, True), 'Oversized Legends': (None, True), 'Elven Heritage': (None, True), 'Black Market': (None, True),
        'Heroic Proclamation': (1, None), 'Villainous Proclamation': (1, None),
        'Legendary Lands': (2, None), 'Legendary Participation': (2, None), 'Legendary Attendance': (2, None), 'Legendary Party': (3, None)}
    if name == 'Sylvan Treasure Frills':      # adds to the base clicking reward, which the penalty does not touch
        for p_ in paras: p_['s'] = None; p_['np'] = None
    if name == 'Elven Luck': paras[0]['np'] = True      # its start Ascension returns 5 (no penalty) at Ascension 4
    if name in PEN_AUDIT:
        st_, np_ = PEN_AUDIT[name]
        for p_ in paras:
            if p_.get('s') or st_:
                if st_: p_['s'] = st_
                if np_ is not None: p_['np'] = np_
                break
    if name in ('Mercenary First Contract', 'Mercenary Fourth Contract', 'Archon Bloodline'):
        for p_ in paras: p_['s'] = None
    if name == 'Round Table' and paras: paras[0]['s'] = None
    if name.startswith('Know Your Enemy, Part'):      # only Mercenaries can use these, so their current faction is Mercenary
        for f_ in paras[0]['formulas']:
            for v_ in f_['vars']:
                v_['text'] = v_['text'].replace('as your current faction', 'as Mercenary')
    if name == 'Elven Perk 1':      # the Ascension penalty the probe saw is the one on the Elven Luck text below, not on this value
        paras[0]['s'] = None
    if name == 'Djinn Perk 6':
        paras[0]['text'] = paras[0]['text'].replace('its active spells', 'its activated spells')
    if name == 'Dragon Perk 4':
        paras[0]['text'] = 'Red and Black Breath count their stats in this Reincarnation instead of this Era.'
    if name == 'Drow Perk 4' and len(paras) == 1:      # one sentence per value
        t0, sp = paras[0]['text'], paras[0].get('s')
        a_, b_ = t0.split('. While ', 1)
        paras[:] = [{'text': a_ + '.', 'formulas': [], 's': None}, {'text': 'While ' + b_, 'formulas': [], 's': sp}]
    if name == 'Suggestion Master':
        paras[0]['formulas'] = []     # the code only has the constant 4*10 + 3 + 0*0.1 + 14*0.01
        paras[0]['text'] = 'Increase the production of all buildings based on mysterious events. (43.14%)'
    if name == 'Fairy Heritage':      # from Ascension 1 the game words it this way (the number is in the formula)
        paras[0]['text'] = 'Increase the production of all buildings based on Farms, Inns and Blacksmiths owned.'
    if name == 'Demonic Heritage':
        paras[0]['text'] = 'Increase the production of all buildings based on Halls of Legends owned.'
    if name == 'Arcane Brilliance':
        paras[0]['formulas'] = [_m(r'v = 2 \cdot S \cdot \max\left(0,\, C + 1 - A\right)',
            ('S', 'Total tier of your active spells (each active spell counts its tier)'),
            ('C', 'The number of Arcane Brilliance trophies you have unlocked'), ('A', 'Your Ascension number'))]
    if name == 'Ancestral Hourglass':
        paras[0]['formulas'] = [_m(r'v = \frac{0.002 \cdot R}{A}',
            ('v', 'Amount taken off the Lineage cost exponent growth (per 25 levels of a Lineage)'),
            ('R', 'Reincarnations made'), ('A', 'Your Ascension number (this upgrade needs Ascension 2 or more)'))]
    # building-tier multipliers that sit in the production code, not in the description (T = building tier, counted from 1; checked in game)
    TIER = ('T', "The building's tier (1 for the first building in the list)")
    if name == 'Mathematician':
        paras[0]['formulas'] = [_m(r'v = 10 \cdot \left(12 - T\right)', TIER)]
        paras[0]['s'] = 1
    if name == 'Wall Fragment':
        paras[0]['formulas'] = [_m(r'v = 500 \cdot \left(2 \cdot \left(11 - T\right)\right)^{2.5}', TIER)]
        paras[0]['s'] = 2
    if name == 'Wall Chunk':
        paras[0]['formulas'] = [_m(r'v = 30000 \cdot \left(11 - T\right)^{3.5}', TIER)]
        paras[0]['s'] = 3
    if name == 'Ancient Heirloom':
        paras[0]['formulas'] = [_m(r'c_{\text{new}} = c^{0.97}',
            ('c', 'The Lineage upgrade cost without this upgrade'))]
    if name == 'Art of the Crow':
        spec = {
            'Good:': (r'v = 0.1 \cdot D^{0.9}', ('D', 'Your excavation depth')),
            'Neutral:': (r'v = 1.5 \cdot N^{0.6}', ('N', 'Royal Exchanges purchased in this Era')),
            'Evil:': (r'v = \left(\ln\left(1 + W\right)\right)^{2}', ('W', 'Mana produced in this Reincarnation')),
        }
        for p in paras:
            for k, (lt, var) in spec.items():
                if p['text'].startswith(k): p['formulas'] = [_m(lt, var)]
    for p in paras:
        p['text'] = re.sub(r'(?<=\d)\.00(?!\d)', '', READOUT.sub('', p['text'])).strip()


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


# the Misc upgrades covered so far (the rest of the category is seasonal events, research facilities, unlocks ...)
MISC_GROUPS = {'GemUpgrade', 'ReincarnationPowerUpgrade', 'RubyUpgrade', 'ClickingBase', 'ClickingProduction',
               'ClickingTotalProduction', 'OfflineUpgrade', 'AssistantUpgrade'}
MISC_NAMES = {'Gem Power', 'Challenge Power'}
SKIP_NAMES = set()
SPELL_TIER_CLASS = '§%p§'
# Allegiances: the tier upgrades (Trade Treaty ... Union) and the twelve faction upgrades of every faction; bloodlines, lineages,
# heritages, sets, legacies, remnants, quests and the unique building upgrades belong to later pages
ALLEG_TAGS = {f'{n}Faction' for n in ('Angel', 'Demon', 'Drow', 'Druid', 'Dwarven', 'Elven', 'Faceless', 'Fairy', 'Goblin',
                                     'Mercenary', 'Titan', 'Undead', 'Dragon', 'Archon', 'Djinn', 'Makers')}
TIER_NO = [('Trade Treaty', 1), ('First Contract', 1), ('Friendship Pact', 2), ('Second Contract', 2), ('Alliance', 3),
           ('Third Contract', 3), ('Union', 4), ('Fourth Contract', 4)]
AXIS = {4: 'Order', 5: 'Chaos', 6: 'Balance'}
MERC_PERKS = {'Trade Lords', 'Holy Crusaders', 'Heresiarchs'}      # the Mercenary faction upgrades (one per alignment)
ALEG_NAME = {0: 'Fairy', 1: 'Elf', 2: 'Angel', 3: 'Goblin', 4: 'Undead', 5: 'Demon', 6: 'Titan', 7: 'Druid', 8: 'Faceless',
             9: 'Dwarf', 10: 'Drow', 11: 'Mercenary', 12: 'Dragon', 13: 'Archon', 14: 'Djinn', 15: 'Makers'}


def role_text(f):
    if f in (9, 10, 12): return f'having {ALEG_NAME[f]} as your prestige faction'
    if f in (13, 14, 15): return f'having {ALEG_NAME[f]} as your astral faction'
    return f'playing as {ALEG_NAME.get(f, f)}'


def tier_of(name):
    for k, n in TIER_NO:
        if k in name: return n
    return None


# the unique building upgrades are the ones whose text starts "Upgrade X to Y, boosting their production"
UNIQUE_NAMES = {r_['n'] for r_ in rows if r_['cat'] == 0 and str(r_.get('d', '')).startswith('Upgrade ') and 'boosting' in str(r_.get('d', ''))}
QUEST_FACTION = {"Sturdy Bearded Man's Quest": 9, "Cloaked Shady Figure's Quest": 10}      # entry quests of the prestige factions
ASTRAL_QUESTS = {'Archon Quest', 'Djinn Quest', 'Makers Quest'}


def alleg_kind(r):
    """which family of Allegiances upgrades a category 0 row belongs to (None: not covered yet)"""
    n = r['n']
    if r.get('idx'): return 'perk'
    if r.get('grp') in ALLEG_TAGS and tier_of(n) is not None: return 'tier'
    if n in MERC_PERKS: return 'perk'
    if n.startswith('Proof of ') and r['f'] == -1: return 'proof'
    if n in QUEST_FACTION: return 'quest'
    if n == 'Mercenary Badge': return 'heritage'      # the Mercenary's Heritage
    if r['f'] != -1:
        if n.endswith('Heritage'): return 'heritage'
        if n.endswith(' Bloodline'): return 'bloodline'
        if r.get('tg') == 'SpellFactionUpgrade': return 'spell'
        if n in ASTRAL_QUESTS: return 'quest'
        if n in UNIQUE_NAMES or (n.endswith(' Quest') and (n[:-6] in UNIQUE_NAMES or n == 'Mercenary Encampment Quest')): return 'unique'
    if n == 'Bloodline': return 'bloodline_c'
    if n == 'Artifact Set': return 'set_c'
    if r['f'] != -1 and n.endswith(' Set') and r.get('tg') != 'SpellFactionUpgrade': return 'set'
    if n == 'Lineage': return 'lineage_c'
    if r['f'] != -1 and n.endswith(' Lineage'): return 'lineage'
    if r['f'] != -1 and re.fullmatch(r'.+ Perk \d+', n): return 'lineage_perk'
    return None


def wanted(r):
    if r['cat'] == 0:
        return alleg_kind(r) is not None
    if r['cat'] == 1: return r.get('grp') in MISC_GROUPS or r['n'] in MISC_NAMES
    return True
by_cat = {name: [] for name in CATS.values()}
problems = []
todo = [(idx, r) for idx, r in enumerate(rows) if r['n'] not in SKIP_NAMES and r['q'].split('.')[-1] != SPELL_TIER_CLASS
        and wanted(r)]
avail = availability([r['i'] for _, r in todo if r['cat'] not in (0, 4)])
TIER_ITEM = {}      # (faction tag, tier) -> name
for _, r in todo:
    if r['cat'] == 0 and r.get('grp') in ALLEG_TAGS and not r.get('idx'): TIER_ITEM[(r['grp'], tier_of(r['n']))] = r['n']
tcost = tier_costs([r['i'] for _, r in todo if r['cat'] == 0])
for idx, r in todo:
    tok = r['q'].split('.')[-1]
    c = next(k for k in cl.values() if k.name == tok)
    templates = D.formulas_for(c, r['n'])
    texts = [rr['rows'][idx].get('d2', rr['rows'][idx]['d']) for rr in runs]
    lines0, lines1, lines2 = clean_lines(*texts)
    paras = []
    for k, ln in enumerate(lines0):
        if not ln.strip(): continue
        p = D.para(c, templates, ln, r['n'])
        rw_, pw_ = ln.split(), p['text'].split()       # a building name must not be replaced by the value symbol
        if len(rw_) >= len(pw_) and 'v' in pw_:
            p['text'] = ' '.join(a_ if (b_ == 'v' and re.fullmatch(r"[A-Za-z']+", a_)) else b_ for a_, b_ in zip(rw_[:len(pw_)], pw_))
        if p['text'] == D.pow10_text(ln.strip()) and not p['formulas']:
            # no template matched: drop a trailing live readout "(x%)" if the numbers change between states
            if not (ln == lines1[k] == lines2[k]):
                p['text'] = pow10_text(re.sub(r'\s*\((?:[^()]*)\)\s*$', '', ln).strip())
        paras.append(p)
    # Ascension penalty start: the first Ascension at which the game's own text for the value changes
    if r['cat'] != 4 and paras and paras[0].get('s') is None:
        base = texts[0]
        for a, ar in enumerate(asc_runs, 1):
            if ar['rows'][idx].get('d2', ar['rows'][idx]['d']) != base:
                paras[0]['s'] = a; FALLBACK_S.append(r['n']); break
    fix_raw(r['n'], c, paras)
    fix_text(r['n'], paras)
    av = next((m for m in c.methods if m.name == '§-6§'), None)
    body = re.sub(r'\s+', ' ', av.body.strip()) if av else ''
    ctx = {'name': r['n'], 'thr': r.get('thr') if isinstance(r.get('thr'), (int, float, str)) else None, 'tid': r.get('tid'),
           'tier': r.get('tier'), 'bld': r.get('bld'), 'group': r.get('grp'), 'file': getattr(c, 'path', None),
           'cat': r['cat'], 'ax': r.get('ax'), 'f': r['f'], 'kind': alleg_kind(r) if r['cat'] == 0 else None}
    src, cond, bad, (alo, ahi), extra = decode(body, c, ctx)
    if r['cat'] not in (0, 4):
        row = avail.get(r['i'])
        if row and any(row):
            first = row.index(True)
            alo = first if first > 0 else None
            tail = [a for a in range(first, 5) if not row[a]]
            ahi = tail[0] if tail else None
        # (a row that is never true needs a prerequisite the probe does not model: keep the decoded bounds)
    if r['n'] == 'Reverse Autocasting':       # stated in the text of its trophy ("Can only be unlocked starting from ...")
        cond.append('starting from Ascension 1, at Reincarnation 40+')
    if r['f'] != -1 and r['cat'] not in (0, 4):
        cond.insert(0, f"playing as {FACTION.get(r['f'], r['f'])}")
    if alleg_kind(r) in ('set', 'set_c'): bad = []
    if bad: problems.append((r['n'], bad))
    item = {
        'name': r['n'], 'icon': r['icon'] if r['icon'] in sprites else None, 'order': r['i'], 'id': r['id'],
        'description': paras, 'sources': [describe_source(s) for s in src], 'requirements': extra,
        'conditions': cond, 'undecoded': bad, 'asc_min': alo, 'asc_max': ahi, 'group': r.get('grp') or None,
        'tier': r.get('tier'), 'building': r.get('bld'),
    }
    if r['cat'] == 0 and alleg_kind(r) == 'set':
        _init = next((m_.body for m_ in c.methods if m_.name == '§[!C§'), '')
        _bonus = next((m_.body for m_ in c.methods if m_.name == '§8"M§'), '')

        def _art(short_):
            q_ = c.imports.get(short_)
            nm_ = named.get(q_) if q_ else None
            return nm_[1] if nm_ else f'?{short_}'
        item['set_artifacts'] = [_art(x_) for _, x_ in re.findall(r'(§[^§]+§) = (§[^§]+§)\.id;', _init)]
        _b2 = re.findall(r'§<P§\((§[^§]+§)\.id\)', _bonus)
        item['set_artifact4'] = _art(_b2[0]) if _b2 else None
        item['conditions'] = []
        item['requirements'] = ['Artifact: ' + a_ for a_ in item['set_artifacts']]
        if item['set_artifact4']: item['requirements'].append(f"Artifact: {item['set_artifact4']} (for Set Bonus 2)")
        item['asc_min'] = 2
        for p_ in item['description']: p_['formulas'] = []      # the values are not decoded reliably yet (INFERENCES.md)
        if r['n'] == 'Mercenary Set':      # a constant: the game writes 25, the converter would show v
            for p_ in item['description']: p_['text'] = p_['text'].replace('v%', '25%')
    if r['cat'] == 0 and alleg_kind(r) == 'set_c':
        item['conditions'] = []; item['undecoded'] = []
        item['requirements'] = ['Reincarnation 100 or higher (Reincarnation 225 at Ascension 4)', 'Complete one faction Artifact Set (all three of its artifacts)']
        item['asc_min'] = 2
    if r['cat'] == 0:
        if alleg_kind(r) == 'exchange':          # a live readout ("Current overall bonus: ...")
            item['description'] = [p_ for p_ in item['description'] if not p_['text'].startswith('Current overall bonus')]
        # manual formulas replace what the converter could not read (the paragraph's own formulas are dropped first)
        _done = set()
        for pi, f_ in AM.FORMULAS.get(r['n'], []):
            ps = item['description']
            if pi < len(ps):
                if pi not in _done:
                    ps[pi]['formulas'] = []; _done.add(pi)
                ps[pi]['formulas'].append(dict(f_, vars=[dict(v) for v in f_['vars']]))
        for tx_, f_ in AMF.EXTRA_PARAS.get(r['n'], []):
            item['description'].append({'text': tx_, 'formulas': [dict(f_, vars=[dict(v) for v in f_['vars']])] if f_ else [], 's': None})
        # a tier lookup names the building of the PLAYER's alignment (the upgrade can be used through a Legacy or as a
        # Mercenary), so the text names the tier and lists the three possibilities instead of the faction's own building
        _src = '\n'.join(m_.body for m_ in c.methods if m_.name in ('§@"§', '§8!1§', '§>!d§', '§1!6§'))
        _al = r.get('ial') or AM.FACTION_ALIGN.get(r['f'])
        for t_ in dict.fromkeys(int(x_) for x_ in re.findall(r'§8G§\.§-e§\((\d+)\)\.id', _src)):
            if t_ < 4 or not _al: continue
            nm_ = plural(AM.TIER_BUILDING[_al][t_ - 1])
            names3 = [plural(AM.TIER_BUILDING[a_][t_ - 1]) for a_ in (1, 2, 3)]
            if len(set(names3)) == 1: continue          # the same building for every alignment (Halls of Legends)
            alts = ', '.join(names3[:-1]) + ' or ' + names3[-1]
            ph_ = f'the tier {t_} building of your alignment ({alts})'
            for p_ in item['description']:
                if nm_ in p_['text']:
                    p_['text'] = p_['text'].replace(nm_, ph_, 1); break
        if r['n'] in AMF.BUILDING_TEXT:
            for p_ in item['description']: p_['text'] = p_['text'].replace(AMF.BUILDING_TEXT[r['n']][0], AMF.BUILDING_TEXT[r['n']][1], 1)
        item['faction'] = QUEST_FACTION.get(r['n'], r['f'])
        item['akind'] = alleg_kind(r)
        if item['akind'] == 'lineage':
            keep, perks = [], []
            for p_ in item['description']:
                m_ = re.fullmatch(r'Perk (\d+) unlock: Reincarnation ([\d,.KMBT]+), Lineage Level (\d+)(?:, (.*))?', p_['text'].strip(), re.S)
                if m_: perks.append({'n': int(m_.group(1)), 'reinc': m_.group(2), 'level': int(m_.group(3)),
                                     'challenge': (m_.group(4) or '').strip() or None})
                else: keep.append(p_)
            item['description'], item['perks'] = keep, perks
        item['perk'] = r.get('idx') or None
        item['tier_no'] = None if r.get('idx') else tier_of(r['n'])
        tc = tcost.get(r['i'], {})
        lo, hi, free = tc.get('001', {}), tc.get('401', {}), tc.get('000', {})
        item['cost'] = {'coins': tc.get('coins'),
                        'fc': {ALEG_NAME[int(k)]: v for k, v in lo.items()},
                        'fc_a4': {ALEG_NAME[int(k)]: v for k, v in hi.items()},
                        'free_start': bool(lo) and not free}
    if r['n'] in MM.MORE:       # a bigger popup opened by clicking: every bonus with its formula
        mo = MM.MORE[r['n']]
        item['more'] = [{'text': t, 'formulas': [dict(f, vars=list(f['vars'])) for f in fs], 's': sp}
                        for t, fs, sp in mo['more']]
        item['more_note'] = mo.get('note')
    by_cat[CATS[r['cat']]].append(item)

# the Dragon faction (a prestige faction) becomes available at Ascension 1, and so does everything that needs it
for items_ in by_cat.values():
    for u in items_:
        if u.get('faction') == 12 or u.get('spell') == "Dragon's Breath" or u['name'] == 'Dragon Tamer' \
                or any('Dragon as your prestige faction' in c_ for c_ in u['conditions']):
            if (u['asc_min'] or 0) < 1: u['asc_min'] = 1

# the astral factions (Archon, Djinn, Makers) exist from Ascension 2, and so does everything that belongs to them
for u in by_cat['allegiances']:
    if u['faction'] in (13, 14, 15) and (u['asc_min'] or 0) < 2: u['asc_min'] = 2

# a unique building upgrade is bought after its quest is done, so it starts at the quest's Ascension and Reincarnation
_q = {u['name']: u for u in by_cat['allegiances'] if u['akind'] == 'unique' and u['name'].endswith(' Quest')}
for u in by_cat['allegiances']:
    q_ = _q.get(u['name'] + ' Quest') or (_q.get('Mercenary Encampment Quest') if u['faction'] == 11 and u['akind'] == 'unique' else None)
    if u['akind'] != 'unique' or u['name'].endswith(' Quest') or not q_: continue
    if (u['asc_min'] or 0) < (q_['asc_min'] or 0): u['asc_min'] = q_['asc_min']
    if not u['sources']: u['requirements'].insert(0, f"Complete the {q_['name']}")
    for c_ in q_['conditions']:
        if c_.startswith('being at Reincarnation') and c_ not in u['conditions']: u['conditions'].append(c_)

# the hidden "Research <Faction> Trophy" is what finishing a faction's first unique building quest grants: name the quest
_RF = {'Fairy': 0, 'Elven': 1, 'Angel': 2, 'Goblin': 3, 'Undead': 4, 'Demon': 5, 'Titan': 6, 'Druid': 7, 'Faceless': 8,
       'Dwarven': 9, 'Drow': 10, 'Mercenary': 11, 'Dragon': 12}
_RQ = {}      # faction index -> its first unique building quest: the one whose upgrade lists that Research trophy
for u in by_cat['allegiances']:
    if u['akind'] == 'unique' and not u['name'].endswith(' Quest'):
        for s_ in u['sources']:
            m_ = re.fullmatch(r'Research (\w+) Trophy', s_['name'])
            if m_ and m_.group(1) in _RF:
                _RQ[_RF[m_.group(1)]] = 'Mercenary Encampment Quest' if u['faction'] == 11 else u['name'] + ' Quest'
for u in by_cat['allegiances']:
    keep = []
    for s_ in u['sources']:
        m_ = re.fullmatch(r'Research (\w+) Trophy', s_['name'])
        if m_ and m_.group(1) in _RF and _RQ.get(_RF[m_.group(1)]):
            u['requirements'].insert(0, f"Complete the {_RQ[_RF[m_.group(1)]]}")
        else: keep.append(s_)
    u['sources'] = keep
    u['conditions'] = [re.sub(r'Miscellaneous trophy: Research (\w+) Trophy',
                              lambda m: 'completed ' + (_RQ.get(_RF.get(m.group(1))) or m.group(0)), c_) for c_ in u['conditions']]

# the hidden "Archeology <X> Trophy" is not on the Trophies page: it is only the flag an archaeology upgrade sets when bought
_ARCH = {'Titan': 'Fragment of a Titan Statue', 'Druid': 'Druidic Runestone', 'Faceless': 'Octopus Shaped Spine',
         'Dwarf': "Sturdy Bearded Man's Quest", 'Drow': "Cloaked Shady Figure's Quest", 'Underworld': 'Passage to the Underworld'}
_ARCH_RE = re.compile(r'(?:Allegiances|Miscellaneous) trophy: Archeology (\w+) Trophy')
for u in [u_ for items_ in by_cat.values() for u_ in items_]:
    keep = []
    for s_ in u['sources']:
        m_ = re.fullmatch(r'Archeology (\w+) Trophy', s_['name'])
        if m_ and m_.group(1) in _ARCH:
            u['requirements'].insert(0, ('Complete the ' if _ARCH[m_.group(1)].endswith('Quest') else 'Upgrade: ') + _ARCH[m_.group(1)])
        else: keep.append(s_)
    u['sources'] = keep
    for k_ in ('requirements', 'conditions'):
        out_ = []
        for c_ in u[k_]:
            ms_ = _ARCH_RE.findall(c_)
            if ms_ and all(m in _ARCH for m in ms_):
                names_ = [_ARCH[m] for m in ms_]
                c_ = (('Complete the ' if names_[0].endswith('Quest') else 'Upgrade: ') + names_[0]) if len(names_) == 1 else 'Any one of the upgrades: ' + ', '.join(names_)
            out_.append(c_)
        u[k_] = out_

# the chain of a faction's tier upgrades: Pact needs the Treaty, Alliance the Pact, Union the Alliance and the faction's
# second unique building (that is an availability condition: it is checked every time, together with the Ascension / faction).
_TIERS = {}
for u_ in by_cat['allegiances']:
    if u_['akind'] == 'tier' and u_['faction'] in FACTION and u_['faction'] != 11:
        for suf_ in ('Trade Treaty', 'Friendship Pact', 'Alliance', 'Union'):
            if u_['name'].endswith(suf_): _TIERS[(u_['faction'], suf_)] = u_['name']
_PREV = {'Friendship Pact': 'Trade Treaty', 'Alliance': 'Friendship Pact', 'Union': 'Alliance'}
for u_ in by_cat['allegiances']:
    if u_['akind'] != 'tier' or u_['faction'] not in FACTION or u_['faction'] == 11: continue
    for suf_, prev_ in _PREV.items():
        if u_['name'].endswith(suf_) and (u_['faction'], prev_) in _TIERS:
            # (the previous tier upgrade is not listed: it is implied by the stack)
            if suf_ == 'Union':
                bld_ = [r_ for r_ in u_['requirements'] if r_.startswith('Upgrade: ')]
                u_['requirements'] = [r_ for r_ in u_['requirements'] if r_ not in bld_]
                u_['conditions'] += ['having the upgrade ' + r_[len('Upgrade: '):] for r_ in bld_]
                rs_ = [c_ for c_ in u_['conditions'] if re.match(r'being at Reincarnation \d+ or higher$', c_)]
                u_['conditions'] = [c_ for c_ in u_['conditions'] if c_ not in rs_]
                u_['requirements'] += [c_.replace('being at ', '').replace(' or higher', ' or higher') for c_ in rs_]
                if rs_ and (u_['asc_min'] or 0) < 2: u_['asc_min'] = 2      # Reincarnation 115 / 130 are Ascension 2 territory

# the faction upgrades (bronze, silver, gold, diamond) are shown once the tier upgrade is owned (or its Legacy): availability
for u_ in by_cat['allegiances']:
    if u_['akind'] == 'perk':
        mv_ = [r_ for r_ in u_['requirements'] if r_.startswith('Upgrade: ')]
        u_['requirements'] = [r_ for r_ in u_['requirements'] if r_ not in mv_]
        u_['conditions'] = ['having ' + r_.replace('Upgrade: ', '') for r_ in mv_] + u_['conditions']
    u_['conditions'] = [c_ for c_ in u_['conditions'] if c_ != 'having found at least one Dwarven Coin and one Drow Coin in this Era']
    u_['conditions'] = [c_ for c_ in u_['conditions'] if c_ not in ('not having a bloodline yet', 'not having a lineage yet')]
    if u_['akind'] in ('bloodline_c', 'lineage_c'):      # the Reincarnation that makes them appear is an unlock
        rc_ = [c_ for c_ in u_['conditions'] if c_.startswith('being at Reincarnation')]
        u_['conditions'] = [c_ for c_ in u_['conditions'] if c_ not in rc_]
        u_['requirements'] += [c_.replace('being at ', '').replace(' (230 at', ' (Reincarnation 230 at') for c_ in rc_]
        if u_['akind'] == 'lineage_c' and (u_['asc_min'] or 0) < 1: u_['asc_min'] = 1      # Reincarnation 60 is Ascension 1 territory

# conditions the reader already knows from the page: the faction picked in the selector, the spell's own parenthesis,
# the warning that the description gives, the treaty's note
for u in [u_ for items_ in by_cat.values() for u_ in items_]:
    f_ = u.get('faction', -1)
    desc_ = ' '.join(p_['text'] for p_ in u['description']).lower()
    out_ = []
    for c_ in u['conditions']:
        if f_ in FACTION and c_ in ('playing as ' + FACTION[f_], f'having {FACTION[f_]} as your prestige faction',
                                    f'having {FACTION[f_]} as your astral faction'): continue
        if f_ in FACTION and c_ == 'not having a faction yet': continue
        if c_.startswith('not having a prestige faction, unless') and 'prestige faction' in desc_: continue
        c_ = re.sub(r'^(having the spell [^()]+) \(.*\)$', r'\1', c_)
        c_ = re.sub(r'^following the (\w+) path \(needed from Ascension 2\)$',
                    r'following the path of \1 (Ascension 2 onwards)', c_)
        c_ = re.sub(r'^following the (\w+) path$', r'following the path of \1', c_)
        out_.append(c_)
    u['conditions'] = out_
    # one-time things (activity time, completed challenges, upgrades bought) are unlocks, not availability: they go to the requirements
    keep_ = []
    for c_ in u['conditions']:
        m_ = re.fullmatch(r'having used (.+) for at least (.+) of activity time', c_)
        if m_:
            u['requirements'].append(f'Use {m_.group(1)} for {m_.group(2)} of activity time in a single Era')
            continue
        m_ = re.fullmatch(r'having completed (.+)', c_)
        if m_ and 'this Era' not in c_:
            u['requirements'].append('Complete ' + m_.group(1)); continue
        keep_.append(c_)
    u['conditions'] = keep_
    # prestige and astral Trade Treaties: only the Reincarnation needed at each Ascension is worth listing
    if u.get('akind') == 'tier' and u['name'].endswith('Trade Treaty') and f_ in (9, 10, 12, 13, 14, 15):
        steps_ = []
        for c_ in u['conditions']:
            m_ = re.match(r'being at Reincarnation (\d+) or higher$', c_)
            if m_ and f_ >= 13: steps_.append((2, f'Reincarnation {m_.group(1)}'))
            if c_.startswith('having reached Ascension'):
                for part_ in c_.split('; '):
                    m_ = re.match(r'(?:having reached )?Ascension (\d): Reincarnation (\d+)\+( and the trophy .*)?$', part_)
                    if m_:
                        extra_ = m_.group(3)[len(' and the trophy '):] if m_.group(3) else ''
                        steps_.append((int(m_.group(1)), f'Reincarnation {m_.group(2)}' + (f' and the artifact {extra_}' if extra_ else '')))
        if steps_:
            al_ = [r_ for r_ in u['requirements'] if r_.startswith('Upgrade: the Alliance of your')]
            u['requirements'] = [r_ for r_ in u['requirements'] if r_ not in al_]
            u['conditions'] = [('having the Alliance of your ' + r_.split('your ')[1]) for r_ in al_] + \
                              ['starting from ' + ' / '.join(f'{t_} (Ascension {a_})' for a_, t_ in sorted(steps_))]
    # the hidden "<Astral> Quest Trophy" is only set by buying that faction's Quest upgrade
    ks_ = []
    for s_ in u['sources']:
        m_ = re.fullmatch(r'(Archon|Djinn|Makers) Quest Trophy', s_['name'])
        if m_: u['requirements'].insert(0, f'Complete the {m_.group(1)} Quest')
        else: ks_.append(s_)
    u['sources'] = ks_
    u['description'] = [p_ for p_ in u['description'] if not p_['text'].startswith('Note: purchasing this upgrade will prevent you')]

# a Reincarnation requirement that the Ascension's range of Reincarnations cannot reach rules that Ascension out
for u in [u_ for items_ in by_cat.values() for u_ in items_]:
    ns = [int(m.group(1)) for c_ in u['conditions'] for m in [re.search(r'Reincarnation (\d+)', c_)] if m and c_.startswith('being at')]
    if ns:
        need = 1 if max(ns) < 100 else 2 if max(ns) < 160 else 3 if max(ns) < 220 else 4
        if max(ns) >= 40 and (u['asc_min'] or 0) < need: u['asc_min'] = need

# the fourth-tier faction upgrades (10 to 12) need the Union, so they cannot be bought earlier than it
_union = {u['faction']: u for u in by_cat['allegiances'] if u['tier_no'] == 4}
for u in by_cat['allegiances']:
    un = _union.get(u['faction'])
    if u['perk'] and u['perk'] >= 10 and un and un['asc_min'] and (u['asc_min'] or 0) < un['asc_min']:
        u['asc_min'] = un['asc_min']

# ---- spell tiers ("<Spell> 2" ... "<Spell> 5"): the game builds the whole text itself; the numbers depend on the Ascension
SMAP = runs[0]['smap']
TIER_SRC = open(os.path.join(ROOT, 'out', 'script', 'scripts', '§3%3F§', '§%p§.as'), encoding='utf8').read()
_cls_t = next(k for k in cl.values() if k.name == SPELL_TIER_CLASS)
_nm_t = D.name_of_for(_cls_t)
TIER_PREREQ = {}        # spell id token -> (Reincarnation, upgrade name)
for mm_ in re.finditer(r'\(§8G§\.§8!H§ < (\d+) \|\| !§8G§\.§7d§\((§[^§]*§)\.id\)\) && \((.*?)\)\)', TIER_SRC.replace("\\'", "'")):
    up = _nm_t(mm_.group(2))
    for tk in re.findall(r'§`g§ == (§[^§]*§)\.id', mm_.group(3)):
        sp = _nm_t(tk)
        if sp and up: TIER_PREREQ[sp[1]] = (int(mm_.group(1)), up[1])
OFFLINE_F = _m(r'v = \left(M_{\max}^{\frac{2}{\max\left(3,\,A\right)}} + \left(30 \cdot R\right)^{\frac{2}{\max\left(3,\,A\right)}}\right)^{0.4}',
               (r'M_{\max}', 'Your Maximum Mana'), ('R', 'Your mana regeneration per second'), ('A', 'Your Ascension number'))
for idx, r in enumerate(rows):
    if r['q'].split('.')[-1] != SPELL_TIER_CLASS: continue
    spell = SMAP.get(str(r['sg']))
    texts_a = {a: [l.strip() for l in ar['rows'][idx]['d'].split('\n') if l.strip()] for a, ar in enumerate(asc_runs, 1)}
    ra = {}
    for a, ls in texts_a.items():
        t0 = next((l for l in ls if l.startswith('To unlock')), None)
        if t0: ra[a] = pow10_text(t0)
    paras = []
    for l in texts_a[4]:
        if l.startswith('To unlock'): continue
        if l.startswith('Also increase Offline production'):
            paras.append({'text': 'Also increase Offline production based on mana statistics.',
                          'formulas': [dict(OFFLINE_F, vars=list(OFFLINE_F['vars']))], 's': r['sr'] + 1})
        else:
            paras.append({'text': pow10_text(l), 'formulas': [], 's': None})
    reqs = []
    if spell: reqs.append(f'Spell: {spell}')
    pre = TIER_PREREQ.get(spell)
    # the Reincarnation / dragon-growth upgrade each spell group needs belongs to the Unlocks page, not here
    if r.get('sv') and r.get('sw'):
        d_ = describe_source({'kind': 'artifact' if r['sw'] in ARTIFACT else 'trophy', 'name': r['sw']})
        reqs.append(f"{d_['kind']}: {d_['name']}")
    reaches = r['sr']
    by_cat['magic'].append({
        'name': r['n'], 'icon': r['icon'] if r['icon'] in sprites else None, 'order': r['i'], 'id': r['id'],
        'description': paras, 'sources': [], 'requirements': reqs, 'conditions': [], 'undecoded': [],
        'asc_min': (None if ra and all(v.startswith('To unlock, you need to have at least') and 'activity time' not in v for v in ra.values()) else reaches or None), 'asc_max': None, 'group': r.get('grp'), 'tier': None, 'building': None,
        'spell': spell, 'spell_tier': r['sr'] + 1, 'unlock_by_asc': ra,
    })

for u in by_cat['magic']:      # the spell tiers were added after the pass above
    if u.get('spell') == "Dragon's Breath" and (u['asc_min'] or 0) < 1: u['asc_min'] = 1

# value symbols: v, or v1, v2 ... when a description has several computed values
raw = []
for items in by_cat.values():
    for u in items:
        forms = [f for p in u['description'] for f in p['formulas']]
        for f in forms:
            if 'raw' in f: raw.append((u['name'], f['raw']))
        conv = [f for f in forms if 'latex' in f]
        if len(conv) > 1:
            for k, f in enumerate(conv, 1):
                f['latex'] = re.sub(r'^v(?:_\{\d+\})? = ', f'v_{{{k}}} = ', f['latex'])
for n, e in raw: print('RAW (dropped)', n, '|', e[:120])
for items in by_cat.values():
    for u in items:
        for p in u['description']: p['formulas'] = [f for f in p['formulas'] if 'latex' in f]

json.dump(by_cat, open(os.path.join(ROOT, 'data', 'upgrade_pages.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
print('ambiguous trophy names:', amb)
print('data/upgrade_pages.json:', {k: len(v) for k, v in by_cat.items()},
      '| undecoded conditions:', len(problems))
for n, b in problems: print('  ', n, b)

