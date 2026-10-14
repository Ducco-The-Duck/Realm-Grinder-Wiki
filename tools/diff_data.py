"""What did a rebuild change? Compares the working-copy data files with the last committed ones.

    python -I tools/diff_data.py            # added / removed / changed items, per file
    python -I tools/diff_data.py -v         # also the old and new value of each changed field
    python -I tools/diff_data.py --ref v4.3.14   # compare with another commit / tag instead of HEAD

Items are matched by a stable key (trophy id, artifact name, research code, challenge faction + name, upgrade id).
Hand-written overrides in the exporters (formulas, notes, corrections) are checked too: an override whose item
changed or vanished is listed, since its hand-written text may be stale. Read-only; nothing is rewritten.
"""
import ast, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
VERBOSE = '-v' in sys.argv
REF = sys.argv[sys.argv.index('--ref') + 1] if '--ref' in sys.argv else 'HEAD'
IGNORE = {'order'}          # registry order shifts whenever something is inserted; not a content change


def items_trophies(d):    return {x['id']: x for x in d}
def items_artifacts(d):   return {x['name']: x for x in d}
def items_research(d):    return {x['code']: x for x in d}
def items_challenges(d):  return {f"{f['name']}: {i['name']}": i for f in d for i in f['items']}
def items_upgrades(d):    return {f"{sec}: {u['name']} ({u['id']})": u for sec, lst in d.items() for u in lst}


FILES = [('trophies.json', items_trophies), ('artifacts.json', items_artifacts), ('research.json', items_research),
         ('challenges.json', items_challenges), ('upgrade_pages.json', items_upgrades)]


def committed(name):
    r = subprocess.run(['git', 'show', f'{REF}:data/{name}'], cwd=ROOT, capture_output=True)
    return json.loads(r.stdout.decode('utf8')) if r.returncode == 0 else None


def short(v, n=110):
    s = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
    return s if len(s) <= n else s[:n - 1] + '…'


def short_pair(x, y, n=100):
    """Both values, trimmed around the first place they differ."""
    sx = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)
    sy = y if isinstance(y, str) else json.dumps(y, ensure_ascii=False)
    p = 0
    while p < min(len(sx), len(sy)) and sx[p] == sy[p]:
        p += 1
    lo = max(0, p - 25)
    cut = lambda s: ('…' if lo else '') + s[lo:lo + n] + ('…' if len(s) > lo + n else '')
    return cut(sx), cut(sy)


def changed_fields(a, b):
    return [k for k in sorted(set(a) | set(b)) if k not in IGNORE and a.get(k) != b.get(k)]


def override_names():
    """Item names the exporters special-case (dict keys / sets / `name == '...'` tests)."""
    found = {}
    for fn in ('export_upgrades.py', 'export_challenges.py', 'export_research.py', 'export_artifacts.py', 'export_trophies.py',
               'misc_manual.py', 'alleg_manual.py', 'alleg_manual_family.py'):
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            continue
        tree = ast.parse(open(p, encoding='utf8').read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id.isupper() \
                    and isinstance(node.value, (ast.Dict, ast.Set)):
                elts = node.value.keys if isinstance(node.value, ast.Dict) else node.value.elts
                for e in elts:
                    if isinstance(e, ast.Constant) and isinstance(e.value, str):
                        found.setdefault(e.value, set()).add(f'{fn}:{node.targets[0].id}')
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'update' \
                    and node.args and isinstance(node.args[0], ast.Dict):          # FORMULAS.update({...})
                for e in node.args[0].keys:
                    if isinstance(e, ast.Constant) and isinstance(e.value, str):
                        found.setdefault(e.value, set()).add(f'{fn}:update')
            if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name) and node.left.id == 'name' \
                    and len(node.comparators) == 1 and isinstance(node.comparators[0], ast.Constant) \
                    and isinstance(node.comparators[0].value, str):
                found.setdefault(node.comparators[0].value, set()).add(f'{fn}:name ==')
    return found


touched, names_old, names_now, anything = set(), set(), set(), False


def names_of(items):
    out = set()
    for k, v in items.items():
        if isinstance(v, dict):
            out |= {v.get('name'), v.get('game_name')}
    return out - {None, ''}


for fname, keyer in FILES:
    path = os.path.join(ROOT, 'data', fname)
    old, new = committed(fname), (json.load(open(path, encoding='utf8')) if os.path.exists(path) else None)
    if old is None or new is None:
        print(f'{fname}: not available ({"no committed version" if old is None else "no working copy"})')
        continue
    a, b = keyer(old), keyer(new)
    added, removed = sorted(set(b) - set(a)), sorted(set(a) - set(b))
    chg = [(k, changed_fields(a[k], b[k])) for k in sorted(set(a) & set(b))]
    chg = [(k, f) for k, f in chg if f]
    names_old |= names_of(a)
    names_now |= names_of(b)
    touched |= names_of({k: a[k] for k in removed}) | names_of({k: a[k] for k, _ in chg})
    if not (added or removed or chg):
        print(f'{fname}: no changes ({len(b)} items)')
        continue
    anything = True
    print(f'{fname}: {len(b)} items; {len(added)} added, {len(removed)} removed, {len(chg)} changed')
    for k in added[:40]:
        print('   + ', k)
    for k in removed[:40]:
        print('   - ', k)
    for k, f in chg[:60]:
        print('   ~ ', k, '->', ', '.join(f))
        if VERBOSE:
            for field in f:
                x, y = short_pair(a[k].get(field), b[k].get(field))
                print('        ', field + ':', x, '=>', y)
    for lst, limit, label in ((added, 40, 'added'), (removed, 40, 'removed'), (chg, 60, 'changed')):
        if len(lst) > limit:
            print(f'   ... and {len(lst) - limit} more {label} (use -v or git diff)')

print('\nHand-written overrides whose item changed or is gone:')
rows = []
for n, w in sorted(override_names().items()):
    if n not in names_old:
        continue                                  # not an item name that ever matched (a text fix, a skip list, ...)
    if n not in names_now:
        rows.append((n, w, 'no item with this name any more'))
    elif n in touched:
        rows.append((n, w, 'item changed'))
for n, w, why in rows:
    print('   ', n, '<-', ', '.join(sorted(w)), f'({why})')
if not rows:
    print('    none')
if not anything:
    print('\nNo data changes since', REF)
