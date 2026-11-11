"""An artifact as the pages show it (name, hint, unlock requirements, how it is found, flavor text), shared by the Archaeology page and the pages that show an artifact beside a text
(the Unlocks and Mechanics pages, the Challenges page). The hover popup is `artifactTip` in tools/pages/templates/shared.js.
"""
import json, os, shutil
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
artifacts = json.load(open(os.path.join(ROOT, 'data', 'generated/artifacts.json'), encoding='utf8'))
icons = json.load(open(os.path.join(ROOT, 'data', 'generated/icons.json')))
sprites = json.load(open(os.path.join(ROOT, 'data', 'derived/sprites.json')))
icon_dir = os.path.join(ROOT, 'docs', 'assets', 'icons')
os.makedirs(icon_dir, exist_ok=True)


def icon_file(a):
    """the artifact's icon, copied from the game assets to docs/assets/icons"""
    n = a['icon']
    if not n: return None
    dst = os.path.basename(sprites[n][0]['file'])
    path = os.path.join(icon_dir, dst)
    if not os.path.exists(path):
        src = os.path.join(ROOT, sprites[n][0]['file'])
        if os.path.exists(src): shutil.copy(src, path)
    if not os.path.exists(path): return None
    icons[n] = dst
    return dst


def item(a):
    ch = a.get('chance', {})
    return {'n': a['name'], 'f': a['flavor'], 'h': a['hint'], 'q': a['requirements'],
            'x': a['undecoded_conditions'], 'i': icon_file(a),
            'c': ch.get('mode'), 'p': ch.get('percent'), 'l': ch.get('latex'), 'v': ch.get('vars')}


def by_name(names):
    """{name: item} of the artifacts with these names"""
    have = {a['name']: a for a in artifacts}
    assert all(n in have for n in names), ('artifact not found in the game data', [n for n in names if n not in have])
    return {n: item(have[n]) for n in names}
