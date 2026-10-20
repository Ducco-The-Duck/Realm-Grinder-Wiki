"""Stamp docs/index.html (written by hand) with the game version, like the generated pages.

    python -I tools/build_index.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import search_snippet
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'index.html')
html = open(p, encoding='utf8').read()
open(p, 'w', encoding='utf8').write(search_snippet.stamp(html))
print('docs/index.html stamped with game version', search_snippet.game_version())
