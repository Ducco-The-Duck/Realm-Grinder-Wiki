# Inferences and open questions

Everything on the wiki pages that comes from the game's **code** (as opposed to its text) rests on
interpretations of obfuscated names. This file lists what was inferred, how, and how sure we are,
so it can be checked against the real game. Update it when something is confirmed or corrected.

Confidence: **high** = confirmed by the game's own UI text or consistent in several places;
**medium** = consistent but only one line of evidence; **low** = a guess worth checking in-game.

## Corrected so far

| Was | Now | How it was caught |
|---|---|---|
| "Bloodline" for the prestige-faction field | "Prestige faction" / "No prestige faction" | User (plays the game) |
| Spell counter = "time active" | Number of **casts** | Game UI: "Cast This Era: %0, Total: %1" |
| `§#!!§.§!-§()` = "clicking reward" | **Number of assistants** (before multipliers) | User, from the 4.3.x patch notes; confirmed in code: Titan Sized Walls ("based on assistants owned") calls the wrapper `§&c§.§!-§()`, which calls it |
| "Neutral Order path" | "Order alignment" (a second alignment axis: Order/Chaos/Balance) | Contradiction with "Evil alignment" on the same artifact |
| "Make N excavations" | "N excavations since your last Excavation Reset" | Code: the counter `§1!5§` is zeroed by both kinds of Excavation Reset |

## Notation

- `Math.pow(Math.log(x), n)` is `(ln x)^n` (the log is taken once and the result raised to n), **not** an
  iterated log. Formulas are written `\left(\ln(...)\right)^{n}` and never `\ln^{n}`.
- Large round constants are written as powers of ten (10^6, 5 × 10^7, ...).
- Some formulas keep the game's literal factors (e.g. `66·T / 6.6×10^7`), even where they simplify.

## Stat arrays (`§8G§.§5!V§`, `§=y§`, `§@w§`)

| Item | Meaning | Confidence | Evidence |
|---|---|---|---|
| `§5!V§[i]` | stat `i` **this Era** | medium | Abdication code folds `5!V` into `=y` and zeroes it |
| `§=y§[i]` | stat `i` for earlier Eras of this Reincarnation | medium | same; "Max depth in this Reincarnation" uses `max(5!V, =y)` |
| `§@w§[i]` | stat `i` for previous Reincarnations (so 5!V + =y + @w = all-time) | medium | `=y` is added into `@w` at Reincarnation; only a full game wipe zeroes it |
| index 4 | Clicks | high | stats panel / trophy text |
| index 1 | Playtime (seconds, this Era) | medium | `=y[29] = 5!V[1]` at Abdication, "Playtime: %0" |
| index 15 / 40 | Spells Cast / Spells Cast (Max) | high | stats panel |
| index 24 | Royal Exchanges made | high | stats panel |
| index 35 | Excavations made | high | stats panel |
| index 135 | Excavation Resets (Free) | high | stats panel |
| index 104 | Excavation Resets (regular) | medium | incremented in the excavation code; no panel label |
| index 98 | Excavation depth | medium | "Max Excavation Depth" trophy |
| index 3 / 61 | Evil time spent / Mercenary time spent | medium | trophy text |
| index 96 | Assistants (Max) | high | stats panel |
| index 3 | Time spent with Evil alignment (s) | medium | trophy text; Arachnid Figurine ("Embrace Evil") |
| index 50 + faction | Time spent as that faction (s): 52 Angel, 54 Undead, 55 Demon, 61 Mercenary | medium | 61 from trophy text; artifact themes match the rest |
| index 49 | Times you affiliated with the Mercenaries | medium | "No Recruiting" trophy: "without ever affiliating with the Mercenaries" checks it is 0 |
| index 101 | Elven Luck streak (clicks in a row that triggered it); `=y[101]` = best this Reincarnation | medium | +1 in the Elven Luck click branch, zeroed on a click without it |
| `=y[39]` | Longest earlier Era in this Reincarnation (s) | medium | upgrades "based on your longest Era in this Reincarnation" use `max(playtime, =y[39])` |
| index 133 | Maximum Mana reached (max with `=y`) | medium | Encompass / Dimension Door texts |
| indices 90-95, 154 | Research points bought per branch (Spellcraft, Craftsmanship, Divine, Economics, Alchemy, Warfare; 154 Forbidden) | medium | the repeatable research-point upgrade adds 1 to `90 + branch`; branch names table |

## Game-state fields (`§8G§.…`)

