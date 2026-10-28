"""Copy the sprites of the game's tab buttons (the left-hand Upgrades / Trophies / ... column) for the wiki's nav.

    python -I tools/export_nav.py

Reads assets/sprites/realmgrinderui_new (made by slice_atlases.py), writes docs/assets/ui/nav/.
"""
import os, shutil
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'assets', 'sprites', 'realmgrinderui_new')
DST = os.path.join(ROOT, 'docs', 'assets', 'ui', 'nav')
NAMES = ['UiBuildings', 'UiUpgrades', 'UiTrophies', 'UiExcavation', 'UiResearch', 'UiChallenges', 'redRibbon', 'redRibbon_Selected']
os.makedirs(DST, exist_ok=True)
for n in NAMES:
    shutil.copyfile(os.path.join(SRC, n + '.png'), os.path.join(DST, n + '.png'))
print('nav sprites:', len(NAMES))
