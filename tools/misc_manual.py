"""Hand-written descriptions of the Misc upgrades whose effects live in many places in the game code
(Reincarnation Power 1-5, Gem Power, Ruby Power). Every formula was read from the code:
`§@"J§` and its siblings (the Power classes), `§#!!§.§'"=§` (Reincarnations counted), the production /
mana / assistants / Faction Coin functions that call them.

MANUAL_PARAS[name] = [(text, [formula, ...], penalty_start_or_None), ...]; a formula is built with F().
"""


def F(latex, *vs):
    return {'latex': latex, 'vars': [{'symbol': a, 'text': b} for a, b in vs]}


HEAD = 'Unlock the power of Reincarnations, providing unique bonuses.'


def N(extra=''):
    return ('N', 'Reincarnations made' + extra)


MANUAL_PARAS = {
    # Formulas only where the description does not already give the value (per-Reincarnation values are written in the text).
    # N = Reincarnations counted: R for Power 1, then R - 39, R - 99, R - 159, R - 219.
    'Reincarnation Power 1': [
        (HEAD, [], None),
        ('R1-119: Increase the production of all buildings by 50% per Reincarnation.', [], 1),
        ('R10-119: Also increase the production of all buildings over time based on Reincarnations made '
         '(on top of the 50% per Reincarnation above).',
         [F(r'v = N^{1.75} \cdot \left(\frac{t}{3600}\right)^{0.65}', N(),
            ('t', 'Time played in this Reincarnation (seconds)'))], 1),
        ('Increase Offline production by 500% per Reincarnation.', [], 1),
        ('Increase Faction Coin find chance by +10% per Reincarnation.', [], None),
        ('Increase Mana Regeneration by +2 per Reincarnation.', [], None),
        ('R2+: Increase production bonus from Gems by 0.2% per Reincarnation.', [], None),
        ('R5+: Gain 1 assistant per Reincarnation.', [], None),
        ('R5+: Increase the production of assistants by 2% per Reincarnation made.', [], 1),
        ('R12+: Increase Maximum Mana by 35 per Reincarnation.', [], None),
        ('R20+: Increase the production of each building by 0.01% per Reincarnation made per building of the same type.',
         [], 2),
        ('R25+: Increase Royal Exchange Bonus by 0.5% per Reincarnation.', [], None),
    ],
    'Reincarnation Power 2': [
        (HEAD, [], None),
        ('R43+, from Ascension 1: Increase Maximum Mana based on Reincarnations made.',
         [F(r'v = 70 \cdot N^{1.25}', N(' after the 39th (Reincarnations made − 39)'))], None),
        ('R46+: Increase the production of all buildings by 10% per Reincarnation after the 39th.', [], 2),
        ('R50+: Multiplicatively increase Faction Coin find chance based on Reincarnations made.',
         [F(r'v = 1.5 \cdot N^{0.95}', N(' after the 39th (Reincarnations made − 39)'))], None),
        ('R58+: Multiply Faction Coins found based on Reincarnations made if they match your Faction or Bloodline.',
         [F(r'v = 1.2 \cdot N^{1.05}', N(' after the 39th (Reincarnations made − 39)'))], None),
        ('R70+: Autoclicks based on Reincarnations made.',
         [F(r'v = \left\lfloor \sqrt{N} \right\rfloor', N(' after the 39th (Reincarnations made − 39)'))], None),
        ('R75+: Mercenaries gain one additional research slot in branches based on their alignment. '
         '(Good: Spellcraft and Divine, Evil: Economics and Warfare, Neutral: Craftsmanship and Alchemy)', [], None),
        ('R80+: Gain 4 assistants per Reincarnation after the 39th.', [], None),
        ('R90+, before Ascension 2: Gain one additional Research Slot in each branch.', [], None),
    ],
    'Reincarnation Power 3': [
        (HEAD, [], None),
        ('R101+: Increase Mana Regeneration by 2% per Reincarnation after the 99th.', [], None),
        ('R107+: Increase the production of Unique Buildings based on the difference of time spent as their '
         'respective faction against your most used faction in this Reincarnation.',
         [F(r'v = 50 + 0.15 \cdot \max\left(0,\ t_{\max} - t_{f}\right)^{0.85}',
            ('t_{\\max}', 'Time spent as your most used faction in this Reincarnation (seconds)'),
            ('t_{f}', 'Time spent in this Reincarnation as the faction of that Unique Building (seconds)'))], 3),
        ('R115+: Multiply Faction Coins found based on Reincarnations made if they match your Faction, Bloodline '
         'or Artifact Set.',
         [F(r'v = 1.2 \cdot N^{1.05}', N(' after the 99th (Reincarnations made − 99)'))], None),
        ('R120+: Increase the production of all buildings by 25% per Reincarnation after the 99th.', [], 3),
        ('R150+: Unique buildings count more for Call to Arms purposes, multiplied by the number of Reincarnations '
         'after the 99th.', [], None),
    ],
    'Reincarnation Power 4': [
        (HEAD, [], None),
        ('R170+: Increase Research budget in each branch based on Reincarnations made.',
         [F(r'v = 150 \cdot A + 3.5 \cdot N', ('A', 'Your Ascension number'),
            N(' after the 159th (Reincarnations made − 159)'))], None),
        ('R200+: Increase the production of all buildings by 150% per Reincarnation after the 159th.', [], 4),
    ],
    'Reincarnation Power 5': [
        (HEAD, [], None),
        ('R220+: Multiplicatively increase Mana Regeneration and Faction Coin find chance based on Reincarnations made.',
         [F(r'v = 500 \cdot \sqrt{N}', N(' after the 219th (Reincarnations made − 219)'))], None),
    ],
    'Gem Power': [
        ('Unlocks the power of gems, each of which will increase your overall production by 2%.', [], None),
        ('All your Gems increase Faction Coin find chance.',
         [F(r'v = \left\lfloor \left(1.25 + \frac{n}{4}\right) \cdot 0.5 \cdot \left(\ln\left(1 + G\right)\right)^{0.9} \right\rfloor',
            ('n', 'Gem upgrades bought (Gem Potency, Gem Supremacy, Gem Sovereignty)'), ('G', 'Your Gems'))], None),
    ],
    'Ruby Power': [
        ('Unlocks the power of Rubies, increasing the production of all buildings by 100% and allowing you to purchase '
         'many upgrades which increase all aspect of your production.', [], None),
        ('Ruby Power bonus will increase based on the all-time amount of Rubies you collected.', [], None),
        ('Visit the Shop to purchase more!', [], None),
        ('Current Production Bonus: 100% plus the increase of every Ruby Tier upgrade you have bought.', [], None),
        ('Current Assistants Bonus: +1 assistant and +1% assistants production for each level of "Ruby Assistant" '
         'bought in the Shop.', [], None),
        ('Current Mana Regen Bonus: +1 per second and +1% for each level of "Ruby Mana Regeneration" bought in the Shop.',
         [], None),
        ('Current Max Mana Bonus: +100 and +1% for each level of "Ruby Max Mana" bought in the Shop.', [], None),
        ('Current Gem Bonus: +1% to Gem Power and +1% to the production bonus from Gems for each level of "Ruby Gem '
         'Bonus" bought in the Shop.', [], None),
        ('Current Royal Exchange Bonus: +2% and +2% for each level of "Ruby Royal Trading" bought in the Shop.',
         [], None),
    ],
}

# the three assistant upgrades share one value: 5% per assistant, per upgrade of the series bought
ASSISTANT_NAMES = {'Assistant Trade Union', 'Assistant Syndicate', 'Assistant Cartel'}
ASSISTANT_FORMULA = F(r'v = 5 \cdot n \cdot A', ('n', 'Assistant upgrades of this series you have bought'),
                      ('A', 'Your number of assistants (as shown in the game)'))

