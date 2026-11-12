"""A challenge as the pages show it (name, requirements, the challenge, reward, formulas ...), shared by the Challenges page and the Factions page.
The hover popup is `challengeTip` in tools/pages/templates/shared.js.
"""
import json, os, shutil
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
factions = json.load(open(os.path.join(ROOT, 'data', 'generated/challenges.json'), encoding='utf8'))
icons = json.load(open(os.path.join(ROOT, 'data', 'generated/icons.json')))
sprites = json.load(open(os.path.join(ROOT, 'data', 'derived/sprites.json')))
icon_dir = os.path.join(ROOT, 'docs', 'assets', 'icons')
os.makedirs(icon_dir, exist_ok=True)


def icon_file(n):
    """the icon, copied from the game assets to docs/assets/icons"""
    if not n or n not in sprites: return None
    dst = os.path.basename(sprites[n][0]['file'])
    path = os.path.join(icon_dir, dst)
    if not os.path.exists(path):
        src = os.path.join(ROOT, sprites[n][0]['file'])
        if os.path.exists(src): shutil.copy(src, path)
    if not os.path.exists(path): return None
    icons[n] = dst
    return dst


def item(f, it):
    return {'n': it['name'], 'i': icon_file(it['icon']), 'su': it['spell_upgrade'], 'num': it['number'],
            'fl': it['flavor'], 'q': it['requirements'], 'c': it['challenge'], 'r': it['rewards'],
            'f': [{'l': g['latex'], 'v': g['vars'], 'lb': g['label']} for g in it['formulas']], 'a': it['applies_to'], 'sh': any(g['shown'] for g in it['formulas']), 'nt': it['note'], 'rn': it.get('rnotes') or [],
            'g': it['game_name']}


def section(f):
    """a faction's challenges: {id, name (the faction's name in the challenge data: Elven, Dwarven ...), kind, items}"""
    return {'id': f['id'], 'name': f['name'], 'kind': f['kind'], 'items': [item(f, it) for it in f['items']]}
