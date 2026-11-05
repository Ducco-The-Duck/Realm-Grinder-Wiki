# Formula mismatches register

Every place where the formula in the game code (4.3.14, what the wiki shows) differs from the last documented version
(the user's 4.3.11 patch-notes doc or the old wiki). Add a row whenever a new mismatch is found; when it is checked in game (or settled some
other way), move its row to `FORMULA_MISMATCHES_RESOLVED.md` with the status "Resolved: ...", because the older sources stay
different even when the code turns out to be right. The open ones are also listed in `STATUS.md` (item 1).

| Object | Where on the wiki | Last documented version | Code (shown on the wiki) | Status |
|---|---|---|---|---|
| Poison Vial | Archaeology page; perk on the Allegiance upgrades page (Drow Perk 4) | 100 * x^0.9 | (100 + P) * x^0.9, P = Drow lineage perk 4 bonus | Open: check the tooltip with and without the perk |
| Druid Perk 4, first value | Allegiance upgrades page (Druid lineage perks) | 3 * (ln(1 + x))^3, x = assistants owned | 2 * (ln(1 + A))^2 | Open: needs the tooltip value once the perk is reached |
| Artificial Currency (Makers challenge 2), Tax Collection increase | Challenges page | log10 | ln (the code uses the natural logarithm) | Open: code checked, not confirmed in game |

Not mismatches (agree with the older sources): First Iron Fragment, Wall Chunk, Mathematician, Folgoration (A12250), Spark of
Life's Faction Coin find chance, and the other lore artifacts listed as confirmed in `INFERENCES.md` (apart from cleanup terms
like 0.5 and +1).

## Other mismatches (not formulas)

Places where the last documented version of something (a requirement, a reward text, a line that is missing) differs from the game
or the code. Same rules as above. None is open at the moment.

| Object | Where on the wiki | Last documented version | Game / code | Status |