| Field | Meaning | Confidence | Evidence |
|---|---|---|---|
| `§-!^§` | current faction (0 Fairy … 11 Mercenary, 12 Dragon, 13 Archon) | high | `XFaction` tags, unlock texts |
| `§#3§` | **prestige faction** (-1 = none; 9 Dwarf, 10 Drow, 12 Dragon) | medium | artifact themes and unlock texts agree, except the "Drow Union" upgrade checks `== 2` (unexplained) |
| `§,!Y§` | alignment: 1 Good, 2 Evil, 3 Neutral | high | alignment-name table |
| `§9!m§` | second axis: 4 Order, 5 Chaos, 6 Balance | high | alignment-name table `[Neutral, Good, Evil, Neutral, Order, Chaos, Balance]` |
| `§8!H§` | Reincarnation count | high | "Reincarnation %0" label |
| `§,P§` | Ascension count | medium | "Requires ascension %0 to increase further." |
| `§1!5§` | Excavations **since the last Excavation Reset** (compared with the artifact threshold) | high | zeroed by regular and free Excavation Resets; "Max Excavation Depth" trophy tracks it |
| `§8t§` | Trophies unlocked (not feats, quests or artifacts) | high | +1 in the trophy-unlock code |
| `§"!0§` | Gems | high | "No Recruiting" trophy ("Reach 1 Novg Gems") compares it with 1e90 |
| `§["&§` | Consecutive days played (UTC server days) | medium | +1 when today = last day + 1, else reset to 1 |
| `§1!#§[f]` | Lineage level of faction `f` | medium | Genealogist / Chemistry "total amount of Lineage levels" sum it |
| spell `§?j§`/`§<q§`/`§<!G§` | Spell activity time (s): this Era / earlier Eras / previous Reincarnations | high | UI "Active Time This Era / This Reincarnation" |
| spell `§`r§` | Spell tier, stored from 0 (the game shows +1) | medium | "Unlock Tier %0" prints the stored value + 1; Dragon Soul's "five deep breaths" = stored 4 |
| upgrade `§?!6§` | Upgrade permanently unlocked (set when a challenge reward is bought) | low | Veteran Figurine checks it on "Dracomet Vault" (a Dragon challenge reward) |
| trophy "Research Mercenary Trophy" | Hidden flag: Mercenary researches unlocked | medium | gates Mercenary researches (Chemistry, Flanking, ...) |
| `§7d§(id)` / `§<P§(id)` | upgrade/trophy `id` owned/purchased | medium | used as "has X" in conditions; difference between the two not established |

## Helpers used by artifact find-chance formulas

| Helper | Described as | Confidence | Check in-game? |
|---|---|---|---|
| `§&c§.§1",§()` | **Research points spent** (sum of purchased researches' cost) | **high** | User + patch notes; research Tinkering (C150) "based on Research points" calls it |
| `§#!!§.§,d§()` | Offline production bonus (multiplier or %?) | medium | units unclear |
| `§#!!§.§@!?§()` | **Royal Exchange bonus** (% per exchange) | **high** | User-confirmed; research Offering (E300) text "based on Royal Exchange Bonus" calls it |
| `§#!!§.§!-§()` | **Number of assistants** (counts purchased building production upgrades of tier ≤ 2; floor'd) | **high** | User + patch notes; Titan Sized Walls goes through its wrapper `§&c§.§!-§(multipliers, raw)` |
| `§#!!§.§57§()` | Mana regeneration **per tick**; the game always uses `§57§() * 30` for the per-second (m/s) value | **high** | Every call site multiplies by 30 (e.g. `* 30 >= 300`); user's patch notes give ln(1+x)^3/1e6 with x = mana regen, which equals First Iron Fragment's `ln(1 + §57§()*30)^3/1e6` |
| `§&c§.§0#§(-1,true)` | Total buildings owned | medium | text: "Total Buildings" |
| `§&c§.§@![§(true,false,true)` | Faction Coins found this Era | medium | text: "Faction Coins" |
| `§&c§.§]!s§(2,false,false,true)` | Total casts of Evil spells this Reincarnation, before bonus multipliers | medium | parameter meanings read from code, not UI |
| `spell.§2-§` | Casts of that spell this Era | **high** | UI "Cast This Era: %0" |
| `§&c§.§9!P§(spell, allTime, eraOnly, raw)` | Casts of a spell | high | same fields as the UI cast counter |
| `§&c§.§7i§(spell, allTime, eraOnly, raw)` | Activity time of a spell (s) | high | same fields as "Active Time" UI |
| `§&c§.§1!;§(spell)` | Spell duration (s), set at cast | medium | "based on its duration" upgrades |
| `§&c§.§?&§(true)` | Sum of the (displayed) tiers of active spells | medium | "Autoclick based on active spells" |
| `§&c§.§"" §(false,false,true)` | Activity time of your most used spell this Reincarnation (some spells excluded) | medium | Plagued Buildings / Mercenary Spirit texts |
| `§#!!§.§0F§()` | Faction Coin find chance (%) | high | "Current Chance to find Faction Coins: %0%." |
| `§#!!§.§2!&§()` | Maximum Mana | high | base 1000 plus upgrade bonuses |
| `§#!!§.§@"0§()` (`§&c§.§!-§(false,true)`) | Base Assistants | high | UI "Base Assistants: %0" |
| `§#!!§.§^!&§()` | Factions you bought an upgrade from as a Mercenary | high | Harlequin trophy text, same function |
| `§&c§.§&!<§(branch, true)` | Research points bought in a branch, all Reincarnations | medium | see stat indices 90-95 |
| `§&c§.§3"&§` | Mana produced (stat 16) | high | stats panel "Mana Produced" |
| `§&c§.§>!h§` | Clicks (stat 4) | high | stats panel |
| `§&c§.§`!=§()` | Total Lineage level | medium | Genealogist text |
| `§@W§.§'!b§()` | Combo Strike's current production bonus (%) | medium | Combo Strike tooltip "Current: %1%" |
| `Brainwave.§"!P§()` | Brainwave headstart (s): 600 per tier + bonuses | medium | tooltip "Increase headstart time based on spell tier", "Headstart: %0" |
| `§8G§.§%Z§(building)` | Buildings of that type owned; without `true`, times bonuses that multiply the count | medium/low | raw field is the owned count; the multiplier list was not traced to UI text |

**Name collisions:** the obfuscator reuses member names in different classes, so `§#!!§.§!-§` and
`§&c§.§!-§` are different functions (the second wraps the first). Always key helpers by class + name.

## Mechanics

| Claim | Confidence | Evidence |
|---|---|---|
| On every excavation, each not-yet-found artifact whose requirements are met rolls its own chance; chance ≥ 100 means found on the next excavation | high | `§&b§()` loop in the excavation code; matches Flame of Bondelnar/Horn of the Kings at 0.5% (user-confirmed) |
| Chance values are percentages | high | compared with a 0–100 random roll |
| 903 trophies = registry entries with none of the four special flags | high | matches the in-game count |
| Trophy categories 0–4 = Allegiances, Misc, Magic, Buildings, Secret | high | counts match user's numbers exactly (45/170/62/566/60) |
| Quest vs Lore artifact = lore flag false/true | high | counts 25/81 match |

## Open: code vs. patch-notes doc (4.3.11) disagree on constant factors

The game's own artifact tooltip prints "Chance: X%" using exactly the same getter the wiki transcribes
(`§5",§`, shown as a percent), and the in-game changelog lists no change to these artifacts in
4.3.12-4.3.14. So the code is what the game applies, but the user's patch-notes doc differs:

| Artifact | Code (4.3.14) | Doc (user) | Ratio |
|---|---|---|---|
| Second Crystal Fragment | 4 · (ln(1+F))³ / 5×10⁷ | (ln(1+x))³ / 5×10⁷, x = Faction Coins found this Era | 4× |
| Third Crystal Fragment | 66 · T / 66×10⁶ (= T / 10⁶) | x / 66×10⁶, x = Evil spells cast this Reincarnation | 66× |
| Second Stone Fragment | 2 · B / 10⁷ | x / 10⁷, x = buildings built | 2× |

The wiki shows the code's version. These artifacts need Ascension 2 and Reincarnation 125+, so the user
cannot check the in-game "Chance:" readout yet. The in-game changelog (4.3.14 back to 3.0.0) never mentions
these fragments (only Wall Fragment), so it does not explain the difference. If someone can, compare the tooltip percent to both.
First Iron Fragment agrees exactly with the doc.

**Logs changed in 4.3.1.** The in-game changelog for 4.3.1 says "Fixed logs in ... spark of life, primal leaf,
dwarven anvil, eye of the dragon, excavated mirage, factory, battlefield and mana loom artifacts". A 4.3.0 doc
gives Spark of Life as (log10(1+x))^2 / 60,000; the current code is 2*(0.5*ln(1+F))^2 / 120,000 = (ln(1+F))^2 / 240,000
(about 1.33x the old value). Docs older than 4.3.1 will disagree with the code for these eight artifacts; the code is current.

## Not decoded yet

- All 106 artifacts' unlock conditions and all find-chance formulas are now decoded (Chocolate Cookie and
  Fossilized Rodent have no unlock condition). The items marked medium/low above are the ones worth checking
  in-game, e.g. by comparing the tooltip's "Chance: X%" with the formula.
