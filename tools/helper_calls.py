"""Parameter-aware translation of the game's helper calls (`§&c§.§X§(args)`, `§#!!§.§X§(args)`) and stat
array reads into named inputs for formulas.  Used by chance_latex.convert for research formulas.

Each handler returns (symbol, description) or None when the call (or its parameter combination) is not
understood, in which case the whole formula is left unconverted rather than guessed.  Meanings and their
confidence are recorded in data/INFERENCES.md.
"""
import re

FACTION = {0: 'Fairy', 1: 'Elf', 2: 'Angel', 3: 'Goblin', 4: 'Undead', 5: 'Demon', 6: 'Titan', 7: 'Druid',
           8: 'Faceless', 9: 'Dwarf', 10: 'Drow', 11: 'Mercenary', 12: 'Dragon', 13: 'Archon', 14: 'Djinn', 15: 'Makers'}
BRANCH = ['Spellcraft', 'Craftsmanship', 'Divine', 'Economics', 'Alchemy', 'Warfare', 'Forbidden']
G = r'§8G§\.'

# stat array index -> (symbol, description without scope)
STAT_NAMES = {1: ('t', 'Time played'), 2: ('t', 'Time spent with Good alignment'),
              3: ('t', 'Time spent with Evil alignment'), 14: ('t', 'Time spent with Balance alignment'),
              36: ('t', 'Time spent with Chaos alignment'), 48: ('t', 'Time spent with Order alignment'),
              4: ('C', 'Clicks made'), 15: ('N', 'Spells cast'), 16: ('W', 'Mana produced'),
              24: ('N', 'Royal Exchanges made'), 45: ('t', 'Time spent offline'),
              49: ('N', 'Times you affiliated with the Mercenaries'),
              97: ('t', 'Time spent with at least one spell active'), 102: ('N', 'Rubies collected'),
              13: ('N', 'Upgrades purchased'), 134: ('N', 'Elven Luck triggered')}
for _i in range(50, 64):
    STAT_NAMES[_i] = ('t', f'Time spent as {FACTION.get(_i - 50, "?")}')
TIME_SYMS = {'t'}
# stat index -> description of "highest value in this Reincarnation" (max of this Era and earlier Eras)
MAXSTAT = {40: ('N', 'Most spells cast in a single Era of this Reincarnation'),
           155: ('K', 'Highest Combo Strike counter you had in this Reincarnation'),
           156: ('N', 'Most Grand Balance targets you had at once in this Reincarnation'),
           96: (r'A_{\max}', 'Highest number of assistants you have had in this Reincarnation'),
           133: (r'M_{\max}', 'Highest Maximum Mana you have had in this Reincarnation'),
           39: (r'E_{\max}', 'Length of your longest Era in this Reincarnation (seconds)')}
ALIGN_STAT = {1: 2, 2: 3, 4: 48, 5: 36, 6: 14}
ALIGN_WORD = {-1: 'all', 0: 'Neutral', 1: 'Good', 2: 'Evil', 4: 'Order', 5: 'Chaos', 6: 'Balance'}


def _lit(a):
    a = a.strip()
    if a == 'true': return True
    if a == 'false': return False
    if re.fullmatch(r'-?\d+', a): return int(a)
    return None


def _scope(p2, p3):
    """The game's stat-reader flags: p3 = this Era only, p2 = also all earlier Reincarnations."""
    if p3 and not p2: return 'in this Era'
    if p2 and not p3: return 'all-time'
    if not p2 and not p3: return 'in this Reincarnation'
    return None


def _stat(i, p2, p3):
    sc = _scope(bool(p2), bool(p3))
    if sc is None or i not in STAT_NAMES: return None
    sym, name = STAT_NAMES[i]
    return sym, f'{name} {sc}' + (' (seconds)' if sym in TIME_SYMS else '')


def split_args(a):
    out, depth, cur = [], 0, ''
    for ch in a:
        if ch in '([': depth += 1
        elif ch in ')]': depth -= 1
        if ch == ',' and depth == 0: out.append(cur); cur = ''
        else: cur += ch
    if cur.strip() or out: out.append(cur)
    return [x.strip() for x in out]


