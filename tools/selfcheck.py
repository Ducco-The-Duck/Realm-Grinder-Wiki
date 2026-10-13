"""Quick sanity check of the extracted game code before (re)building the data.

    python -I tools/selfcheck.py            # check
    python -I tools/selfcheck.py --update   # also store the item-id baseline (data/item_ids.json)

Answers one question: did the game's obfuscated names move? It reports
  1. how many of the obfuscated names the exporters rely on still exist in the code,
  2. whether the few structural facts the pipeline depends on still hold (Ascension thresholds, save version),
  3. whether the numeric item ids (the stable anchor, also used by saves) are unchanged since the baseline.
Exit code 0 = fine, 1 = something to look at.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
SCRIPTS = os.environ.get('RG_SCRIPTS') or os.path.join(ROOT, 'out', 'script', 'scripts')
BASELINE = os.path.join(ROOT, 'data', 'item_ids.json')
TOKEN = re.compile(r'§[^§\n]{1,12}§')
problems = []


def read_all():
    texts = {}
    for r, _, fs in os.walk(SCRIPTS):
        for f in fs:
            if f.endswith('.as'):
                texts[os.path.join(r, f)] = open(os.path.join(r, f), encoding='utf8', errors='replace').read()
    return texts


texts = read_all()
if not texts:
    sys.exit('no extracted scripts under out/script/scripts (run tools/extract.sh first)')
blob = '\n'.join(texts.values())
print(f'{len(texts)} script files, {len(blob) // 1024} KB')

# 1. obfuscated names the exporters use
NAME = re.compile(r'''^[A-Za-z0-9!"#$%&'+,\-;<=>?@\[\]^_` ]{1,3}$''')    # what a real name looks like (1-3 chars)
used = set()
for fn in os.listdir(HERE):
    if fn.endswith('.py') and fn != 'selfcheck.py':
        src = open(os.path.join(HERE, fn), encoding='utf8', errors='replace').read()
        for t in re.findall(r'§([^§\n]{1,16})§', src):
            t = re.sub(r'\\(.)', r'\1', t)              # names written inside regexes are escaped
            if NAME.match(t):
                used.add('§' + t + '§')
used.discard('§X§')                 # placeholder used in the tools' own docs
present = set(TOKEN.findall(blob))
missing = sorted(t for t in used if t not in present)
share = 100 * (len(used) - len(missing)) / max(1, len(used))
verdict = 'stable' if share >= 98 else ('partly changed' if share >= 80 else 'RE-OBFUSCATED')
print(f'1. names used by the tools: {len(used)}; still in the game code: {share:.1f}% -> {verdict}')
if missing:
    print('   missing:', ' '.join(missing[:25]) + (' ...' if len(missing) > 25 else ''))
if missing:
    problems.append(f'{len(missing)} obfuscated name(s) used by the tools are gone from the code')

# 2. structural facts (found by shape, so they can still be located after a rename)
asc = re.search(r'(\S+\.\S+) == 0 && (\S+\.\S+) >= 40 \|\| \1 == 1 && \2 >= 100 \|\| \1 == 2 && \2 >= 160 \|\| \1 == 3 && \2 >= 220', blob)
if asc:
    a, r = asc.group(1), asc.group(2)
    print(f'2. Ascension needs Reincarnation 40/100/160/220: found with {a} (Ascension) and {r} (Reincarnation)')
    if a != '§8G§.§,P§' or r != '§8G§.§8!H§':
        problems.append(f'Ascension/Reincarnation fields are now {a} / {r}')
else:
    print('2. Ascension thresholds 40/100/160/220 NOT found: the rule or its shape changed')
    problems.append('Ascension thresholds not found')
sv = re.search(r'writeShort\((\d+)\);\s*\S+\.writeShort\(', blob)
print('   save format version written:', sv.group(1) if sv else 'not found (save writer changed shape)')
pen = re.search(r'return (\S+)\.(\S+) >= param2 \? Math\.pow\(param1,Math\.pow\(0\.1,\1\.\2 - \(param2 - 1\)\)\) : param1;', blob)
print('   Ascension penalty shape:', 'found' if pen else 'NOT found')
if not pen:
    problems.append('penalty function shape changed')

# 3. item ids: (display name, numeric id) of every item class
ids = set()
for t in texts.values():
    m, i = re.search(r'§1i§ = _\("([^"]+)"\)', t), re.search(r'§6!Z§ = (\d+);', t)
    if m and i:
        ids.add((m.group(1), int(i.group(1))))
rows = sorted([n, i] for n, i in ids)
print(f'3. item classes with a name and an id: {len(rows)}')
if not rows:
    problems.append('no item ids found (the id or name field was renamed)')
if os.path.exists(BASELINE):
    old = {tuple(x) for x in json.load(open(BASELINE, encoding='utf8'))}
    gone, new = sorted(old - ids), sorted(ids - old)
    by_name_old = {}
    for n, i in gone: by_name_old.setdefault(n, []).append(i)
    moved = [(n, by_name_old[n], [i for m, i in new if m == n]) for n in by_name_old if any(m == n for m, _ in new)]
    print(f'   against baseline: {len(new)} new, {len(gone)} no longer present, {len(moved)} with a changed id')
    for n, o, nw in moved[:15]:
        print(f'   CHANGED ID {n}: {o} -> {nw}')
    if moved:
        problems.append('item ids changed')
    if new and len(new) <= 25:
        print('   new:', ', '.join(f'{n} ({i})' for n, i in new))
    elif new:
        print('   new (first 25):', ', '.join(f'{n} ({i})' for n, i in new[:25]))
    if gone:
        print('   gone:', ', '.join(f'{n} ({i})' for n, i in gone[:25]))
else:
    print('   no baseline yet (run with --update to store one)')
if '--update' in sys.argv:
    json.dump(rows, open(BASELINE, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    print('   baseline written to data/item_ids.json')

# 4. translators that gave up in the last data build (counts of undecoded pieces)
try:
    d = json.load(open(os.path.join(ROOT, 'data', 'upgrade_pages.json'), encoding='utf8'))
    und = sum(1 for s in d.values() for u in s if u['undecoded'])
    a = json.load(open(os.path.join(ROOT, 'data', 'artifacts.json'), encoding='utf8'))
    und_a = sum(1 for x in a if x['undecoded_conditions'])
    print(f'4. undecoded conditions in the current data: upgrades {und}, artifacts {und_a}')
    if und or und_a:
        problems.append('undecoded conditions in the data')
except OSError:
    pass

print('\nOK' if not problems else '\nLOOK AT: ' + '; '.join(problems))
sys.exit(1 if problems else 0)
