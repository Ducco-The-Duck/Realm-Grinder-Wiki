"""Translate an artifact's find-chance expression (ActionScript) into a LaTeX formula plus a list
of named variables.  Only inputs listed in VARS / ENTITY_VARS are understood; anything else makes
`convert` return None so the caller can fall back to generic wording.

The chance is a percentage rolled once per excavation.  The meaning of each input is documented
(with confidence) in data/INFERENCES.md.
"""
import ast, re
from helper_calls import subst_helpers, subst_stats, to_py_ternary

FACTION = {0: 'Fairy', 1: 'Elf', 2: 'Angel', 3: 'Goblin', 4: 'Undead', 5: 'Demon', 6: 'Titan', 7: 'Druid',
           8: 'Faceless', 9: 'Dwarf', 10: 'Drow', 11: 'Mercenary', 12: 'Dragon', 13: 'Archon'}
BRANCH = ['Spellcraft', 'Craftsmanship', 'Divine', 'Economics', 'Alchemy', 'Warfare', 'Forbidden']
SCOPE = {'era': 'in this Era', 'reinc': 'in this Reincarnation', 'all': 'all-time'}


def stat_desc(i, scope):
    """Description of stat array index i summed over `scope`, or None if unknown."""
    if i == 3: return f'Time spent with Evil alignment {SCOPE[scope]} (seconds)'
    if 50 <= i <= 63: return f'Time spent as {FACTION[i - 50]} {SCOPE[scope]} (seconds)'
    if i == 49: return f'Number of times you affiliated with the Mercenaries {SCOPE[scope]}'
    if i == 1: return f'Time played {SCOPE[scope]} (seconds)'
    if i == 4: return f'Clicks made {SCOPE[scope]}'
    if i == 24: return f'Royal Exchanges made {SCOPE[scope]}'
    return None


def stat_sym(i):
    return 'N' if i in (49, 4, 24) else 't'


S = r'§[^§]*§'
G = r'§8G§\.'
STAT_ALL = G + r'§5!V§\[(\d+)\] \+ ' + G + r'§=y§\[\1\] \+ ' + G + r'§@w§\[\1\]'

