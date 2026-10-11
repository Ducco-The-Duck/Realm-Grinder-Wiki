"""Evaluate every entity's static formulas and description methods in the transpiled engine
(fresh-game state) and write data/formula_values.json.

    python -I tools/eval_formulas.py
"""
import json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(HERE, 'pylib'))
import quickjs

names = json.load(open(os.path.join(ROOT, 'data', 'engine_names.json'), encoding='utf8'))['names']
# the JSON stores token -> js name for classes ('K..') and members ('_..')
ctx = quickjs.Context()
ctx.eval(open(os.path.join(ROOT, 'data', 'engine.js'), encoding='utf8').read())
ctx.eval('__boot()')
ctx.eval('''
function __call(q, kind, name, argsJson) {
  var K = __byQ[q];
  if (!K) return JSON.stringify({err: 'no class'});
  try {
    var v;
    if (kind === 'static') v = K[name].apply(K, JSON.parse(argsJson));
    else {
      var o = new K();
      v = o[name]();
    }
    if (typeof v === 'number' && !isFinite(v)) return JSON.stringify({v: String(v)});
    return JSON.stringify({v: v === undefined ? null : v});
  } catch (e) { return JSON.stringify({err: String(e).slice(0, 120)}); }
}
''')

def jsname(tok):
    return names.get(tok)

out = {}
stats = collections.Counter()
errs = collections.Counter()
for kind in ['upgrade', 'achievement', 'spell', 'building', 'research']:
    for r in json.load(open(os.path.join(ROOT, 'data', f'{kind}s.json'), encoding='utf8')):
        q = r['class']
        rec = {}
        for fn, f in r.get('formulas', {}).items():
            if f['params'].strip():
                continue
            n = jsname(fn)
            if not n: stats['formula_noname'] += 1; continue
            res = json.loads(ctx.eval(f'__call({json.dumps(q, ensure_ascii=False)}, "static", {json.dumps(n)}, "[]")'))
            if 'err' in res: stats['formula_err'] += 1; errs[res['err'][:70]] += 1
            else: stats['formula_ok'] += 1; rec.setdefault('formulas', {})[n] = res['v']
        methods = {t['method'] for t in r.get('texts', [])}
        for m in sorted(methods):
            n = jsname(m)
            if not n: stats['text_noname'] += 1; continue
            res = json.loads(ctx.eval(f'__call({json.dumps(q, ensure_ascii=False)}, "inst", {json.dumps(n)}, "[]")'))
            if 'err' in res: stats['text_err'] += 1; errs[res['err'][:70]] += 1
            else: stats['text_ok'] += 1; rec.setdefault('rendered', {})[n] = res['v']
        if rec: out[q] = rec
json.dump(out, open(os.path.join(ROOT, 'data', 'formula_values.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
print(dict(stats))
for k, v in errs.most_common(10): print(v, k)
