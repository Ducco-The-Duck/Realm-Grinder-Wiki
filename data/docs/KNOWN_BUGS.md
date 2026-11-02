# Known bugs in the game's texts

Places where the game's own text disagrees with what the game does (4.3.15). The wiki shows what the game does and says so in a
"Known bug" note on the page. Add a row whenever we notice another one, and add the note to the page that shows it.

| Where | What the text says | What the game does | Shown on |
|---|---|---|---|
| Mystic Maze (Faceless challenge reward) | "the highest amount of buildings you had in this Reincarnation" | the highest number you currently own of any single building type (including bonuses that make buildings count as more), which starts over every Era | Challenges page (Known bug note), `BUGS` in `tools/export_challenges.py` |
| Art of the Crow (Secret upgrade) | the first paragraph says Evil Faction and Set use the production bonus from Gems | Evil uses the mana produced in this Reincarnation, as the Evil line of the same text says | Secret Upgrades page (Known bug note), `BUGS` in `tools/build_upgrades_page.py` |
