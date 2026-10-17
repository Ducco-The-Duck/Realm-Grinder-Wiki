"""Formulas of the Allegiances (faction) upgrades that the generic converter cannot read, written from the code.

Most of them are the static value functions of the upgrade's class; a few (the ones that act on the production of each
building) live in the production code of the game, and some show no number in the in-game tooltip at all.  `FORMULAS`
maps an upgrade name to a list of (paragraph index, formula).  A formula is {'latex', 'vars', 'label'}.
"""


def V(sym, text):
    return {'symbol': sym, 'text': text}


def F(latex, *vs, label=None):
    return {'latex': latex, 'vars': [V(a, b) for a, b in vs], 'label': label}


def most(b):      # the highest number of a building built in this Reincarnation
    return f'Most {b} buildings you have built in this Reincarnation'


def owned(b):
    return f'Number of {b} buildings you own'


TIER = ('T', "The building's tier (1 for the first building in the list)")
S_ACTIVE = ('S', 'Total tier of your active spells (each active spell counts its tier)')
WORKS = 'a bonus the game applies to the production of each building separately'

FORMULAS = {
    'Starmetal Alloys': [(0, F(r'v = \left\lfloor S \right\rfloor', S_ACTIVE))],
    'Elven Luck': [(0, F(r'v = \left(R + 1\right) \cdot Q',
                         ('R', 'Reincarnations you have made'), ('Q', 'Your Faction Coin find chance (%)'),
                         label='Faction Coins generated per trigger'))],
    'Wooden Dice': [
        (0, F(r'v_{1} = N^{0.4}', ('N', most('Arboreal City')), label='Chance to trigger (+%)')),
        (0, F(r'v_{2} = 80 \cdot N^{0.8}', ('N', most('Arboreal City')), label='Production (%)')),
        (0, F(r'v_{3} = 7.5 \cdot N^{0.75}', ('N', most('Arboreal City')), label='Faction Coins found (+%)'))],
    'Guardian Angels': [(0, F(r'v = 40 + 40 \cdot N^{0.4}', ('N', 'Number of buildings of tier 7 of your alignment you own (Cathedrals, Dark Temples or Monasteries)')))],
    'Angelic Wisdom': [(0, F(r'v = 5 \cdot \ln\left(1 + M\right)',
                             ('M', 'Your offline mana regeneration per second'), label='Offline spell casts (%)'))],
    'Angelic Dominance': [(0, F(r'v = 0.3 \cdot t^{0.7}', ('t', "Activity time of God's Hand in this Era (seconds)"),
                                label='Production bonus from Gems (+%)'))],
    'Angelic Fortitude': [(0, F(r'v = U^{0.7}', ('U', 'Combined activity time of all your available spells in this Reincarnation (seconds)')))],
    "Fool's Gold": [(0, F(r'v = 2 \cdot N^{0.6}', ('N', most('Witch Conclave'))))],
    'Hobgoblin Gladiators': [(0, F(r'v = 4 \cdot \left(\ln\left(1 + W\right)\right)^{2}',
                                   ('W', 'The worth of a Tax Collection (seconds)')))],
    'Lousy Architecture': [
        (0, F(r'v = 2 \cdot N^{0.75}', ('N', 'Number of buildings of that type you own'), label='Production of each Non-Unique building (%)')),
        (0, F(r'v = 0.01', ('v', 'Amount taken off the cost multiplier of Non-Unique buildings'), label='Cost multiplier'))],
    'Deadened Muscles': [(0, F(r'v = 40 + 4 \cdot N^{0.8}', ('N', most('Necropolis'))))],
    'Death Temples': [(0, F(r'v = 3 + 1.5 \cdot N^{0.5}', ('N', most('Necropolis'))))],
    'Undead Resilience': [(0, F(r'v = 5 + 1.5 \cdot \left(\ln\left(1 + F\right)\right)^{1.5}',
                                ('F', 'Undead Coins found in this Era (with the bonuses that increase them)')))],
    'Infernal Magic': [(0, F(r'v = 3 + 1.5 \cdot N^{0.5}', ('N', 'Number of buildings of tier 10 of your alignment you own (Heaven\'s Gates, Hell Portals or Ancient Pyramids)')))],
    'Burning Legion': [(0, F(r'v = 6 + 1.6 \cdot N^{0.6}', ('N', 'Most buildings of tier 10 of your alignment (Heaven\'s Gates, Hell Portals or Ancient Pyramids) you have built in this Reincarnation')))],
    'Devil Tyrant': [(0, F(r'v = 1.5 \cdot t^{0.5}', ('t', 'Time spent with Evil alignment in this Reincarnation (seconds)')))],
    'Evil Conquerors': [(0, F(r'v = 4 \cdot N^{0.8}', ('N', most('Hell Portal'))))],
    'Abyssal Furnace': [(0, F(r'v = 0.5 \cdot T^{2} \cdot N^{0.7}', TIER, ('N', most('Burning Abyss')),
                              label='Production of each building (%)'))],
    'Druidic Vocabulary': [(0, F(r'v = 1000 \cdot \left(12 - T\right)', TIER, label='Production of each building (%)'))],
    'Mabinogion': [(0, F(r'v = 16 \cdot 2^{12 - T}', TIER, label='Production of each building (%)'))],
    'Building Jungle': [(0, F(r'v = 3 \cdot N^{0.9}', ('N', 'Number of buildings of that type you own'),
                              label='Production of each building (%)'))],
    'Grove Farming': [(0, F(r'v = 0.8 \cdot \left(6 - \left|6 - T\right|\right)^{4}', TIER,
                            label='Production of each building (%)'))],
    'Earthly Bond': [(0, F(r'v = 2 \cdot N', ('N', most('Stone Pillars'))))],
    'Earthly Soul': [(0, F(r'v = 1.35 \cdot N^{0.35}', ('N', most('Stone Pillars'))))],
    'Evolutive Mutation': [(0, F(r'v = 12 + 3 \cdot N^{0.6}', ('N', most('Labyrinth'))))],
    'Deep Memory': [(0, F(r'v = 0.6 \cdot t^{0.6}', ('t', 'Length of your longest Era in this Reincarnation, including the current one (seconds)')))],
    'Overgrowth': [(0, F(r'v = 2 \cdot B^{0.75}', ('B', 'Most buildings you have owned at once in this Reincarnation')))],
    'Dimension Door': [(0, F(r'v = 2.25 \cdot \left(\ln\left(1 + M_{\max}\right)\right)^{2.25}',
                             (r'M_{\max}', 'Highest Maximum Mana you have had in this Reincarnation')))],
    'Battlehammers': [(0, F(r'v = 2.5 \cdot \left(\ln\left(1 + D\right)\right)^{2.5}', ('D', 'Dwarven Coins found in this Era (with the bonuses that increase them)')))],
    'Blood Sacrifices': [(0, F(r'v = 1.5 \cdot N^{0.95}', ('N', most('Dark Temple'))))],
    'Blade Dance': [(0, F(r'v = 60 + 60 \cdot K^{0.6}', ('K', "Combo Strike counter")))],
    'Dragonscales': [
        (0, F(r'v_{1} = 0.3 \cdot t^{0.7}', ('t', 'Time spent with Neutral alignment in this Reincarnation (seconds)'),
              label='All buildings (%)')),
        (0, F(r'v_{2} = 7.5 \cdot t^{0.75}', ('t', 'Time spent with Neutral alignment in this Reincarnation (seconds)'),
              label='The three buildings it names (%)'))],
    'Iron Flight': [(0, F(r'v = n \cdot \left(\ln\left(1 + O\right)\right)^{3}',
                          ('n', 'The number of spell effects on Iron Strongholds (a spell with several effects counts several times)'),
                          ('O', 'Your Offline production bonus')))],
    'Imposing Presence': [
        (0, F(r'v_{1} = 0.7 \cdot B^{0.7}', ('B', 'Neutral buildings you have built'), label='Mana Regeneration (+)')),
        (0, F(r'v_{2} = 75 + 1.25 \cdot \left(\ln\left(1 + t\right)\right)^{1.25}',
              ('t', 'Time spent as Dragon in this Reincarnation (seconds)'), label='Assistants while White Breath is active (%)'))],
    'Dragonborn': [
        (0, F(r'v_{1} = 5 \cdot t^{0.5}', ('t', 'All-time time spent as Dragon (seconds)'), label='Additive assistants')),
        (0, F(r'v_{2} = 0.6 \cdot t^{0.4}', ('t', 'All-time time spent as Dragon (seconds)'), label='Multiplicative assistants (%)')),
        (0, F(r'v_{3} = 0.8 \cdot t^{0.4}', ('t', 'All-time time spent as Dragon (seconds)'), label='Assistant production (%)'))],
    'Chromatic Scales': [(0, F(r'v = 250 \cdot j^{2}', ('j', "Tier Dragon's Breath is cast at (1 is the base tier); 0 bonus while the spell is unavailable")))],
    'Fang Food': [(0, F(r'v = 0.6 \cdot N^{0.6}', ('N', most('Dragon Pasture'))))],
    'Star Trading': [(0, F(r'v = 0.9 \cdot X', ('X', 'Most Royal Exchanges you have made at once in this Reincarnation')))],
    'Energy Recharge': [(0, F(r'v = 0.25 \cdot t^{0.5}', ('t', 'Time spent with Order alignment in this Reincarnation (seconds)')))],
    'Archon Pride': [
        (0, F(r'v_{1} = L', ('L', 'Your current Lineage level'), label='Assistants (%)')),
        (1, F(r'v_{2} = 1.15 \cdot L^{1.15}', ('L', 'Your current Lineage level'), label='Mana produced while offline (%)'))],
    'Absent-mindedness': [(0, F(r'v = 30 + 0.75 \cdot D^{0.75} + 4 \cdot \left(1 + E\right)^{4}',
                                ('D', 'Your excavation depth'),
                                ('E', 'Excavation Resets made in this Reincarnation (regular and free)')))],
    'Superior Consciousness': [(0, F(r'v = N', ('N', 'Number of buildings of that type you own'),
                                     label='Production of each Unique building (%)'))],
    'The Desire Within': [(0, F(r'v = 25 \cdot \left(\ln\left(1 + T\right)\right)^{2.5}',
                                ('T', 'Casts in this Era of the spells that match your alignment and your Order / Chaos / Balance')))],
    'Forbidden Will': [(0, F(r'v = 0.2 \cdot \left(0.5 \cdot \ln\left(1 + F\right)\right)^{2}',
                             ('F', 'Most Faction Coins you have found at once in this Reincarnation')))],
    'Magical Circuit': [(0, F(r'v = D^{1.15}',
                              ('D', 'Sum, over the researches you have selected, of the digit sum of the number for each research')))],
    'Sylvan Treasure Frills': [(0, F(r'v = 0.5 \cdot P', ('P', 'Your total building production per second'),
                                     label='Added to the base clicking reward'))],
    'Heresiarchs': [(0, F(r'v = 30 + 0.7 \cdot t^{0.7}', ('t', 'Combined activity time of your available Evil spells in this Reincarnation (seconds)')))],
    'Mana Creatures': [(0, F(r'v = 1.8 \cdot \left(0.5 \cdot \ln\left(1 + W\right)\right)^{1.8}',
                             ('W', 'Most mana you have produced at once in this Reincarnation')))],
    'Everlasting Materials': [(0, F(r'v = 0.25 \cdot B^{0.85}', ('B', 'Most buildings you have owned at once in this Reincarnation')))],
    'Bedrock Foundations': [(0, F(r'v = 10^{0.75 \cdot T}', TIER, label='Base production added to each building (per second)'))],
    'Pixie Dust Fertilizer': [(0, F(r'v = 0.02', ('v', 'Amount taken off the cost multiplier of those buildings'), label='Cost multiplier'))],
    'Expert Masonry': [(0, F(r'v = 0.01', ('v', 'Amount taken off the cost multiplier of all buildings'), label='Cost multiplier'))],
    'Magic Resistance': [(0, F(r'v = 0.02', ('v', 'Amount taken off the Excavation cost multiplier'), label='Cost multiplier'))],
    'Blackmail': [(0, F(r'v = 0.02', ('v', 'Amount taken off the cost multiplier of Royal Exchanges'), label='Cost multiplier'))],
}

