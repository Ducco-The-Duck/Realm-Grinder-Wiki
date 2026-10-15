"""Hand-written descriptions of the Misc upgrades whose effects live in many places in the game code
(Reincarnation Power 1-5, Gem Power, Ruby Power). Every formula was read from the code:
`§@"J§` and its siblings (the Power classes), `§#!!§.§'"=§` (Reincarnations counted), the production /
mana / assistants / Faction Coin functions that call them.

MANUAL_PARAS[name] = [(text, [formula, ...], penalty_start_or_None), ...]; a formula is built with F().
MORE[name] = {'tip': [(text, penalty_start), ...], 'more': [(text, [formula, ...], penalty_start), ...], 'note': str}:
the tooltip shows `tip` (the game's wording without numbers) and the page opens `more` (every bonus with its
formula) on click.
"""


def F(latex, *vs):
    return {'latex': latex, 'vars': [{'symbol': a, 'text': b} for a, b in vs]}


HEAD = 'Unlock the power of Reincarnations, providing unique bonuses.'


def N(extra=''):
    return ('N', 'Reincarnations made' + extra)


MANUAL_PARAS = {
    'Gem Power': [
        ('Unlocks the power of gems, each of which will increase your overall production by 2%.', [], None),
        ('All your Gems increase Faction Coin find chance.',
         [F(r'v = \left\lfloor \left(1.25 + \frac{n}{4}\right) \cdot 0.5 \cdot \left(\ln\left(1 + G\right)\right)^{0.9} \right\rfloor',
            ('n', 'Gem upgrades bought (Gem Potency, Gem Supremacy, Gem Sovereignty)'), ('G', 'Your Gems'))], None),
    ],
}

NB = ' (Reincarnations made - {k})'


def n_after(k):
    return N(' after the %dth' % k + NB.format(k=k))


