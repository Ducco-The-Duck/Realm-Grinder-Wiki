"""Slice the game's Starling/TexturePacker atlases into individual PNGs.

    python -I tools/slice_atlases.py [game_dir]

Reads <game_dir>/images/*.xml (default: the Steam install), writes
assets/sprites/<atlas>/<name>.png (git-ignored) and data/sprites.json (index).
Trimmed sprites are restored to their original frame size, rotated ones are un-rotated.
"""
import glob, json, os, sys, xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(HERE, 'pylib'))
from PIL import Image

game = sys.argv[1] if len(sys.argv) > 1 else r'C:\games\Steam\steamapps\common\Realm Grinder'
img_dir = os.path.join(game, 'images')
out_root = os.path.join(ROOT, 'assets', 'sprites')
index = {}
dups = []
n = 0
for xml_path in sorted(glob.glob(os.path.join(img_dir, '*.xml'))):
    atlas_xml = ET.parse(xml_path).getroot()
    if atlas_xml.tag != 'TextureAtlas': continue
    atlas = os.path.splitext(os.path.basename(xml_path))[0]
    sheet = Image.open(os.path.join(img_dir, atlas_xml.get('imagePath'))).convert('RGBA')
    out_dir = os.path.join(out_root, atlas)
    os.makedirs(out_dir, exist_ok=True)
    for st in atlas_xml.iter('SubTexture'):
        name = st.get('name')
        x, y, w, h = (int(st.get(k)) for k in ('x', 'y', 'width', 'height'))
        rotated = st.get('rotated') == 'true'
        # width/height are the packed rectangle; a rotated sprite is stored turned 90 deg clockwise.
        box = (x, y, x + w, y + h)
        tile = sheet.crop(box)
        if rotated: tile = tile.transpose(Image.ROTATE_90)
        fx, fy = int(st.get('frameX', 0)), int(st.get('frameY', 0))
        fw, fh = int(st.get('frameWidth', w)), int(st.get('frameHeight', h))
        if st.get('frameWidth') is not None and (fw, fh) != tile.size:
            canvas = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
            canvas.paste(tile, (-fx, -fy))
            tile = canvas
        safe = name.replace('/', '__')
        tile.save(os.path.join(out_dir, safe + '.png'))
        if name in index: dups.append(name)
        index.setdefault(name, []).append({'atlas': atlas, 'file': f'assets/sprites/{atlas}/{safe}.png',
                                           'width': tile.size[0], 'height': tile.size[1]})
        n += 1
    print(atlas, 'ok')

json.dump(index, open(os.path.join(ROOT, 'data', 'sprites.json'), 'w', encoding='utf8'), indent=0, sort_keys=True)
print(n, 'sprites,', len(index), 'unique names,', len(set(dups)), 'names appear in several atlases')
