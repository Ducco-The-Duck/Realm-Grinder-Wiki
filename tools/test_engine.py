import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'pylib'))
import quickjs
ctx = quickjs.Context()
src = open(os.path.join(HERE, '..', 'data', 'engine.js'), encoding='utf8').read()
try:
    ctx.eval(src)
except Exception as e:
    print('LOAD ERROR:', str(e)[:500]); sys.exit(1)
print('classes', ctx.eval('__classes.length'))
ie = json.loads(ctx.eval('JSON.stringify(__initErr)'))
print('static init errors', len(ie)//2)
for q, e in list(zip(ie[::2], ie[1::2]))[:5]: print('  ', e[:120])
ctx.eval('__boot()')
be = json.loads(ctx.eval('JSON.stringify(__bootErr)'))
print('boot errors', len(be))
for e in be[:3]: print('  ', e[:600])
print('ids registered:', ctx.eval('Object.keys(__byId).length'),
      'numeric K.id:', ctx.eval('__classes.filter(x=>x.ids.length && typeof x.K.id==="number").length'))
