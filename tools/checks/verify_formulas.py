"""Check the hand-written spell formulas against the game code.

    python -I tools/checks/verify_formulas.py [spell name ...]
    python -I tools/checks/verify_formulas.py --items [name ...]       (upgrades, researches, challenges)
    python -I tools/checks/verify_formulas.py --mechanics [name ...]   (the Mechanics page)
    python -I tools/checks/verify_formulas.py --buildings              (the Buildings page)

Every number in a spell's detail text (data/handwritten/spells_overview.json: formulas, variable descriptions and the explaining
sentences) must be found in the game code the spell was read from: the spell's own class and the classes that import
it (the production code, the upgrades and the challenges that use the spell). A number may appear in the code as
itself or scaled by one of the unit factors the game uses (percent, ticks per second, minutes, hours). A number that
cannot be found is listed; it was typed from something other than the code, or the game changed since.
"""
import json, os, re, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..'))
SCRIPTS = os.path.join(ROOT, 'out', 'script', 'scripts')
ENC = {'?': '%3F', '<': '%3C', '>': '%3E', ':': '%3A', '"': '%22', '|': '%7C', '*': '%2A'}


def enc(s): return ''.join(ENC.get(c, c) for c in s)
def path_of(cls):
    pkg, _, name = cls.rpartition('.')
    return os.path.join(SCRIPTS, enc(pkg), enc(name) + '.as')


_cache = {}
def read(p):
    if p not in _cache: _cache[p] = open(p, encoding='utf8', errors='replace').read()
    return _cache[p]


_importers = None
_users = None
def importers(cls):
    """the files that use the class: the ones that import it, and the ones that name it (a class in the same package, or in the
    unnamed package, is used without an import). The obfuscator reuses names, so this can include files that mean another class."""
    global _importers, _users
    if _importers is None:
        _importers, _users = {}, {}
        pat = re.compile(r'^\s*import ([^;]+);', re.M)
        tok = re.compile(r'§[^§\n]*§')
        for dp, _, fs in os.walk(SCRIPTS):
            for f in fs:
                if not f.endswith('.as'): continue
                p = os.path.join(dp, f)
                t = read(p)
                for m in pat.finditer(t): _importers.setdefault(m.group(1), []).append(p)
                for sym in set(tok.findall(t)): _users.setdefault(sym, set()).add(p)
    sym = cls.rsplit('.', 1)[-1]
    return sorted(set(_importers.get(cls, [])) | _users.get(sym, set()))


NUM = re.compile(r'(?<![\w§.])-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?')
def code_numbers(text):
    out = set()
    for m in NUM.finditer(text):
        try: out.add(abs(float(m.group())))
        except ValueError: pass
    return out


SCALES = [1, 100, 0.01, 30, 1 / 30, 60, 1 / 60, 3600, 1 / 3600]
def found(x, nums):
    for c in nums:
        if x == c + 1 and x == int(x): return True      # a tier is stored from 0 and shown from 1
        if abs((x - 1) * 100 - c) <= 1e-9 * max(1.0, abs(c)): return True      # a factor the code writes as 1 + 0.01 * c (12 for 1.12)
        for k in SCALES:
            v = c * k
            if v and abs(v - x) <= 1e-9 * max(1.0, abs(x)): return True
    return False


def latex_numbers(s):
    """the numbers a LaTeX / text string states (10^{6} counts as 1000000, the dollar signs are kept out of it)"""
    s = re.sub(r'10\^\{?(\d+)\}?', lambda m: str(10 ** int(m.group(1))), s)
    s = re.sub(r'\[a-zA-Z]+', ' ', s)
    s = re.sub(r'_\{[^}]*\}|_\w', ' ', s)      # subscripts (v_{1}, c_0) are names, not numbers
    return [float(m.group()) for m in re.finditer(r'(?<![\w.])\d+(?:\.\d+)?', s)]


TRIVIAL = {0, 1, 2}


def strings_of(detail):
    """(where, text) of everything a spell detail states"""
    out = []
    def sec(sections, tag):
        for s in sections or []:
            if isinstance(s, str): continue
            out.append((tag + ': ' + s.get('title', ''), s.get('text', '') or ''))
            for f in s.get('formulas', []) or []:
                if isinstance(f, dict):
                    out.append((tag + ': ' + s.get('title', '') + ' formula', f.get('latex', '')))
                    for v in f.get('vars', []): out.append((tag + ': ' + s.get('title', '') + ' variable ' + v[0], v[1]))
            for l in s.get('list', []) or []: out.append((tag + ': ' + s.get('title', ''), str(l)))
    sec(detail.get('sections'), 'detail'); sec(detail.get('tier_sections'), 'tiers')
    return out


