"""Transpile the game's ActionScript classes to a single JavaScript module (data/engine.js).

Scope: entity classes (upgrades, spells, buildings, ...), their ancestors, and the closure of helper
classes/members they reference.  Library packages (starling, feathers, flash, playfab...) are left
unresolved; calling into them raises at runtime.

    python -I tools/as3js.py
"""
import json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'pylib'))
from as3parse import parse_all, resolve, ROOT
from build_data import kind_of

OUT = os.path.join(ROOT, 'data', 'engine.js')

TOKEN = re.compile(r'''
    (?P<ws>\s+)
  | (?P<mid>§[^§]*§)
  | (?P<str>"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')
  | (?P<num>0x[0-9a-fA-F]+|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)
  | (?P<id>[A-Za-z_$][\w$]*)
  | (?P<op>>>>=|\.\.\.|===|!==|>>>|<<=|>>=|&&=|\|\|=|==|!=|<=|>=|&&|\|\||\+\+|--|\+=|-=|\*=|/=|%=|&=|\|=|\^=|<<|>>|::|\.\.|\.<|.)
''', re.X | re.S)

LIB_PKG = re.compile(r'^(starling|feathers|flash|com|mx|fl|adobe|gestouch|org|net)\b')
JS_RESERVED = {'var', 'let', 'function', 'class', 'new', 'delete', 'typeof', 'void', 'in', 'of', 'instanceof',
               'this', 'super', 'null', 'true', 'false', 'if', 'else', 'for', 'while', 'do', 'switch', 'case',
               'default', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'with', 'const',
               'each', 'is', 'as', 'get', 'set', 'static', 'override', 'public', 'private', 'protected',
               'internal', 'final', 'import', 'package', 'extends', 'implements', 'interface', 'native',
               'undefined', 'NaN', 'Infinity', 'arguments'}


class Names:
    def __init__(self):
        self.m = {}; self.used = set()

    def get(self, tok, prefix='_'):
        k = (prefix, tok)
        if k in self.m: return self.m[k]
        base = re.sub(r'[^A-Za-z0-9]+', '_', tok.strip('§')).strip('_') or 'x'
        n = prefix + base; i = 2
        while n in self.used:
            n = f'{prefix}{base}_{i}'; i += 1
        self.used.add(n); self.m[k] = n
        return n


NM = Names()


def lex(src):
    out = []
    for m in TOKEN.finditer(src):
        k = m.lastgroup
        if k == 'ws': continue
        out.append((k, m.group()))
    return out


class Unsupported(Exception):
    pass


def match_close(toks, i, open_='(', close=')'):
    d = 0
    for j in range(i, len(toks)):
        if toks[j][1] == open_: d += 1
        elif toks[j][1] == close:
            d -= 1
            if d == 0: return j
    raise Unsupported('unbalanced')


def strip_type(toks, i):
    """toks[i] is ':' ; return index after the type expr."""
    j = i + 1
    if toks[j][1] == '*': return j + 1
    if toks[j][0] not in ('mid', 'id'): raise Unsupported('type')
    j += 1
    while j + 1 < len(toks) and toks[j][1] == '.' and toks[j + 1][0] in ('mid', 'id'):
        j += 2
    if j < len(toks) and toks[j][1] == '.<':
        k = match_close(toks, j, '.<', '>') if False else None
        d = 0
        while j < len(toks):
            if toks[j][1] == '.<': d += 1
            elif toks[j][1] == '>': d -= 1
            elif toks[j][1] == '>>': d -= 2
            j += 1
            if d <= 0: break
    return j


class Ctx:
    def __init__(self, cl, c, members, classmap):
        self.cl, self.c, self.members, self.classmap = cl, c, members, classmap


