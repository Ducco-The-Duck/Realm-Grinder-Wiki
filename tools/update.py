"""Update the wiki for a game version in one command.

    python -I tools/update.py 4.3.16            # extract raw/4.3.16, check it, make it current, rebuild everything
    python -I tools/update.py 4.3.16 --dry-run  # extract and compare only: nothing is swapped or rebuilt
    python -I tools/update.py 4.3.15            # the version already current: just rebuild (should change nothing)

What it does, in order (it stops at the first problem):
  1. needs raw/<version>/RealmGrinderDesktop.swf and a clean git tree (so the rebuild shows up as a plain diff you can
     throw away with `git checkout -- data docs`; --force skips this check)
  2. extracts into out_<version>/ (kept if it already exists) and reports which script files are new, gone or changed
     and which changelog lines the game added
  3. runs selfcheck.py on the new build: if the game's scrambled names moved it stops, nothing has been swapped yet
  4. makes the new build current: out/ is renamed out_<old version>/ (never overwritten) and the new folder becomes out/
  5. rebuilds the data and every page (the order is in STEPS), then runs selfcheck.py again and diff_data.py

It never commits or pushes, never deletes a build, and never edits the hand-written tables in the tools. What it cannot do
for you: decode a new kind of item or condition, write formulas and notes, or confirm anything in game. Read the summary,
look at the "undecoded" counters and the diff_data list, then commit.
"""
import difflib, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
PY = sys.executable
STEPS = ['parse_mo', 'build_data', 'as3js', 'eval_formulas', 'runtime_icons', 'export_icons', 'export_artifacts',
         'export_challenges', 'export_research', 'export_trophies', 'export_upgrades', 'build_archaeology_page',
         'build_challenges_page', 'build_research_page', 'build_trophies_page', 'build_upgrades_page', 'build_index']      # (effect_tags / build_effects_page: not in use, see data/EFFECT_SEARCH_NOT_IN_USE.md)
# derived files that sit in out/ next to the extraction (kept when the build changes)
EXTRAS = ['text', 'stat_labels.json', 'artifact_survey.txt', 'runtime_icons_unresolved.json']
SCRIPTS = os.path.join('script', 'scripts')


def say(msg=''): print(msg, flush=True)


def die(msg, code=1):
    say('\nSTOPPED: ' + msg)
    sys.exit(code)


def run(args, env=None, quiet=False):
    r = subprocess.run(args, cwd=ROOT, env=env, capture_output=quiet, text=True, encoding='utf8', errors='replace')
    return r


def git_clean():
    r = run(['git', 'status', '--porcelain', '--untracked-files=no'], quiet=True)
    return r.returncode == 0 and not r.stdout.strip()


def read_version(folder):
    try:
        return open(os.path.join(ROOT, folder, 'VERSION')).read().strip()
    except OSError:
        return ''


def find_sh():
    sh = shutil.which('sh')
    if sh: return sh
    git = shutil.which('git')
    if git:
        for rel in (r'..\bin\sh.exe', r'..\..\bin\sh.exe', r'..\usr\bin\sh.exe'):
            p = os.path.normpath(os.path.join(os.path.dirname(git), rel))
            if os.path.exists(p): return p
    die('no `sh` found (Git for Windows brings one); run `sh tools/extract.sh <version> out_<version>` yourself and repeat')


def scripts_of(folder):
    root = os.path.join(ROOT, folder, SCRIPTS)
    d = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith('.as'):
                p = os.path.join(dp, f)
                d[os.path.relpath(p, root)] = p
    return d


