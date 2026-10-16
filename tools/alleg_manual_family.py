"""Formulas of the faction heritages, spell upgrades, unique building upgrades and bloodlines (merged into FORMULAS)."""
from alleg_manual import F, most, TIER, FORMULAS, S_ACTIVE

LIN = ('m', 'Multiplier from your Lineage level of that faction: 1 + 0.2 x the level while you use that lineage, 1 otherwise '
            '(other upgrades change the numbers)')
FORMULAS.update({
    'Elven Heritage': [(0, F(r'v = 2 \cdot \left(\ln\left(1 + Q\right)\right)^{2}', ('Q', 'Your Faction Coin find chance (%)'),
                             label='Clicking reward (%)'))],
    'Faceless Heritage': [(0, F(r'v = 0.25 \cdot B^{0.75}', ('B', 'Most buildings built in a single Era of this Reincarnation')))],
    'Dragon Heritage': [(0, F(r'v = 0.7 \cdot t^{0.85}', ('t', 'Time spent as Dragon in this Reincarnation (seconds)')))],
    'Advanced Fairy Heritage': [(0, F(r'v = \left\lfloor 2 \cdot N^{0.8} \right\rfloor \cdot m',
                                      ('N', 'Farms, Inns and Blacksmiths you own, added together'), LIN))],
    'Advanced Elven Heritage': [(0, F(r'v = 0.2 \cdot \left(\ln\left(1 + F\right)\right)^{0.8} \cdot m',
                                      ('F', 'Faction Coins found in this Era'), LIN))],
    'Advanced Angelic Heritage': [(0, F(r'v = 5 \cdot N^{0.25} \cdot m', ('N', 'Spells cast in this Era'), LIN))],
    'Advanced Goblin Heritage': [(0, F(r'v = 0.15 \cdot \left(\ln\left(1 + G\right)\right)^{0.95} \cdot m', ('G', 'Your Gems'), LIN))],
    'Advanced Undead Heritage': [(0, F(r'v = 0.5 \cdot t^{0.5} \cdot m', ('t', 'Time spent offline in this Reincarnation (seconds)'), LIN))],
    'Advanced Demonic Heritage': [(0, F(r'v = 0.25 \cdot N^{0.75} \cdot m', ('N', 'Number of trophies you have unlocked'), LIN))],
    'Advanced Titan Heritage': [(0, F(r'v = 0.85 \cdot \left(\ln\left(1 + N\right)\right)^{1.15} \cdot m',
                                      ('N', 'Royal Exchanges purchased in this Era'), LIN))],
    'Advanced Druid Heritage': [(0, F(r'v = 9 \cdot D^{0.3} \cdot m', ('D', 'The durations of all your spells added together (seconds)'), LIN))],
    'Advanced Faceless Heritage': [(0, F(r'v = 2.25 \cdot U^{0.8} \cdot m', ('U', 'Unique buildings you have built'), LIN))],
    'Advanced Dwarven Heritage': [(0, F(r'v = 0.025 \cdot D^{0.65} \cdot m',
                                        ('D', 'Your excavation depth'), LIN))],
    'Advanced Drow Heritage': [(0, F(r'v = 0.2 \cdot \ln\left(1 + O\right) \cdot t^{0.4} \cdot m',
                                     ('O', 'Your Offline production bonus'), ('t', 'Time played in this Era (seconds)'), LIN))],
    'Advanced Dragon Heritage': [(0, F(r'v = \left\lfloor \left(1 + 0.05 \cdot \left(\ln\left(1 + A\right)\right)^{1.15}\right) \cdot m \right\rfloor',
                                       ('A', 'Artifacts you have found'), LIN))],
    'Reality Crater': [(0, F(r'v = 0.0005 \cdot \ln\left(1 + A\right)', ('A', 'Your number of assistants'),
                             label='Taken off the Excavation cost multiplier'))],
    'Burning Abyss': [(0, F(r'v = \sum_{i} d_{i}^{\,p}',
                            ('d', 'The decimal digits of x (each digit is raised to the power p and they are added up)'),
                            ('p', '2 + (floor(0.5 * ln(1 + x)) + 1) / 10'),
                            ('x', '1.25 times your time with Evil alignment in this Reincarnation (seconds)')))],
    "Wyrm's Den": [(0, F(r'v = 0.25 \cdot \left(\ln\left(1 + F\right)\right)^{5}', ('F', 'Faction Coins found in this Era')))],
    'Demon Bloodline': [(0, F(r'v = 2.5 \cdot N^{0.5}', ('N', most('Hell Portal'))))],
    'Dwarven Bloodline': [(0, F(r'v = \left(\ln\left(1 + D\right)\right)^{1.75} \cdot 10^{\left(1.25 \cdot T\right)^{0.75}}',
                                ('D', 'Your excavation depth'), TIER,
                                label='Base production added to each building (per second)'))],
    'Goblin Bloodline': [(0, F(r'v = 0.01', ('v', 'Amount taken off the cost multiplier of all buildings'), label='Cost multiplier'))],
    'Elven Perk 6': [(0, F(r'v = 1.6 \cdot C^{0.4}', ('C', 'Highest amount of clicks in this Reincarnation')))],
    'Goblin Perk 6': [(0, F(r'v = \min\left(3000,\, 4 \cdot W^{0.5}\right)', ('W', 'The worth of a Tax Collection, as the spell computes it')))],
    'Undead Perk 1': [(1, F(r'v_{1} = D^{0.6}', ('D', 'Duration of Spiritual Surge (seconds)'), label='Offline production (%)')),
                      (1, F(r'v_{2} = 0.6 \cdot D^{0.6}', ('D', 'Duration of Spiritual Surge (seconds)'),
                            label='Offline gains of mana produced and spells cast (%)'))],
    'Faceless Perk 6': [(0, F(r'v = 0.7 \cdot t^{0.7}', ('t', 'Length of your last Era (seconds)')))],
    'Drow Perk 1': [(0, F(r'v = 2 \cdot \left(\ln\left(1 + K\right)\right)^{2}',
                          ('K', 'Highest Combo Strike counter you have ever had'), label='Maximum Mana (%)'))],
    'Drow Perk 4': [(0, F(r'v = 2 \cdot \left(\ln\left(1 + \left(C^{0.9}\right)^{j + 1}\right)\right)^{2}',
                          ('C', 'Combo Strike counter'), ('j', 'Tier Combo Strike is cast at, minus 1 (0 for the base tier)'),
                          label='Combo Strike bonus'))],
    'Archon Lineage': [(0, F(r'v = 15 \cdot L', ('L', 'Your Archon Lineage level')))],
    'Makers Lineage': [(0, F(r'v = 3 \cdot L', ('L', 'Your Makers Lineage level')))],
    'Archon Bloodline': [(0, F(r'v = 1 + \max\left(0, \left\lfloor \frac{\sqrt{1 + \frac{t}{16200}} - 1}{2} \right\rfloor\right)',
                               ('t', 'Time played in this Era (seconds)'), label='Research slots for every branch (Ascension 0 to 2)'))],
    'Angel Bloodline': [(1, F(r'v = 1 + 0.5 \cdot t^{0.5}', ('t', 'Seconds since Holy Light was cast (rounded)'),
                              label='Holy Light bonus multiplier (Good alignment)'))],
})