# regex (on the raw expression) -> (tex symbol, description or fn(match) -> description)
# Order matters: longer / more specific patterns first.
VARS = [
    (r'\(' + G + r'§5!V§\[104\] \+ ' + G + r'§=y§\[104\] \+ ' + G + r'§5!V§\[135\] \+ ' + G + r'§=y§\[135\]\)',
     'R', 'Excavation Resets made in this Reincarnation (regular and free)'),
    (G + r'§5!V§\[135\] \+ ' + G + r'§=y§\[135\] \+ ' + G + r'§5!V§\[104\] \+ ' + G + r'§=y§\[104\]',
     'R', 'Excavation Resets made in this Reincarnation (regular and free)'),
    (r'\(' + G + r'§5!V§\[135\] \+ ' + G + r'§5!V§\[104\]\)', 'R', 'Excavation Resets made in this Era (regular and free)'),
    (r'\(' + STAT_ALL + r'\)', lambda m: stat_sym(int(m.group(1))), lambda m: stat_desc(int(m.group(1)), 'all')),
    (STAT_ALL, lambda m: stat_sym(int(m.group(1))), lambda m: stat_desc(int(m.group(1)), 'all')),
    (r'§&c§\.§"!B§\((\d+),true,false,false,true\)', lambda m: stat_sym(int(m.group(1))),
     lambda m: stat_desc(int(m.group(1)), 'all')),
    (r'§&c§\.§ !;§\((\d+)\)', lambda m: stat_sym(int(m.group(1))), lambda m: stat_desc(int(m.group(1)), 'all')),
    (r'§&c§\.§1",§\(\)', 'P', 'Research points you have spent on researches'),
    (r'§&c§\.§&!<§\((\d),true\)', 'P',
     lambda m: f'{BRANCH[int(m.group(1))]} Research points bought, all-time (before bonus multipliers)'),
    (r'§#!!§\.§,d§\(\)', 'O', 'Your Offline production bonus'),
    (r'§&c§\.§\]!s§\(2,false,false,true\)', 'T',
     'Total number of casts of all Evil spells in this Reincarnation (before bonus multipliers)'),
    (r'§&c§\.§\]!s§\(2,false,true,true\)', 'T',
     'Total number of casts of all Evil spells in this Era (before bonus multipliers)'),
    (r'\(' + G + r'§5!V§\[4\] \+ ' + G + r'§=y§\[4\]\)', 'C', 'Clicks made in this Reincarnation'),
    (r'§&c§\.§>!h§\(false,false,true\)', 'C', 'Clicks made in this Reincarnation (before bonus multipliers)'),
    (G + r'§5!V§\[4\]', 'C', 'Clicks made in this Era'),
    (G + r'§5!V§\[1\]', 'E', 'Time played in this Era (seconds)'),
    (G + r'§=y§\[39\]', r'E_{\max}', 'Length of your longest Era in this Reincarnation, not counting the current one (seconds)'),
    (G + r'§5!V§\[24\]', 'N', 'Royal Exchanges made in this Era'),
    (r'§#!!§\.§@!\?§\(\)', 'X', 'Your Royal Exchange bonus (%)'),
    (r'§&c§\.§0#§\(-1,true\)', 'B', 'Total buildings you own'),
    (r'§&c§\.§@!\[§\(true,false,true\)', 'F', 'Faction Coins found in this Era'),
    (r'§&c§\.§@!\[§\(false,false,true\)', 'F', 'Faction Coins found in this Reincarnation (before bonus multipliers)'),
    (r'§#!!§\.§0F§\(\)', 'Q', 'Your Faction Coin find chance (%)'),
    (r'§#!!§\.§!-§\(\)', 'A', 'Your number of assistants (before multipliers)'),
    (r'§&c§\.§!-§\(false,true\)', 'A', 'Your Base Assistants (as shown in the game)'),
    (r'Math\.max\(' + G + r'§5!V§\[96\],' + G + r'§=y§\[96\]\)', r'A_{\max}',
     'Highest number of assistants you have had in this Reincarnation'),
    (r'§#!!§\.§57§\(\) \* 30', 'M', 'Your mana regeneration per second (the m/s shown in game)'),
    (r'§#!!§\.§2!&§\(\)', r'M_{\max}', 'Your Maximum Mana'),
    (r'Math\.max\(' + G + r'§5!V§\[133\],' + G + r'§=y§\[133\]\)', r'M_{\max}',
     'Highest Maximum Mana you have had in this Reincarnation'),
    (r'§&c§\.§3"&§\(true,false,true\)', 'W', 'Mana produced in this Era (before bonus multipliers)'),
    (G + r'§=y§\[101\]', 'L', 'Longest Elven Luck streak in this Reincarnation (clicks in a row that triggered Elven Luck)'),
    (G + r'§1!#§\[(\d+)\]', 'L', lambda m: f'Your {FACTION[int(m.group(1))]} Lineage level'),
    (r'§&c§\.§`!=§\(\)', 'L', 'Your total Lineage level (all factions added together)'),
    (G + r'§8!H§', 'R', 'Your Reincarnation number'),
    (G + r'§1!5§', 'N', 'Excavations made since your last Excavation Reset (the game\'s "Excavations" counter)'),
    (G + r'§\["&§', 'D', 'Consecutive days you have logged in (days counted in UTC)'),
    (r'§&c§\.§,o§\(' + G + r'§"!0§\)', 'G', 'Order of magnitude of your Gems (e.g. 3.2e45 Gems counts as 45)'),
    (r'§@W§\.§\'!b§\(\)', 'K', 'Combo Strike\'s current production bonus (%)'),
    (r'\(' + G + r'§#N§\(§%!J§\.id\) as §%!J§\)\.§"!P§\(\)', 'H', 'Brainwave\'s headstart time (seconds)'),
    (r'§&c§\.§\?&§\(true\)', 'S', 'Total tier of your active spells (each active spell counts its tier)'),
    (r'§&c§\.§"" §\(false,false,true\)', 'U',
     'Activity time of your most used spell in this Reincarnation (seconds; a few spells such as Tax Collection are not counted)'),
]

