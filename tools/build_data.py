"""Build data/*.json from the deobfuscated scripts in out/script and data/strings.json.

Run:  python -I tools/build_data.py
Field meanings are inferred (see FIELD_LABELS); unmapped fields are kept under "raw" with
their mangled names so nothing is lost.
"""
import json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from as3parse import parse_all, resolve, ROOT
from as3calls import find_msg_calls

DATA = os.path.join(ROOT, 'data')

# ---- constants inferred from the code (evidence: see data/GLOSSARY.md) --------------------
FACTIONS = {0: 'Fairy', 1: 'Elf', 2: 'Angel', 3: 'Goblin', 4: 'Undead', 5: 'Demon', 6: 'Titan',
            7: 'Druid', 8: 'Faceless', 9: 'Dwarf', 10: 'Drow', 11: 'Mercenary'}
ALIGNMENTS = {0: 'None', 1: 'Good', 2: 'Evil', 3: 'Neutral'}

# base class (short mangled name) -> entity kind
ROOTS = {'§`6§': 'upgrade', '§#!`§': 'achievement', '§84§': 'spell', '§`!;§': 'building', '§&!_§': 'research'}

FIELD_LABELS = {
    '§6!Z§': 'num_id', '§1i§': 'name', '§-v§': 'name_plural', '§^!#§': 'icon', '§?!=§': 'tag',
    '§@1§': 'tag2', '§7#§': 'description', '§>=§': 'cost', '§<R§': 'cost', '§,!Y§': 'alignment',
    '§-!^§': 'faction', '§,!B§': 'category', '§,\'§': 'cost_growth', '§ 4§': 'base_production',
    '§`r§': 'building_index', '§\'T§': 'unique_names', '§-!&§': 'unique_names_plural',
    '§+§': 'duration', '§9!m§': 'spell_tier', '§ r§': 'internal_name',
}
SKIP_RAW = {'§3y§', '§1!+§', '§%@§', '§<!t§', '§6&§', '§-!u§', '§?"\'§', '§="\'§'}  # UI-only / format strings


def unq(s):
    """Python value of a simple AS literal, else the text."""
    s = s.strip()
    if not s.startswith(('"', '_("')) and ' = ' in s: s = s.split(' = ')[-1].strip()  # a = b = value
    m = re.fullmatch(r'_\("((?:[^"\\]|\\.)*)"\)', s)
    if m: return ('msg', m.group(1).replace("\\'", "'").replace('\\"', '"').replace('\\n', '\n'))
    m = re.fullmatch(r'"((?:[^"\\]|\\.)*)"', s)
    if m: return unescape(m.group(1))
    if s in ('true', 'false'): return s == 'true'
    try:
        f = float(s)
        return int(f) if f == int(f) and abs(f) < 1e15 and re.fullmatch(r'-?\d+', s) else f
    except ValueError:
        return s



def unescape(s):
    return re.sub(r'\\(.)', lambda m: '\n' if m.group(1) == 'n' else m.group(1), s)


def kind_of(c, cl):
    seen = 0
    while c and seen < 20:
        if c.name in ROOTS: return ROOTS[c.name]
        c = cl.get(c.parent); seen += 1
    return None


