"""What an upgrade costs, read from the game's class: the coins of each Ascension and the Faction Coins.

The game's base class (the upgrade base, `§`6§`) gives the coin cost of an Ascension from the fields the upgrade sets: the Ascension 0 cost,
the cost it has instead from Ascension 1, 2, 3 and 4 on, and the tier an upgrade of the later Ascensions costs by. The Faction Coins an upgrade costs are
the values its own class returns for each faction (0 to 15). Anything else in a class that this does not understand stops the build.
"""
import math, os, re, sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('checks',)]
import verify_formulas as V
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pylib'))

F_A0, F_A1, F_A2, F_A3, F_A4 = '§>=§', '§<R§', '§#!m§', '§#"-§', '§;">§'      # the coin cost of Ascension 0, and the one it has instead from Ascension 1, 2, 3, 4 on
F_TIER, F_FACTION = '§!"E§', '§-!^§'
FN_COINS, FN_FACTION = '§9!U§', '§75§'      # the coin cost (the base class's getter) and the Faction Coins of one faction (a method each class may override)
OTHER_COSTS = ('§\'B§', '§6U§', '§%!;§', '§&q§')      # other kinds of cost (items, mana, money): the pages do not show them
BASE = '§`6§'
MAXA = 4
NUM = re.compile(r'^[0-9eE+\-*/(). ]+$')


def _num(expr):
    expr = expr.strip()
    assert NUM.match(expr), expr
    return float(eval(expr, {'__builtins__': {}}))


def _body(text, fn):
    """the text of a method from its signature to the closing brace at the class level"""
    m = re.search(r'^( {6})(?:override )?public (?:static )?function (?:get )?' + re.escape(fn) + r'\(.*?^\1\}', text, re.M | re.S)
    return m.group(0) if m else None


def tier_cost(tier, fac):
    k = (tier - 1) // 3
    base = 1e189 if fac in (13, 15, 14) else 1.0e120 if fac in (9, 10, 12) else 1e48
    return base * math.pow(1000, tier - 1) * math.pow(1000, 0.5 * k * (k + 1))


def coins(f, a):
    """the base class's getter: the coins at Ascension a"""
    if f[F_TIER] > 0 and a >= 4: return tier_cost(f[F_TIER], f[F_FACTION])
    if f[F_A4] != 0 and a >= 4: return 0 if a >= 5 else f[F_A4]
    if f[F_A3] != 0 and a >= 3: return 0 if a >= 4 else f[F_A3]
    if f[F_A2] != 0 and a >= 2: return 0 if a >= 3 else f[F_A2]
    if f[F_A1] != 0 and a >= 1: return 0 if a >= 2 else f[F_A1]
    return 0 if a >= 1 else f[F_A0]


def faction_coins(text):
    """{faction: amount}: what the class's own method returns for each faction"""
    body = _body(text, FN_FACTION)
    if body is None: return {}
    out = {}
    rest = body
    for m in re.finditer(r'if\(param1 == (\d+)\)\s*\{\s*return ([^;]+);\s*\}', body):
        out[int(m.group(1))] = _num(m.group(2)); rest = rest.replace(m.group(0), '')
    left = re.sub(r'\s+', '', rest.split('{', 1)[1])
    assert left == 'return0;}', ('a Faction Coin cost this does not read', left)
    return out


def static_cost(cls):
    """cost[a] for Ascension 0 to MAXA: (coins, [(faction, amount), ...]), or None below the Ascension the upgrade starts at"""
    text = V.read(V.path_of(cls))
    assert re.search(r'class .+? extends ' + re.escape(BASE) + r'(?!\S)', text), ('not a direct upgrade', cls)
    assert _body(text, FN_COINS) is None, ('its own coin cost', cls)
    for fn in OTHER_COSTS: assert _body(text, fn) is None, ('another cost', fn, cls)
    name = cls.split('.')[-1]
    ctor = _body(text, name)
    assert ctor, cls
    f = {F_A0: 0.0, F_A1: 0.0, F_A2: 0.0, F_A3: 0.0, F_A4: 0.0, F_TIER: 0, F_FACTION: -1}
    given = set()
    for m in re.finditer(r'^\s+(§[^§\n]*§) = ([^;\n]+);\s*$', ctor, re.M):
        if m.group(1) in f: f[m.group(1)] = _num(m.group(2)); given.add(m.group(1))
    # an upgrade that has no cost of Ascension 0 starts at the first Ascension that has one (the upgrades the pages already say need Ascension 1 or 2 are all
    # set up this way): below it there is no cost to show
    first = 0 if F_A0 in given or F_TIER in given else next((a for a, k in enumerate((F_A0, F_A1, F_A2, F_A3, F_A4)) if k in given), 0)
    f[F_TIER] = int(f[F_TIER]); f[F_FACTION] = int(f[F_FACTION])
    fc = sorted(faction_coins(text).items())
    return [None if a < first else (coins(f, a), [(i, v) for i, v in fc if v > 0]) for a in range(MAXA + 1)]


SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'out', 'script', 'scripts')


def names():
    """the game's names of the coins: (the main currency of Ascension 0 to MAXA, the Faction Coin of each faction 0 to 15)"""
    t = open(os.path.join(SCRIPTS, '§&c§.as'), encoding='utf8').read()
    body = _body(t, '§=!n§')
    cur = {}
    for m in re.finditer(r'§,P§ (>=|==) (\d)\)\s*\{\s*return _\("([^"]+)"\);', body): cur.setdefault(int(m.group(2)), m.group(3))
    cur[0] = re.search(r'return _\("([^"]+)"\);\s*\}\s*$', body).group(1)
    assert sorted(cur) == list(range(MAXA + 1)), cur
    d = open(os.path.join(SCRIPTS, '§-D§.as'), encoding='utf8').read()
    fac = re.findall(r'_\("([^"]+)"\)', re.search(r'const §45§:Array = new Array\((.*?)\);', d).group(1))
    assert len(fac) == 16, fac
    return [cur[a] for a in range(MAXA + 1)], fac


# ---- the engine: the game's own code run in QuickJS (data/derived/engine.js), asked for the cost of each upgrade object -------------------------------------
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')


def engine_raw(indexes):
    """{index into the game's upgrade list: cost[a] for a in 0..MAXA} where cost[a] is (coins, [(faction, amount), ...]) or None below the Ascension the upgrade starts at.
    The numbers are what the game's own getters return (coins: the getter above; Faction Coins: the method of each class, rounded like the game rounds what it takes).
    Every state a cost could depend on (Reincarnations, Gems) is tried: a cost that changes with one stops the build."""
    import json, quickjs
    names = json.load(open(os.path.join(ROOT, 'data', 'derived/engine_names.json'), encoding='utf8'))['names']
    J = lambda t: names[t]
    g = J('§8G§')
    ctx = quickjs.Context()
    ctx.eval(open(os.path.join(ROOT, 'data', 'derived/engine.js'), encoding='utf8').read()); ctx.eval('__boot()')
    prog = """(function () {
  var G = __G, U = G.__U, out = {}, idx = __IDX__;
  for (var n = 0; n < idx.length; n++) { var o = U[idx[n]]; if (!o) continue; var row = { n: o.__NAME, rows: [], fld: [o.__A0, o.__A1, o.__A2, o.__A3, o.__A4], tier: o.__TIER };
    for (var A = 0; A <= __MAXA; A++) { var seen = [];
      [[0, 0], [1, 0], [60, 1e6], [300, 1e30]].forEach(function (st) {
        G.__ASC = A; G.__REINC = st[0]; G.__GEMS = st[1];
        var coins = 0; try { coins = o.__COINS; } catch (e) { row.err = 'coins ' + e; }
        var f = []; for (var k = 0; k < 16; k++) { var v = 0; try { v = Math.round(o.__FACN(k)); } catch (e) { row.err = 'faction ' + e; } f.push(v); }
        seen.push(JSON.stringify([coins, f]));
        for (var q = 0; q <= 30; q++) { var w = 0; try { w = o.__ITEMN(q); } catch (e) {} if (w) (row.other = row.other || []).push(['item', q, w]); }
        var mana = 0; try { mana = o.__MANA(); } catch (e) {} if (mana) (row.other = row.other || []).push(['mana', 0, mana]); });
      row.rows.push(seen); }
    out[idx[n]] = row; }
  return JSON.stringify(out); })()"""
    for k, v in (('__G', g), ('__U', J('§-!4§')), ('__NAME', J('§1i§')), ('__A0', J('§>=§')), ('__A1', J('§<R§')), ('__A2', J('§#!m§')), ('__A3', J('§#"-§')),
                 ('__A4', J('§;">§')), ('__TIER', J('§!"E§')), ('__ASC', J('§,P§')), ('__REINC', J('§8!H§')), ('__GEMS', J('§"!0§')), ('__COINS', J('§9!U§')),
                 ('__FACN', J('§75§')), ('__ITEMN', J("§'B§")), ('__MANA', J('§6U§')), ('__MAXA', str(MAXA)), ('__IDX__', json.dumps(list(indexes)))):
        prog = prog.replace(k, v)
    return json.loads(ctx.eval(prog))


