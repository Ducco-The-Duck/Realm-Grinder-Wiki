"""Export every trophy (achievement registry entry) from the engine to data/trophies.json.

The game's "normal" trophy count (903) is the set with none of the four special flags set;
the remaining entries are grouped by which flag they carry.

    python -I tools/export_trophies.py
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
J = lambda tok: names[tok]
src = f"""JSON.stringify({J('§8G§')}.{J('§0Q§')}.map(function (o, i) {{
  var d = null, e = null;
  try {{ d = o.{J('§@"§')}(); }} catch (x) {{ e = String(x).slice(0, 80); }}
  return {{ order: i, id: o.ids, num_id: o.{J('§6!Z§')}, name: o.{J('§1i§')}, requirement: d, error: e,
           icon: o.{J('§^!#§')}, type: o.{J('§?!=§')}, alignment: o.{J('§,!Y§')}, threshold: o.{J('§>=§')} === undefined ? null : null,
           f_a: !!o.{J('§3!9§')}, f_b: !!o.{J('§?!,§')}, f_c: !!o.{J('§@!R§')}, f_d: !!o.{J('§@!Z§')} }};
}}))"""
rows = json.loads(ctx.eval(src))
GROUPS = {'a': 'special', 'b': 'seasonal', 'c': 'excavation', 'd': 'event-quest'}
out = []
for r in rows:
    flag = next((GROUPS[k[2]] for k in ('f_a', 'f_b', 'f_c', 'f_d') if r[k]), None)
    out.append({
        'order': r['order'], 'id': r['id'], 'name': r['name'], 'requirement': (r['requirement'] or '').strip(),
        'icon': r['icon'] if r['icon'] in sprites else None, 'icon_name': r['icon'],
        'type': r['type'] or None, 'alignment': r['alignment'],
        'listed': flag is None, 'group': flag or 'trophy',
        **({'requirement_error': r['error']} if r['error'] else {}),
    })
json.dump(out, open(os.path.join(ROOT, 'data', 'trophies.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
listed = [t for t in out if t['listed']]
print(len(out), 'entries;', len(listed), 'listed trophies;',
      'without requirement text:', sum(1 for t in listed if not t['requirement']),
      '; without icon:', sum(1 for t in listed if not t['icon']))