def tr(src, ctx, params=''):
    """Translate a function body / expression / param list into JS text."""
    toks = lex(src)
    # pass 1: strip types / AS-only syntax
    out = []; i = 0; locals_ = set()
    for p in re.findall(r'(§[^§]*§|[A-Za-z_]\w*)\s*:', params): locals_.add(p)
    while i < len(toks):
        k, v = toks[i]
        if v in ('§§push', '§§pop', '§§goto', '§§dup', '§§swap') or (k == 'mid' and v.startswith('§§')):
            raise Unsupported('stack ops')
        if v in ('var', 'const') and i + 1 < len(toks) and toks[i + 1][0] in ('mid', 'id'):
            locals_.add(toks[i + 1][1])
            out.append(('id', 'var')); out.append(toks[i + 1]); i += 2
            if i < len(toks) and toks[i][1] == ':': i = strip_type(toks, i)
            continue
        if v == 'catch' and toks[i + 1][1] == '(':
            locals_.add(toks[i + 2][1]); out.append(toks[i]); out.append(toks[i + 1]); out.append(toks[i + 2]); i += 3
            if toks[i][1] == ':': i = strip_type(toks, i)
            continue
        if v == 'function':
            # anonymous / nested function: strip param types + return type
            out.append(toks[i]); i += 1
            if toks[i][0] in ('mid', 'id') and toks[i][1] != '(': out.append(toks[i]); i += 1
            assert toks[i][1] == '('
            j = match_close(toks, i)
            seg = toks[i:j + 1]; q = 0; clean = []
            while q < len(seg):
                if seg[q][1] == ':' : q = strip_type(seg, q); continue
                if seg[q][0] in ('mid', 'id') and seg[q][1] not in ('=',): locals_.add(seg[q][1])
                clean.append(seg[q]); q += 1
            out.extend(clean); i = j + 1
            if i < len(toks) and toks[i][1] == ':': i = strip_type(toks, i)
            continue
        if v == 'as' and k == 'id':
            i = strip_type(toks, i); continue
        if v == 'is' and k == 'id':
            out.append(('id', 'instanceof')); i += 1; continue
        if v == 'new' and i + 1 < len(toks) and toks[i + 1][1] == '.<' or (v == 'new' and toks[i + 1][1] == '<'):
            # new <T>[...]
            j = i + 1; d = 0
            while j < len(toks):
                if toks[j][1] in ('.<', '<'): d += 1
                elif toks[j][1] == '>': d -= 1
                j += 1
                if d == 0: break
            i = j; continue
        if v == '.<':
            d = 0; j = i
            while j < len(toks):
                if toks[j][1] == '.<': d += 1
                elif toks[j][1] == '>': d -= 1
                elif toks[j][1] == '>>': d -= 2
                j += 1
                if d <= 0: break
            i = j; continue
        if v == 'for' and i + 2 < len(toks) and toks[i + 1][1] == 'each':
            # for each (var x[:T] in expr)  ->  for (var x of __vals(expr))
            j = i + 2
            end = match_close(toks, j)
            seg = toks[j + 1:end]
            seg2 = []; q = 0
            while q < len(seg):
                if seg[q][1] == ':': q = strip_type(seg, q); continue
                seg2.append(seg[q]); q += 1
            if not seg2 or seg2[0][1] != 'var':
                seg2 = [('id', 'var')] + seg2
            idx = next(n for n, t in enumerate(seg2) if t[1] == 'in' and t[0] == 'id')
            locals_.add(seg2[1][1])
            out += [('id', 'for'), ('op', '(')] + seg2[:idx] + [('id', 'of'), ('id', '__vals'), ('op', '(')] + seg2[idx + 1:] + [('op', ')'), ('op', ')')]
            i = end + 1; continue
        if v in ('..',) or (v == '@' and k == 'op'):
            raise Unsupported('e4x')
        out.append(toks[i]); i += 1
    toks = out

    # pass 2: identifier resolution
    c = ctx.c
    res = []
    n = len(toks)
    for i, (k, v) in enumerate(toks):
        prev = toks[i - 1][1] if i else ''
        nxt = toks[i + 1][1] if i + 1 < n else ''
        if k == 'mid' or (k == 'id' and v not in JS_RESERVED and v not in ('of',)):
            is_prop = prev == '.'
            is_key = nxt == ':' and prev in ('{', ',') and not is_prop
            if is_prop or is_key:
                res.append(NM.get(v) if k == 'mid' else v)
                continue
            if v in locals_:
                res.append(NM.get(v) if k == 'mid' else v)
                continue
            if k == 'id' and v in ('loop0', 'loop1') or re.fullmatch(r'loop\d+', v):
                res.append(v); continue
            # member of this class (or ancestor)
            kind = ctx.members.get(v)
            if kind == 'static':
                res.append(ctx.classmap[c.q] + '.' + (NM.get(v) if k == 'mid' else v)); continue
            if kind == 'inst':
                res.append('this.' + (NM.get(v) if k == 'mid' else v)); continue
            q = resolve(c, v, ctx.cl)
            if q and q in ctx.classmap:
                res.append(ctx.classmap[q]); continue
            res.append(NM.get(v) if k == 'mid' else v)
            continue
        res.append(v)
    # re-join with spaces; fix `. <` artefacts not expected
    return ' '.join(res)