def main(only):
    spells = json.load(open(os.path.join(ROOT, 'data', 'derived/spells.json'), encoding='utf8'))
    ov = json.load(open(os.path.join(ROOT, 'data', 'handwritten/spells_overview.json'), encoding='utf8'))['spells']
    total = bad = 0
    for sp in spells:
        name = sp['name']
        if only and name not in only: continue
        if name not in ov or not ov[name].get('detail'): continue
        cls = sp['class']
        files = [path_of(cls)] + importers(cls)
        nums = set()
        for p in files:
            if os.path.exists(p): nums |= code_numbers(read(p))
        miss = []
        for where, text in strings_of(ov[name]['detail']):
            if text.startswith('@'): continue      # the shared penalty formulas
            for x in latex_numbers(text):
                if x in TRIVIAL: continue
                total += 1
                if not found(x, nums): miss.append((where, x))
        bad += len(miss)
        print(f'{name}: {len(files)} code files, {len(nums)} numbers; not found: {len(miss)}')
        for where, x in miss: print(f'    {x:g}   {where}')
    print(f'\n{total} numbers checked, {bad} not found in the spell\'s code')


def item_formulas(it):
    """the formula texts (formulas, variable descriptions) of an upgrade or challenge item"""
    out = []
    fl = list(it.get('formulas') or [])
    for p in it.get('description') or []:
        if isinstance(p, dict): fl += p.get('formulas') or []
    for f in fl:
        if not isinstance(f, dict) or 'latex' not in f: continue
        out.append(f['latex'])
        for v in f.get('vars') or []:
            out.append(v.get('text', '') if isinstance(v, dict) else str(v[1]))
    return out


def main_items(only=()):
    """the same check for the upgrades, the researches and the challenge rewards that carry formulas (the generated ones pass by construction;
    the hand-written tables in the tools are what it is there for)"""
    ups = json.load(open(os.path.join(ROOT, 'data', 'derived/upgrades.json'), encoding='utf8'))
    cls_of = {u['name']: u['class'] for u in ups if u.get('name') and u.get('class')}
    for u in ups:
        if u.get('game_name') and u.get('class'): cls_of.setdefault(u['game_name'], u['class'])
    pages = json.load(open(os.path.join(ROOT, 'data', 'generated/upgrade_pages.json'), encoding='utf8'))
    chal = json.load(open(os.path.join(ROOT, 'data', 'generated/challenges.json'), encoding='utf8'))
    items = [(k, it) for k, lst in pages.items() if isinstance(lst, list) for it in lst if isinstance(it, dict)]
    items += [('challenge', it) for f in chal for it in f['items']]
    for r in json.load(open(os.path.join(ROOT, 'data', 'derived/researchs.json'), encoding='utf8')):
        if r.get('name') and r.get('class'): cls_of.setdefault(r['name'], r['class'])
    def research_items(x):
        if isinstance(x, dict):
            if 'code' in x and 'formulas' in x: yield x
            else:
                for v in x.values(): yield from research_items(v)
        elif isinstance(x, list):
            for v in x: yield from research_items(v)
    items += [('research', it) for it in research_items(json.load(open(os.path.join(ROOT, 'data', 'generated/research.json'), encoding='utf8')))]
    total = bad = skipped = 0
    for kind, it in items:
        texts = item_formulas(it)
        if not texts: continue
        name = it.get('game_name') or it['name']
        cls = cls_of.get(name) or cls_of.get(it['name'])
        if not cls:
            skipped += 1; continue
        if only and name not in only and it['name'] not in only: continue
        files = [path_of(cls)] + importers(cls)
        nums = set()
        for p in files:
            if os.path.exists(p): nums |= code_numbers(read(p))
        miss = []
        for t in texts:
            for x in latex_numbers(t):
                if x in TRIVIAL: continue
                total += 1
                if not found(x, nums): miss.append(x)
        if miss:
            bad += len(miss)
            print(f'{kind}: {it["name"]}: not found: ' + ', '.join(f'{x:g}' for x in miss))
    print(f'\n{total} numbers checked in upgrade, research and challenge formulas, {bad} not found ({skipped} items with formulas have no class to check against)')
    return bad


def fn_text(text, fn):
    """the source of one function of a class file (from its line to the next member at the same indent)"""
    lines = text.split('\n')
    for i, l in enumerate(lines):
        if f'function {fn}(' in l:
            j = i + 1
            while j < len(lines) and not re.match(r'^      (public|private|protected|override|internal|static)\b', lines[j]): j += 1
            return '\n'.join(lines[i:j])
    return ''


