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
              sg: o.{J('§`g§')}, sr: o.{J('§`r§')}, sw: o.{J('§2!w§')}, sv: o.{J('§;!v§')} }};
    try {{ r.bld = o.{J('§%<§')}.{J('§1i§')}; }} catch (e) {{}}
    try {{ r.tid = o.{J('§`!5§')}; }} catch (e) {{}}
    var keepR = {g}.{J('§8!H§')};
    if (r.grp === 'ReincarnationPowerUpgrade') {g}.{J('§8!H§')} = 9999;      // show every line of the text
    try {{ r.d = o.{J('§@"§')}(); }} catch (e) {{ r.d = 'ERR ' + e; }}
    {g}.{J('§8!H§')} = keepR;
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
    return f'10{str(e).translate(_SUP)}' if mant == 1 else f'{mant:g} × 10{str(e).translate(_SUP)}'


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
            cond.append(f'having bought upgrades from at least {mm.group(1)} different factions other than Mercenary'); continue
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
                        f'"{nm(mm.group(1))[1]}" is bought'); continue
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
    if name == 'Suggestion Master':
        paras[0]['formulas'] = []     # the code only has the constant 4*10 + 3 + 0*0.1 + 14*0.01
        paras[0]['text'] = 'Increase the production of all buildings based on mysterious events. (43.14%)'
    if name == 'Ancestral Hourglass':
        paras[0]['formulas'] = [_m(r'v = \frac{0.002 \cdot R}{A}',
            ('v', 'Amount taken off the Lineage cost exponent growth (per 25 levels of a Lineage)'),
            ('R', 'Reincarnations made'), ('A', 'Your Ascension number (this upgrade needs Ascension 2 or more)'))]
    # building-tier multipliers that sit in the production code, not in the description (T = building tier, counted from 1; checked in game)
    TIER = ('T', "The building's tier (1 for the first building in the list)")
    if name == 'Mathematician':
        paras[0]['formulas'] = [_m(r'v = 10 \cdot \left(12 - T\right)', TIER)]
        paras[0]['s'] = 2
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
            'Good:': (r'v = 0.1 \cdot D^{0.9}', ('D', 'Your excavation depth (excavations made since your last Excavation Reset)')),
            'Neutral:': (r'v = 1.5 \cdot N^{0.6}', ('N', 'Royal Exchanges made in this Era')),
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


def tier_of(name):
    for k, n in TIER_NO:
        if k in name: return n
    return None


def wanted(r):
    if r['cat'] == 0:
        return bool(r.get('idx')) or (r.get('grp') in ALLEG_TAGS and tier_of(r['n']) is not None) or r['n'] in MERC_PERKS
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
    # Ascension penalty start: the first Ascension at which the game's own text for the value changes
    if r['cat'] != 4 and paras and paras[0].get('s') is None:
        base = texts[0]
        for a, ar in enumerate(asc_runs, 1):
            if ar['rows'][idx]['d'] != base:
                paras[0]['s'] = a; break
    fix_raw(r['n'], c, paras)
    fix_text(r['n'], paras)
    av = next((m for m in c.methods if m.name == '§-6§'), None)
    body = re.sub(r'\s+', ' ', av.body.strip()) if av else ''
    ctx = {'name': r['n'], 'thr': r.get('thr') if isinstance(r.get('thr'), (int, float, str)) else None, 'tid': r.get('tid'),
           'tier': r.get('tier'), 'bld': r.get('bld'), 'group': r.get('grp'), 'file': getattr(c, 'path', None),
           'cat': r['cat'], 'ax': r.get('ax')}
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
    if bad: problems.append((r['n'], bad))
    item = {
        'name': r['n'], 'icon': r['icon'] if r['icon'] in sprites else None, 'order': r['i'], 'id': r['id'],
        'description': paras, 'sources': [describe_source(s) for s in src], 'requirements': extra,
        'conditions': cond, 'undecoded': bad, 'asc_min': alo, 'asc_max': ahi, 'group': r.get('grp') or None,
        'tier': r.get('tier'), 'building': r.get('bld'),
    }
    if r['cat'] == 0:
        item['faction'] = r['f']
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

# a Reincarnation requirement that the Ascension's range of Reincarnations cannot reach rules that Ascension out
for u in by_cat['allegiances']:
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
    if pre: reqs.append(f'Reincarnation {pre[0]}+ and Upgrade: {pre[1]}')
    if r.get('sv') and r.get('sw'):
        d_ = describe_source({'kind': 'artifact' if r['sw'] in ARTIFACT else 'trophy', 'name': r['sw']})
        reqs.append(f"{d_['kind']}: {d_['name']}")
    reaches = r['sr']
    by_cat['magic'].append({
        'name': r['n'], 'icon': r['icon'] if r['icon'] in sprites else None, 'order': r['i'], 'id': r['id'],
        'description': paras, 'sources': [], 'requirements': reqs, 'conditions': [], 'undecoded': [],
        'asc_min': reaches or None, 'asc_max': None, 'group': r.get('grp'), 'tier': None, 'building': None,
        'spell': spell, 'spell_tier': r['sr'] + 1, 'unlock_by_asc': ra,
    })

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
