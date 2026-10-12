"""The game's short number notation ("10 M", "1.5 B", "2 Qa") rewritten as powers of ten ("10⁷", "1.5 × 10⁹").

The suffix table is read from the game's number formatter, so every suffix it can print is understood.
"""
import os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
_src = open(os.path.join(ROOT, 'out', 'script', 'scripts', '§-D§.as'), encoding='utf8').read()
_suffixes = [x.strip() for x in re.findall(r'"( [A-Za-z]+)"', re.search(r'§1X§:Array = \[(.*?)\];', _src).group(1))]
SUFFIX_EXP = {sfx: 6 + 3 * i for i, sfx in enumerate(_suffixes)}
SUFFIX_RE = re.compile(r'(?<![\w.])(\d+(?:\.\d+)?) ?(' + '|'.join(sorted(map(re.escape, SUFFIX_EXP), key=len, reverse=True))
                       + r')(?![A-Za-z])')
_SUP = str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻')


def pow10_text(text):
    """'10 M' -> '10⁷', '1.5 B' -> '1.5 × 10⁹' (plain numbers and times are left alone)."""
    def rep(m):
        mant, e = float(m.group(1)), SUFFIX_EXP[m.group(2)]
        while mant >= 10: mant /= 10; e += 1
        while 0 < mant < 1: mant *= 10; e -= 1
        mant = round(mant, 6)
        pw = '10' + str(e).translate(_SUP)
        return pw if mant == 1 else f'{mant:g} × {pw}'
    return SUFFIX_RE.sub(rep, text)