def mechanic_strings(m):
    """(where, text) of everything a mechanic of data/handwritten/unlocks.json states"""
    out = [('unlock', t) for t in m.get('unlock', [])]
    for s in m.get('sections', []):
        t = s.get('title', '')
        out += [(t, s.get('text', '') or ''), (t + ' (after)', s.get('after', '') or '')]
        for l in s.get('lists', []) or []:
            out += [(t + ' list', l.get('title', ''))] + [(t + ' list', x) for x in l.get('items', [])]
        for f in s.get('formulas', []) or []:
            out.append((t + ' formula', f.get('latex', '')))
            for v in f.get('vars', []): out.append((t + ' variable ' + v[0], v[1]))
    return out


def main_mechanics(only=()):
    """the same check for the mechanics of the Mechanics page that name their code ("source": class, or class::function for one function of it):
    every number of the mechanic must be in that code"""
    d = json.load(open(os.path.join(ROOT, 'data', 'handwritten/unlocks.json'), encoding='utf8'))
    total = bad = 0
    for m in d['mechanics']:
        if not m.get('source') or (only and m['name'] not in only): continue
        nums = set()
        for src in m['source']:
            cls, _, fn = src.partition('::')
            p = path_of(cls)
            if not os.path.exists(p):
                print(f"{m['name']}: source {src} not found"); bad += 1; continue
            nums |= code_numbers(fn_text(read(p), fn) if fn else read(p))
        miss = []
        for where, text in mechanic_strings(m):
            for x in latex_numbers(text):
                if x in TRIVIAL: continue
                total += 1
                if not found(x, nums): miss.append((where, x))
        bad += len(miss)
        print(f"{m['name']}: {len(m['source'])} code sources, {len(nums)} numbers; not found: {len(miss)}")
        for where, x in miss: print(f'    {x:g}   {where}')
    print(f'\n{total} numbers checked in the mechanics, {bad} not found in their code')
    return bad


def main_buildings():
    """the same check for the Buildings page: every number of data/handwritten/buildings.json must be in the code it names ("source")"""
    d = json.load(open(os.path.join(ROOT, 'data', 'handwritten/buildings.json'), encoding='utf8'))
    nums = set()
    for src in d['source']:
        cls, _, fn = src.partition('::')
        nums |= code_numbers(fn_text(read(path_of(cls)), fn) if fn else read(path_of(cls)))
    texts = [d['production']['text'], d['hall']['text'], d['cost']['text']] + [r['text'] for r in d['cost']['reductions']]
    for sec in (d['hall'], d['cost']):
        for f in sec.get('formulas', []) + ([d['cost']['m0']] + list(d['cost']['multiplier'].values()) if sec is d['cost'] else []):
            texts.append(f['latex']); texts += [v[1] for v in f.get('vars', [])] + ([f['note']] if f.get('note') else [])
    total = bad = 0
    for t in texts:
        for x in latex_numbers(t):
            if x in TRIVIAL: continue
            total += 1
            if not found(x, nums): bad += 1; print(f'    {x:g}   {t[:70]}')
    print(f'{total} numbers checked on the Buildings page, {bad} not found in their code')
    return bad


def main_costs():
    """the costs shown on the pages (tools/pages/costs.py): every coin and Faction Coin amount of an upgrade must be a number its own class writes"""
    sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pages')]
    import costs
    pages = json.load(open(os.path.join(ROOT, 'data', 'generated/upgrade_pages.json'), encoding='utf8'))
    cls = {u['name']: u['class'] for u in json.load(open(os.path.join(ROOT, 'data', 'derived/upgrades.json'), encoding='utf8')) if u.get('class') and u.get('name')}
    total = bad = 0
    for pg in ('secret',):      # the pages that show costs so far
        for it in pages[pg]:
            nums = code_numbers(read(path_of(cls[it['name']])))
            for coins, fcs in costs.upgrade_cost(cls[it['name']]):
                for x in [coins] + [v for _, v in fcs]:
                    if not x: continue
                    total += 1
                    if x not in nums: bad += 1; print(f"    {x:g}   {it['name']}")
    print(f'{total} cost amounts checked on the pages, {bad} not found in their class')
    return bad


if __name__ == '__main__':
    args = set(sys.argv[1:])
    if '--costs' in args: main_costs(); sys.exit(0)
    if '--buildings' in args: main_buildings(); sys.exit(0)
    if '--mechanics' in args: main_mechanics(args - {'--mechanics'})
    elif '--items' in args: main_items(args - {'--items'})
    else: main(args)