# paragraphs added after the game's own text: name -> [(text, formula, first Ascension of the Ascension penalty)]
EXTRA_PARAS = {
    'Archon Bloodline': [('From Ascension 3 it gives research budget instead of research slots: increase Research budget based on '
                          'time spent in this Era.',
                          F(r'v = \left(\ln\left(1 + t\right)\right)^{3}', ('t', 'Time played in this Era (seconds)'),
                            label='Research budget (Ascension 3 and up)'))],
}

# the astral unique buildings upgrade the building of a tier of the player's alignment; the game's text names whichever it is
BUILDING_TEXT = {
    'Nexus': ('Farms', 'the tier 6 building of your alignment (Wizard Towers, Witch Conclaves or Alchemist Labs)'),
    'Pavilion': ('Farms', 'the tier 4 building of your alignment (Warrior Barracks, Slave Pens or Deep Mines)'),
}

# the Unions: text and value functions the generic converter cannot read
FORMULAS.update({
    'Fairies Union': [(1, F(r'v = 13 \cdot X^{0.65}',
                            ('X', 'Farms, Inns and Blacksmiths owned added together if the total number of buildings you own is even, '
                                  'otherwise all your other buildings added together'), label='Assistant production (%)'))],
    'Druids Union': [(1, F(r'v = L \cdot \min\left(11, G\right)^{1.25}',
                           ('L', 'Your total Lineage level'), ('G', 'The maximum amount of Grand Balance targets'),
                           label='Non-Unique Buildings production (%)'))],
    'Faceless Union': [(1, F(r'v = 40 + 0.4 \cdot t^{0.4}', ('t', 'Total time spent as the random faction currently chosen (seconds)'),
                             label='Assistants (%)'))],
})
_DU = 'Unlock %s upgrades.'
_AX = {'O': 'Order path: ', 'C': 'Chaos path: ', 'B': 'Balance path: '}
EXTRA_PARAS.update({
    'Dwarven Union': [
        (_DU % 'Dwarven', None),
        (_AX['O'] + 'Increase the production of all buildings based on time spent in this Reincarnation.',
         F(r'v = 3.5 \cdot t^{0.65}', ('t', 'Time played in this Reincarnation (seconds)'), label='Production (%)')),
        (_AX['B'] + 'Multiplicatively increase Mana Regeneration based on clicks made in this Reincarnation.',
         F(r'v = 1.5 \cdot \left(\ln\left(1 + C\right)\right)^{2.5}', ('C', 'Clicks made in this Reincarnation'), label='Mana Regeneration (%)')),
        (_AX['C'] + 'Multiplicatively increase assistants with a chaotic formula based on spells cast in this Reincarnation.',
         F(r'v = \left(\sum_{i} d_{i}^{\,p}\right)^{0.8}', ('d_{i}', 'The decimal digits of your total spells cast in this Reincarnation'),
           ('p', 'Exponent: 2 + (the number of digits of that total) / 10'), label='Assistants (%)')),
    ],
    'Drow Union': [
        (_DU % 'Drow', None),
        (_AX['O'] + 'Increase Offline production based on Maximum Mana.',
         F(r'v = 0.1 \cdot M^{0.85}', ('M', 'Your Maximum Mana'), label='Offline production (%)')),
        (_AX['B'] + 'Multiplicatively increase Maximum Mana based on Tax Collections cast in this Era.',
         F(r'v = 0.05 \cdot \left(\ln\left(1 + T\right)\right)^{2.5}', ('T', 'Tax Collections cast in this Era'), label='Maximum Mana (%)')),
        (_AX['C'] + 'Increase the production of a specific building tier, depending on buildings built, based on time spent offline in this '
                    'Reincarnation. The tier is 1 + (the number of buildings you have built) modulo 11.',
         F(r'v = 100 + 3 \cdot t^{0.87}', ('t', 'Time spent offline in this Reincarnation (seconds)'), label='Production (%)')),
    ],
    'Dragon Union': [
        (_DU % 'Dragon', None),
        (_AX['O'] + 'Increase the production of all buildings based on time spent as Order in this Reincarnation.',
         F(r'v = 0.7 \cdot t^{0.7}', ('t', 'Time spent as Order in this Reincarnation (seconds)'), label='Production (%)')),
        (_AX['B'] + 'Multiplicatively increase Maximum Mana based on your current lineage level.',
         F(r'v = 8 \cdot L^{0.8}', ('L', 'Your current Lineage level'), label='Maximum Mana (%)')),
        (_AX['C'] + 'Increase the production of Unique or Non-Unique Buildings based on assistants owned. Target buildings depend on '
                    'Faction Coin find chance: Non-Unique Buildings when the whole part of ln(1 + Faction Coin find chance) is odd, '
                    'Unique Buildings otherwise.',
         F(r'v = k \cdot 2 \cdot A^{0.3}', ('A', 'Your number of assistants'), ('k', '3 for Non-Unique Buildings, 1 for Unique Buildings'),
           label='Production (%)')),
    ],
})