# the buildings of a given tier for each alignment (Good, Evil, Neutral), as the game's tier lookup returns them
TIER_BUILDING = {
    1: ['Farm', 'Inn', 'Blacksmith', 'Warrior Barracks', 'Knights Joust', 'Wizard Tower', 'Cathedral', 'Citadel',
        'Royal Castle', "Heaven's Gate", 'Hall of Legends'],
    2: ['Farm', 'Inn', 'Blacksmith', 'Slave Pen', 'Orcish Arena', 'Witch Conclave', 'Dark Temple', 'Necropolis',
        'Evil Fortress', 'Hell Portal', 'Hall of Legends'],
    3: ['Farm', 'Inn', 'Blacksmith', 'Deep Mine', 'Stone Pillars', 'Alchemist Lab', 'Monastery', 'Labyrinth',
        'Iron Stronghold', 'Ancient Pyramid', 'Hall of Legends'],
}
# upgrades whose text names buildings through the tier lookup: the tiers, in the order of the text's %0, %1 ...
TIER_NAMED = {'Guardian Angels': [7], 'Infernal Magic': [10], 'Burning Legion': [10], 'Lava Pits': [9, 10], 'Titan Drill': [4, 7]}
FACTION_ALIGN = {0: 1, 1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 3, 7: 3, 8: 3, 9: 1, 10: 2, 12: 3}
