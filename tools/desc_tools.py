"""Description-to-formula helpers shared by the entity exporters (copied from export_challenges.py).

Call init() first; then formulas_for(class, name) reads the `_("template", args)` calls of a description and
para(class, templates, raw_paragraph) turns one paragraph of the game's text into clean text plus formulas.
"""
import json, re
from as3parse import resolve
from chance_latex import convert

cl = named = MANUAL = None
pow10_text = lambda t: t


def init(classes, named_map, pow10, manual=None):
    global cl, named, MANUAL, pow10_text
    cl, named, pow10_text, MANUAL = classes, named_map, pow10, manual or {}


def name_of_for(c):
    def f(tok):
        q = resolve(c, tok, cl)
        return named.get(q) if q else None
    return f




def source_templates(c):
    """-> {method name: body} for the description method and the string-returning helpers it calls"""
    meths = {m.name: m for m in c.methods}
    desc = meths.get('§@"§') or meths.get('§>!d§')       # bloodlines describe themselves through the second one
    bodies = [desc.body] if desc else []
    for n in re.findall(r'(§[^§]*§)\(\)', desc.body if desc else ''):
        m = meths.get(n)
        if m is not None and n not in ('§@"§', '§>!d§') and '_("' in m.body: bodies.append(m.body)
    return meths, '\n'.join(bodies)




def inline_helpers(c, expr):
    """Replace calls to one-expression methods that only wrap param1, and zero-argument static getters of other
    classes (e.g. the Hive Mind bonus), by their expression."""
    meths = {m.name: m for m in c.methods}
    for _ in range(4):
        def rep(m):
            mm = meths.get(m.group(1))
            if mm is None: return m.group(0)
            b = re.fullmatch(r'return (.+);', re.sub(r'\s+', ' ', mm.body.strip()))
            if not b or 'param1' not in b.group(1) or 'param2' in b.group(1): return m.group(0)
            return '(' + b.group(1).replace('param1', '(' + m.group(2) + ')') + ')'
        new = re.sub(r'(?<![.\w§])(§[^§]*§)\(((?:[^()]|\([^()]*(?:\([^()]*\))?[^()]*\))*)\)', rep, expr)
        def rep2(m):
            if m.group(1) in ('§&c§', '§#!!§', '§8G§'): return m.group(0)
            q = resolve(c, m.group(1), cl)
            oc = cl.get(q) if q else None
            if oc is None: return m.group(0)
            mm = next((x for x in oc.methods if x.name == m.group(2)), None)
            if mm is None: return m.group(0)
            b = re.fullmatch(r'return (.+);', re.sub(r'\s+', ' ', mm.body.strip()))
            return '(' + b.group(1) + ')' if b and 'param' not in b.group(1) else m.group(0)
        new = re.sub(r'(§[^§]*§)\.(§[^§]*§)\(\)', rep2, new)
        if new == expr: break
        expr = new
    return expr




def split_args(a):
    out, depth, cur = [], 0, ''
    for ch in a:
        if ch in '([': depth += 1
        elif ch in ')]': depth -= 1
        if ch == ',' and depth == 0: out.append(cur); cur = ''
        else: cur += ch
    if cur.strip() or out: out.append(cur)
    return [x.strip() for x in out]




