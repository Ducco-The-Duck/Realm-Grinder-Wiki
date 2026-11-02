"""Check the hand-written spell formulas against the game code.

    python -I tools/verify_formulas.py [spell name ...]

Every number in a spell's detail text (data/spells_overview.json: formulas, variable descriptions and the explaining
sentences) must be found in the game code the spell was read from: the spell's own class and the classes that import
it (the production code, the upgrades and the challenges that use the spell). A number may appear in the code as
itself or scaled by one of the unit factors the game uses (percent, ticks per second, minutes, hours). A number that
cannot be found is listed; it was typed from something other than the code, or the game changed since.
"""
import json, os, re, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
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
def importers(cls):
    """the files that import the class (the callers that see it by name)"""
    global _importers
    if _importers is None:
        _importers = {}
        pat = re.compile(r'^\s*import ([^;]+);', re.M)
        for dp, _, fs in os.walk(SCRIPTS):
            for f in fs:
                if not f.endswith('.as'): continue
                p = os.path.join(dp, f)
                for m in pat.finditer(read(p)): _importers.setdefault(m.group(1), []).append(p)
    return _importers.get(cls, [])


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
    spells = json.load(open(os.path.join(ROOT, 'data', 'spells.json'), encoding='utf8'))
    ov = json.load(open(os.path.join(ROOT, 'data', 'spells_overview.json'), encoding='utf8'))['spells']
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


if __name__ == '__main__':
    main(set(sys.argv[1:]))