def member_table(c, cl):
    """name -> 'static' | 'inst' for c and ancestors."""
    t = {}
    chain = []; x = c; seen = set()
    while x and x.q not in seen:
        chain.append(x); seen.add(x.q); x = cl.get(x.parent)
    for a in reversed(chain):
        for v in a.vars:
            t[v['name']] = 'static' if v['static'] else 'inst'
        for m in a.methods:
            if m.name == a.name: continue
            t[m.name] = 'static' if 'static' in m.mods else 'inst'
    return t


LITERAL = re.compile(r'-?(?:\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+)|"(?:[^"\\]|\\.)*"|true|false|null|undefined|NaN|0x[0-9a-fA-F]+')
SUPER_CALL = re.compile(r'(?<![.\w])super\s*\(')
REF = re.compile(r'(§[^§]*§)\.(§[^§]*§|\w+)')


def build():
    cl = parse_all()
    ents = {q for q, c in cl.items() if kind_of(c, cl) and c.name not in
            ('§`6§', '§#!`§', '§84§', '§`!;§', '§&!_§')}
    # include entity ancestors
    include = {}  # q -> None (all members) | set(member names)
    def game_class(q):
        c = cl[q]
        return not c.pkg or not LIB_PKG.match(c.pkg)

    def add_all(q):
        while q and q in cl and include.get(q, 0) is not None and game_class(q):
            include[q] = None
            q = cl[q].parent
    for q in ents: add_all(q)
    for q, c in cl.items():  # base classes
        if c.name in ('§`6§', '§#!`§', '§84§', '§`!;§', '§&!_§'): add_all(q)

    byname = collections.defaultdict(list)
    for q, c in cl.items(): byname[c.name].append(q)

    for q, c in cl.items():
        if c.name in ('§9!A§', '§8G§'): add_all(q)
    work = list(include)
    done_members = set()
    def need(q, mem=None):
        if q not in cl or not game_class(q): return
        if mem is None:
            if include.get(q, 0) is not None:
                include[q] = None; work.append(q)
            return
        if include.get(q, 0) is None: return
        s = include.setdefault(q, set())
        if mem not in s:
            s.add(mem); work.append((q, mem))
    # initial pass handled by loop below
    queue = [(q, None) for q in list(include)]
    visited = set()
    while queue:
        q, mem = queue.pop()
        if (q, mem) in visited: continue
        visited.add((q, mem))
        c = cl[q]
        bodies = []
        if mem is None:
            bodies = [m.body for m in c.methods] + [v['init'] or '' for v in c.vars]
            need(c.parent) if c.parent else None
            if c.parent in cl and (c.parent, None) not in visited: queue.append((c.parent, None)); include.setdefault(c.parent, None)
        else:
            bodies = [m.body for m in c.methods if m.name == mem] + [v['init'] or '' for v in c.vars if v['name'] == mem]
        for body in bodies:
            for a, b in REF.findall(body):
                tq = resolve(c, a, cl)
                if tq and game_class(tq):
                    if include.get(tq, 0) is None: continue
                    include.setdefault(tq, set())
                    if isinstance(include[tq], set): include[tq].add(b)
                    queue.append((tq, b))
            for m in re.finditer(r'\bnew\s+(§[^§]*§)', body):
                tq = resolve(c, m.group(1), cl)
                if tq and game_class(tq) and (tq, None) not in visited:
                    include[tq] = None; queue.append((tq, None))
            # bare same-class static/instance calls
            for m in re.finditer(r'(?<![.\w§])(§[^§]*§)\s*\(', body):
                b = m.group(1)
                if any(x.name == b for x in c.methods) and isinstance(include.get(q, 0), set) and b not in include[q]:
                    include[q].add(b); queue.append((q, b))
            for m in re.finditer(r'(?<![.\w§])(§[^§]*§)(?!\s*\()', body):
                b = m.group(1)
                if isinstance(include.get(q, 0), set) and (any(v['name'] == b for v in c.vars)) and b not in include[q]:
                    include[q].add(b); queue.append((q, b))
            # imported class used as a bare identifier (e.g. Class.id handled above, casts etc. ignored)
    return cl, include