MORE = {
    'Reincarnation Power 1': {
        'tip': [
            (HEAD, None),
            ('Increase the production of all buildings.', 1),
            ('Increase the production of all buildings over time based on Reincarnations made.', 1),
            ('Increase Offline production.', 1),
            ('Increase Faction Coin find chance.', None),
            ('Increase Mana Regeneration.', None),
            ('Increase production bonus from Gems per Reincarnation.', None),
            ('Gain assistants per Reincarnation and increase the production of assistants per Reincarnation made.', 1),
            ('Increase Maximum Mana per Reincarnation.', None),
            ('Increase the production of each building made per building of the same type.', 2),
            ('Increase Royal Exchange Bonus per Reincarnation.', None),
        ],
        'more': [
            ('Increase the production of all buildings, from Reincarnation 1 up to 119.',
             [F(r'v = 50 \cdot N', N())], 1),
            ('Increase the production of all buildings over time, from Reincarnation 10 up to 119. It applies together '
             'with the bonus above.',
             [F(r'v = N^{1.75} \cdot \left(\frac{t}{3600}\right)^{0.65}', N(),
                ('t', 'Time played in this Reincarnation (seconds)'))], 1),
            ('Increase Offline production.', [F(r'v = 500 \cdot N', N())], 1),
            ('Increase Faction Coin find chance (+%).', [F(r'v = 10 \cdot N', N())], None),
            ('Increase Mana Regeneration (+ per second).', [F(r'v = 2 \cdot N', N())], None),
            ('From Reincarnation 2: increase production bonus from Gems (+%).', [F(r'v = 0.2 \cdot N', N())], None),
            ('From Reincarnation 5: gain assistants.', [F(r'v = N', N())], None),
            ('From Reincarnation 5: increase the production of assistants.', [F(r'v = 2 \cdot N', N())], 1),
            ('From Reincarnation 12: increase Maximum Mana.', [F(r'v = 35 \cdot N', N())], None),
            ('From Reincarnation 20: increase the production of each building made, per building of the same type.',
             [F(r'v = 0.01 \cdot N \cdot B', N(), ('B', 'Number of buildings of that type you own'))], 2),
            ('From Reincarnation 25: increase Royal Exchange Bonus.', [F(r'v = 0.5 \cdot N', N())], None),
        ],
        'note': None,
    },
    'Reincarnation Power 2': {
        'tip': [
            (HEAD, None),
            ('Increase Maximum Mana based on Reincarnations made.', None),
            ('Increase the production of all buildings based on Reincarnations made.', 2),
            ('Multiplicatively increase Faction Coin find chance based on Reincarnations made.', None),
            ('Multiply Faction Coins found based on Reincarnations made if they match your Faction or Bloodline.', None),
            ('Autoclicks based on Reincarnations made.', None),
            ('Mercenaries gain one additional research slot in branches based on their alignment. (Good: Spellcraft and '
             'Divine, Evil: Economics and Warfare, Neutral: Craftsmanship and Alchemy)', None),
            ('Gain assistants per Reincarnation.', None),
            ('Gain one additional Research Slot in each branch.', None),
        ],
        'more': [
            ('From Reincarnation 43, and only from Ascension 1: increase Maximum Mana.',
             [F(r'v = 70 \cdot N^{1.25}', n_after(39))], None),
            ('From Reincarnation 46: increase the production of all buildings.', [F(r'v = 10 \cdot N', n_after(39))], 2),
            ('From Reincarnation 50: multiplicatively increase Faction Coin find chance (%).',
             [F(r'v = 1.5 \cdot N^{0.95}', n_after(39))], None),
            ('From Reincarnation 58: multiply Faction Coins found if they match your Faction or Bloodline.',
             [F(r'v = 1.2 \cdot N^{1.05}', n_after(39))], None),
            ('From Reincarnation 70: autoclicks per second.',
             [F(r'v = \left\lfloor \sqrt{N} \right\rfloor', n_after(39))], None),
            ('From Reincarnation 75: Mercenaries gain one additional research slot in branches based on their alignment.',
             [], None),
            ('From Reincarnation 80: gain assistants.', [F(r'v = 4 \cdot N', n_after(39))], None),
            ('From Reincarnation 90, before Ascension 2: gain one additional Research Slot in each branch.', [], None),
        ],
        'note': None,
    },
    'Reincarnation Power 3': {
        'tip': [
            (HEAD, None),
            ('Increase Mana Regeneration per Reincarnation.', None),
            ('Increase the production of Unique Buildings based on the difference of time spent as their respective '
             'faction against your most used faction in this Reincarnation.', 3),
            ('Multiply Faction Coins found based on Reincarnations made if they match your Faction, Bloodline or '
             'Artifact Set.', None),
            ('Increase the production of all buildings based on Reincarnations made.', 3),
            ('Unique buildings count more for Call to Arms purposes based on Reincarnations made.', None),
        ],
        'more': [
            ('From Reincarnation 101: increase Mana Regeneration (multiplicatively, %).',
             [F(r'v = 2 \cdot N', n_after(99))], None),
            ('From Reincarnation 107: increase the production of Unique Buildings, depending on the time spent as the '
             'faction of each Unique Building against your most used faction in this Reincarnation (%).',
             [F(r'v = 50 + 0.15 \cdot \max\left(0,\ t_{\max} - t_{f}\right)^{0.85}',
                ('t_{\\max}', 'Time spent as your most used faction in this Reincarnation (seconds)'),
                ('t_{f}', 'Time spent in this Reincarnation as the faction of that Unique Building (seconds)'))], 3),
            ('From Reincarnation 115: multiply Faction Coins found if they match your Faction, Bloodline or Artifact Set.',
             [F(r'v = 1.2 \cdot N^{1.05}', n_after(99))], None),
            ('From Reincarnation 120: increase the production of all buildings.', [F(r'v = 25 \cdot N', n_after(99))], 3),
            ('From Reincarnation 150: Unique buildings count more for Call to Arms purposes (the multiplier shown).',
             [F(r'v = N', n_after(99))], None),
        ],
        'note': None,
    },
    'Reincarnation Power 4': {
        'tip': [
            (HEAD, None),
            ('Increase Research budget in each branch based on Reincarnations made.', None),
            ('Increase the production of all buildings based on Reincarnations made.', 4),
        ],
        'more': [
            ('From Reincarnation 170: increase Research budget in each branch.',
             [F(r'v = 150 \cdot A + 3.5 \cdot N', ('A', 'Your Ascension number'), n_after(159))], None),
            ('From Reincarnation 200: increase the production of all buildings.',
             [F(r'v = 150 \cdot N', n_after(159))], 4),
        ],
        'note': None,
    },
    'Reincarnation Power 5': {
        'tip': [
            (HEAD, None),
            ('Multiplicatively increase Mana Regeneration and Faction Coin find chance based on Reincarnations made.',
             None),
        ],
        'more': [
            ('From Reincarnation 220: multiplicatively increase Mana Regeneration and Faction Coin find chance (the '
             'same % for both).', [F(r'v = 500 \cdot \sqrt{N}', n_after(219))], None),
        ],
        'note': None,
    },
    'Ruby Power': {
        'tip': [
            ('Unlocks the power of Rubies, increasing the production of all buildings by 100% and allowing you to '
             'purchase many upgrades which increase all aspect of your production.', None),
            ('Ruby Power bonus will increase based on the all-time amount of Rubies you collected.', None),
        ],
        'more': [
            ('Production Bonus: +v% production of all buildings.',
             [F(r'v = 100 + S', ('S', 'Sum of the increases of the Ruby Tier upgrades you have bought'))], None),
            ('Assistant Bonus: +v assistants and +v% assistants production.',
             [F(r'v = n', ('n', 'Levels of "Ruby Assistant" bought in the Shop'))], None),
            ('Max Mana Bonus: +v\u2081 Maximum Mana and +v\u2082% Maximum Mana.',
             [F(r'v_{1} = 100 \cdot n', ('n', 'Levels of "Ruby Max Mana" bought in the Shop')),
              F(r'v_{2} = n', ('n', 'Levels of "Ruby Max Mana" bought in the Shop'))], None),
            ('Mana Regen Bonus: +v mana per second and +v% Mana Regeneration.',
             [F(r'v = n', ('n', 'Levels of "Ruby Mana Regeneration" bought in the Shop'))], None),
            ('Gem Bonus: +v% Gem Power and +v% production bonus from Gems.',
             [F(r'v = n', ('n', 'Levels of "Ruby Gem Bonus" bought in the Shop'))], None),
            ('Royal Exchange Bonus: +v% Royal Exchange Bonus and a further +v% on top of it.',
             [F(r'v = 2 \cdot n', ('n', 'Levels of "Ruby Royal Trading" bought in the Shop'))], None),
        ],
        'note': 'Each level bought increases the Ruby cost of the next purchase of that bonus by 1.',
    },
}

# the three Gem upgrades point to the formula on Gem Power
GEM_UPGRADE_NAMES = {'Gem Potency', 'Gem Supremacy', 'Gem Sovereignty'}
GEM_UPGRADE_NOTE = 'The Faction Coin find chance formula is shown in the Gem Power upgrade.'

# the three assistant upgrades share one value: 5% per assistant, per upgrade of the series bought
ASSISTANT_NAMES = {'Assistant Trade Union', 'Assistant Syndicate', 'Assistant Cartel'}
ASSISTANT_FORMULA = F(r'v = 5 \cdot n \cdot A', ('n', 'Assistant upgrades of this series you have bought'),
                      ('A', 'Your number of assistants (as shown in the game)'))

