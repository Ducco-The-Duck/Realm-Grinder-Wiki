import re, glob, json, os
root = os.path.join('out', 'script', 'scripts')
labels = {}
pat = re.compile(r'_\("([^"]*?)(?::? ?%0)?"[^;]*?§(?:\^!r|\ !q)§\((\d+)')
for f in glob.glob(os.path.join(root, '**', '*.as'), recursive=True):
    t = open(f, encoding='utf8', errors='replace').read()
    if 'Excavations made' not in t and 'Spells Cast' not in t: continue
    for line in t.split('\n'):
        for m in pat.finditer(line):
            labels.setdefault(int(m.group(2)), set()).add(m.group(1).strip())
for k in sorted(labels): print(k, sorted(labels[k]))
json.dump({k: sorted(v) for k, v in labels.items()}, open('out/stat_labels.json', 'w'), indent=0)
