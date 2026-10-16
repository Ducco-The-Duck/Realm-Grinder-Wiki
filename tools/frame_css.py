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
    """vertical gradient of the sprite's left (x=0) or right (x=19) column: 5 rows fixed at each end, the middle stretched.
    Positions are the shared variables --q0..--q10 (the stretched middle) and --e1..--e5 (from the bottom edge)."""
    col = [rows[y][x] for y in range(20)]
    for y in range(20):                      # the rounded corner pixels are transparent: borrow the next row
        if col[y][3] == 0: col[y] = col[y + 1] if y < 10 else col[y - 1]

    def pos(y):                              # start of row y
        if y <= 5: return f'{y}px'
        if y < 15: return f'var(--q{y - 5})'
        return 'calc(100% - ' + str(20 - y) + 'px)' if y < 20 else '100%'
    runs = []                                # (colour, first row, last row + 1)
    for y in range(20):
        if runs and runs[-1][0] == col[y]: runs[-1][2] = y + 1
        else: runs.append([col[y], y, y + 1])
    return 'linear-gradient(to bottom,' + ','.join(f'{hexc(c)} {pos(a)} {pos(b)}' for c, a, b in runs) + ')'


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
    gl, gr = side_gradient(rows, 0), side_gradient(rows, 19)
    return (f'--{k}t:{hexc(top)};--{k}b:{hexc(bot)};--{k}l:{gl};--{k}r:{"var(--" + k + "l)" if gr == gl else gr};'
            f'--{k}c:{hexc(fill)};--{k}s:{",".join(shadows) or "none"}')


def frame_css():
    out = [
        '.cell{position:relative;padding:0;border:5px solid transparent;border-radius:0;background:none;--q1:calc(5px + (100% - 10px) * 0.1);--q2:calc(5px + (100% - 10px) * 0.2);--q3:calc(5px + (100% - 10px) * 0.3);--q4:calc(5px + (100% - 10px) * 0.4);--q5:calc(5px + (100% - 10px) * 0.5);--q6:calc(5px + (100% - 10px) * 0.6);--q7:calc(5px + (100% - 10px) * 0.7);--q8:calc(5px + (100% - 10px) * 0.8);--q9:calc(5px + (100% - 10px) * 0.9);--q10:calc(5px + (100% - 10px) * 1)}',
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
