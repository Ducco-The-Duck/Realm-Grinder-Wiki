"""Search bar shared by the page builders: CSS, the input, and the JS that filters `.cell` buttons.

A page sets `cell._s` (lower-case, accent-free text of what the game shows for the item: name, hint, flavor
text, description) on every cell it wants searchable, then calls `searchInit(root)` once the cells exist.
`qmatch(text)` tells whether a normalised text matches the current query (used to filter stack popups).
"""

import tmpl
CSS = tmpl.load('shared.css')
from frame_css import frame_css
CSS = CSS.replace('/*FRAMES*/', frame_css())

BAR = ('<div class="search"><input id="q" type="search" placeholder="__PLACEHOLDER__" autocomplete="off" '
       'aria-label="Search"><span class="qn" id="qn"></span></div>')

JS = tmpl.load('shared.js')


UPGRADE_PAGES = [('upgrades-allegiance.html', 'Allegiance'), ('upgrades-magic.html', 'Magic'),
                 ('upgrades-secret.html', 'Secret'), ('upgrades-misc.html', 'Miscellaneous')]
CODEX = 'codex.html'      # key of the Codex tab (it has no page of its own)
UNLOCK_PAGES = [(f'unlocks-a{a}.html', f'Ascension {a}') for a in range(5)]      # what the Unlocks entry of the Codex menu opens on hover
CODEX_PAGES = [('mechanics.html', 'Mechanics'), ('unlocks.html', 'Unlocks')]
DROPDOWNS = {'upgrades.html': UPGRADE_PAGES, CODEX: CODEX_PAGES}      # tab key -> its pages


def mech_slug(name):
    import re as _re
    return _re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def mechanics_list():
    """the mechanics of data/handwritten/unlocks.json as (name, href): a mechanic with its own page ("page") links there, the others to their section of the Mechanics page"""
    import json, os
    d = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'data', 'handwritten/unlocks.json'), encoding='utf8'))
    return [(m['name'], m.get('page') or 'mechanics.html#' + mech_slug(m['name'])) for m in d['mechanics']]


HAT = '''<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 17.5h18v2.2H3z" fill="#f2b705" stroke="#3a2a00" stroke-width="1.1" stroke-linejoin="round"/><path d="M5 17.5a7 7 0 0 1 14 0z" fill="#f2b705" stroke="#3a2a00" stroke-width="1.1" stroke-linejoin="round"/><path d="M10.5 10.5V6.8h3v3.7z" fill="#d99a00" stroke="#3a2a00" stroke-width="1" stroke-linejoin="round"/></svg>'''      # the Under construction icon (a hard hat)
UNDER_CONSTRUCTION = '<div class="bugs"><p><b>Under construction:</b> this page is still being written and is not finished yet.</p></div>'


# the nav is the game's tab column laid out in a row: 72x62 button with the icon, the red ribbon (126x34) with the name on it
TABS = [('index.html', 'Home', 'UiBuildings', 0), ('upgrades.html', 'Upgrades', 'UiUpgrades', 0), ('trophies.html', 'Trophies', 'UiTrophies', -6),
        ('archaeology.html', 'Archaeology', 'UiExcavation', -6), ('research.html', 'Research', 'UiResearch', -3), ('challenges.html', 'Challenges', 'UiChallenges', -3), ('codex.html', 'Codex', 'UICrystalBall', 0)]

SMALL = ('UiUpgrades', 'UICrystalBall')

NAV_CSS = tmpl.load('nav.css')


