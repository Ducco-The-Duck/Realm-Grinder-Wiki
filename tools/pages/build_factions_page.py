"""Generate docs/factions.html: the base factions in a grid (alignment down, axis across), the prestige factions beside their alignment and the astral factions
under their axis, each as its alliance icon; clicking one opens its details (with the text of its Trade Treaty).

    python -I tools/pages/build_factions_page.py
"""
import json, os, shutil, sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('extract', 'export', 'manual', 'pages', 'checks')]
import tmpl, factions, search_snippet
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
sprites = json.load(open(os.path.join(ROOT, 'data', 'derived/sprites.json')))
AL = {1: 'Good', 2: 'Evil', 3: 'Neutral'}
AX = {4: 'Order', 5: 'Chaos', 6: 'Balance'}
ICON = {'Elf': 'Elven', 'Dwarf': 'Dwarven'}      # the alliance icons carry the in-game adjectives
TREATY = {'Fairy': 'Fairies', 'Elf': 'Elven', 'Angel': 'Angels', 'Goblin': 'Goblins', 'Demon': 'Demons', 'Titan': 'Titans', 'Druid': 'Druids', 'Dwarf': 'Dwarven', 'Dragon': 'Dragons'}      # the names of the Trade Treaties
treaties = {u['name']: ' '.join(p['text'] for p in u['description']) for u in json.load(open(os.path.join(ROOT, 'data', 'generated/upgrade_pages.json'), encoding='utf8'))['allegiances'] if u['name'].endswith('Trade Treaty')}


def icon_file(n):
    """the alliance icon of the game, copied from the game assets to docs/assets/icons"""
    assert n in sprites, ('no such icon in the game assets', n)
    dst = os.path.basename(sprites[n][0]['file'])
    path = os.path.join(ROOT, 'docs', 'assets', 'icons', dst)
    if not os.path.exists(path): shutil.copy(os.path.join(ROOT, sprites[n][0]['file']), path)
    return dst


out = []
for f in factions.FACTIONS:
    if f['role'] == 'merc': continue      # not part of the grid
    out.append({'name': f['n'], 'icon': icon_file(ICON.get(f['n'], f['n']) + 'Alliance'), 'al': AL.get(f.get('al')), 'ax': AX.get(f.get('ax')),
                'blurb': treaties[TREATY.get(f['n'], f['n']) + ' Trade Treaty'], 'tags': [t for t in (AL.get(f.get('al')), AX.get(f.get('ax'))) if t]})
assert len(out) == 15 and all((f['al'] or f['ax']) for f in out)
data = json.dumps(out, ensure_ascii=False, separators=(',', ':')).replace('</', '<\/')
mech = next(m for m in json.load(open(os.path.join(ROOT, 'data', 'handwritten/unlocks.json'), encoding='utf8'))['mechanics'] if m['name'] == 'Factions')
import html as _html
BLURB = _html.escape(next(s for s in mech['sections'] if s['title'] == 'What they are')['text'])      # the same text as on the Mechanics page
page = search_snippet.apply(tmpl.load('factions.html').replace('__DATA__', data).replace('__BLURB__', BLURB).replace('__UC__', search_snippet.UNDER_CONSTRUCTION), '', 'factions.html')
open(os.path.join(ROOT, 'docs', 'factions.html'), 'w', encoding='utf8').write(page)
print('docs/factions.html', len(page) // 1024, 'KB;', len(out), 'factions')