def main():
    cl, include = build()
    # class order: parents first
    order = []; seen = set()
    def visit(q):
        if q in seen or q not in include: return
        seen.add(q)
        p = cl[q].parent
        if p in include: visit(p)
        order.append(q)
    for q in sorted(include): visit(q)
    classmap = {q: NM.get(cl[q].name, 'K') for q in order}

    report = {'classes': len(order), 'members_ok': 0, 'members_failed': [], 'static_init_failed': []}
    lines = []
    statics_init = []
    import quickjs
    qc = quickjs.Context()

    def compiles(js):
        try:
            qc.eval('(function(){ ' + js + ' })')
            return None
        except Exception as e:
            return str(e)[:160]

    for q in order:
        c = cl[q]; members = member_table(c, cl)
        ctx = Ctx(cl, c, members, classmap)
        full = include[q]
        K = classmap[q]
        ext = f' extends {classmap[c.parent]}' if c.parent in classmap else ' extends __Base'
        body = []; fields = []; defaults = []
        for v in c.vars:
            if full is not None and v['name'] not in full: continue
            nm = NM.get(v['name']) if v['name'].startswith('§') else v['name']
            if v['static']:
                if v['init']:
                    try:
                        js = tr(v['init'], ctx)
                        err = compiles('return (' + js + ');')
                        if err: raise Unsupported(err)
                        statics_init.append((q, f'Object.defineProperty({K}, {json.dumps(nm)}, {{value: {js}, writable: true, configurable: true, enumerable: true}});'))
                    except Unsupported as e:
                        report['static_init_failed'].append([q, v['name'], str(e)])
                else:
                    statics_init.append((q, f'Object.defineProperty({K}, {json.dumps(nm)}, {{value: undefined, writable: true, configurable: true, enumerable: true}});'))
            else:
                init = {'int': '0', 'uint': '0', 'Number': 'NaN', 'Boolean': 'false'}.get(v['type'], 'null')
                explicit = False
                defaults.append(f'this.{nm} = {init};')
                if v['init']:
                    try:
                        js = tr(v['init'], ctx)
                        if compiles('return (' + js + ');'): raise Unsupported('init')
                        init = js
                        if LITERAL.fullmatch(v['init'].strip()):
                            defaults[-1] = f'this.{nm} = {js};'   # slot default (constant initialiser)
                        else:
                            explicit = True
                    except Unsupported:
                        init = 'undefined'
                if explicit: fields.append(f'this.{nm} = {init};')
        ctor_present = False
        for m in c.methods:
            if full is not None and m.name not in full and m.name != c.name: continue
            is_ctor = m.name == c.name
            nm = '_ctor' if is_ctor else (NM.get(m.name) if m.name.startswith('§') else m.name)
            params = m.params
            plist = []
            for part in [p for p in re.split(r',(?![^(]*\))', params) if p.strip()]:
                part = part.strip()
                if part.startswith('...'):
                    plist.append('...' + (NM.get(part[3:].split(':')[0].strip()) if part[3:].lstrip().startswith('§') else part[3:].split(':')[0].strip())); continue
                pm = re.match(r'(§[^§]*§|[A-Za-z_]\w*)\s*(?::\s*[^=]+?)?\s*(?:=\s*(.+))?$', part)
                if not pm: plist.append('p'); continue
                pn = NM.get(pm.group(1)) if pm.group(1).startswith('§') else pm.group(1)
                if pm.group(2):
                    try: plist.append(f'{pn} = {tr(pm.group(2), ctx)}')
                    except Unsupported: plist.append(pn)
                else: plist.append(pn)
            prefix = 'static ' if 'static' in m.mods else ''
            kind = {'get': 'get ', 'set': 'set '}.get(m.kind, '')
            try:
                js = tr(m.body, ctx, params)
                if is_ctor:
                    has_super = bool(SUPER_CALL.search(js))
                    js = SUPER_CALL.sub('super._ctor(', js)
                    js = f'this.__f_{K}(); ' + ('' if has_super else 'super._ctor(); ') + js
                src = f'  {prefix}{kind}{nm}({", ".join(plist)}) {{ {js} }}'
                err = compiles('class _T extends Object { ' + src + ' }')
                if err: raise Unsupported(err)
                report['members_ok'] += 1
                body.append(src)
                if is_ctor: ctor_present = True
            except (Unsupported, AssertionError, StopIteration, IndexError) as e:
                report['members_failed'].append([q, m.name, str(e)[:120]])
                if not is_ctor:
                    body.append(f'  {prefix}{kind}{nm}({", ".join(plist)}) {{ throw new Error("untranslated: {m.name}"); }}')
        if not ctor_present:
            body.append(f'  _ctor(...a) {{ this.__f_{K}(); super._ctor(...a); }}')
        body.append(f'  __f_{K}() {{ ' + ' '.join(fields) + ' }')
        body.append(f'  __d() {{ super.__d(); ' + ' '.join(defaults) + ' }')
        lines.append(f'class {K}{ext} {{\n' + '\n'.join(body) + '\n}')
        lines.append(f'__reg({json.dumps(q, ensure_ascii=False)}, {K}, {json.dumps(c.ids)});')

    with open(os.path.join(HERE, 'engine_runtime.js'), encoding='utf8') as f:
        runtime = f.read()
    names = {v: k[1] for k, v in NM.m.items()}
    out = ['// GENERATED by tools/as3js.py - do not edit', runtime]
    # forward-declare classes via var hoisting trick: class declarations are TDZ-bound, so define in order.
    out += lines
    out.append('// ---- static initialisers ----')
    for q, s in statics_init:
        out.append(f'try {{ {s} }} catch (e) {{ __initErr.push({json.dumps(q, ensure_ascii=False)}, String(e)); }}')
    g8 = classmap.get(next((q for q in order if cl[q].name == '§8G§'), None))
    r9 = classmap.get(next((q for q in order if cl[q].name == '§9!A§'), None))
    regs = [NM.get(t) for t in ('§8!D§', '§ !U§', '§-z§', '§-!1§')]
    p4 = NM.get('§4P§')
    hc = classmap.get(next((q for q in order if cl[q].name == '§&c§'), None))
    init = NM.get('§[!C§')
    regs_lists = [NM.get(t) for t in ('§0!A§', '§%<§', '§-!4§', '§0Q§')]
    out.append('function __boot() {')
    out.append(f'  try {{ var a = {g8}.{p4}; for (var i = 0; i <= 43; i++) a.push(0); a[3] = 1; a[29] = 1; }} catch (e) {{ __bootErr.push("4P: " + e); }}')
    for r in regs:
        out.append(f'  try {{ {r9}.{r}(); }} catch (e) {{ __bootErr.push("{r}: " + String(e) + " | " + (e.stack || "")); }}')
    # mirrors the tail of the game's own init: helper tables, then per-entity init for every registry
    out.append(f'  try {{ {hc}.{init}(); }} catch (e) {{ __bootErr.push("helpers: " + String(e) + " | " + (e.stack || "")); }}')
    for lst in regs_lists:
        out.append(f'  try {{ var L = {g8}.{lst}; for (var i = 0; i < L.length; i++) {{ try {{ L[i].{init}(); }} catch (e) {{ __bootErr.push("{lst}[" + i + "]: " + String(e)); }} }} }} catch (e) {{}}')
    out.append('}')
    with open(OUT, 'w', encoding='utf8') as f:
        f.write('\n'.join(out) + '\n')
    json.dump({'names': {v: k for k, v in names.items()}}, open(os.path.join(ROOT, 'data', 'engine_names.json'), 'w', encoding='utf8'),
              ensure_ascii=False, indent=0)
    json.dump(report, open(os.path.join(ROOT, 'data', 'engine_report.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print('classes', report['classes'], 'members ok', report['members_ok'], 'failed', len(report['members_failed']),
          'static init failed', len(report['static_init_failed']))


if __name__ == '__main__':
    main()
