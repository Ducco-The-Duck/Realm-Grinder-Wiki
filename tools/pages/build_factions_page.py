"""Generate docs/factions.html: the base factions in a grid (alignment down, axis across), the prestige factions beside their alignment and the astral factions
under their axis, each as its alliance icon; clicking one opens its details: the Trade Treaty text, its upgrades, spell and unique buildings.

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
treaties = {u['name']: ' '.join(p['text'] for p in u['description']) for u in json.load(open(os.path.join(ROOT, 'data', 'generated/upgrade_pages.json'), encoding='utf8'))['allegiances'] if u['name'].endswith('Trade Treaty') or u['name'] == 'Mercenary First Contract'}
FU = json.load(open(os.path.join(ROOT, 'data', 'derived/faction_upgrades.json'), encoding='utf8'))      # the upgrades of each faction (from the Upgrades page builder)
UB = json.load(open(os.path.join(ROOT, 'data', 'derived/unique_buildings.json'), encoding='utf8'))      # the unique buildings (from the Buildings page builder)
SC = json.load(open(os.path.join(ROOT, 'data', 'derived/spell_cards.json'), encoding='utf8'))      # the spells (from the Spells page builder)
MAXA = json.load(open(os.path.join(ROOT, 'data', 'generated/research_meta.json'), encoding='utf8'))['max_ascension']


def icon_file(n):
    """the alliance icon of the game, copied from the game assets to docs/assets/icons"""
    assert n in sprites, ('no such icon in the game assets', n)
    dst = os.path.basename(sprites[n][0]['file'])
    path = os.path.join(ROOT, 'docs', 'assets', 'icons', dst)
    if not os.path.exists(path): shutil.copy(os.path.join(ROOT, sprites[n][0]['file']), path)
    return dst


out = []
for f in factions.FACTIONS:
    out.append({'name': f['n'], 'icon': icon_file('MercenaryBadge' if f['n'] == 'Mercenary' else ICON.get(f['n'], f['n']) + 'Alliance'), 'al': AL.get(f.get('al')), 'ax': AX.get(f.get('ax')),
                'i': f['i'], 'merc': f['role'] == 'merc', 'blurb': treaties['Mercenary First Contract' if f['role'] == 'merc' else TREATY.get(f['n'], f['n']) + ' Trade Treaty'], 'asp': FU['f'][str(f['i'])], 'tags': [t for t in (AL.get(f.get('al')), AX.get(f.get('ax'))) if t]})
mech0 = next(m for m in json.load(open(os.path.join(ROOT, 'data', 'handwritten/unlocks.json'), encoding='utf8'))['mechanics'] if m['name'] == 'Factions')
for f in out: f['note'] = mech0.get('faction_notes', {}).get(f['name'])      # when the faction can be unlocked (hand-written, shown under its name)
assert len(out) == 16 and all((f['al'] or f['ax'] or f['merc']) for f in out)
for n in sorted({c['tags'][0] for c in SC.values() if c['tags']} & {'Good', 'Evil', 'Neutral', 'Order', 'Chaos', 'Balance'}):      # the spell boxes of the game
    for st in ('Up', 'Hover', 'Down'):
        dst = os.path.join(ROOT, 'docs', 'assets', 'ui', f'spellBox_{n}_{st}.png')
        if not os.path.exists(dst): shutil.copy(os.path.join(ROOT, sprites[f'spellBox_{n}_{st}'][0]['file']), dst)
USED_SPELLS = {f['asp']['spell'] for f in out if f['asp']['spell']}
USED_BUILDINGS = {b for f in out for b in f['asp']['uniques']}
import re, artifact_items, challenge_items
CH = {f['id']: challenge_items.section(f) for f in challenge_items.factions}      # each faction's challenges (the Challenges page's data)
for f in out:      # the lore artifacts of the faction's Artifact Set (the Set upgrade names them in its unlock requirements)
    st = f['asp']['set']
    f['asp']['arts'] = [re.match(r'Artifact: (.*?)(?: \(|$)', x).group(1) for x in FU['items'][st]['s'] if x.startswith('Artifact: ')] if st else []
ARTS = artifact_items.by_name(list(dict.fromkeys(n for f in out for n in f['asp']['arts'])))
data = json.dumps({'factions': out, 'chal': {str(k): v for k, v in CH.items()}, 'arts': ARTS, 'items': FU['items'], 'spells': {k: v for k, v in SC.items() if k in USED_SPELLS}, 'buildings': {k: v for k, v in UB.items() if k in USED_BUILDINGS}, 'coins': __import__('costs').names(), 'max': MAXA}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\/')
mech = next(m for m in json.load(open(os.path.join(ROOT, 'data', 'handwritten/unlocks.json'), encoding='utf8'))['mechanics'] if m['name'] == 'Factions')
import html as _html
BLURB = _html.escape(next(s for s in mech['sections'] if s['title'] == 'What they are')['text'])      # the same text as on the Mechanics page
page = search_snippet.apply(tmpl.load('factions.html').replace('__DATA__', data).replace('__BLURB__', BLURB), '', 'factions.html')
open(os.path.join(ROOT, 'docs', 'factions.html'), 'w', encoding='utf8').write(page)
print('docs/factions.html', len(page) // 1024, 'KB;', len(out), 'factions')
