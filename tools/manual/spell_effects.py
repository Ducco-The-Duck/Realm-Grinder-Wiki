"""How an effect that changes the default value of a spell is written on its own page.

The Spells page names a variable of a spell and its default ("the base bonus, 1500% by default, changed by various
effects") without saying which effect changes it.  The effect says so itself: it carries the change as a formula whose
variable is the one of the spell.  Every default and factor below is read from the value function of the spell in the
game code (data/docs/INFERENCES.md); the part that belongs to the effect is the formula the converter already made for
it, put in at {v}.  `SPELL_EFFECTS` maps the name of an effect to the spec of its formula, per kind of page:

    at      position of the formula to rewrite in the effect's formula list (None: add a new one at the end)
    tmpl    the new formula; {v} is the right-hand side of the formula it replaces
    vars    the variables of the spell the formula introduces: (symbol, text)
    label   what the value is (shown when the effect has several formulas)
    para    (upgrades only) the reward paragraph of the game text the formula belongs to
"""
import re


def S(tmpl, vars, at=0, label=None, para=0):
    return {'tmpl': tmpl, 'vars': vars, 'at': at, 'label': label, 'para': para}


UPGRADES = {
    'Demon Bloodline': S(r'X = 1500 \cdot \left(1 + 0.01 \cdot {v}\right)', [('X', "Blood Frenzy's base bonus (%)")],
                         label='Blood Frenzy base bonus (Evil alignment)', para=1),
    'Angel Bloodline': S(r'X = 1750 \cdot \left({v}\right)', [('X', "Holy Light's base bonus (%)")],
                         label='Holy Light base bonus (Good alignment)', para=1),
    'Faceless Bloodline': S(r'X_{0} = 2500 \cdot \left(1 + 0.01 \cdot {v}\right)', [('X_{0}', "Gem Grinder's base bonus (%)")],
                            label='Gem Grinder base bonus (Neutral alignment)', para=1),
    'Drow Perk 4': S(r'X_{0} = 100 + {v}', [('X_{0}', "Combo Strike's base bonus (%)")],
                     label="Combo Strike's base bonus (%)", para=0),
    'Minedwarf': S(r'F_{0} = 200 + 100', [('F_{0}', "Diamond Pickaxe's base value of the Faction Coin find chance (%)")], at=None),
    'Lightning Storm': S(r'X_{0} = 900 \cdot 1.5', [('X_{0}', "Lightning Strike's base bonus per Iron Stronghold (%)")], at=None),
    'True Night': S(r'X_{0} = 50 \cdot \left(1 + 0.01 \cdot {v}\right)', [('X_{0}', "Night Time's bonus per Necropolis (%)")]),
}

RESEARCH = {
    'Rarity': S(r'X_{0} = 2500 \cdot \left(1 + 0.01 \cdot {v}\right)', [('X_{0}', "Gem Grinder's base bonus (%)")]),
    'Deflagration': S(r'X_{0} = 120 \cdot \left(1 + 0.01 \cdot 1600\right)', [('X_{0}', "Hellfire Blast's base bonus (%)")], at=None),
    'Delayed Reaction': dict(S(r'V = 20000 + \left\lfloor 1000 \cdot t^{1.5} \right\rfloor',
                               [('V', "Fairy Chanting's base value"), ('t', 'Seconds since Fairy Chanting was cast (rounded up)')],
                               at=None, label="Fairy Chanting's base value"),
                             first_label='Fairy Chanting duration'),
}

CHALLENGES = {
    'Midnight Time': S(r'X_{0} = 50 \cdot \left(1 + 0.01 \cdot {v}\right)', [('X_{0}', "Night Time's bonus per Necropolis (%)")]),
    "God's Plan": S(r'X_{0} = 10 \cdot \left(1 + 0.01 \cdot 3 \cdot P\right)',
                    [('X_{0}', "God's Hand's base bonus (%)"),
                     ('P', "The extra count Precognition gives (its X, in %), only while Precognition is active")],
                    at=None, label="God's Hand's base bonus (%)"),
}


def _rhs(latex):
    return latex.split(' = ', 1)[1]


def apply(forms, spec):
    """-> the formula list with the formula of the spec in it (the list itself is changed)"""
    old = forms[spec['at']] if spec['at'] is not None else None
    assert spec['at'] is None or old is not None, spec
    latex = spec['tmpl'].replace('{v}', _rhs(old['latex'])) if old else spec['tmpl']
    assert '{v}' not in latex
    new_vars = [{'symbol': s, 'text': t} for s, t in spec['vars']]
    have = {v['symbol'] for v in new_vars}
    f = dict(old or {}, latex=latex, vars=new_vars[:1] + [v for v in (old['vars'] if old else []) if v['symbol'] not in have] + new_vars[1:])
    if spec['label']: f['label'] = spec['label']
    if old: forms[spec['at']] = f
    else: forms.append(f)
    if spec.get('first_label') and len(forms) > 1: forms[0]['label'] = spec['first_label']
    return forms