# the Artifact Sets: (paragraph 0 = the Set's own bonus, paragraph 1 = Set Bonus 2).  Values are the base ones: the game
# multiplies them further when upgrades that strengthen Sets are owned.
_TE = ('t', 'Time played in this Era (seconds)')
FORMULAS.update({
    'Fairy Set': [(0, F(r'v = G^{0.5}', ('G', 'Good buildings you have built'))),
                  (1, F(r'v = 2 \cdot \left(\ln\left(1 + t\right)\right)^{1.5}', ('t', 'Time spent as Fairy in this Reincarnation (seconds)')))],
    'Elven Set': [(1, F(r'v = \left(\ln\left(1 + C\right)\right)^{2.5} + C^{0.25}', ('C', 'Automatic clicks made in this Era')))],
    'Angel Set': [(0, F(r'v = 3.5 \cdot N^{0.35}', ('N', 'Most spells cast in a single Era of this Reincarnation'))),
                  (1, F(r'v = B^{0.5}', ('B', 'Unique buildings you have built')))],
    'Goblin Set': [(0, F(r'v_{1} = 70 \cdot t^{0.7}', _TE, label='Faction Coin find chance (+%)')),
                   (0, F(r'v_{2} = 0.6 \cdot t^{0.6}', _TE, label='Faction Coin find chance (multiplicative, %)')),
                   (1, F(r'v = \left\lfloor 1 + 0.25 \cdot \left(\ln\left(1 + t\right)\right)^{1.5} \right\rfloor', _TE,
                         label='Free Tax Collections per spell cast'))],
    'Undead Set': [(0, F(r'v = 7500 + 7.5 \cdot \left(\ln\left(1 + O\right)\right)^{3.75}', ('O', 'Your Offline production bonus'))),
                   (1, F(r'v = \left(\ln\left(1 + F\right)\right)^{2}', ('F', 'Faction Coins found in this Era')))],
    'Demon Set': [(0, F(r'v = N^{0.5}', ('N', 'Buildings of tier 9, 10 and 11 of your alignment you own, added together'))),
                  (1, F(r'v = 2.25 \cdot \left(\ln\left(1 + S\right)\right)^{2.25}', ('S', 'Evil spells cast in this Reincarnation')))],
    'Titan Set': [(0, F(r'v_{1} = 3 \cdot t^{0.7}', _TE, label='Royal Exchange Bonus (+%)')),
                  (0, F(r'v_{2} = 0.6 \cdot t^{0.6}', _TE, label='Royal Exchange Bonus (multiplicative, %)')),
                  (1, F(r'v = A^{0.7}', ('A', 'Activity time of Lightning Strike in this Reincarnation (seconds)'), label='Production (%)'))],
    'Dwarven Set': [(0, F(r'v = 8 \cdot X^{0.4}', ('X', 'Your Royal Exchange bonus (%)'))),
                    (1, F(r'v = 0.7 \cdot t^{0.7}', _TE))],
    'Drow Set': [(0, F(r'v = 6 \cdot \left(\ln\left(1 + t\right)\right)^{1.6}', ('t', 'Time spent as Evil in this Reincarnation (seconds)')))],
    'Druid Set': [(0, F(r'v = 0.5 \cdot t^{0.5}', ('t', 'Activity time of that spell in this Era (seconds)'), label='Duration of each spell (+%)')),
                   (1, F(r'v = 0.5 \cdot \left(\ln\left(1 + N\right)\right)^{1.5}', ('N', 'Spells cast in this Era')))],
    'Faceless Set': [(0, F(r'v = 4500 + 12 \cdot A^{0.3}', ('A', 'Highest number of assistants you had in a previous Era'))),
                     (1, F(r'v = \min\left(3000, \left(\ln\left(1 + F\right)\right)^{1.5}\right)', ('F', 'Faction Coins found in this Era')))],
})