def formulas_for(c, gname=''):
    """-> [(template, {placeholder index: ('const'|'f'|'raw', value)}, is_readout)] for each `_("template", args)`
    of the description (and of the string helpers it calls) whose arguments call getters of the class."""
    meths, body = source_templates(c)
    out = []
    for m in re.finditer(r'_\("((?:[^"\\]|\\.)*)"((?:[^;]|\n)*?)\)\s*[;+]', body):
        tmpl = m.group(1).replace("\\'", "'").replace('\\"', '"').replace('\\n', '\n').strip()
        args = m.group(2).lstrip(',').replace(c.name + '.', '')
        if '§%`§' in args: continue
        forms, readout = {}, bool(re.search(r'§8G§\.|§#!!§\.', args))
        scales = {}     # placeholder -> Ascension the penalty (§6!T§) of that value starts at
        for i, a in enumerate(split_args(args)):
            pm = re.search(r'§6!T§\((?:(§[^§]*§)\(\)|(-?[\d.]+))(?:,(\d+))?', a)
            if pm: scales[i] = int(pm.group(3) or 1)
            keys = re.findall(r'(?<![.\w§])(§[^§]*§)\(\)', a)
            if not keys: continue
            mt = meths.get(keys[0])
            if mt is None: continue
            b = re.sub(r'\s+', ' ', mt.body.strip())
            mm = re.fullmatch(r'return (.+);', b)
            man = MANUAL.get((gname, keys[0]))
            if man: forms[i] = ('f', man); readout = True; continue
            if not mm: forms[i] = ('raw', b); readout = True; continue
            e = mm.group(1).strip()
            if re.fullmatch(r'-?[\d.]+', e): forms[i] = ('const', e); continue
            readout = True
            e = inline_helpers(c, e)
            # a single read of a this-Era stat array entry -> the game's helper call for the same value
            e = re.sub(r'§8G§\.§5!V§\[(\d+)\]', lambda mt_: '§&c§.§"!B§(' + mt_.group(1) + ',false,true)', e)
            cv = convert(e, name_of_for(c))
            if cv: forms[i] = ('f', {'latex': cv['latex'].replace('p = ', 'v = ', 1), 'vars': cv['vars']})
            else: forms[i] = ('raw', e)
        out.append((tmpl, forms, readout, scales))
    return out




def tmpl_re(tmpl):
    parts = re.split(r'%\d', tmpl)
    return re.compile(r'^' + '(.*?)'.join(re.escape(p) for p in parts) + r'$', re.S)


APPLIES = re.compile(r'This reward can be used (?:only )?while playing with (?:the (.+?) faction|any (.+?))\.$')
TAIL_GROUP = re.compile(r'\s*\(([^()]*)\)\.?$')


SUBS = '₁₂₃₄₅₆₇₈₉'


def para(c, templates, raw, ctx):
    """-> {'text', 'formulas'} for one reward paragraph of the game text.  Values the game computes are replaced by
    v (or v1, v2 ...) in the text, and the trailing live readout "(+x%)" is dropped."""
    tmpl = forms = None
    readout = False
    scales = {}
    for t, f, ro, sc in templates:
        if tmpl_re(t).match(raw):
            tmpl, forms, readout, scales = t, f, ro, sc
            break
    if tmpl is None:
        return {'text': pow10_text(raw.strip()), 'formulas': [], 's': None}
    vals = tmpl_re(tmpl).match(raw).groups()
    tg = TAIL_GROUP.search(tmpl)
    labels, cut = {}, None
    if readout and tg and '%' in tg.group(1):
        cut = tg.start()
        for lab, i in re.findall(r'([A-Za-z][A-Za-z ]*?): ?[+x]?%(\d)', tg.group(1)): labels[int(i)] = lab.strip()
    fkeys = sorted(i for i, (k, _) in forms.items() if k == 'f')
    multi = len(fkeys) > 1
    # several values with identical formulas (both bonuses equal the same number)
    same = multi and len({json.dumps(forms[i][1], sort_keys=True) for i in fkeys}) == 1
    sym = lambda i: 'v' if (not multi or same) else 'v' + SUBS[fkeys.index(i)]
    text, last = '', 0
    for k, m in enumerate(re.finditer(r'%(\d)', tmpl)):
        if cut is not None and m.start() >= cut: break
        text += tmpl[last:m.start()]
        i = int(m.group(1))
        text += sym(i) if forms.get(i, ('',))[0] == 'f' else vals[k]
        last = m.end()
    if cut is not None:
        text += tmpl[last:cut]
        rest = tmpl[tg.end():]
        text += '.' if tg.group(0).endswith('.') and not text.rstrip().endswith('.') else ''
    else:
        text += tmpl[last:]
    text = text.replace("\'", "'").strip()
    fl = []
    use = fkeys[:1] if same else fkeys
    for i in use:
        f = dict(forms[i][1])
        if multi and not same:
            f['latex'] = f['latex'].replace('v = ', 'v_{' + str(fkeys.index(i) + 1) + '} = ', 1)
        if i in labels: f['label'] = labels[i]
        f['shown'] = cut is not None or sym(i) in text
        fl.append(f)
    for i in sorted(forms):
        if forms[i][0] == 'raw': fl.append({'raw': forms[i][1], 'label': labels.get(i)})
    return {'text': pow10_text(text), 'formulas': fl, 's': min(scales.values()) if scales else None}


