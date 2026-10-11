"""Resolve entity icon names that the game builds at runtime, by reading `icon` off the
registered instances after __boot().  Writes data/runtime_icons.json {class: icon_name}.

    python -I tools/runtime_icons.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(HERE, 'pylib'))
import quickjs

names = json.load(open(os.path.join(ROOT, 'data', 'engine_names.json'), encoding='utf8'))['names']
sprites = json.load(open(os.path.join(ROOT, 'data', 'sprites.json')))
ctx = quickjs.Context()
ctx.eval(open(os.path.join(ROOT, 'data', 'engine.js'), encoding='utf8').read())
ctx.eval('__boot()')
g, icon = names['§8G§'], names['§^!#§']
regs = [names[t] for t in ('§-!4§', '§0Q§', '§0!A§', '§%<§')]
ctx.eval('''
function __icons(g, regs, icon) {
  var out = {};
  var K = eval(g);
  for (var i = 0; i < regs.length; i++) {
    var arr = K[regs[i]] || [];
    for (var j = 0; j < arr.length; j++) {
      var o = arr[j];
      if (!o || !o.constructor) continue;
      var q = null;
      for (var c = 0; c < __classes.length; c++) if (__classes[c].K === o.constructor) { q = __classes[c].q; break; }
      if (q !== null) out[q] = o[icon];
    }
  }
  return JSON.stringify(out);
}''')
res = json.loads(ctx.eval(f'__icons({json.dumps(g)}, {json.dumps(regs)}, {json.dumps(icon)})'))
out = {}; stat = {'checked': 0, 'resolved': 0, 'unresolved': []}
for kind in ['upgrade', 'achievement', 'spell', 'building', 'research']:
    for r in json.load(open(os.path.join(ROOT, 'data', f'{kind}s.json'), encoding='utf8')):
        ic = r.get('icon')
        if ic and ic in sprites: continue
        rt = res.get(r['class'])
        if ic is None and rt is None: continue
        stat['checked'] += 1
        if isinstance(rt, str) and rt in sprites:
            out[r['class']] = rt; stat['resolved'] += 1
        else:
            stat['unresolved'].append([r.get('name'), ic, rt])
json.dump(out, open(os.path.join(ROOT, 'data', 'runtime_icons.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
print(stat['checked'], 'checked,', stat['resolved'], 'resolved,', len(stat['unresolved']), 'unresolved')
for u in stat['unresolved'][:12]: print('  ', u)
import collections
c = collections.Counter(str(u[2]) for u in stat['unresolved'])
print(len(c), 'distinct unresolved runtime values;', 'sample:', c.most_common(14))
json.dump(stat['unresolved'], open(os.path.join(ROOT, 'out', 'runtime_icons_unresolved.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