# patterns with one entity token (group 1); description gets the entity's display name
SPELL_SCOPE = {('false', 'true'): 'era', ('false', 'false'): 'reinc', ('true', 'false'): 'all'}
ENTITY_VARS = [
    (G + r'§#N§\((' + S + r')\.id\)\.§2-§', 'spell', 'S', lambda n, m: f'Number of times you have cast "{n}" in this Era'),
    (r'§&c§\.§9!P§\((' + S + r')\.id,false,true,true\)', 'spell', 'S',
     lambda n, m: f'Number of times you have cast "{n}" in this Era (before bonus multipliers)'),
    (r'§&c§\.§7i§\((' + S + r')\.id,(true|false),(true|false),true\)', 'spell', 't',
     lambda n, m: f'Activity time of "{n}" {SCOPE[SPELL_SCOPE[(m.group(2), m.group(3))]]} (seconds)'
     if (m.group(2), m.group(3)) in SPELL_SCOPE else None),
    (r'§&c§\.§1!;§\((' + S + r')\.id,true\)', 'spell', 'D',
     lambda n, m: f'Duration of "{n}" (seconds, as set when it was cast)'),
    (G + r'§%Z§\((' + S + r')\.id,true\)', 'building', 'N', lambda n, m: f'Number of "{n}" buildings you own (bonuses that make buildings count as more are not included)'),
    (G + r'§%Z§\((' + S + r')\.id\)', 'building', 'N',
     lambda n, m: f'Number of "{n}" buildings you own'),
]


def convert(expr, name_of):
    """expr: raw AS expression.  name_of(token) -> (kind, display name) or None."""
    slots = {}   # (tex, desc) -> placeholder identifier

    def slot(tex, desc):
        key = (tex, desc)
        if key not in slots: slots[key] = f'v{len(slots)}'
        return slots[key]

    s = expr
    failed = []
    for pat, kind, tex, fn in ENTITY_VARS:
        def rep(m):
            n = name_of(m.group(1))
            d = fn(n[1], m) if n and n[0] == kind else None
            if not d: failed.append(m.group(0)); return m.group(0)
            return slot(tex, d)
        s = re.sub(pat, rep, s)
    for pat, tex, desc in VARS:
        def rep(m):
            t = tex(m) if callable(tex) else tex
            d = desc(m) if callable(desc) else desc
            if not d: return m.group(0)
            return slot(t, d)
        s = re.sub(pat, rep, s)
    s = re.sub(r'§&c§\.§"!B§\(§&c§\.§;!4§\(§&c§\.§7"B§\(§&c§\.§8"3§\(§8G§\.§,!Y§\),§&c§\.§8"3§\(§8G§\.§9!m§\)\)\)\)',
               lambda m: slot('t', 'Time spent as the faction opposite to your current one in this Reincarnation (seconds)'), s)
    s = re.sub(r'§&c§\.§"!0§(?!\()', lambda m: slot('G', 'Your Gems'), s)
    s = re.sub(r'§&c§\.§57§\(\) \* 30', lambda m: slot('M', 'Your mana regeneration per second (the m/s shown in game)'), s)
    s = re.sub(r'§#!!§\.§8!H§(?!\()', lambda m: slot('R', 'Reincarnations you have made'), s)
    s = re.sub(r'§&c§\.§@e§(?!\()', lambda m: slot('Y', 'Gold you own'), s)
    s = re.sub(G + r'§4!Y§', lambda m: slot('N', 'Total number of trophies'), s)

    def _most(m):
        n = name_of(m.group(1))
        return slot('N', f'Most "{n[1]}" buildings you have had in this Reincarnation') if n and n[0] == 'building' else m.group(0)
    s = re.sub(G + r'§\^"C§\((' + S + r')\.id,0\)', _most, s)

    def _tier(m):
        n = name_of(m.group(1))
        return slot('j', f'Tier "{n[1]}" is cast at (1 is the base tier)') if n and n[0] == 'spell' else m.group(0)
    s = re.sub(G + r'§#N§\((' + S + r')\.id\)\.§`r§ \+ 1', _tier, s)
    s = re.sub(G + r'§8t§', lambda m: slot('N', 'Number of trophies you have unlocked'), s)
    s = subst_stats(s, slot)
    s = subst_helpers(s, slot, name_of)
    s = to_py_ternary(s)
    if '§' in s or failed: return None
    s = (s.replace('Math.pow', 'pow').replace('Math.log', 'log').replace('Math.max', 'max').replace('Math.min', 'min')
         .replace('Math.floor', 'floor').replace('Math.abs', 'abs').replace('Math.sqrt', 'sqrt'))
    # symbols shared by several different inputs get subscripts 1, 2, ...
    count = {}
    for tex, _ in slots: count[tex] = count.get(tex, 0) + 1
    seen, sym = {}, {}
    for (tex, desc), v in slots.items():
        if count[tex] > 1:
            seen[tex] = seen.get(tex, 0) + 1
            base = tex.split('_')[0]
            sym[v] = f'{base}_{{{seen[tex]}}}'
        else:
            sym[v] = tex
    try:
        tree = ast.parse(s, mode='eval').body
        tex = to_tex(tree, sym=sym)
    except (SyntaxError, ValueError):
        return None
    return {'latex': 'p = ' + tex, 'vars': [{'symbol': sym[v], 'text': d} for (t, d), v in slots.items()]}


