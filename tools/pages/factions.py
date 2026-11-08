"""The factions (names, alignment, path, role), shared by the page builders."""
FNAME = {0: 'Fairy', 1: 'Elf', 2: 'Angel', 3: 'Goblin', 4: 'Undead', 5: 'Demon', 6: 'Titan', 7: 'Druid', 8: 'Faceless',
         9: 'Dwarf', 10: 'Drow', 11: 'Mercenary', 12: 'Dragon', 13: 'Archon', 14: 'Djinn', 15: 'Makers'}
# the name the search matches (the community codes map to these)
FSEARCH = {**FNAME, 1: 'Elven', 9: 'Dwarven'}
# base factions: alignment 1 Good, 2 Evil, 3 Neutral; axis 4 Order, 5 Chaos, 6 Balance
FACTIONS = [
    {'i': 0, 'n': 'Fairy', 'role': 'base', 'al': 1, 'ax': 5}, {'i': 1, 'n': 'Elf', 'role': 'base', 'al': 1, 'ax': 6},
    {'i': 2, 'n': 'Angel', 'role': 'base', 'al': 1, 'ax': 4}, {'i': 3, 'n': 'Goblin', 'role': 'base', 'al': 2, 'ax': 6},
    {'i': 4, 'n': 'Undead', 'role': 'base', 'al': 2, 'ax': 4}, {'i': 5, 'n': 'Demon', 'role': 'base', 'al': 2, 'ax': 5},
    {'i': 6, 'n': 'Titan', 'role': 'base', 'al': 3, 'ax': 4}, {'i': 7, 'n': 'Druid', 'role': 'base', 'al': 3, 'ax': 6},
    {'i': 8, 'n': 'Faceless', 'role': 'base', 'al': 3, 'ax': 5}, {'i': 11, 'n': 'Mercenary', 'role': 'merc'},
    {'i': 9, 'n': 'Dwarf', 'role': 'prestige', 'al': 1}, {'i': 10, 'n': 'Drow', 'role': 'prestige', 'al': 2},
    {'i': 12, 'n': 'Dragon', 'role': 'prestige', 'al': 3},
    {'i': 13, 'n': 'Archon', 'role': 'astral', 'ax': 4}, {'i': 14, 'n': 'Djinn', 'role': 'astral', 'ax': 5},
    {'i': 15, 'n': 'Makers', 'role': 'astral', 'ax': 6},
]
