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


def engine_costs(indexes):
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
  for (var n = 0; n < idx.length; n++) { var o = U[idx[n]], row = { n: o.__NAME, rows: [], fld: [o.__A0, o.__A1, o.__A2, o.__A3, o.__A4], tier: o.__TIER };
    for (var A = 0; A <= __MAXA; A++) { var seen = [];
      [[0, 0], [1, 0], [60, 1e6], [300, 1e30]].forEach(function (st) {
        G.__ASC = A; G.__REINC = st[0]; G.__GEMS = st[1];
        var coins = 0; try { coins = o.__COINS; } catch (e) {}
        var f = []; for (var k = 0; k < 16; k++) { var v = 0; try { v = Math.round(o.__FACN(k)); } catch (e) {} f.push(v); }
        seen.push(JSON.stringify([coins, f])); });
      row.rows.push(seen); }
    out[idx[n]] = row; }
  return JSON.stringify(out); })()"""
    for k, v in (('__G', g), ('__U', J('§-!4§')), ('__NAME', J('§1i§')), ('__A0', J('§>=§')), ('__A1', J('§<R§')), ('__A2', J('§#!m§')), ('__A3', J('§#"-§')),
                 ('__A4', J('§;">§')), ('__TIER', J('§!"E§')), ('__ASC', J('§,P§')), ('__REINC', J('§8!H§')), ('__GEMS', J('§"!0§')), ('__COINS', J('§9!U§')),
                 ('__FACN', J('§75§')), ('__MAXA', str(MAXA)), ('__IDX__', json.dumps(list(indexes)))):
        prog = prog.replace(k, v)
    res = json.loads(ctx.eval(prog))
    out = {}
    for k, r in res.items():
        per = []
        for a, seen in enumerate(r['rows']):
            assert len(set(seen)) == 1, ('a cost that changes with Reincarnations or Gems', r['n'], a, seen)
            coins, f = json.loads(seen[0]); per.append((coins, [(i, v) for i, v in enumerate(f) if v > 0]))
        fld = r['fld']
        first = 0 if fld[0] or r['tier'] else next((a for a in range(1, MAXA + 1) if fld[a]), 0)      # no cost of Ascension 0, a later one: the upgrade starts there
        out[int(k)] = (r['n'], [None if a < first else per[a] for a in range(MAXA + 1)])
    return out
