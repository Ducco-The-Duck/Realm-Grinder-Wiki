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
| "Neutral Order path" | "Order alignment" (a second alignment axis: Order/Chaos/Balance) | Contradiction with "Evil alignment" on the same artifact |

## Stat arrays (`§8G§.§5!V§`, `§=y§`, `§@w§`)

| Item | Meaning | Confidence | Evidence |
|---|---|---|---|
| `§5!V§[i]` | stat `i` **this Era** | medium | Abdication code folds `5!V` into `=y` and zeroes it |
| `§=y§[i]` | stat `i` for earlier Eras of this Reincarnation | medium | same; "Max depth in this Reincarnation" uses `max(5!V, =y)` |
| `§@w§[i]` | stat `i` all-time | low | seen alongside the others, not traced |
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

## Game-state fields (`§8G§.…`)

| Field | Meaning | Confidence | Evidence |
|---|---|---|---|
| `§-!^§` | current faction (0 Fairy … 11 Mercenary, 12 Dragon, 13 Archon) | high | `XFaction` tags, unlock texts |
| `§#3§` | **prestige faction** (-1 = none; 9 Dwarf, 10 Drow, 12 Dragon) | medium | artifact themes and unlock texts agree, except the "Drow Union" upgrade checks `== 2` (unexplained) |
| `§,!Y§` | alignment: 1 Good, 2 Evil, 3 Neutral | high | alignment-name table |
| `§9!m§` | second axis: 4 Order, 5 Chaos, 6 Balance | high | alignment-name table `[Neutral, Good, Evil, Neutral, Order, Chaos, Balance]` |
| `§8!H§` | Reincarnation count | high | "Reincarnation %0" label |
| `§,P§` | Ascension count | medium | "Requires ascension %0 to increase further." |
| `§1!5§` | Excavations made (in a run; compared with the artifact threshold) | medium | "Excavations" progress bar |
| `§7d§(id)` / `§<P§(id)` | upgrade/trophy `id` owned/purchased | medium | used as "has X" in conditions; difference between the two not established |

## Helpers used by artifact find-chance formulas

| Helper | Described as | Confidence | Check in-game? |
|---|---|---|---|
| `§&c§.§1",§()` | **Research points spent** (sum of purchased researches' cost) | low–medium | yes: confirm "spent" vs "earned/total" |
| `§#!!§.§,d§()` | Offline production bonus (multiplier or %?) | medium | units unclear |
| `§#!!§.§@!?§()` | **Royal Exchange bonus** (per exchange?) | low–medium | yes; text nearby says "Individual Bonus: %0%" |
| `§#!!§.§!-§()` | **Clicking reward** (coins per click) | medium | upgrades "increase base clicking reward" feed it |
| `§#!!§.§57§()` | Mana regeneration per second | medium | "m/s Mana Regeneration" strings |
| `§&c§.§0#§(-1,true)` | Total buildings owned | medium | text: "Total Buildings" |
| `§&c§.§@![§(true,false,true)` | Faction Coins found this Era | medium | text: "Faction Coins" |
| `§&c§.§]!s§(2,false,false,true)` | Total casts of Evil spells this Reincarnation, before bonus multipliers | medium | parameter meanings read from code, not UI |
| `spell.§2-§` | Casts of that spell this Era | **high** | UI "Cast This Era: %0" |

## Mechanics

| Claim | Confidence | Evidence |
|---|---|---|
| On every excavation, each not-yet-found artifact whose requirements are met rolls its own chance; chance ≥ 100 means found on the next excavation | high | `§&b§()` loop in the excavation code; matches Flame of Bondelnar/Horn of the Kings at 0.5% (user-confirmed) |
| Chance values are percentages | high | compared with a 0–100 random roll |
| 903 trophies = registry entries with none of the four special flags | high | matches the in-game count |
| Trophy categories 0–4 = Allegiances, Misc, Magic, Buildings, Secret | high | counts match user's numbers exactly (45/170/62/566/60) |
| Quest vs Lore artifact = lore flag false/true | high | counts 25/81 match |

## Not decoded yet

- 21 artifacts have extra unlock conditions (time of day, per-spell time arrays, helper calls) listed as "additional conditions not listed here"; 9 show only the game's hint.
- ~57 lore artifacts have find-chance formulas using helpers not yet named (generic "depends on your stats" wording).
- Stat indices 133, 101, 39, 61 and the `§@w§` all-time array need confirming.
