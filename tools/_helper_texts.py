import sys, re, collections
sys.path.insert(0, 'tools')
from as3parse import parse_all
cl = parse_all()
MSG = re.compile(r'_\("([^"]*)"')
want = sys.argv[1:]
for w in want:
    seen = collections.Counter()
    for c in cl.values():
        for m in c.methods:
            if w in m.body:
                for t in MSG.findall(m.body)[:2]:
                    seen[t[:130]] += 1
    print('##', w, '->', [(t, n) for t, n in seen.most_common(4)])
