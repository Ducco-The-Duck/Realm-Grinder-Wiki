"""Translate an artifact's find-chance expression (ActionScript) into a LaTeX formula plus a list
of named variables.  Only inputs listed in VARS are understood; anything else makes `convert`
return None so the caller can fall back to generic wording.

The chance is a percentage rolled once per excavation.
"""
import ast, re

# regex (on the raw expression)  ->  (symbol, description)
# Order matters: longer / more specific patterns first.
S = r'§[^§]*§'
VARS = [
    (r'\(§8G§\.§5!V§\[104\] \+ §8G§\.§=y§\[104\] \+ §8G§\.§5!V§\[135\] \+ §8G§\.§=y§\[135\]\)',
     ('R', 'Excavation Resets made in this Reincarnation (regular and free)')),
    (r'§&c§\.§1",§\(\)', ('P', 'Research points you have spent')),
    (r'§#!!§\.§,d§\(\)', ('O', 'Your Offline production bonus')),
    (r'§&c§\.§\]!s§\(2,false,false,true\)',
     ('T', 'Total number of casts of all Evil spells in this Reincarnation (before bonus multipliers)')),
    (r'§8G§\.§5!V§\[4\]', ('C', 'Clicks made in this Era')),
    (r'§8G§\.§5!V§\[1\]', ('E', 'Time played in this Era (seconds)')),
    (r'§#!!§\.§@!\?§\(\)', ('X', 'Your Royal Exchange bonus')),
    (r'§&c§\.§0#§\(-1,true\)', ('B', 'Total buildings you own')),
    (r'§&c§\.§@!\[§\(true,false,true\)', ('F', 'Faction Coins found in this Era')),
    (r'§#!!§\.§!-§\(\)', ('K', 'Your clicking reward (coins per click)')),
    (r'§#!!§\.§57§\(\)', ('M', 'Your mana regeneration (per second)')),
]
SPELL_TIME = re.compile(r'§8G§\.§#N§\((' + S + r')\.id\)\.§2-§')


def convert(expr, spell_name_of):
    """expr: raw AS expression.  spell_name_of(token) -> spell display name or None."""
    used = {}
    s = expr
    # spell activity time (this Era) of one named spell
    def spell(m):
        name = spell_name_of(m.group(1))
        if not name: return m.group(0)
        sym = 'S'
        used[sym] = f'Number of times you have cast "{name}" in this Era'
        return sym
    s = SPELL_TIME.sub(spell, s)
    for pat, (sym, desc) in VARS:
        if re.search(pat, s):
            used[sym] = desc
            s = re.sub(pat, sym, s)
    if '§' in s: return None
    s = s.replace('Math.pow', 'pow').replace('Math.log', 'log').replace('Math.max', 'max')
    try:
        tree = ast.parse(s, mode='eval').body
    except SyntaxError:
        return None
    try:
        tex = to_tex(tree)
    except ValueError:
        return None
    order = [k for k in ['R', 'P', 'O', 'T', 'C', 'E', 'X', 'B', 'F', 'K', 'M', 'S'] if k in used]
    return {'latex': 'p = ' + tex, 'vars': [{'symbol': k, 'text': used[k]} for k in order]}


def num(n):
    if isinstance(n, float) and n.is_integer(): n = int(n)
    if isinstance(n, int) and abs(n) >= 10000:
        return f'{n:,}'.replace(',', r'\,')
    return str(n)


def to_tex(n, parent=None):
    if isinstance(n, ast.Constant): return num(n.value)
    if isinstance(n, ast.Name): return n.id
    if isinstance(n, ast.BinOp):
        op = n.op
        if isinstance(op, ast.Div):
            return r'\frac{' + to_tex(n.left) + '}{' + to_tex(n.right) + '}'
        if isinstance(op, ast.Mult):
            a, b = to_tex(n.left, '*'), to_tex(n.right, '*')
            return f'{a} \\cdot {b}'
        if isinstance(op, (ast.Add, ast.Sub)):
            sym = '+' if isinstance(op, ast.Add) else '-'
            t = f'{to_tex(n.left)} {sym} {to_tex(n.right, sym)}'
            return f'\\left({t}\\right)' if parent in ('*', 'pow', '-') else t
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
        f = n.func.id; a = n.args
        if f == 'pow' and len(a) == 2 and isinstance(a[0], ast.Call) and getattr(a[0].func, 'id', '') == 'log':
            return '\\ln^{' + to_tex(a[1]) + '}\\left(' + to_tex(a[0].args[0]) + '\\right)'
        if f == 'pow' and len(a) == 2:
            return '\\left(' + to_tex(a[0]) + '\\right)^{' + to_tex(a[1]) + '}'
        if f == 'log' and len(a) == 1:
            return '\\ln\\left(' + to_tex(a[0]) + '\\right)'
        if f == 'max':
            return '\\max\\left(' + ', '.join(to_tex(x) for x in a) + '\\right)'
    raise ValueError('unsupported')
