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
  return {{ named: named, arts: arts }};
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


def decode(c, art):
    meth = next((m for m in c.methods if m.name == '§ !3§'), None)
    if meth is None: return [], [], False
    body = re.sub(r'\s+', ' ', meth.body.strip())
    m = re.fullmatch(r'return (.+);', body)
    if not m: return [], [body[:200]], True
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
    return reqs, undec, True


def _one(s, c, art, reqs, undec, ref_name):
    s = s.strip()
    if s == '§-6§': return
    thr = art['threshold']
    m = re.fullmatch(G + r'§1!5§ >= §\?"M§', s)
    if m: reqs.append(f'Make {int(thr):,} excavations'); return
    m = re.fullmatch(G + r'§1!5§ >= (\d+)', s)
    if m: reqs.append(f'Make {int(m.group(1)):,} excavations'); return
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
        if n: reqs.append(f'Requires {n[0]} "{n[1]}"'); return
    m = re.fullmatch(r'\(?((?:' + G + r'§7d§\(§[^§]*§\.id\)(?: \|\| )?)+)\)?', s)
    if m:
        toks = re.findall(r'(§[^§]*§)\.id', m.group(1))
        ns = [ref_name(t) for t in toks]
        if all(ns): reqs.append('Requires one of: ' + ', '.join(f'{k} "{v}"' for k, v in ns)); return
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
            return {'mode': 'variable'}
        k = cl.get(k.parent)
        if k is not None and k.name == '§-+§': break
    return {'mode': 'guaranteed', 'percent': 100.0}  # base class default


out = []
for a in res['arts']:
    c = cl.get(a['q'])
    reqs, undec, has_cond = decode(c, a) if c else ([], [], False)
    hint = (a['hint'] or '').strip()
    out.append({
        'order': a['order'], 'kind': 'lore' if a['lore'] else 'quest', 'name': a['name'], 'flavor': a['flavor'].strip(),
        'icon': a['icon'] if a['icon'] in sprites else None, 'icon_name': a['icon'],
        'hint': hint, 'chance': find_chance(c), 'requirements': reqs, 'undecoded_conditions': len(undec),
        'undecoded': undec,
    })
json.dump(out, open(os.path.join(ROOT, 'data', 'artifacts.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
q = [x for x in out if x['kind'] == 'quest']; l = [x for x in out if x['kind'] == 'lore']
print(len(out), 'artifacts:', len(q), 'quest,', len(l), 'lore')
print('no icon:', sum(1 for x in out if not x['icon']), '| with hint:', sum(1 for x in out if x['hint']),
      '| fully decoded:', sum(1 for x in out if x['requirements'] and not x['undecoded_conditions']),
      '| partially:', sum(1 for x in out if x['requirements'] and x['undecoded_conditions']),
      '| nothing decoded:', sum(1 for x in out if not x['requirements']))
