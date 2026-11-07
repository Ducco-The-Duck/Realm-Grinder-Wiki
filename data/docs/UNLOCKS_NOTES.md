# Working notes for the Unlocks page: when each mechanic unlocks (read from the code, build 4.3.15)

Source of the list: the user's own list of mechanics and Reincarnations, checked against the code. This is a work file; the page content is in `data/handwritten/unlocks.json`.
Ascension starts: A1 = Reincarnation 40, A2 = 100, A3 = 160, A4 = 220.

| Reincarnation | Mechanic | Result of the check |
|---|---|---|
| 0 | Excavations, Neutral factions, Prestige factions | no Reincarnation test for any of them: Excavations need the "Archeology" upgrade (appears at 1e9 Gems, costs 1e29 coins); Neutral factions need one of the 1e30 upgrades (Fragment of a Titan Statue, Druidic Runestone, Octopus Shaped Spine); the underworld (Prestige) ones need Passage to the Underworld |
| 1 | Reincarnation Power 1 upgrade | game text at Reincarnation 1: buy the Reincarnation Power upgrade |
| 2 | Challenges | confirmed (tab needs Reincarnation 2; game text at 2) |
| 3 | Mercenaries | confirmed (Mercenary Tribute upgrade available from 3; game text at 3). At 3 (or owning Underworld Diplomacy) the underworld coins, exchanges and heritages are also unlocked |
| 7 | Bloodlines | confirmed (Bloodline upgrade needs 7; game text at 7) |
| 14 | **Spiritual Surge** (spell, based on Reincarnations) | missing from the user's list; code and game text at 14 |
| 16 | Vanilla faction research | confirmed (game text at 16). Also first unique buildings of the six vanilla factions |
| 24 | Neutral faction research | confirmed (game text at 24: lost city). Also first unique buildings Olympian Hall, Stonehenge, Sunken City; artifact Key to the Lost City |
| 32 | Prestige faction research | confirmed (game text at 32: Underworld). Also unique buildings Dwarven Forge, Spider Sanctuary; artifact Earth Core |
| 40 | Ascension | confirmed (button enabled from 40; game text from 39) |
| 42 | Dragons | confirmed (game text at 42: egg excavation; artifact Spiky Rough Egg) |
| 42 | Spell tiers | tier N needs Ascension N-1; each spell has its own Reincarnation, 42 to 48 (Dragon's Breath 54/60/66/72) |
| 46 | Wyrm's Den (Dragon unique building) | missing from the user's list |
| 60 | Lineages | confirmed (230 at Ascension 4) |
| 75 | Mercenary research | confirmed (game text at 75). Also Mercenary unique buildings |
| 100 | Second alignment, second unique buildings (vanilla and neutral) | these follow Ascension 2 (which starts at 100), no separate Reincarnation test found |
| 100 | Artifact Sets | confirmed (225 at Ascension 4) |
| 105 | Union additional effects | confirmed (the nine base Unions test 105) |
| 110 | Trade Treaties of Dwarven, Drow, Dragon | the code tests 110 (165 at Ascension 3, 235 at 4) only for the treaties; no test hiding the prestige factions themselves was found |
| 112 | second unique buildings of the prestige factions | confirmed (High Bastion, Brothel, Dragon Pasture) |
| 115 | Prestige faction Unions | confirmed (Dwarven, Drow, Dragon Union) |
| 125 | Astral factions | confirmed for the Trade Treaties and the three Iron Fragment artifacts; their first unique buildings need 130 |
| 130 | Astral unique buildings, unions, bloodlines and lineages | from the user; the code has several Reincarnation 130 tests in the astral places (the first unique buildings, the astral Unions, the astral faction selection), the Bloodline and Lineage tests were not traced individually |
| 135 | Astral faction challenges | from the user; the code was not checked for it |
