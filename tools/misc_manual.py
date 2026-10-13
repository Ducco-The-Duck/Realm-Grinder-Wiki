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
    'Reincarnation Power 1': [
        (HEAD, [], None),
        ('R1-119: Increase the production of all buildings per Reincarnation.',
         [F(r'v = 50 \cdot N', N())], 1),
        ('R10-119: Increase the production of all buildings over time based on Reincarnations made.',
         [F(r'v = N^{1.75} \cdot \left(\frac{t}{3600}\right)^{0.65}', N(),
            ('t', 'Time played in this Reincarnation (seconds)'))], 1),
        ('Increase Offline production per Reincarnation.', [F(r'v = 500 \cdot N', N())], 1),
        ('Increase Faction Coin find chance per Reincarnation.', [F(r'v = 10 \cdot N', N())], None),
        ('Increase Mana Regeneration per Reincarnation.', [F(r'v = 2 \cdot N', N())], None),
        ('R2+: Increase production bonus from Gems per Reincarnation.', [F(r'v = 0.2 \cdot N', N())], None),
        ('R5+: Gain 1 assistant per Reincarnation.', [F(r'v = N', N())], None),
        ('R5+: Increase the production of assistants per Reincarnation made.', [F(r'v = 2 \cdot N', N())], 1),
        ('R12+: Increase Maximum Mana per Reincarnation.', [F(r'v = 35 \cdot N', N())], None),
        ('R20+: Increase the production of each building made per building of the same type.',
         [F(r'v = 0.01 \cdot N \cdot B', N(),
            ('B', 'Number of buildings of that type you own'))], 2),
        ('R25+: Increase Royal Exchange Bonus per Reincarnation.', [F(r'v = 0.5 \cdot N', N())], None),
    ],
    'Reincarnation Power 2': [
        (HEAD, [], None),
        ('R43+, from Ascension 1: Increase Maximum Mana based on Reincarnations made.',
         [F(r'v = 70 \cdot N^{1.25}', N(' after the 39th (Reincarnations made − 39)'))], None),
        ('R46+: Increase the production of all buildings based on Reincarnations made.',
         [F(r'v = 10 \cdot N', N(' after the 39th (Reincarnations made − 39)'))], 2),
        ('R50+: Multiplicatively increase Faction Coin find chance based on Reincarnations made.',
         [F(r'v = 1.5 \cdot N^{0.95}', N(' after the 39th (Reincarnations made − 39)'))], None),
        ('R58+: Multiply Faction Coins found based on Reincarnations made if they match your Faction or Bloodline.',
         [F(r'v = 1.2 \cdot N^{1.05}', N(' after the 39th (Reincarnations made − 39)'))], None),
        ('R70+: Autoclicks based on Reincarnations made.',
         [F(r'v = \left\lfloor \sqrt{N} \right\rfloor', N(' after the 39th (Reincarnations made − 39)'))], None),
        ('R75+: Mercenaries gain one additional research slot in branches based on their alignment. '
         '(Good: Spellcraft and Divine, Evil: Economics and Warfare, Neutral: Craftsmanship and Alchemy)', [], None),
        ('R80+: Gain 4 assistants per Reincarnation.',
         [F(r'v = 4 \cdot N', N(' after the 39th (Reincarnations made − 39)'))], None),
        ('R90+, before Ascension 2: Gain one additional Research Slot in each branch.', [], None),
    ],
    'Reincarnation Power 3': [
        (HEAD, [], None),
        ('R101+: Increase Mana Regeneration per Reincarnation.',
         [F(r'v = 2 \cdot N', N(' after the 99th (Reincarnations made − 99)'))], None),
        ('R107+: Increase the production of Unique Buildings based on the difference of time spent as their '
         'respective faction against your most used faction in this Reincarnation.',
         [F(r'v = 50 + 0.15 \cdot \max\left(0,\ t_{\max} - t_{f}\right)^{0.85}',
            ('t_{\\max}', 'Time spent as your most used faction in this Reincarnation (seconds)'),
            ('t_{f}', 'Time spent in this Reincarnation as the faction of that Unique Building (seconds)'))], 3),
        ('R115+: Multiply Faction Coins found based on Reincarnations made if they match your Faction, Bloodline '
         'or Artifact Set.',
         [F(r'v = 1.2 \cdot N^{1.05}', N(' after the 99th (Reincarnations made − 99)'))], None),
        ('R120+: Increase the production of all buildings based on Reincarnations made.',
         [F(r'v = 25 \cdot N', N(' after the 99th (Reincarnations made − 99)'))], 3),
        ('R150+: Unique buildings count more for Call to Arms purposes based on Reincarnations made.',
         [F(r'v = N', N(' after the 99th (Reincarnations made − 99)'))], None),
    ],
    'Reincarnation Power 4': [
        (HEAD, [], None),
        ('R170+: Increase Research budget in each branch based on Reincarnations made.',
         [F(r'v = 150 \cdot A + 3.5 \cdot N', ('A', 'Your Ascension number'),
            N(' after the 159th (Reincarnations made − 159)'))], None),
        ('R200+: Increase the production of all buildings based on Reincarnations made.',
         [F(r'v = 150 \cdot N', N(' after the 159th (Reincarnations made − 159)'))], 4),
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
        ('Current Production Bonus.',
         [F(r'v = 100 + S', ('S', 'Sum of the increases of the Ruby Tier upgrades you have bought'))], None),
        ('Current Assistants Bonus (assistants gained, and % of assistants production).',
         [F(r'v = n', ('n', 'Levels of "Ruby Assistant" bought in the Shop'))], None),
        ('Current Mana Regen Bonus (per second, and %).',
         [F(r'v = n', ('n', 'Levels of "Ruby Mana Regeneration" bought in the Shop'))], None),
        ('Current Max Mana Bonus (flat).',
         [F(r'v = 100 \cdot n', ('n', 'Levels of "Ruby Max Mana" bought in the Shop'))], None),
        ('Current Max Mana Bonus (%).',
         [F(r'v = n', ('n', 'Levels of "Ruby Max Mana" bought in the Shop'))], None),
        ('Current Gem Bonus (% added to Gem Power, and % of the production bonus from Gems).',
         [F(r'v = n', ('n', 'Levels of "Ruby Gem Bonus" bought in the Shop'))], None),
        ('Current Royal Exchange Bonus (% added, and % of the bonus).',
         [F(r'v = 2 \cdot n', ('n', 'Levels of "Ruby Royal Trading" bought in the Shop'))], None),
    ],
}

# the three assistant upgrades share one value: 5% per assistant, per upgrade of the series bought
ASSISTANT_NAMES = {'Assistant Trade Union', 'Assistant Syndicate', 'Assistant Cartel'}
ASSISTANT_FORMULA = F(r'v = 5 \cdot n \cdot A', ('n', 'Assistant upgrades of this series you have bought'),
                      ('A', 'Your number of assistants (as shown in the game)'))

