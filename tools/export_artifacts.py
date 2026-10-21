"""Export the archaeology artifacts (quest + lore) to data/artifacts.json.

For each artifact: name, flavor text, icon, kind (quest/lore), the game's hint text for undiscovered
artifacts, and the unlock condition decoded from the game's code into plain language.  Clauses that
cannot be decoded are listed under `undecoded` (never guessed).

    python -I tools/export_artifacts.py
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'pylib'))
import quickjs
from as3parse import parse_all, resolve
from chance_latex import convert, STAT_ALL, BRANCH

names = json.load(open(os.path.join(ROOT, 'data', 'engine_names.json'), encoding='utf8'))['names']
sprites = json.load(open(os.path.join(ROOT, 'data', 'sprites.json')))
J = lambda t: names[t]

FACTION = {0: 'Fairy', 1: 'Elf', 2: 'Angel', 3: 'Goblin', 4: 'Undead', 5: 'Demon', 6: 'Titan', 7: 'Druid',
           8: 'Faceless', 9: 'Dwarf', 10: 'Drow', 11: 'Mercenary', 12: 'Dragon', 13: 'Archon'}
ALIGN = {1: 'Good', 2: 'Evil', 3: 'Neutral'}
PATH = {4: 'Order', 5: 'Chaos', 6: 'Balance'}  # second alignment axis (game's alignment-name table)

ctx = quickjs.Context()
ctx.eval(open(os.path.join(ROOT, 'data', 'engine.js'), encoding='utf8').read())
ctx.eval('__boot()')
g = J('§8G§')
src = f"""JSON.stringify((function () {{
  var qOf = function (o) {{ for (var c = 0; c < __classes.length; c++) if (__classes[c].K === o.constructor) return __classes[c].q; return null; }};
  var lists = {{ upgrade: {g}.{J('§-!4§')}, trophy: {g}.{J('§0Q§')}, spell: {g}.{J('§0!A§')}, building: {g}.{J('§%<§')} }};
  var named = {{}}, arts = [];
  for (var k in lists) for (var i = 0; i < lists[k].length; i++) {{
    var o = lists[k][i], q = qOf(o);
    if (q !== null) named[q] = [k, o.{J('§1i§')}];
  }}
  var T = lists.trophy;
  for (var i = 0; i < T.length; i++) {{
    var o = T[i];
    if (!o.{J('§@!R§')}) continue;
    var hint = null; try {{ hint = o.{J('§8!s§')}(); }} catch (e) {{}}
    arts.push({{ order: i, q: qOf(o), name: o.{J('§1i§')}, flavor: o.{J('§@"§')}(), icon: o.{J('§^!#§')},
                lore: !!o.{J('§4!3§')}, threshold: o.{J('§?"M§')}, hint: hint }});
  }}
  var B = lists.building, blds = [];
  for (var i = 0; i < B.length; i++) blds.push([B[i].{J('§1i§')}, B[i].{J('§,!Y§')}]);
  return {{ named: named, arts: arts, blds: blds }};
}})())"""
res = json.loads(ctx.eval(src))
named = res['named']

cl = parse_all()
HAS_UPGRADE = {J('§7d§'), J('§<P§')}  # (not used directly; clauses are matched on source tokens)


def clauses(expr):
    """Split on top-level && (outside parentheses)."""
    out, depth, cur, i = [], 0, '', 0
    while i < len(expr):
        ch = expr[i]
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if depth == 0 and expr.startswith('&&', i):
            out.append(cur.strip()); cur = ''; i += 2; continue
        cur += ch; i += 1
    if cur.strip(): out.append(cur.strip())
    return out


G = r'§8G§\.'


def dur(sec):
    """14400 -> '4 hours'."""
    for size, unit in ((86400, 'day'), (3600, 'hour'), (60, 'minute'), (1, 'second')):
        if sec >= size and sec % size == 0:
            n = sec // size
            return f'{n:,} {unit}' + ('s' if n != 1 else '')
    return f'{sec:,} seconds'


# Hidden trophies used as flags, shown in words
FLAG_TROPHY = {'Research Mercenary Trophy': 'Mercenary researches unlocked'}

# Method-body conditions (loops) recognised by their shape; the `if(...)` condition is decoded normally
GLYPH = re.compile(r'while\(_loc\d_ < §8G§\.§%<§\.length\).*§,!Y§ != 0 && _loc\d_\.§,!Y§ != 3.*§!a§')
UNION = re.compile(r'§<!7§ && _loc\d_\.§-!\^§ != 11 && _loc\d_\.§<`§ .*if\(_loc\d_ >= (\d+)\) \{ return true;')


def decode(c, art):
    meth = next((m for m in c.methods if m.name == '§ !3§'), None)
    if meth is None: return [], [], False
    body = re.sub(r'\s+', ' ', meth.body.strip())
    # local-time window (Dawnstone, Duskstone)
    body = re.sub(r'^var _loc1_:Date = new Date\(\); ', '', body)
    body = re.sub(r'\(_loc1_\.getHours\(\) >= (\d+) && _loc1_\.getHours\(\) <= (\d+)\)', r'__HOURS(\1,\2)', body)
    extra = None
    m = re.fullmatch(r'return (.+);', body)
    if not m:
        mi = re.search(r'if\((.+?)\) \{', body)
        if mi and GLYPH.search(body):
            names = [n for n, al in res['blds'] if al in (0, 3)]
            extra = 'Own exactly the same number of each of these buildings: ' + ', '.join(names)
        elif mi and UNION.search(body):
            extra = f'Have purchased upgrades from {UNION.search(body).group(1)} different factions'
        else:
            return [], [body[:200]], True
        expr = mi.group(1).strip()
    else:
        expr = m.group(1).strip()
    reqs, undec = [], []

    def ref_name(tok):
        q = resolve(c, tok, cl)
        return named.get(q) if q else None

    for cl_ in clauses(expr):
        s = cl_.strip()
        while s.startswith('(') and s.endswith(')') and len(clauses(s[1:-1])) >= 1 and s.count('(') == s.count(')'):
            # strip one redundant outer paren pair only if it wraps the whole clause
            depth = 0; ok = True
            for i, ch in enumerate(s):
                depth += ch == '('; depth -= ch == ')'
                if depth == 0 and i < len(s) - 1: ok = False; break
            if not ok: break
            s = s[1:-1].strip()
            sub = clauses(s)
            if len(sub) > 1:
                for x in sub: _one(x, c, art, reqs, undec, ref_name)
                s = None; break
        if s is not None: _one(s, c, art, reqs, undec, ref_name)
    if extra: reqs.append(extra)
    return reqs, undec, True


def _one(s, c, art, reqs, undec, ref_name):
    s = s.strip()
    if s == '§-6§': return
    thr = art['threshold']
    EXC = '{:,} excavations'
    m = re.fullmatch(G + r'§1!5§ >= §\?"M§', s)
    if m: reqs.append(EXC.format(int(thr))); return
    m = re.fullmatch(G + r'§1!5§ >= (\d+)', s)
    if m: reqs.append(EXC.format(int(m.group(1)))); return
    m = re.fullmatch(r'__HOURS\((\d+),(\d+)\)', s)
    if m:
        reqs.append(f'Excavate between {int(m.group(1)):02d}:00 and {int(m.group(2)):02d}:59 (your computer\'s local time)')
        return
    m = (re.fullmatch(r'\(?' + STAT_ALL + r'\)? >= (\d+)', s)
         or re.fullmatch(r'§&c§\.§"!B§\((\d+),true,false,false,true\) >= (\d+)', s))
    if m:
        i, v = int(m.group(1)), int(m.group(2))
        if i == 3: reqs.append(f'Spend {dur(v)} with Evil alignment (all-time)'); return
        if 50 <= i <= 63: reqs.append(f'Spend {dur(v)} as {FACTION[i - 50]} (all-time)'); return
        if i == 49: reqs.append(f'Affiliate with the Mercenaries {v:,} times (all-time)'); return
    m = re.fullmatch(G + r'§5!V§\[35\] == 0', s)
    if m: reqs.append('No excavations made yet in this Era (only the first excavation of an Era can find it)'); return
    m = re.fullmatch(G + r'§5!V§\[4\] == 0', s)
    if m: reqs.append('No clicks made in this Era'); return
    m = re.fullmatch(G + r'§5!V§\[1\] >= (\d+)', s)
    if m: reqs.append(f'Play for at least {dur(int(m.group(1)))} in this Era'); return
    m = re.fullmatch(G + r'§5!V§\[1\] <= (\d+)', s)
    if m: reqs.append(f'Within the first {dur(int(m.group(1)))} of an Era'); return
    m = re.fullmatch(r'§#!!§\.§2!&§\(\) >= (\d+)', s)
    if m: reqs.append(f'At least {int(m.group(1)):,} Maximum Mana'); return
    m = re.fullmatch(G + r'§\?!2§\("LegacyUpgrade"\) >= (\d+)', s)
    if m: reqs.append(f'Own {m.group(1)} Legacy upgrades'); return
    m = re.fullmatch(G + r'§8t§ >= (\d+)', s)
    if m: reqs.append(f'Unlock {int(m.group(1)):,} trophies'); return
    m = re.fullmatch(r'§#!!§\.§\^!&§\(\) >= (\d+)', s)
    if m: reqs.append(f'Purchase one upgrade from {m.group(1)} different factions'); return
    m = re.fullmatch(G + r'§-!\^§ == -1', s)
    if m: reqs.append('No faction chosen yet'); return
    m = re.fullmatch(r'§&c§\.§`!=§\(\) > 0', s)
    if m: reqs.append('At least one Lineage level'); return
    m = re.fullmatch(r'§&c§\.§&!<§\((\d),true\) >= (\d+)', s)
    if m:
        reqs.append(f'Buy {int(m.group(2)):,} {BRANCH[int(m.group(1))]} Research points (all-time)')
        return
    m = re.fullmatch(r'§&c§\.§7i§\((§[^§]*§)\.id,false,true,true\) >= (\d+)', s)
    if m:
        n = ref_name(m.group(1))
        if n and n[0] == 'spell':
            reqs.append(f'Have {n[1]} active for {dur(int(m.group(2)))} in total in this Era'); return
    m = re.fullmatch(G + r'§#N§\((§[^§]*§)\.id\)\.§`r§ >= (\d+)', s)
    if m:
        n = ref_name(m.group(1))
        # the stored tier counts from 0; the game displays it from 1 ("Unlock Tier %0" uses +1)
        if n and n[0] == 'spell':
            reqs.append(f'Have {n[1]} active at tier {int(m.group(2)) + 1} or higher'); return
    m = re.fullmatch(G + r'§\'"§\((§[^§]*§)\.id\)', s)
    if m:
        n = ref_name(m.group(1))
        if n and n[0] == 'upgrade':
            reqs.append(f'Have completed challenge {n[1]} (Dragon Challenge 6)' if n[1] == 'Dracomet Vault' else f'Have completed challenge {n[1]}'); return
    m = re.fullmatch(G + r'§,P§ >= (\d+)', s)
    if m: reqs.append(f'Ascension {m.group(1)} or higher'); return
    m = re.fullmatch(G + r'§8!H§ >= (\d+)', s)
    if m: reqs.append(f'Reincarnation {m.group(1)} or higher'); return
    m = re.fullmatch(G + r'§-!\^§ == (\d+)', s)
    if m: reqs.append(f'Playing as {FACTION.get(int(m.group(1)), "faction " + m.group(1))}'); return
    m = re.fullmatch(G + r'§#3§ == (-?\d+)', s)
    if m:
        v = int(m.group(1))
        reqs.append('No prestige faction' if v == -1 else f'{FACTION.get(v, "#" + str(v))} as prestige faction'); return
    m = re.fullmatch(G + r'§9!m§ == (\d)', s)
    if m and int(m.group(1)) in PATH:
        reqs.append(f'{PATH[int(m.group(1))]} alignment'); return
    m = re.fullmatch(G + r'§,!Y§ == (\d)', s)
    if m: reqs.append(f'{ALIGN.get(int(m.group(1)), "?")} alignment'); return
    m = re.fullmatch(G + r'(?:§7d§|§<P§)\((§[^§]*§)\.id\)', s)
    if m:
        n = ref_name(m.group(1))
        if n and n[1] in FLAG_TROPHY: reqs.append(FLAG_TROPHY[n[1]]); return
        if n: reqs.append(f'Requires {n[0]} {n[1]}'); return
    m = re.fullmatch(r'\(?((?:' + G + r'§7d§\(§[^§]*§\.id\)(?: \|\| )?)+)\)?', s)
    if m:
        toks = re.findall(r'(§[^§]*§)\.id', m.group(1))
        ns = [ref_name(t) for t in toks]
        if all(ns): reqs.append('Requires one of: ' + ', '.join(f'{k} {v}' for k, v in ns)); return
    undec.append(s)


def find_chance(c):
    """How the artifact is rolled once its requirements are met (game: per excavation, percent)."""
    if c is None: return {'mode': 'unknown'}
    # nearest override of the chance getter along the class chain
    k = c
    while k is not None:
        m = next((m for m in k.methods if m.name == '§5",§' and m.kind == 'get'), None)
        if m:
            body = re.sub(r'\s+', ' ', m.body.strip())
            mm = re.fullmatch(r'return (-?\d+(?:\.\d+)?);', body)
            if mm:
                v = float(mm.group(1))
                return {'mode': 'guaranteed' if v >= 100 else 'fixed', 'percent': v}
            # Rough Stone: "first excavation of an Era" -> fixed chance (its unlock condition needs 0 excavations)
            mf = re.fullmatch(r'return §8G§\.§5!V§\[35\] < \d+ \? (\d+(?:\.\d+)?) : 0;', body)
            if mf: return {'mode': 'fixed', 'percent': float(mf.group(1))}
            mx = re.fullmatch(r'return (.+);', body)
            return {'mode': 'variable', 'expr': mx.group(1) if mx else None, 'cls': k.q}
        k = cl.get(k.parent)
        if k is not None and k.name == '§-+§': break
    return {'mode': 'guaranteed', 'percent': 100.0}  # base class default


def chance_info(c):
    ch = find_chance(c)
    if ch.get('mode') == 'variable' and ch.get('expr'):
        owner = cl[ch.pop('cls')]
        def name_of(tok):
            q = resolve(owner, tok, cl)
            return named.get(q) if q else None
        r = convert(ch['expr'], name_of)
        if r: ch.update(r)
        ch['expr'] = ch['expr']
    ch.pop('cls', None)
    return ch


out = []
for a in res['arts']:
    c = cl.get(a['q'])
    reqs, undec, has_cond = decode(c, a) if c else ([], [], False)
    hint = (a['hint'] or '').strip()
    out.append({
        'order': a['order'], 'kind': 'lore' if a['lore'] else 'quest', 'name': a['name'], 'flavor': a['flavor'].strip(),
        'icon': a['icon'] if a['icon'] in sprites else None, 'icon_name': a['icon'],
        'hint': hint, 'chance': chance_info(c), 'requirements': reqs, 'undecoded_conditions': len(undec),
        'undecoded': undec,
    })
json.dump(out, open(os.path.join(ROOT, 'data', 'artifacts.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
q = [x for x in out if x['kind'] == 'quest']; l = [x for x in out if x['kind'] == 'lore']
print(len(out), 'artifacts:', len(q), 'quest,', len(l), 'lore')
print('no icon:', sum(1 for x in out if not x['icon']), '| with hint:', sum(1 for x in out if x['hint']),
      '| fully decoded:', sum(1 for x in out if x['requirements'] and not x['undecoded_conditions']),
      '| partially:', sum(1 for x in out if x['requirements'] and x['undecoded_conditions']),
      '| nothing decoded:', sum(1 for x in out if not x['requirements']))