def main():
    cl = parse_all()
    strings = json.load(open(os.path.join(DATA, 'strings.json'), encoding='utf8'))

    # ---- pick entities -----------------------------------------------------------------
    ents = {}
    for q, c in cl.items():
        k = kind_of(c, cl)
        if not k or c.name in ROOTS: continue
        fields = {f: unq(v) for f, i, v in c.ctor if i is None and '.' not in f and not f.startswith('_loc')}
        if '§6!Z§' not in fields and not c.ids and '§1i§' not in fields: continue
        ents[q] = (k, c, fields)

    # inherit constructor fields from ancestors (child overrides)
    def merged(c):
        chain = []
        while c: chain.append(c); c = cl.get(c.parent)
        out = {}
        for a in reversed(chain):
            for f, i, v in a.ctor:
                if i is None and '.' not in f and not f.startswith('_loc'): out[f] = unq(v)
        return out

    short_name = {}  # qualified class -> display name for formula rendering
    for q, (k, c, f) in ents.items():
        n = merged(c).get('§1i§')
        if isinstance(n, tuple): n = n[1]
        short_name[q] = n if isinstance(n, str) else c.name

    def render(expr, c):
        """Replace Class.id references with [Name] for readability."""
        def sub(m):
            q = resolve(c, m.group(1), cl)
            return f'[{short_name.get(q, m.group(1))}]'
        return re.sub(r'(§[^§]*§)\.id\b', sub, expr)

    out = collections.defaultdict(list)
    for q, (kind, c, _f) in sorted(ents.items(), key=lambda kv: kv[0]):
        f = merged(c)
        rec = {'class': q, 'kind': kind}
        if c.ids: rec['ids'] = c.ids
        raw = {}
        for fld, v in f.items():
            if fld in SKIP_RAW: continue
            lab = FIELD_LABELS.get(fld)
            if isinstance(v, tuple): v = v[1]  # message id -> English text
            if lab: rec.setdefault(lab, v)
            else: raw[fld] = v
        if isinstance(rec.get('faction'), int) and rec['faction'] in FACTIONS:
            rec['faction_name'] = FACTIONS[rec['faction']]
        if isinstance(rec.get('alignment'), int) and rec['alignment'] in ALIGNMENTS:
            rec['alignment_name'] = ALIGNMENTS[rec['alignment']]
        # indexed ctor assignments (unique building names etc.)
        for fld, i, v in c.ctor:
            if i is not None and FIELD_LABELS.get(fld) in ('unique_names', 'unique_names_plural'):
                lst = rec.setdefault(FIELD_LABELS[fld] + '_list', {})
                lst[int(i)] = unq(v)
        # methods: statics (formulas), text, references
        statics, texts, refs = {}, [], set()
        for m in c.methods:
            if m.name == c.name: continue
            body = m.body.strip()
            for rm in re.finditer(r'(§[^§]*§)\.id\b', body):
                rq = resolve(c, rm.group(1), cl)
                if rq in short_name: refs.add(short_name[rq])
            if 'static' in m.mods:
                sm = re.fullmatch(r'return (.+);', body, re.S)
                statics[m.name] = {'params': m.params, 'expr': render(sm.group(1), c) if sm else render(body, c)}
            elif m.ret == 'String':
                for msg, args in find_msg_calls(body):
                    texts.append({'method': m.name, 'text': unescape(msg),
                                  'args': [render(a, c) for a in args]})
        # numeric value of args that call a constant static function, e.g. fmt(§++§())
        for t in texts:
            vals = []
            for a in t['args']:
                v = None
                for fn in re.findall(r'(§[^§]*§)\(\)', a):
                    if fn in statics:
                        try: v = float(statics[fn]['expr'])
                        except ValueError: pass
                vals.append(v)
            if any(v is not None for v in vals): t['values'] = vals
        if statics: rec['formulas'] = statics
        if texts: rec['texts'] = texts
        refs.discard(short_name.get(q))
        if refs: rec['refs'] = sorted(refs)
        if raw: rec['raw'] = raw
        if isinstance(rec.get('name'), str) and re.fullmatch(r'param\d+', rec['name']):
            del rec['name']; rec['templated'] = True  # name supplied by a subclass/instantiation
        if 'name' not in rec and not c.ids and not rec.get('templated'): continue  # abstract base class
        out[kind].append(rec)

    # ---- group & write -------------------------------------------------------------------
    os.makedirs(DATA, exist_ok=True)
    summary = {}
    for kind, recs in out.items():
        recs.sort(key=lambda r: (r.get('num_id') if isinstance(r.get('num_id'), int) else 10**9, r['class']))
        json.dump(recs, open(os.path.join(DATA, f'{kind}s.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
        summary[kind] = len(recs)
    json.dump({'factions': FACTIONS, 'alignments': ALIGNMENTS},
              open(os.path.join(DATA, 'enums.json'), 'w', encoding='utf8'), indent=1)
    print(summary)


if __name__ == '__main__':
    main()