def game_nav(current=None, current_file=None):
    """the nav: `current` is the href of the open page (an upgrade page counts as upgrades.html), `current_file` the upgrade page"""
    out = []
    for href, label, ic, y in TABS:
        cur = ' aria-current="page"' if href == current else ''
        lg = ' long' if len(label) > 10 else ''      # a longer name gets a ribbon a little wider than the frame
        z = ';--z:.84' if ic in SMALL else ''      # sprites that fill their whole square are drawn a little smaller so they stay inside the frame
        inner = f'<img src="assets/ui/nav/{ic}.png" alt="" style="--y:{4 + y}{z}"><span class="n">{label}</span>'
        if href == CODEX:      # the Codex is still being written
            inner += '<span class="uc">'+HAT+'</span>'
        if href in DROPDOWNS:
            def link(f, n):
                own = {h for _, h in mechanics_list() if '#' not in h}      # the pages of mechanics that have their own
                cur_ = f == current_file or (f == 'mechanics.html' and current_file in own) or (f == 'unlocks.html' and current_file in [u for u, _ in UNLOCK_PAGES])
                return f'<a href="{f}"' + (' aria-current="page"' if cur_ else '') + f'>{n}</a>'
            links = ''
            for f, n in DROPDOWNS[href]:
                if f in ('mechanics.html', 'unlocks.html'):      # hovering Mechanics opens the list of the mechanics, hovering Unlocks the pages of the Ascensions
                    sub = ''.join(f'<a href="{h}">{mn}</a>' for mn, h in (mechanics_list() if f == 'mechanics.html' else [(un, uf) for uf, un in UNLOCK_PAGES]))
                    links += f'<span class="dd-item">{link(f, n)}<span class="dd-sub">{sub}</span></span>'
                else:
                    links += link(f, n)
            q = "'"
            if href == CODEX: links = '<span class="uc-note">'+HAT+'Under construction</span>' + links
            out.append(f'<span class="dd-nav"><a class="tab{lg}" role="button" tabindex="0"{cur} onclick="this.parentNode.classList.toggle({q}open{q})">{inner}</a>'
                       f'<span class="dd-menu">{links}</span></span>')
        else:
            out.append(f'<a class="tab{lg}" href="{href}"{cur}>{inner}</a>')
    return '<nav class="tabs">' + ''.join(out) + '</nav>'


def put_nav(html, current_file=None):
    """replace the page's `<nav>` by the game-style one (the open page is read from the old nav)"""
    import re as _re
    old = html[html.find('<nav'):html.find('</nav>')] if '<nav' in html else ''
    m = _re.search(r'<a (?:class="tab" )?href="([^"]+)"[^>]*aria-current="page"', old) or _re.search(r'<a [^>]*role="button"[^>]*(aria-current)', old)
    cur = (m.group(1) if m.group(1) != 'aria-current' else 'upgrades.html') if m else None
    if cur and (cur in [f for f, _ in CODEX_PAGES + UNLOCK_PAGES] or cur in [h for _, h in mechanics_list()]): cur, current_file = CODEX, current_file or cur      # the Codex pages
    return _re.sub(r'<nav[^>]*>.*?</nav>', lambda _: game_nav(cur, current_file), html, count=1, flags=_re.S)


GV_CSS = '.gv{margin-top:36px;text-align:center;font-size:18px;color:var(--muted);opacity:.7}'


def game_version():
    """the game build the pages were made from (out/VERSION, written by tools/extract.sh)"""
    import os
    try:
        return open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'out', 'VERSION')).read().strip()
    except OSError:
        return ''


def stamp(html):
    """a small, faint "Game version X" line at the bottom of the page (replaces an earlier one)"""
    import re as _re
    v = game_version()
    html = _re.sub(r'<div class="gv">.*?</div>', '', html)
    html = _re.sub(r'\.gv\{[^}]*\}', '', html)
    if not v: return html
    if GV_CSS not in html: html = html.replace('</style>', GV_CSS + '</style>', 1)
    return html.replace('</main>', '<div class="gv">Game version ' + v + '</div></main>', 1)


def apply(html, placeholder, current_file=None):
    """Fill the markers of a page template: /*SEARCH_CSS*/, <!--SEARCH_BAR-->, /*SEARCH_JS*/ (and the nav)."""
    import re as _re
    # every page's tooltip placement: remember the side and where the object is, 
    html = _re.sub(r"var y=(\w)\.top-t\.height-8; if\(y<8\) y=\1\.bottom\+8;",
                   lambda m: ("var up=%(a)s.top-t.height-8>=8, y=up?%(a)s.top-t.height-8:%(a)s.bottom+8; "
                              "tip.className=up?'above':'below'; "
                              "tip.style.setProperty('--ax', Math.min(Math.max(%(a)s.left+%(a)s.width/2-x,24),t.width-24)+'px');")
                   % {'a': m.group(1)}, html)
    html = _re.sub(r'<p class="sub">.*?</p>\n?', '', html, flags=_re.S)      # no explanation under the page header
    html = html.replace('<body>', '<body class="steel">', 1)
    html = put_nav(html, current_file)
    html = stamp(html)
    return (html.replace('/*SEARCH_CSS*/', CSS + NAV_CSS).replace('<!--SEARCH_BAR-->', BAR.replace('__PLACEHOLDER__', placeholder))
                .replace('/*SEARCH_JS*/', JS))
