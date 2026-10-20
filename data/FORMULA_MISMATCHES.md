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

Not mismatches (agree with the older sources): First Iron Fragment, Wall Chunk, Mathematician, Folgoration (A12250), Spark of
Life's Faction Coin find chance, and the other lore artifacts listed as confirmed in `INFERENCES.md` (apart from cleanup terms
like 0.5 and +1).
