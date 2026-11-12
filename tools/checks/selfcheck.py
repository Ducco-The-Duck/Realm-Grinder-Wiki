"""Quick sanity check of the extracted game code before (re)building the data.

    python -I tools/checks/selfcheck.py            # check
    python -I tools/checks/selfcheck.py --update   # also store the item-id baseline (data/generated/item_ids.json)

Answers one question: did the game's obfuscated names move? It reports
  1. how many of the obfuscated names the exporters rely on still exist in the code,
  2. whether the few structural facts the pipeline depends on still hold (Ascension thresholds, save version),
  3. whether the numeric item ids (the stable anchor, also used by saves) are unchanged since the baseline.
Exit code 0 = fine, 1 = something to look at.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(HERE, '..')
SCRIPTS = os.environ.get('RG_SCRIPTS') or os.path.join(ROOT, 'out', 'script', 'scripts')
BASELINE = os.path.join(ROOT, 'data', 'generated/item_ids.json')
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
TOOL_FILES = [os.path.join(dp, fn) for dp, _, fns in os.walk(HERE) if os.sep + 'pylib' not in dp and os.sep + 'ffdec' not in dp
              for fn in fns if fn.endswith('.py') and fn != 'selfcheck.py']
for tool in TOOL_FILES:
    if True:
        src = open(tool, encoding='utf8', errors='replace').read()
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
    print('   baseline written to data/generated/item_ids.json')

# 4. translators that gave up in the last data build (counts of undecoded pieces)
try:
    d = json.load(open(os.path.join(ROOT, 'data', 'generated/upgrade_pages.json'), encoding='utf8'))
    und = sum(1 for s in d.values() for u in s if u['undecoded'])
    a = json.load(open(os.path.join(ROOT, 'data', 'generated/artifacts.json'), encoding='utf8'))
    und_a = sum(1 for x in a if x['undecoded_conditions'])
    print(f'4. undecoded conditions in the current data: upgrades {und}, artifacts {und_a}')
    if und or und_a:
        problems.append('undecoded conditions in the data')
except OSError:
    pass

# 5. the hand-written unlocks page data
try:
    uk = json.load(open(os.path.join(ROOT, 'data', 'handwritten/unlocks.json'), encoding='utf8'))
    bad = [m.get('name', '?') for m in uk['mechanics'] if not isinstance(m.get('asc'), int) or not 0 <= m['asc'] <= uk['max_ascension'] or not m.get('name')]
    arts = {a['name'] for a in json.load(open(os.path.join(ROOT, 'data', 'generated/artifacts.json'), encoding='utf8'))}
    bad += [n for m in uk['mechanics'] for sec in m.get('sections', []) for l in sec.get('lines', []) for n in l.get('artifacts', []) if n not in arts]      # artifacts shown beside a line of a mechanic
    print(f"5. unlocks page: {len(uk['mechanics'])} mechanics" + (f"; bad entries: {bad}" if bad else ''))
    if bad:
        problems.append('data/handwritten/unlocks.json has entries without a name or a valid Ascension')
except (OSError, ValueError, KeyError) as e:
    print('5. data/handwritten/unlocks.json unreadable:', e)
    problems.append('data/handwritten/unlocks.json unreadable')

# 6. the hand-written spell overview covers every spell
try:
    ov = json.load(open(os.path.join(ROOT, 'data', 'handwritten/spells_overview.json'), encoding='utf8'))['spells']
    names = {x['name'] for x in json.load(open(os.path.join(ROOT, 'data', 'derived/spells.json'), encoding='utf8'))}
    miss = sorted(names - set(ov)); extra = sorted(set(ov) - names)
    print(f"6. spell overview: {len(ov)} spells" + (f"; missing: {miss}; unknown: {extra}" if miss or extra else ''))
    if miss or extra:
        problems.append('data/handwritten/spells_overview.json does not match the spells')
except (OSError, ValueError, KeyError) as e:
    print('6. data/handwritten/spells_overview.json unreadable:', e)
    problems.append('data/handwritten/spells_overview.json unreadable')

# 7-9. every number in the hand-written spell details (and, for 9, the mechanics that name their code) still appears in the game code the spell was read from (tools/checks/verify_formulas.py)
if os.environ.get('RG_SCRIPTS'):      # checking a new build before it replaces out/: the data files still belong to the old build, so 7 and 8 run after the rebuild
    print('7, 8. formula numbers: skipped here, they run in the selfcheck after the rebuild')
else:
  try:
      import io, contextlib
      sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('extract', 'export', 'manual', 'pages', 'checks')]
      import verify_formulas
      buf = io.StringIO()
      with contextlib.redirect_stdout(buf): n_bad = verify_formulas.main(set())
      print(f"7. spell detail numbers: {buf.getvalue().strip().splitlines()[-1]}")
      buf2 = io.StringIO()
      with contextlib.redirect_stdout(buf2): n_bad2 = verify_formulas.main_items()
      print(f"8. upgrade and challenge formula numbers: {buf2.getvalue().strip().splitlines()[-1]}")
      buf3 = io.StringIO()
      with contextlib.redirect_stdout(buf3): n_bad3 = verify_formulas.main_mechanics()
      print(f"9. mechanics page numbers: {buf3.getvalue().strip().splitlines()[-1]}")
      buf4 = io.StringIO()
      with contextlib.redirect_stdout(buf4): n_bad4 = verify_formulas.main_buildings()
      print(f"10. buildings page numbers: {buf4.getvalue().strip().splitlines()[-1]}")
      buf5 = io.StringIO()
      with contextlib.redirect_stdout(buf5): n_bad5 = verify_formulas.main_costs()
      print(f"11. costs on the pages: {buf5.getvalue().strip().splitlines()[-1]}")
      if n_bad5:
          print(buf5.getvalue())
          problems.append(f"{n_bad5} cost(s) on the pages differ from their class (run tools/checks/verify_formulas.py --costs)")
      if n_bad4:
          print(buf4.getvalue())
          problems.append(f"{n_bad4} number(s) in data/handwritten/buildings.json are not found in the game code (run tools/checks/verify_formulas.py --buildings)")
      if n_bad3:
          print(buf3.getvalue())
          problems.append(f"{n_bad3} number(s) in the mechanics of data/handwritten/unlocks.json are not found in the game code (run tools/checks/verify_formulas.py --mechanics)")
      if n_bad2:
          print(buf2.getvalue())
          problems.append(f"{n_bad2} number(s) in upgrade or challenge formulas are not found in the game code (run tools/checks/verify_formulas.py --items)")
      if n_bad:
          print(buf.getvalue())
          problems.append(f"{n_bad} number(s) in data/handwritten/spells_overview.json are not found in the game code (run tools/checks/verify_formulas.py)")
  except Exception as e:
      problems.append(f"tools/checks/verify_formulas.py failed: {e}")

# 12. the Factions page: its data (written by the Upgrades, Buildings and Spells page builders into data/derived) is complete and consistent
if not os.environ.get('RG_SCRIPTS'):      # the data files belong to the old build while a new one is checked
    try:
        def _d(n): return json.load(open(os.path.join(ROOT, 'data', 'derived', n), encoding='utf8'))
        fu, ub, sc = _d('faction_upgrades.json'), _d('unique_buildings.json'), _d('spell_cards.json')
        bad = []
        if len(fu['f']) != 16: bad.append(f"{len(fu['f'])} factions instead of 16")
        for i, f in fu['f'].items():
            names = [n for r in f['rows'] for n in r] + f['heritage'] + f['combos'] + [x for x in (f['bloodline'], f['lineage'], f['set']) if x]
            bad += [f'faction {i}: {n} has no item' for n in names if n not in fu['items']]
            bad += [f'faction {i}: {n} has no icon' for n in names if n in fu['items'] and not fu['items'][n].get('i')]
            if not f['rows']: bad.append(f'faction {i}: no upgrades')
            if f['spell'] and f['spell'] not in sc: bad.append(f"faction {i}: spell {f['spell']} is not on the Spells page")
            bad += [f"faction {i}: unique building {u} is not on the Buildings page" for u in f['uniques'] if u not in ub]
            if f['lineage'] and len(fu['items'].get(f['lineage'], {}).get('lp', [])) != 6: bad.append(f'faction {i}: the Lineage has no six perks')
            if int(i) <= 5 and len(f['combos']) != 5: bad.append(f"faction {i}: {len(f['combos'])} legacy combos instead of 5")
        ch_ids = {f['id'] for f in json.load(open(os.path.join(ROOT, 'data', 'generated/challenges.json'), encoding='utf8'))}
        art_names = {a['name'] for a in json.load(open(os.path.join(ROOT, 'data', 'generated/artifacts.json'), encoding='utf8'))}
        for i, f in fu['f'].items():
            if int(i) not in ch_ids: bad.append(f'faction {i}: no challenges')
            if f['set']:
                arts = [x[len('Artifact: '):].split(' (')[0] for x in fu['items'][f['set']]['s'] if x.startswith('Artifact: ')]
                if not arts: bad.append(f"faction {i}: the Artifact Set names no artifacts")
                bad += [f"faction {i}: artifact {n} does not exist" for n in arts if n not in art_names]
        slugs = [re.sub('[^a-z0-9]+', '-', n.lower()) for n in ub]
        if len(set(slugs)) != len(slugs): bad.append('two unique buildings share a link address')
        if not os.path.exists(os.path.join(ROOT, 'docs', 'factions.html')): bad.append('docs/factions.html is missing (run build_factions_page.py)')
        print(f"12. factions page: {len(fu['f'])} factions, {len(fu['items'])} upgrades, {len(ub)} unique buildings" + (f"; problems: {bad[:6]}" if bad else ''))
        if bad: problems.append('the Factions page data is incomplete (see 12)')
    except (OSError, ValueError, KeyError) as e:
        print('12. factions page data unreadable (run the page builders):', e)
        problems.append('the Factions page data is unreadable')

# 13. every icon a page uses exists in docs/assets/icons (a new item of an update needs its artwork, which comes from the game's image atlases, not from the .swf: tools/UPDATING.md step 1b)
if not os.environ.get('RG_SCRIPTS'):
    try:
        icon_dir = os.path.join(ROOT, 'docs', 'assets', 'icons')
        need = {sp['icon'] + '.png': sp['name'] for sp in json.load(open(os.path.join(ROOT, 'data', 'derived/spells.json'), encoding='utf8')) if sp.get('icon')}      # the spells
        docs = os.path.join(ROOT, 'docs')
        for fn in os.listdir(docs):
            if fn.endswith('.html'):
                for m in re.findall(r"""assets/icons/([^"'\s)<>+]+\.png)""", open(os.path.join(docs, fn), encoding='utf8').read()): need.setdefault(m.replace('%20', ' '), fn)
        absent = sorted((w, f) for f, w in need.items() if not os.path.exists(os.path.join(icon_dir, f)))
        print(f"13. icons used by the pages: {len(need)}" + (f"; MISSING {len(absent)}: {absent[:8]}" if absent else '; all present'))
        if absent: problems.append(f"{len(absent)} icon(s) used by the pages are missing in docs/assets/icons (new artwork? see tools/UPDATING.md step 1b)")
    except OSError as e:
        print('13. icons check failed:', e)

# 14. no stray control characters in the hand-written data (a backslash escape written through a shell can turn into one, e.g. a backslash-f into a form feed, and breaks a formula)
CONTROL = {chr(i) for i in range(32)} - {chr(9), chr(10), chr(13)}
try:
    ctl = []
    def _walk(x, fn):
        if isinstance(x, dict): [_walk(v, fn) for v in x.values()]
        elif isinstance(x, list): [_walk(v, fn) for v in x]
        elif isinstance(x, str) and any(c in CONTROL for c in x): ctl.append((fn, x[:40]))
    for fn in os.listdir(os.path.join(ROOT, 'data', 'handwritten')):
        if fn.endswith('.json'): _walk(json.load(open(os.path.join(ROOT, 'data', 'handwritten', fn), encoding='utf8')), fn)
    print('14. control characters in the hand-written data: ' + (f'FOUND {ctl[:3]!r}' if ctl else 'none'))
    if ctl: problems.append('control characters in data/handwritten (a backslash escape lost in a shell?)')
except (OSError, ValueError) as e:
    print('14. hand-written data check failed:', e)

# 15. a page that carries the perks popup (#more) or the group popup (#pop) wires up its close button, outside click and Escape (bindMore / bindPop of the shared script, or the page's own handlers)
try:
    unwired = []
    for fn in sorted(os.listdir(os.path.join(ROOT, 'docs'))):
        if not fn.endswith('.html'): continue
        t = open(os.path.join(ROOT, 'docs', fn), encoding='utf8').read()
        if 'id="more"' in t and t.count('bindMore()') < 2 and 'function closeMore' not in t: unwired.append((fn, 'more'))
        if 'id="pop"' in t and t.count('bindPop()') < 2 and 'function closePop' not in t: unwired.append((fn, 'pop'))
    print('15. popups wired up on the pages: ' + (f'NOT WIRED {unwired}' if unwired else 'ok'))
    if unwired: problems.append(f'a popup cannot be closed on {unwired}')
except OSError as e:
    print('15. popup check failed:', e)

# 16. every object of the wiki (a button with the class "cell") is made by makeCell() of the shared script, which gives it its reference (data-obj); a template that builds one by hand would leave it out of everything that works on all objects
try:
    by_hand = []
    for fn in sorted(os.listdir(os.path.join(ROOT, 'tools', 'pages', 'templates'))):
        if not fn.endswith(('.html', '.js')): continue
        for i, line in enumerate(open(os.path.join(ROOT, 'tools', 'pages', 'templates', fn), encoding='utf8'), 1):
            if re.search(r"""(?:el|ce)\('button',\s*'cell|createElement\('button'\).*'cell""", line) and 'b.className=\'cell\'+(cls' not in line:      # the one place that makes them is makeCell itself
                by_hand.append(f'{fn}:{i}')
    print('16. objects made by makeCell: ' + (f'BUILT BY HAND {by_hand}' if by_hand else 'ok'))
    if by_hand: problems.append(f'objects built without makeCell at {by_hand}')
except OSError as e:
    print('16. object check failed:', e)

print('\nOK' if not problems else '\nLOOK AT: ' + '; '.join(problems))
sys.exit(1 if problems else 0)
