"""Stamp docs/index.html (written by hand) with the game version and give it the same tab nav as the generated pages.

    python -I tools/pages/build_index.py
"""
import os, sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d) for d in ('extract', 'export', 'manual', 'pages', 'checks')]
import search_snippet
p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'docs', 'index.html')
html = open(p, encoding='utf8').read()
import re
html = search_snippet.put_nav(html)
html = re.sub(r'/\*NAVCSS\*/.*?/\*ENDNAVCSS\*/', '', html, flags=re.S).replace('</style>', search_snippet.NAV_CSS + '</style>', 1)
open(p, 'w', encoding='utf8').write(search_snippet.stamp(html))
print('docs/index.html stamped with game version', search_snippet.game_version())