def num(n):
    """Large round numbers as powers of ten (1,000,000 -> 10^{6}; 125,000 -> 1.25 x 10^{5})."""
    if isinstance(n, float) and n.is_integer(): n = int(n)
    if isinstance(n, int) and n >= 10000:
        k, m = 0, n
        while m % 10 == 0:
            m //= 10; k += 1
        if k >= 3:
            digits = len(str(m))
            exp = k + digits - 1
            mant = m if digits == 1 else float(f'{m / 10 ** (digits - 1):.10g}')
            mant = str(int(mant)) if float(mant).is_integer() else str(mant)
            return f'10^{{{exp}}}' if mant == '1' else f'{mant} \\times 10^{{{exp}}}'
        return f'{n:,}'.replace(',', r'\,')
    return str(n)


def to_tex(n, parent=None, sym=None):
    sym = sym or {}
    T = lambda x, p=None: to_tex(x, p, sym)
    if isinstance(n, ast.Constant): return num(n.value)
    if isinstance(n, ast.Name): return sym.get(n.id, n.id)
    if isinstance(n, ast.BinOp):
        op = n.op
        if isinstance(op, ast.Div):
            return r'\frac{' + T(n.left) + '}{' + T(n.right) + '}'
        if isinstance(op, ast.Mult):
            return f'{T(n.left, "*")} \\cdot {T(n.right, "*")}'
        if isinstance(op, (ast.Add, ast.Sub)):
            s = '+' if isinstance(op, ast.Add) else '-'
            t = f'{T(n.left)} {s} {T(n.right, s)}'
            return f'\\left({t}\\right)' if parent in ('*', 'pow', '-') else t
    if isinstance(n, ast.IfExp):
        return (r'\begin{cases} ' + T(n.body) + r' & \text{if } ' + T(n.test) + r' \\ ' + T(n.orelse)
                + r' & \text{otherwise} \end{cases}')
    if isinstance(n, ast.Compare) and len(n.ops) == 1:
        op = {ast.Gt: '>', ast.GtE: r'\ge', ast.Lt: '<', ast.LtE: r'\le'}.get(type(n.ops[0]))
        if op: return f'{T(n.left)} {op} {T(n.comparators[0])}'
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub): return '-' + T(n.operand, '*')
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
        f = n.func.id; a = n.args
        if f in ('floor', 'int') and len(a) == 1: return r'\left\lfloor ' + T(a[0]) + r' \right\rfloor'
        if f == 'abs' and len(a) == 1: return r'\left|' + T(a[0]) + r'\right|'
        if f == 'sqrt' and len(a) == 1: return r'\sqrt{' + T(a[0]) + '}'
        if f == 'pow' and len(a) == 2:
            base = T(a[0])
            if not (isinstance(a[0], ast.Name) and '_' not in sym.get(a[0].id, a[0].id)):
                base = '\\left(' + base + '\\right)'
            return base + '^{' + T(a[1]) + '}'
        if f == 'log' and len(a) == 1:
            return '\\ln\\left(' + T(a[0]) + '\\right)'
        if f in ('max', 'min'):
            return f'\\{f}\\left(' + ', '.join(T(x) for x in a) + '\\right)'
    raise ValueError('unsupported')
