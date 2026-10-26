# Formula mismatches register

Every place where the formula in the game code (4.3.14, what the wiki shows) differs from the last documented version
(the user's 4.3.11 patch-notes doc or the old wiki). Keep every entry, including resolved ones: the older sources stay
different even when the code turns out to be right. Add a row whenever a new mismatch is found; change its status when it
is checked in game. The open ones are also listed in the Status section of `INFERENCES.md` (item 1).

| Object | Where on the wiki | Last documented version | Code (shown on the wiki) | Status |
|---|---|---|---|---|
| Second Crystal Fragment | Archaeology page | (ln(1+x))^3 / 5x10^7, x = Faction Coins found this Era | 4 * (ln(1+F))^3 / 5x10^7 (4x) | Open: needs the in-game "Chance: X%" tooltip (Ascension 2, Reincarnation 125+) |
| Third Crystal Fragment | Archaeology page | x / 66x10^6, x = Evil spells cast this Reincarnation | 66 * T / 66x10^6 = T / 10^6 (66x) | Open, same check |
| Second Stone Fragment | Archaeology page | x / 10^7, x = buildings built | 2 * B / 10^7 (2x) | Open, same check |
| Poison Vial | Archaeology page; perk on the Allegiance upgrades page (Drow Perk 4) | 100 * x^0.9 | (100 + P) * x^0.9, P = Drow lineage perk 4 bonus | Open: check the tooltip with and without the perk |
| Lantern of Guidance (artifact) | Archaeology page | ln(1 + x), x = mana regeneration per second | ln(x) | Open: check the chance tooltip |
| Lantern of Guidance (secret upgrade) | Secret upgrades page | 27 * x^0.3 (Mana Regeneration) | 8 * M^0.3 (constants swapped with Oil Lamp) | Open: needs the tooltip value at Ascension 1-2 |
| Oil Lamp (secret upgrade) | Secret upgrades page | 8 * x^0.3 (Maximum Mana) | 27 * Mmax^0.3 | Open, same check |
| Druid Perk 4, first value | Allegiance upgrades page (Druid lineage perks) | 3 * (ln(1 + x))^3, x = assistants owned | 2 * (ln(1 + A))^2 | Open: needs the tooltip value once the perk is reached |
| Wall Fragment | Secret upgrades page | 3 * (2 * (11 - T))^3 % | 1 + 5 * (2 * (11 - T))^2.5 (shown as 500 * (2 * (11 - T))^2.5 %) | Resolved: checked in game against four buildings, the code is right |
| Spark of Life, Primal Leaf, Dwarven Anvil, Eye of the Dragon, Excavated Mirage, Factory, Battlefield, Mana Loom (artifacts) | Archaeology page | Docs older than 4.3.1 use log10 or a different log term (Spark of Life: (log10(1+x))^2 / 60,000) | Natural-log versions (Spark of Life: (ln(1+F))^2 / 240,000, about 1.33x the old value) | Resolved: the in-game changelog for 4.3.1 says the logs were fixed for these artifacts |
| Nephilim's Blessing (Angel challenge 3) | Challenges page | 2.5 * (log10(1+M))^2.5 | 2 * (ln(1+M))^2.5 | Resolved: confirmed in game, the code is right |
| Silent Assistance (Druid challenge 1) | Challenges page | 1.3 * x^0.7, x = time spent in this Era | 3 * t^0.7 | Resolved: confirmed in game, the code is right |
| Dracomet Vault (Dragon challenge 6) | Challenges page | 0.03 * x^0.6 * t^0.9 %, x = Artifacts found, t = time spent in this Era | 0.03 * t^0.6 * N^0.9 (exponents the other way round: 0.6 on the time, 0.9 on the artifacts) | Resolved: confirmed in game, the code is right |
| Artificial Currency (Makers challenge 2), Tax Collection increase | Challenges page | log10 | ln (the code uses the natural logarithm) | Open: code checked, not confirmed in game |
| Warcry (Mercenary challenge reward): Call to Arms bonus y | Challenges page | y = 25 + (0.3 * L^0.975) (as given, grouping unclear) | y = 25 + (0.3 * L)^0.975, L = buildings Call to Arms counts | Open: compare with the Call to Arms tooltip |

Not mismatches (agree with the older sources): First Iron Fragment, Wall Chunk, Mathematician, Folgoration (A12250), Spark of
Life's Faction Coin find chance, and the other lore artifacts listed as confirmed in `INFERENCES.md` (apart from cleanup terms
like 0.5 and +1).

## Other mismatches (not formulas)

Places where the last documented version of something (a requirement, a reward text, a line that is missing) differs from the game
or the code. Same rules as above: keep resolved entries.

| Object | Where on the wiki | Last documented version | Game / code | Status |
|---|---|---|---|---|
| An Untimely Death (Archon challenge 2), requirement | Challenges page | Offline production of at least 1e25 | at least 1e20 % (the code tests the raw multiplier >= 1e18, which the game shows as 1e20 %) and 1e11 assistants | Open: code checked, the game's own text agrees with the code; not confirmed in game |
| Identity Shaper (Djinn challenge 3), reward text | Challenges page | "Catalyst casts an additional spell" | "Gain the Catalyst spell. Also increases Catalyst casts stat by 100 per cast." | Resolved: the in-game changelog says Djinn Challenge 3 now also grants Catalyst regardless of Djinn Bloodline and increases Catalyst casts by 100 per cast |
| Artificial Currency (Makers challenge 2), line about Goblin Upgrade 6 | Challenges page | no line about Ascension Penalties | the reward also removes Ascension Penalties from Hobgoblin Gladiators (Goblin Upgrade 6); checked in the code: its penalty start becomes 5 (no penalty) once the challenge is done | Open: code checked, not confirmed in game |
| Research budget at Ascension 3 and 4 (the research page does not show it yet) | Research page (slot / budget sources) | Budget starts at 0 and is raised by Reincarnation Power at Reincarnation 170 (+3000) and a 2nd Facility Upgrade (+3000), 6000 in total, and by the Archon Bloodline (+500 and more). Ascension 4: each Trade Treaty, Friendship Pact, Alliance and Union gives +2000 (+8000, 14,000 in total) | Budget is per branch. Reincarnation Power 4 (from Reincarnation 170) gives 150 x Ascension + 3.5 x (R - 159) (about 490 at Reincarnation 170); Research Facility Upgrades (from Reincarnation 180) 500 + (ln(1 + sqrt(a b)))^3 each; Archon Bloodline (ln(1 + t))^3 with t = time played this Era; four perks and the Faceless Set capped at 3000 each; Mercenary contracts. Ascension 4: +5000 for each Trade Treaty and each Union of the nine base factions (Friendship Pact and Alliance give nothing), so 10,000 with one faction's Treaty and Union | Open: code checked; compare in game |
