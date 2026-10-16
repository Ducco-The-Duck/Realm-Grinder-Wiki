"""CSS for the icon frames, generated from the game's 20x20 trim sprites (docs/assets/ui/trim).

The frames used to be drawn with `border-image`; on pages with a thousand cells that left the edge that had just scrolled
into view clipped for a moment.  This draws the same frame with plain borders, gradients and inset shadows on a pseudo
element (no images): outer 1px line (top and bottom lines of their own colour, the sides a vertical gradient), then the
rings of the sprite as inset shadows, then the fill.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pngpix import pixels

TRIM = os.path.join(os.path.dirname(__file__), '..', 'docs', 'assets', 'ui', 'trim')
THEMES = [('', 'Gold', 'Gold_Hover')] + [(n, n + 'Trim', n + 'Trim_Hover') for n in (
    'Fairy', 'Elven', 'Angel', 'Goblin', 'Undead', 'Demon', 'Titan', 'Druid', 'Faceless', 'Dwarven', 'Drow', 'Mercenary',
    'Dragon', 'Archon', 'Djinn', 'Makers', 'Good', 'Evil', 'Order', 'Chaos', 'Balance')] + [('Silver', 'Silver', 'Silver')]


def hexc(p):
    return '#%02x%02x%02x' % p[:3]


def side_gradient(rows, x):
    """vertical gradient of the sprite's left (x=0) or right (x=19) column: 5 rows fixed at each end, the middle stretched"""
    col = [rows[y][x] for y in range(20)]
    for y in range(20):                      # the rounded corner pixels are transparent: borrow the next row
        if col[y][3] == 0: col[y] = col[y + 1] if y < 10 else col[y - 1]
    segs = []                                # (colour, start, end) with start/end as CSS lengths
    for y in range(20):
        if y < 5: a, b = f'{y}px', f'{y + 1}px'
        elif y < 15: a, b = f'calc(5px + (100% - 10px) * {(y - 5) / 10:g})', f'calc(5px + (100% - 10px) * {(y - 4) / 10:g})'
        else: a, b = f'calc(100% - {20 - y}px)', f'calc(100% - {19 - y}px)'
        if segs and segs[-1][0] == col[y]: segs[-1] = (col[y], segs[-1][1], b)
        else: segs.append((col[y], a, b))
    return 'linear-gradient(to bottom,' + ','.join(f'{hexc(c)} {a},{hexc(c)} {b}' for c, a, b in segs) + ')'


def props(rows, k):
    top, bot = rows[0][10], rows[19][10]
    seq = [rows[r][10] for r in range(1, 5)] + [rows[10][10]]       # rings 1..4 then the fill
    runs = []
    for c in seq:
        if runs and runs[-1][0] == c: runs[-1][1] += 1
        else: runs.append([c, 1])
    fill = runs[-1][0]
    shadows, spread = [], 0
    for c, n in runs[:-1]:
        spread += n
        shadows.append(f'inset 0 0 0 {spread}px {hexc(c)}')
    return (f'--{k}t:{hexc(top)};--{k}b:{hexc(bot)};--{k}l:{side_gradient(rows, 0)};--{k}r:{side_gradient(rows, 19)};'
            f'--{k}c:{hexc(fill)};--{k}s:{",".join(shadows) or "none"}')


def frame_css():
    out = [
        '.cell{position:relative;padding:0;border:5px solid transparent;border-radius:0;background:none}',
        # the frame is a pseudo element over the border area, under the icon
        '.cell::before{content:"";position:absolute;inset:-5px;box-sizing:border-box;pointer-events:none;border:1px solid transparent;'
        'border-top-color:var(--fxt);border-bottom-color:var(--fxb);background-color:var(--fxc);'
        'background-image:var(--fxl),var(--fxr);background-position:left top,right top;background-size:1px 100%,1px 100%;'
        'background-repeat:no-repeat;background-origin:border-box;background-clip:border-box;box-shadow:var(--fxs)}',
        '.cell:hover::before,.cell:focus-visible::before{border-top-color:var(--hxt);border-bottom-color:var(--hxb);background-color:var(--hxc);'
        'background-image:var(--hxl),var(--hxr);box-shadow:var(--hxs)}',
    ]
    for name, normal, hover in THEMES:
        rows_n = pixels(os.path.join(TRIM, normal + '.png'))[2]
        rows_h = pixels(os.path.join(TRIM, hover + '.png'))[2]
        sel = '.cell' if not name else f'.t-{name}'
        out.append(f'{sel}{{{props(rows_n, "fx")};{props(rows_h, "hx")}}}')
    return '\n'.join(out)


if __name__ == '__main__':
    print(frame_css())