def helper_call(cls, mem, args, name_of):
    L = [_lit(x) for x in args]
    g = lambda i, d=False: (L[i] if i < len(L) and L[i] is not None else d)
    C, P = '§&c§', '§#!!§'
    if cls == P:
        if mem == '§,!E§': return 'N', 'Number of trophies you have unlocked'
        if mem == '§@!?§': return 'X', 'Your Royal Exchange bonus (%)'
        if mem == '§&"H§': return 'N', 'Number of faction upgrades you own that are different than your own'
        if mem == '§6!Y§': return 'Z', 'Your production bonus from Gems (%)'
        if mem == '§>Z§' and args:
            n = name_of(args[0].replace('.id', ''))
            if n and n[0] == 'building': return 'Y', f'Production of your "{n[1]}" buildings (per second)'
        return None
    if cls != C: return None
    first = L[0] if L else None
    if mem == '§"!B§' and isinstance(first, int):
        return None if first in (59, 60, 79, 139, 140, 141) else _stat(first, g(1), g(2))
    if mem == '§-"!§' and isinstance(first, int) and first in ALIGN_WORD and first != -1:
        if first == 0:
            sc = _scope(bool(g(1)), bool(g(2)))
            return ('t', f'Time spent with Neutral alignment {sc} (seconds)') if sc else None
        return _stat(ALIGN_STAT[first], g(1), g(2))
    if mem == '§^">§': return 'U', 'Upgrades you have purchased in this Era'
    if mem == '§4!`§' and first in (None, -1): return 'H', 'Highest number of buildings you own of a single type'
    if mem == '§!-§':
        if g(1): return 'A', 'Your Base Assistants (as shown in the game)'
        return 'A', ('Your number of assistants (before multipliers)' if g(0) else 'Your number of assistants')
    if mem == '§3"&§':
        sc = 'in this Era' if g(0) else ('all-time' if g(1) else 'in this Reincarnation')
        # unless the third flag is set the game also applies the "mana produced counts more" bonuses
        # (Druid Perk 5 and the Temporal Flux spell)
        return 'W', f'Mana produced {sc}' + (' (before bonus multipliers)' if g(2) else
                                             ' (counting the bonuses that make mana produced count more)')
    if mem == '§@![§':
        return 'F', 'Faction Coins found ' + ('in this Era' if g(0) else ('all-time' if g(1) else 'in this Reincarnation'))
    if mem == '§>!h§':
        sc = _scope(bool(g(1)), bool(g(0)))
        return ('C', f'Clicks made {sc}') if sc else None
    if mem == '§2!&§': return r'M_{\max}', 'Your Maximum Mana'
    if mem == '§[!j§': return 'N', 'Number of artifacts you have found'
    if mem == '§&!<§':
        if not args or args == ['']: return 'P', 'Your total Research points (all branches)'
        if isinstance(first, int) and 0 <= first < len(BRANCH): return 'P', f'Your {BRANCH[first]} Research points'
        return None
    if mem == '§!!8§': return 'D', 'Your excavation depth (excavations made since your last Excavation Reset)'
    if mem == '§?&§': return 'S', 'Total tier of your active spells (each active spell counts its tier)'
    if mem == '§3L§':
        return 't', 'Time spent offline ' + ('in this Era' if g(0) else 'in this Reincarnation') + ' (seconds)'
    if mem == '§1!y§':
        return 'N', 'Spells cast ' + ('in this Era' if g(0) else ('all-time' if g(1) else 'in this Reincarnation'))
    if mem == '§0#§':
        if not args or args == [''] or first == -1: return 'B', 'Total buildings you have built'
        if first in (0, 1, 2, 4) and len(args) == 1:
            return 'B', f'{ {0: "Neutral", 1: "Good", 2: "Evil", 4: "Order"}[first] } buildings you have built'
        return None
    if mem == '§`!D§': return 'N', 'Royal Exchanges made in this Era'
    if mem == '§`!=§': return 'L', 'Your total Lineage level (all factions added together)'
    if mem == '§=`§': return 'B', 'Unique buildings you have built'
    if mem == '§1"O§': return 'B', 'Non-Unique buildings you have built'
    if mem == '§]!s§' and not args or args == [''] and mem == '§]!s§':
        return 'T', 'Total casts of all spells in this Reincarnation'
    if mem == '§]!s§' and isinstance(first, int) and first in ALIGN_WORD:
        who = 'all spells' if first == -1 else f'all {ALIGN_WORD[first]} spells'
        sc = _scope(bool(g(1)), bool(g(2)))
        if not sc: return None
        return 'T', f'Total casts of {who} {sc}' + (' (before bonus multipliers)' if g(3) else '')
    if mem == '§4!r§':
        return 't', 'Total activity time of your faction spells ' + ('in this Era' if g(0) else 'in this Reincarnation') + ' (seconds)'
    if mem == '§=!>§':
        return 'T', 'Total casts of your faction spells ' + ('in this Era' if g(0) else 'in this Reincarnation')
    if mem == '§"!z§': return 'D', f'Duration of your {"shortest" if g(0) else "longest"} spell (seconds)'
    if mem == '§"" §':
        return 'U', (f'Activity time of your {"least" if g(0) else "most"} used spell '
                     + ('in this Era' if g(1) else 'in this Reincarnation')
                     + ' (seconds; a few spells such as Tax Collection are not counted)')
    if mem == '§&!y§':
        sc = _scope(bool(g(1)), bool(g(2)))
        return ('t', f'Time spent with your {"least" if g(0) else "most"} used alignment {sc} (seconds)') if sc else None
    if mem == '§>!y§':
        return 't', f'Time spent with your {"least" if g(0) else "most"} used faction in this Reincarnation (seconds)'
    if mem == '§ !q§' and len(args) == 1 and first == 96: return MAXSTAT[96]
    if mem == '§ !q§' and len(args) == 1 and first == 146:
        return 'M', 'Highest Mana Regeneration you have had in this Reincarnation'
    if mem == '§="&§' and first == 11: return 'F', 'Demon Coins found in this Era'
    if mem == '§ !;§' and first == 102: return 'N', 'Rubies you have collected (all-time)'
    if mem == '§0F§': return 'Q', 'Your Faction Coin find chance (%)'
    if mem == '§5"5§': return 'L', 'Your lowest Lineage level'
    if mem == '§#"!§':
        return 'N', 'Excavations made ' + ('in this Era' if g(0) else ('all-time' if g(1) else 'in this Reincarnation'))
    if mem == '§,"F§': return 'N', 'Number of different factions in your Legacies'
    if mem == '§9[§': return 't', 'Time spent as your current faction ' + ('all-time' if g(0) else 'in this Reincarnation') + ' (seconds)'
    if mem == '§1!;§' and args:
        n = name_of(args[0].replace('.id', ''))
        if n and n[0] == 'spell': return 'D', f'Duration of "{n[1]}" (seconds)'
    if mem in ('§9!P§', '§7i§') and args:
        n = name_of(args[0].replace('.id', ''))
        if n and n[0] == 'spell':
            sc = _scope(bool(g(1)), bool(g(2)))
            if not sc: return None
            if mem == '§9!P§':
                return 'S', f'Number of times you have cast "{n[1]}" {sc}' + (' (before bonus multipliers)' if g(3) else '')
            return 't', f'Activity time of "{n[1]}" {sc} (seconds)'
    return None