# the two Trade Treaties that cost 20 of their faction's coins only once you own a Gem or have Reincarnated (the very first run has no cost)
NO_COST = ('Mercenary Tribute',)      # the price grows with the time played in the Era: the engine cannot give one number, so the Unlocks pages show the formula and no cost
STATE_DEPENDENT = {'Fairies Trade Treaty', 'Goblins Trade Treaty'}


def engine_costs(indexes):
    import json
    res = engine_raw(indexes)
    out = {}
    varies = set()
    for k, r in res.items():
        per = []
        for a, seen in enumerate(r['rows']):
            if len(set(seen)) > 1:
                assert r['n'] in STATE_DEPENDENT, ('a cost that changes with Reincarnations or Gems', r['n'], a, seen)
                varies.add(r['n'])
            coins, f = json.loads(seen[-1])      # the state of someone who has played on (the last one tried)
            if coins is None: coins = float('inf')      # beyond what a number holds (the game shows INF): an Ascension the upgrade cannot be had at
            per.append((coins, [(i, v) for i, v in enumerate(f) if v > 0]))
        assert 'other' not in r, ('a cost that is not coins or Faction Coins', r['n'], r['other'][:2])
        assert 'err' not in r, ('the game could not work out a cost', r['n'], r['err'])
        fld = r['fld']
        first = 0 if fld[0] is None or fld[0] or r['tier'] else next((a for a in range(1, MAXA + 1) if fld[a]), 0)      # no cost of Ascension 0, a later one: the upgrade starts there
        out[int(k)] = (r['n'], [None if a < first else per[a] for a in range(MAXA + 1)])
    return out


def engine_desc(indexes):
    """{index: the game's own description text at Ascension 0} for upgrades whose text the data files hold only as code (a number worked out in the text)"""
    import json, quickjs
    names = json.load(open(os.path.join(ROOT, 'data', 'derived/engine_names.json'), encoding='utf8'))['names']
    J = lambda t: names[t]
    ctx = quickjs.Context()
    ctx.eval(open(os.path.join(ROOT, 'data', 'derived/engine.js'), encoding='utf8').read()); ctx.eval('__boot()')
    prog = ('(function () { var G = %s, U = G.%s, out = {}, ix = %s; G.%s = 0; ix.forEach(function (i) { out[i] = U[i].%s(); }); return JSON.stringify(out); })()'
            % (J('§8G§'), J('§-!4§'), json.dumps(list(indexes)), J('§,P§'), J('§@"§')))
    return {int(k): v for k, v in json.loads(ctx.eval(prog)).items()}


def engine_find(wanted, research=False):
    """{name: index into the game's upgrade list} for the upgrades the pages hold under no entry of their own (the Legacy Combos), or, with research, for researches"""
    import json, quickjs
    names = json.load(open(os.path.join(ROOT, 'data', 'derived/engine_names.json'), encoding='utf8'))['names']
    J = lambda t: names[t]
    ctx = quickjs.Context()
    ctx.eval(open(os.path.join(ROOT, 'data', 'derived/engine.js'), encoding='utf8').read()); ctx.eval('__boot()')
    prog = ('(function () { var U = %s.%s, w = %s, out = {}; for (var i = 0; i < U.length; i++) { var n = U[i].%s; if (w.indexOf(n) >= 0 && !(n in out) && (!%s || U[i].%s >= 0)) out[n] = i; } return JSON.stringify(out); })()'
            % (J('§8G§'), J('§-!4§'), json.dumps(list(wanted)), J('§1i§'), 'true' if research else 'false', J('§!G§')))
    return json.loads(ctx.eval(prog))


