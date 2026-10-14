"""Formulas of the faction heritages, spell upgrades, unique building upgrades and bloodlines (merged into FORMULAS)."""
from alleg_manual import F, most, TIER, FORMULAS

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
                                      ('N', 'Royal Exchanges made in this Era'), LIN))],
    'Advanced Druid Heritage': [(0, F(r'v = 9 \cdot D^{0.3} \cdot m', ('D', 'The durations of all your spells added together (seconds)'), LIN))],
    'Advanced Faceless Heritage': [(0, F(r'v = 2.25 \cdot U^{0.8} \cdot m', ('U', 'Unique buildings you have built'), LIN))],
    'Advanced Dwarven Heritage': [(0, F(r'v = 0.025 \cdot D^{0.65} \cdot m',
                                        ('D', 'Your excavation depth (excavations made since your last Excavation Reset)'), LIN))],
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
                                ('D', 'Your excavation depth (excavations made since your last Excavation Reset)'), TIER,
                                label='Base production added to each building (per second)'))],
    'Goblin Bloodline': [(0, F(r'v = 0.01', ('v', 'Amount taken off the cost multiplier of all buildings'), label='Cost multiplier'))],
    'Archon Bloodline': [(0, F(r'v = 1 + \max\left(0, \left\lfloor \frac{\sqrt{1 + \frac{8 \cdot h}{36}} - 1}{2} \right\rfloor\right)',
                               ('h', 'Hours played in this Era'), label='Research slots for every branch (Ascension 0 to 2)'))],
})

# paragraphs added after the game's own text: name -> [(text, formula, first Ascension of the Ascension penalty)]
EXTRA_PARAS = {
    'Archon Bloodline': [('From Ascension 3 it gives research budget instead of research slots: increase Research budget based on '
                          'time spent in this Era.',
                          F(r'v = \left(\ln\left(1 + t\right)\right)^{3}', ('t', 'Time played in this Era (seconds)'),
                            label='Research budget (Ascension 3 and up)'))],
}
