import sys, re, collections
sys.path.insert(0, 'tools')
from as3parse import parse_all
cl = parse_all()


def isart(c):
    p = c.parent
    while p in cl:
        if cl[p].name == '§-+§': return True
        p = cl[p].parent
    return False


cnt = collections.Counter()
ex = {}
rows = []
for c in cl.values():
    if not isart(c): continue
    for m in c.methods:
        if m.name != '§5",§' or m.kind != 'get': continue
        body = re.sub(r'\s+', ' ', m.body.strip())
        mm = re.fullmatch(r'return (.+);', body)
        if not mm: rows.append(('COMPLEX', body[:200])); continue
        e = mm.group(1)
        if re.fullmatch(r'-?[\d.]+', e): continue
        rows.append(('expr', e))
        # inputs: Class.member calls and stat array refs
        for t in re.findall(r'§[^§]*§\.§[^§]*§\((?:[^()]|\([^()]*\))*\)(?:\.§[^§]*§)?|§8G§\.§[^§]*§\[\d+\]', e):
            k = re.sub(r'§#N§\(§[^§]*§\.id\)', '§#N§(<id>)', t)
            cnt[k] += 1
print(len(rows), 'variable chance expressions')
for k, v in cnt.most_common(60): print(v, k)
print('---- complex')
for k, b in rows:
    if k == 'COMPLEX': print(b)