# ---- the Lineages: the Faction Coins to raise one a level (the lineage base class, tools: out/script/scripts/§3^§/§6P§.as) ------------------------------------
LINEAGE_BASE = os.path.join(SCRIPTS, '§3^§', '§6P§.as')
LINEAGE = {'every': 25, 'hourglass': 0.002, 'heirloom': 0.97}      # the constants of the formula that the class writes as code; lineage_check() holds them to the engine


def lineage_params():
    """what the lineage base class uses: the base and the exponent part c of each Ascension, and the two upgrades that change the cost (their names)"""
    t = open(LINEAGE_BASE, encoding='utf8').read()
    body = _body(t, FN_FACTION)
    head = body.split('if(§8G§.§,P§ == 2)')[0]
    b = {a: _num(re.search(r'_loc8_ = ([^;]+);', head).group(1)) for a in range(MAXA + 1)}
    c = {a: _num(re.search(r'_loc7_ = ([^;]+);', head).group(1)) for a in range(MAXA + 1)}
    E = re.escape
    for m in re.finditer(E('§8G§.§,P§') + r' == (\d)\)\s*\{([^}]*)\}', body):
        a = int(m.group(1))
        for k, d in (('_loc8_', b), ('_loc7_', c)):
            mm = re.search(k + r' = ([^;]+);', m.group(2))
            if mm: d[a] = _num(mm.group(1))
    own = E('§8G§.§7d§') + r'\((.+?)\.id\)'      # the upgrades it checks the player owns
    hg = re.search(own + r' \? ', body).group(1)
    hh = re.search(own + ' && ' + E('§8G§.§1!#§') + r'\[' + E('§0!N§') + r'\] < ' + E('§&c§.§,T§') + r'\(\)', body).group(1)
    import json
    ups = {u['class']: u.get('name') for u in json.load(open(os.path.join(ROOT, 'data', 'derived/upgrades.json'), encoding='utf8')) if u.get('class')}
    imports = {m.group(1).rsplit('.', 1)[-1]: m.group(1) for m in re.finditer(r'^\s*import (.+);\s*$', t, re.M)}
    return {'b': [b[a] for a in range(MAXA + 1)], 'c': [c[a] for a in range(MAXA + 1)], 'hourglass': ups[imports[hg]], 'heirloom': ups[imports[hh]]}


def lineage_log10(a, level, bases, cs, hourglass, heirloom, reincarnations, highest):
    """log10 of the cost the formula gives (the numbers get too large for a float)"""
    r = LINEAGE['hourglass'] * reincarnations / a if hourglass else 0
    lg = (math.log10(bases[a]) + level / a) * (1 + (cs[a] + 1 / (2 * a) - r) * math.floor(level / LINEAGE['every']))
    return lg * LINEAGE['heirloom'] if heirloom and level < highest else lg