# lineage perks: values read from the code
FORMULAS.update({
    'Angel Perk 6': [(0, F(r'v = 1.5 \cdot S^{0.75}', S_ACTIVE))],
    'Dragon Perk 1': [(0, F(r'v = 1.95 \cdot N^{0.95}', ('N', 'Number of buildings of that type you own'),
                            label='Production of each Unique Building (%)'))],
    'Drow Perk 4': [(0, F(r'v = 0.5 \cdot \left\lfloor t \right\rfloor', ('t', 'Time played in this Era (seconds)'), label='Combo Strike combo bonus (%)')),
                    (1, F(r'v = 2 \cdot \left(\ln\left(1 + \left(C^{0.9}\right)^{j + 1}\right)\right)^{2}',
                          ('C', 'Combo Strike counter'), ('j', 'Tier Combo Strike is cast at, minus 1 (0 for the base tier)'),
                          label='Production of all buildings (%)'))],
})

# more lineage perks
FORMULAS.update({
    'Djinn Perk 4': [(0, F(r'v = 888 \cdot n', ('n', 'Limited Wish casts'), label='Automatic clicks added'))],
    'Makers Perk 1': [(1, F(r'v = 0.75 \cdot t^{0.75}', ('t', 'Time spent offline in this Reincarnation (seconds)')))],
})
EXTRA_PARAS.update({
    'Elven Perk 1': [('Elven Luck is affected by Ascension penalties.', None)],
})