CALL = re.compile(r'(§&c§|§#!!§)\.(§[^§]*§)\(')


def subst_helpers(s, slot, name_of):
    """Replace every understood helper call by a slot identifier."""
    for _ in range(60):
        changed = False
        for m in CALL.finditer(s):
            depth, i = 1, m.end()
            while i < len(s) and depth:
                depth += s[i] == '('; depth -= s[i] == ')'; i += 1
            if depth: return s
            args = split_args(s[m.end():i - 1])
            if m.group(2) == '§1"&§' and len(args) == 1:   # bonus wrapper: the inner value is what matters
                s = s[:m.start()] + '(' + args[0] + ')' + s[i:]; changed = True; break
            r = helper_call(m.group(1), m.group(2), args, name_of)
            if r:
                s = s[:m.start()] + slot(r[0], r[1]) + s[i:]; changed = True; break
        if not changed: break
    return s


STAT_PAIR = re.compile(G + r'§5!V§\[(\d+)\] \+ ' + G + r'§=y§\[\1\]')
STAT_MAX = re.compile(r'Math\.max\(' + G + r'§5!V§\[(\d+)\],' + G + r'§=y§\[\1\]\)')


def subst_stats(s, slot):
    def mx(m):
        i = int(m.group(1))
        return slot(*MAXSTAT[i]) if i in MAXSTAT else m.group(0)
    s = STAT_MAX.sub(mx, s)

    def pr(m):
        r = _stat(int(m.group(1)), False, False)
        return slot(*r) if r else m.group(0)
    return STAT_PAIR.sub(pr, s)


def to_py_ternary(s):
    """JS `c ? a : b` (top level, not nested) -> python conditional expression."""
    if '?' not in s: return s
    depth = 0; q = c = -1
    for i, ch in enumerate(s):
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        elif ch == '?' and depth == 0 and q < 0: q = i
        elif ch == ':' and depth == 0 and q >= 0: c = i; break
    if q < 0 or c < 0: return s
    return f'(({s[q + 1:c].strip()}) if ({s[:q].strip()}) else ({s[c + 1:].strip()}))'