def lineage_check():
    """the formula against the game's own method for every lineage, Ascension 1 to 4, a range of levels, with and without the two upgrades: (states compared, worst relative error)"""
    import json, quickjs
    names = json.load(open(os.path.join(ROOT, 'data', 'derived/engine_names.json'), encoding='utf8'))['names']
    J = lambda t: names[t]
    pages = json.load(open(os.path.join(ROOT, 'data', 'generated/upgrade_pages.json'), encoding='utf8'))
    idx = [x['order'] for x in pages['allegiances'] if x.get('akind') == 'lineage']
    P = lineage_params()
    ctx = quickjs.Context()
    ctx.eval(open(os.path.join(ROOT, 'data', 'derived/engine.js'), encoding='utf8').read()); ctx.eval('__boot()')
    prog = """(function () { var G = __G, U = G.__U, out = [], idx = __IDX__, hour = null, heir = null;
  for (var i = 0; i < U.length; i++) { if (U[i].__NAME === __HG) hour = U[i]; if (U[i].__NAME === __HH) heir = U[i]; }
  for (var n = 0; n < idx.length; n++) { var o = U[idx[n]], slot = o.__SLOT, fac = o.__FAC;
    [1, 2, 3, 4].forEach(function (A) { [0, 1, 24, 25, 26, 60, 120].forEach(function (L) { [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 1, 1], [1, 1, 1]].forEach(function (st) {
      G.__ASC = A; G.__REINC = 100 + A; for (var q = 0; q < 15; q++) G.__LEV[q] = 0; G.__LEV[slot] = L; if (st[2]) G.__LEV[(slot + 1) % 15] = L + 30;
      __X.__PICK = fac; hour.__OWN = !!st[0]; heir.__OWN = !!st[1];
      var v = 0; try { v = o.__FACN(fac); } catch (e) { v = null; }
      out.push([A, L, st[0], st[1], st[2], v]); }); }); }); }
  return JSON.stringify(out); })()"""
    rep = (('__G', J('§8G§')), ('__U', J('§-!4§')), ('__IDX__', json.dumps(idx)), ('__NAME', J('§1i§')), ('__HG', json.dumps(P['hourglass'])), ('__HH', json.dumps(P['heirloom'])),
           ('__SLOT', J('§0!N§')), ('__FACN', J('§75§')), ('__FAC', J('§-!^§')), ('__ASC', J('§,P§')), ('__REINC', J('§8!H§')), ('__LEV', J('§1!#§')), ('__X', J('§#!!§')), ('__PICK', J('§3"§')),
           ('__OWN', J('§<!7§')))
    for k, v in rep: prog = prog.replace(k, v)
    res = json.loads(ctx.eval(prog))
    worst, n = 0.0, 0
    for a, level, hg, hh, hi, v in res:
        f = lineage_log10(a, level, P['b'], P['c'], hg, hh, 100 + a, level + 30 if hi else level)
        if v is None or v == 0 or f > 300: continue
        n += 1; worst = max(worst, abs(math.log10(v) - f) / max(abs(f), 1e-9))
    return n, worst


def lineage_spec():
    """what the page needs for the cost section of the Lineages"""
    P = lineage_params()
    return {'b': P['b'], 'c': P['c'], 'hg': P['hourglass'], 'ev': LINEAGE['every']}


# ---- the researches: the research base class prices them by their number (tools: out/script/scripts/§;!J§/§&!_§.as) ------------------------------------
RESEARCH_BASE = os.path.join(SCRIPTS, '§;!J§', '§&!_§.as')


def _big(a, b, e):
    """a * b ** e, infinite where a number cannot hold it (as in the game)"""
    try: return a * math.pow(b, e)
    except OverflowError: return float('inf')


def research_check(indexes_by_name):
    """the coins of every research at each Ascension, worked out from the base class's own numbers and the number the research class writes, against the engine: (compared, differing)"""
    import json
    t = open(RESEARCH_BASE, encoding='utf8').read()
    body = _body(t, FN_COINS)
    E = re.escape
    n = E('§%w§')
    free_to = int(re.search(n + r' <= (\d+)', body).group(1))
    a1 = re.search(r'return ([0-9.e+]+) \* Math\.pow\(([0-9.]+),' + n + r' - (\d+)\)', body)
    a0 = re.search(r'return ([0-9.e+]+) \* Math\.pow\(([0-9.]+),' + n + r'\)', body)
    free_from = int(re.search(E('§8G§.§,P§') + r' >= (\d)\)\s*\{\s*return 0;', body).group(1))
    ec = engine_costs(list(indexes_by_name.values()))
    res = json.load(open(os.path.join(ROOT, 'data', 'derived/researchs.json'), encoding='utf8'))
    bad = total = 0
    for r in res:
        if r['name'] not in indexes_by_name: continue
        text = V.read(V.path_of(r['class']))
        assert '_("' + r['name'] + '")' in text or '_("' + r['name'].replace("'", ""+chr(92)+"'") + '")' in text, ('the class file is another class', r['name'])      # (the exporter writes class names that differ only in case as NAME_2.as: see verify_formulas.path_of)
        w = int(re.search(n + r' = (\d+);', _body(text, r['class'].split('.')[-1])).group(1))
        for a in range(MAXA + 1):
            if a >= free_from: want = 0
            elif a == 1: want = 0 if w <= free_to else _big(float(a1.group(1)), float(a1.group(2)), w - int(a1.group(3)))
            else: want = _big(float(a0.group(1)), float(a0.group(2)), w)
            got = ec[indexes_by_name[r['name']]][1][a][0]
            total += 1
            if not (got == want or (want and got != float('inf') and abs(got - want) <= 1e-9 * abs(want))): bad += 1
    return total, bad


