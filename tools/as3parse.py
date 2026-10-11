"""Lightweight structural parser for the deobfuscated ActionScript in out/script/scripts.

parse_all() -> {qualified_class_name: Cls}
Each Cls has: pkg, name, parent (qualified), imports {short: qualified}, ids [str],
statics {name: raw_value}, ctor [(field, index|None, raw_value)], methods [Method].
"""
import os, re, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'out', 'script', 'scripts')

class Method:
    def __init__(self, name, kind, mods, ret, params, body):
        self.name, self.kind, self.mods, self.ret, self.params, self.body = name, kind, mods, ret, params, body

class Cls:
    def __init__(self):
        self.pkg = ''; self.name = ''; self.parent = None; self.imports = {}
        self.ids = []; self.parent_raw = None; self.statics = {}; self.ctor = []; self.methods = []
    @property
    def q(self):
        return f'{self.pkg}.{self.name}' if self.pkg else self.name

IDENT = r'(?:§[^§]*§|[A-Za-z_]\w*)'
RE_PKG = re.compile(r'^package[ \t]*([^\n{]*?)[ \t]*$', re.M)
RE_IMPORT = re.compile(r'^\s*import\s+(.+?);\s*$', re.M)
RE_CLASS = re.compile(r'^\s*(?:public\s+)?(?:final\s+)?(?:dynamic\s+)?(class|interface)\s+(' + IDENT + r')(?:\s+extends\s+([^\s{]+))?', re.M)
RE_FUNC = re.compile(r'^(\s+)((?:(?:override|public|private|protected|internal|static|final)\s+)*)function\s+(?:(get|set)\s+)?(' + IDENT + r')\s*\(([^)]*)\)\s*(?::\s*([^\s{]+))?\s*$', re.M)
RE_STATIC = re.compile(r'^\s+(?:public|private|protected|internal)\s+static\s+(?:var|const)\s+(' + IDENT + r')(?::[^=;\s]+)?\s*(?:=\s*(.+?))?;\s*$', re.M)
RE_ASSIGN = re.compile(r'^\s+(' + IDENT + r'(?:\.' + IDENT + r')*)(?:\[(\d+)\])?\s*=\s*(.+?);\s*$')


def _match_brace(text, i):
    """text[i] == '{' -> index just past matching '}' (strings aware)."""
    depth = 0; n = len(text); instr = None
    while i < n:
        c = text[i]
        if instr:
            if c == '\\': i += 1
            elif c == instr: instr = None
        elif c == '§':
            j = text.find('§', i + 1)
            if j > 0: i = j
        elif c in '"\'': instr = c
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return i + 1
        i += 1
    return n


def parse_file(path):
    t = open(path, encoding='utf8', errors='replace').read()
    c = Cls()
    m = RE_PKG.search(t); c.pkg = m.group(1) if m else ''
    for im in RE_IMPORT.finditer(t):
        q = im.group(1); c.imports[q.rsplit('.', 1)[-1]] = q
    m = RE_CLASS.search(t)
    if not m: return None
    c.name = m.group(2)
    c.parent_raw = m.group(3)
    body_start = t.index('{', m.end())
    body = t[body_start:_match_brace(t, body_start)]
    for sm in RE_STATIC.finditer(body):
        c.statics[sm.group(1)] = sm.group(2)
    # methods
    pos = 0
    for fm in RE_FUNC.finditer(body):
        if fm.start() < pos: continue
        bs = body.find('{', fm.end())
        if bs < 0: continue
        be = _match_brace(body, bs)
        pos = be
        mods = fm.group(2).split()
        meth = Method(fm.group(4), fm.group(3) or 'method', mods, fm.group(6), fm.group(5), body[bs + 1:be - 1])
        c.methods.append(meth)
        if fm.group(4) == c.name:  # constructor
            for line in meth.body.split('\n'):
                am = RE_ASSIGN.match(line)
                if am: c.ctor.append((am.group(1), am.group(2), am.group(3)))
    ids = c.statics.get('ids')
    if ids: c.ids = re.findall(r'"([^"]+)"', ids)
    return c


def parse_all():
    out = {}
    for f in glob.glob(os.path.join(SRC, '**', '*.as'), recursive=True):
        c = parse_file(f)
        if c: out[c.q] = c
    for c in out.values():
        p = c.parent_raw
        if not p: continue
        cands = [c.imports.get(p), f'{c.pkg}.{p}' if c.pkg else None, p]
        c.parent = next((x for x in cands if x and x in out), c.imports.get(p, p))
    return out

def resolve(c, short, cl):
    """Resolve a short class name used inside class c to a qualified key in cl (or None)."""
    for x in (c.imports.get(short), f'{c.pkg}.{short}' if c.pkg else None, short):
        if x and x in cl: return x
    return None


if __name__ == '__main__':
    cl = parse_all()
    print(len(cl), 'classes;', sum(1 for c in cl.values() if c.ids), 'with ids')