def compare_builds(old, new):
    a, b = scripts_of(old), scripts_of(new)
    only_old, only_new = sorted(set(a) - set(b)), sorted(set(b) - set(a))
    changed = [k for k in sorted(set(a) & set(b)) if open(a[k], 'rb').read() != open(b[k], 'rb').read()]
    say(f'script files: {len(a)} in {old}, {len(b)} in {new}')
    say(f'  identical {len(a) - len(only_old) - len(changed)}, changed {len(changed)}, new {len(only_new)}, gone {len(only_old)}')
    for tag, lst in (('changed', changed), ('new', only_new), ('gone', only_old)):
        for k in lst[:60]:
            say('  ' + tag + ' ' + k.encode('ascii', 'replace').decode())
        if len(lst) > 60: say(f'  ... {len(lst) - 60} more {tag}')
    # changelog lines the game added
    log = os.path.join(SCRIPTS, '§&f§.as')
    try:
        x = open(os.path.join(ROOT, old, log), encoding='utf8', errors='replace').read().split('\n')
        y = open(os.path.join(ROOT, new, log), encoding='utf8', errors='replace').read().split('\n')
        added = [l.strip() for l in y if l not in set(x) and l.strip()]
        if added:
            say('changelog lines added by the game:')
            for l in added[:8]: say('  ' + l[:400].encode('ascii', 'replace').decode())
    except OSError:
        pass


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = {a for a in sys.argv[1:] if a.startswith('--')}
    if len(args) != 1: die(__doc__.split('\n\n')[0].strip(), 2)
    ver = args[0]
    swf = os.path.join(ROOT, 'raw', ver, 'RealmGrinderDesktop.swf')
    if not os.path.exists(swf): die(f'missing raw/{ver}/RealmGrinderDesktop.swf')
    if '--force' not in flags and not git_clean():
        die('the git tree has uncommitted changes. Commit or stash them first, so the rebuild shows up as a plain diff '
            '(or pass --force)')
    cur = read_version('out')
    say(f'current build in out/: {cur or "unknown"}; updating to {ver}')

    if cur != ver:
        new = f'out_{ver}'
        if os.path.isdir(os.path.join(ROOT, new)):
            say(f'{new}/ already exists: using it (not extracted again)')
        else:
            say(f'extracting raw/{ver} into {new}/ ...')
            r = run([find_sh(), 'tools/extract.sh', ver, new])
            if r.returncode != 0 or read_version(new) != ver: die('extraction failed')
        if cur: compare_builds('out', new)
        say('\nselfcheck on the new build:')
        env = dict(os.environ, RG_SCRIPTS=os.path.join(ROOT, new, SCRIPTS))
        r = run([PY, '-I', 'tools/selfcheck.py'], env=env)
        if r.returncode != 0:
            die('selfcheck says LOOK AT: the names or structure the tools rely on moved. Nothing was swapped; see '
                'tools/UPDATING.md ("If the obfuscated names change")')
        if '--dry-run' in flags:
            say('\n--dry-run: stopping here. out/ is untouched.')
            return
        old = f'out_{cur or "previous"}'
        if os.path.exists(os.path.join(ROOT, old)): die(f'{old}/ already exists; will not overwrite it. Move or rename it first')
        os.rename(os.path.join(ROOT, 'out'), os.path.join(ROOT, old))
        os.rename(os.path.join(ROOT, new), os.path.join(ROOT, 'out'))
        for e in EXTRAS:
            src, dst = os.path.join(ROOT, old, e), os.path.join(ROOT, 'out', e)
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copytree(src, dst) if os.path.isdir(src) else shutil.copy(src, dst)
        say(f'\nout/ is now {ver}; the previous build is kept as {old}/')
    elif '--dry-run' in flags:
        say('already current; nothing to compare (--dry-run)')
        return

    say('\nrebuilding ...')
    for s in STEPS:
        r = run([PY, '-I', f'tools/{s}.py'], quiet=True)
        last = [l for l in (r.stdout or '').strip().split('\n') if l][-1:] or ['']
        say(f'  {s}: {"ok" if r.returncode == 0 else "FAILED"}  {last[0][:110]}')
        if r.returncode != 0:
            say((r.stderr or '')[-1200:])
            die(f'step {s} failed. Undo the rebuild with `git checkout -- data docs` (the tree was clean before)')

    say('\nselfcheck:')
    run([PY, '-I', 'tools/selfcheck.py'])
    say('\nwhat changed in the data (diff_data.py, against the last commit):')
    run([PY, '-I', 'tools/diff_data.py'])
    say('\nNext: read the lists above, check the "undecoded conditions" numbers, preview the pages, then commit.'
        '\nNothing was committed or pushed. To undo the rebuild: git checkout -- data docs')


if __name__ == '__main__':
    main()