# ---- the research facilities: what one research point of a branch costs and gives (tools: out/script/scripts/§;!J§/§1!7§.as) --------------------------------
FACILITY = os.path.join(SCRIPTS, '§;!J§', '§1!7§.as')


def facility_params():
    """the numbers of the facility upgrade class: the coin price of each Ascension, the Faction Coin price, the production bonus, the faction lists"""
    t = open(FACILITY, encoding='utf8').read()
    E = re.escape
    P = E('§&c§.§&!<§(§!G§,true)')      # the research points of the branch
    flat = lambda s: re.sub(r'\s+', '', s)
    g = flat(_body(t, FN_COINS))
    num = r'([0-9.e+]+)'
    m4 = re.search(E('§8G§.§,P§>=4){if(') + P + r'<(\d+)\){return0;}returnMath\.pow\(' + num + ',' + num + r'\*\(' + P + r'-(\d+)\)\);', g)
    m2 = re.search(E('§8G§.§,P§>=2&&§8G§.§,P§<4){if(') + P + r'<(\d+)\){return0;}return' + num + r'\*Math\.pow\(' + num + ',' + num + r'\*\(' + P + r'-(\d+)\)\);', g)
    m1 = re.search(E('§8G§.§,P§==1){if(') + P + r'<=(\d+)\){return0;}return' + num + r'\*Math\.pow\(' + num + ',' + P + r'-(\d+)\);', g)
    m0 = re.search(r'return' + num + r'\*Math\.pow\(' + num + ',' + P + r'\);\}$', g)
    assert m4 and m2 and m1 and m0, 'the facility coin price changed shape'
    f = flat(_body(t, FN_FACTION))
    k_hi = re.search(r'if\(_loc5_>=(\d+)\)\{returnMath\.pow\(10,(-?\d+)\)\*Math\.pow\(' + num + r',' + num + r'\*_loc5_\);\}', f)
    k_mid = re.search(r'if\(_loc5_>=(\d+)&&_loc5_<(\d+)\)\{returnMath\.pow\(_loc5_\+1,' + num + r'\);\}returnMath\.pow\(_loc5_\+1,' + num + r'\);', f)
    assert k_hi and k_mid, 'the facility Faction Coin price changed shape'
    b = re.search(r'\(§!G§==6\?(\d+):(\d+)\)\*\(1\+' + num + r'\*Math\.pow\(' + E('§&c§.§&!<§(§!G§)') + ',' + num + r'\)\),§!G§==6\?(\d+):(\d+)\)', flat(t))
    assert b, 'the facility production bonus changed shape'
    import json
    lists = {k: json.loads('[' + v + ']') for k, v in re.findall(r'const(§[^§]*§):Array=\[([^\]]*)\]', flat(t))}
    ext = re.findall(E('§8G§.§7d§(') + r'(§[^§]*§)\.id\)&&(§[^§]*§)\[§!G§\]!=-1', flat(t))
    ups = {u['class']: u.get('name') for u in json.load(open(os.path.join(ROOT, 'data', 'derived/upgrades.json'), encoding='utf8')) if u.get('class')}
    extra = [(ups['§;!J§.' + tok], lst) for tok, lst in ext]      # (upgrade name, the faction list it opens)
    assert len(extra) == 2, extra
    six = re.search(r'§!G§==6&&\(param1==(\d+)\|\|param1==(\d+)\)', f)      # the last branch takes the coins of two factions
    assert six, 'the facility Faction Coins changed shape'
    return {'own': lists['§^!C§'], 'six': [int(six.group(1)), int(six.group(2))], 'extra': [(n, lists[l]) for n, l in extra], 'a4': [float(x) for x in m4.groups()], 'a2': [float(x) for x in m2.groups()], 'a1': [float(x) for x in m1.groups()], 'a0': [float(x) for x in m0.groups()],
            'k_hi': [float(x) for x in k_hi.groups()], 'k_mid': [float(x) for x in k_mid.groups()],
            'boost': [float(x) for x in b.groups()]}


def facility_coins(a, p, F):
    """the coins the next research point costs at Ascension a with p points (log10 of a number too large for a float is not needed: the largest is 10^176)"""
    if a >= 4: return 0 if p < F['a4'][0] else _big(1, F['a4'][1], F['a4'][2] * (p - F['a4'][3]))
    if a >= 2: return 0 if p < F['a2'][0] else _big(F['a2'][1], F['a2'][2], F['a2'][3] * (p - F['a2'][4]))
    if a == 1: return 0 if p <= F['a1'][0] else _big(F['a1'][1], F['a1'][2], p - F['a1'][3])
    return _big(F['a0'][0], F['a0'][1], p)


