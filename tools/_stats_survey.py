import sys, re, json, collections
sys.path.insert(0, 'tools')
from as3parse import parse_all
cl = parse_all()


def isart(c):
    p = c.parent
    while p in cl:
        if cl[p].name == '§-+§': return True
        p = cl[p].parent
    return False


STAT = re.compile(r'§8G§\.(§5!V§|§=y§|§@w§)\[(\d+)\]')
MSG = re.compile(r'_\("([^"]*)"')
need = collections.Counter()
for c in cl.values():
    if isart(c):
        for m in c.methods:
            if m.name == '§5",§':
                for a, i in STAT.findall(m.body): need[int(i)] += 1
print('indices used by artifact chances:', sorted(need))
info = collections.defaultdict(collections.Counter)
for c in cl.values():
    if isart(c): continue
    for m in c.methods:
        refs = STAT.findall(m.body)
        if not refs: continue
        texts = MSG.findall(m.body)
        for a, i in refs:
            if int(i) in need and texts: info[int(i)][(a, texts[0][:90])] += 1
for i in sorted(need):
    print(i, '->', info[i].most_common(3))
