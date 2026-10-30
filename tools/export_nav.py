"""Copy the sprites of the game's tab buttons (the left-hand Upgrades / Trophies / ... column) for the wiki's nav.

    python -I tools/export_nav.py

Reads assets/sprites/realmgrinderui_new (made by slice_atlases.py), writes docs/assets/ui/nav/.
"""
import os, shutil, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'assets', 'sprites', 'realmgrinderui_new')
DST = os.path.join(ROOT, 'docs', 'assets', 'ui', 'nav')
NAMES = ['UiBuildings', 'UiUpgrades', 'UiTrophies', 'UiExcavation', 'UiResearch', 'UiChallenges', 'redRibbon', 'redRibbon_Selected', 'UICrystalBall']
os.makedirs(DST, exist_ok=True)
for n in NAMES:
    src = os.path.join(SRC, n + '.png')
    if not os.path.exists(src): src = os.path.join(os.path.dirname(SRC), 'realmgrinderui2_new', n + '.png')
    if n == 'UICrystalBall':
        # the sprite has the word "SCRY" under the ball: keep the ball only (rows above the text, found as the first row wider than the ball's bottom), in a square
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib'))
        from PIL import Image
        im = Image.open(src).convert('RGBA')
        rows = [sum(1 for x in range(im.width) if im.getpixel((x, y))[3] > 0) for y in range(im.height)]
        top = next(y for y, r in enumerate(rows) if r)
        ball_bottom = next(y for y in range(top + 20, im.height) if rows[y] > rows[y - 1] + 5) - 1      # the text is wider than the narrowing bottom of the ball
        ball = im.crop((0, top, im.width, ball_bottom + 1))
        ball = ball.crop(ball.getbbox())
        side = max(ball.size)
        out = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        out.paste(ball, ((side - ball.width) // 2, (side - ball.height) // 2))
        out.save(os.path.join(DST, n + '.png'))
        continue
    shutil.copyfile(src, os.path.join(DST, n + '.png'))
print('nav sprites:', len(NAMES))