def facility_faction(p, F):
    hi, mid = F['k_hi'], F['k_mid']
    if p >= hi[0]: return math.pow(10, hi[1]) * math.pow(hi[2], hi[3] * p)
    if p >= mid[0] and p < mid[1]: return math.pow(p + 1, mid[2])
    return math.pow(p + 1, mid[3])


def facility_boost(branch, p, F):
    """the production bonus in % before the Ascension penalty"""
    b = F['boost']
    return (b[0] if branch == 6 else b[1]) * (1 + b[2] * math.pow(p, b[3]))


def facility_check(verbose=False):
    """the facility formulas against the game's own getters for the 7 branches, Ascension 0 to 4 and the points around every limit: (states compared, states differing)"""
    import json, quickjs
    names = json.load(open(os.path.join(ROOT, 'data', 'derived/engine_names.json'), encoding='utf8'))['names']
    J = lambda t: names[t]
    F = facility_params()
    ctx = quickjs.Context()
    ctx.eval(open(os.path.join(ROOT, 'data', 'derived/engine.js'), encoding='utf8').read()); ctx.eval('__boot()')
    pts = [0, 1, 2, 100, 779, 780, 781, 1000, 4999, 5000, 5001, 9999, 10000, 10001, 12000]
    prog = """(function () { var G = __G, U = G.__U, out = [], pts = __PTS;
  for (var i = 0; i < U.length; i++) { var o = U[i]; if (o.__FACIL === undefined) continue; var b = o.__BR, idx = b == 6 ? 154 : 90 + b;
    for (var A = 0; A <= 4; A++) pts.forEach(function (P) {
      G.__ASC = A; G.__STAT[idx] = P; G.__ERA[idx] = 0; G.__GAME[idx] = 0;
      var c = 0, f = []; try { c = o.__COINS; } catch (e) { c = null; }
      for (var k = 0; k < 16; k++) { var v = 0; try { v = o.__FACN(k); } catch (e) { v = null; } f.push(v); }
      var d = ''; try { d = o.__DESC(); } catch (e) { d = 'ERR'; }
      out.push([b, A, P, c, f, d]); }); }
  return JSON.stringify(out); })()"""
    rep = (('__FACIL', J('§>E§')), ('__FACN', J('§75§')), ('__DESC', J('§@"§')), ('__COINS', J('§9!U§')), ('__BR', J('§!G§')), ('__ASC', J('§,P§')), ('__STAT', J('§5!V§')),
           ('__ERA', J('§=y§')), ('__GAME', J('§@w§')), ('__G', J('§8G§')), ('__U', J('§-!4§')), ('__PTS', json.dumps(pts)))
    for k, v in rep: prog = prog.replace(k, v)
    res = json.loads(ctx.eval(prog))
    own = F['own']
    n = bad = 0
    for b, a, p, c, f, d in res:
        want_c = facility_coins(a, p, F)
        want_f = {k: 0 for k in range(16)}
        for k in (F['six'] if b == 6 else [own[b]]): want_f[k] = facility_faction(p, F)
        if c is None: c = float('inf')      # a number that cannot hold the price (shown as INF in the game)
        ok = c == want_c or abs(c - want_c) <= 1e-9 * abs(want_c)
        for k in range(16):
            g = f[k]
            ok = ok and g is not None and abs(g - want_f[k]) <= 1e-9 * max(1.0, abs(want_f[k]))
            if g is None: print('   none', b, a, p, k)
        if a == 0:      # the text of the production bonus (no Ascension penalty at Ascension 0), four significant digits
            m = re.search(r'by ([0-9.,e+]+)%', d)
            want = facility_boost(b, p, F)
            ok = ok and m is not None and abs(float(m.group(1).replace(',', '')) - want) <= max(1.0, 1e-3 * want)      # the game shows whole numbers below a million (rounded down)
        if verbose and not ok: print('   differs:', b, a, p, c, want_c, [x for x in f if x], d[:60].replace(chr(10), ' '))
        n += 1; bad += 0 if ok else 1
    return n, bad
