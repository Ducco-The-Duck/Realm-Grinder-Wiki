# Inferences and open questions

Everything on the wiki pages that comes from the game's **code** (as opposed to its text) rests on
interpretations of obfuscated names. This file lists what was inferred, how, and how sure we are,
so it can be checked against the real game. Update it when something is confirmed or corrected.

Confidence: **high** = confirmed by the game's own UI text or consistent in several places;
**medium** = consistent but only one line of evidence; **low** = a guess worth checking in-game.

## Status: what is still open (everything else below is resolved or accepted)

Only these need checking; remove an item when it is settled.

1. **Formula disagreements** (full register, including resolved ones: `data/FORMULA_MISMATCHES.md`; code against older sources; the wiki shows the code, which is probably right; each needs the
   in-game tooltip value). Object, then where it is on the wiki:
   - **Second Crystal** (4x), **Third Crystal** (66x), **Second Stone** (2x): fragment factors that differ between the code and
     the old patch-notes doc (4.3.11). Archaeology page (artifact chances). The in-game "Chance: X%" tooltip is visible only
     before you own the artifact.
   - **Poison Vial:** the chance is K / 10^7 with K = (100 + P) * x^0.9 (x = Combo Strike counter, K before the Ascension
     penalty). The patch-notes doc has 100 * x^0.9, i.e. P = 0. P is the Drow lineage perk 4 bonus, 0.5 * floor(Time played this
     Era), unit and size unconfirmed. Archaeology page; the perk is on the Allegiance upgrades page (Drow Perk 4). Check the
     tooltip with and without the perk.
   - **Lantern of Guidance (artifact):** patch notes have ln(1 + x), the code has ln(x) for x = mana regeneration per second
     (no +1). Archaeology page. Check the chance tooltip.
   - **Lantern of Guidance (secret upgrade)** and **Oil Lamp (secret upgrade):** the code reads (4 * M^0.2)^p for Lantern (Mana
     Regeneration) and (9 * Mmax^0.2)^p for Oil Lamp (Maximum Mana), with p = 1.5 for an Order / Chaos faction, which is
     8 * M^0.3 and 27 * Mmax^0.3. The patch notes give 27 * x^0.3 for Lantern and 8 * x^0.3 for Oil Lamp, so the two constants
     are swapped between the code and the notes (4.3.11 notes: Lantern 9 * x^0.2 -> 27 * x^0.3, Oil Lamp 4 * x^0.2 -> 8 * x^0.3).
     Spark of Life (Faction Coin find chance^0.3) agrees. The installed game is 4.3.14 and its embedded changelog does not
     touch these upgrades after 4.3.2. Secret upgrades page. Needs the in-game tooltip value (at Ascension 1-2, no penalty).
   - **Druid Perk 4 (lineage perk), first value:** the old wiki has 3 * (ln(1 + x))^3 for x = assistants owned; the code has
     2 * (ln(1 + A))^2 with A = assistants. Allegiance upgrades page (Druid lineage perks). Not mentioned in any more recent
     document. Needs the in-game tooltip value once the perk is reached.
2. **Upgrade page verification** (the user checks the upgrade pages in game; built from code until then):
   - **Magic upgrades, Mercenary-only entries** (Round Table, Dark Covenant, Secret Exchange): unchecked because the user has
     not reached them. Arcane Brilliance is left for the Spells item.
   - **Secret and Misc upgrades pages:** to be checked as a whole (what was confirmed so far is under Resolved).
   - **Allegiances upgrades** (treaty tiers and the twelve faction upgrades per faction; built from code, unchecked; prices are
     not shown on the page). A Reincarnation requirement also rules out the Ascensions that cannot reach it (A1 spans R40-99,
     A2 R100-159, A3 R160-219), so Dwarven / Drow Union (R115) start at Ascension 2:
     - **Alternatives:** a faction upgrade's tier requirement can be replaced by the faction's Legacy upgrade (Bronze / Silver /
       Gold / Diamond), and a Union's building upgrade by the Mercenary Building Contract in some cases (helper `§`!i§`, not
       spelled out on the page).
     - **Dragon Friendship Pact / Alliance** require Dwarven Coins and Drow Coins found in this Era (stats 41 and 42, read as
       the Dwarven and Drow coin counters because stats 6 to 11 and 41, 42 are summed as faction coins found).
     - **Formulas written by hand** (`tools/alleg_manual.py`, `tools/alleg_manual_family.py`, read from the static value functions
       and the production code, not shown in any tooltip): the Druid, Dragon, Archon, Djinn and other faction upgrades without a
       number in the text, the Advanced Heritages, bloodlines, Burning Abyss, Wyrm's Den. The earlier doubtful readings (the Tax Collection worth, the Magical Circuit digit sum, the Burning Abyss digit rule) were
       explained by the user and the texts reworded. Not given a formula: Green Fingers Discount (value depends on total production), Seraphim Wings' extra
       terms, the Mercenary-only variants of Evolutive Mutation and Deep Memory.
     - Iron Flight counts spell *effects* on Iron Strongholds (a spell with two effects counts twice): confirmed by the user's tooltip.
     - Heritages and Advanced Heritages (including the multiplier `m` and the Mercenary Badge) were confirmed by the user.
     - Bloodlines, Lineages with their perks, and the Artifact Sets were checked in the game by the user (only the first value of Druid Perk 4 is open, see item 1).
     - Mercenary Upgrades 1-16, Remnants and the Mercenary contracts' extras are still not covered (Legacies: see their own item). Each individual faction upgrade is still to be checked.
3. **Research slot sources** (hover popup of each branch's large icon on the Research page): built from the game's slot
   function, unchecked. Base 4 slots, 1 from Ascension 2; before Ascension 2 the extras are the six slot upgrades (granted
   automatically with their Secret trophy, never shown in the game), Reincarnation Power 2 (R75 as Mercenary by alignment,
   R90 every branch), Ancient Device Power, Legacy of the Dwarven Kings, Dark Light of Bondelnar, and -1 for Mercenaries at
   Ascension 1; at Ascension 2 only, the Archon Bloodline. From Ascension 2 on every other source is ignored. From Ascension 3 the slots become a research budget per branch (code: a research can be bought while points spent in the branch + its point value <= the branch budget); the sources are listed in `FORMULA_MISMATCHES.md` (read from the code and shown in the click-open popup of the large branch icon on the research page at Ascension 3 and 4, Homunculus Lab and the Trade Treaty / Union bonus only at Ascension 4; not checked in game).
4. **Spells page** (Magic upgrades spell tiers and the spell cost scaling; for the Spells page, unchecked).
   - Spell tiers (Magic upgrades; 23 spells x tiers 2 to 5, plus Arcane Brilliance; built from code, unchecked). The unlock
   text is the game's own, evaluated at Ascension 1 to 4 (the thresholds depend on the Ascension). Tier N needs Ascension N-1
   or higher, except Dragon's Breath (Reincarnation 54 / 60 / 66 / 72, any Ascension). The "Offline production" bonus reads v = (Mmax^(2/max(3,A)) + (30 R)^(2/max(3,A)))^0.4 (Maximum Mana, mana
   regeneration per second) with the Ascension penalty starting at the tier number. The game's tooltip shows the product of this
   tier and the lower tiers while a display setting (stored value 23, default off) is at its default; the page shows the
   single-tier formula. The spells' own Reincarnation (R42 to R48) and dragon-growth upgrade prerequisites are left for the Unlocks page; the three Lore-artifact requirements (Precognition, Limited Wish, Infinite Spiral) are read from the code. Arcane Brilliance
   needs one Arcane Brilliance trophy per Ascension (count + 1 > Ascension).
   - Spell tier cost scaling (read from the spell cost function in the game code, unchecked). Tiered spells cost base ^ (1 + k x n) with k = 0.6 and n the tier (plus 1 while below the highest available tier). Tax Collection upgraded to Share Benefits (Round Table) and Twisting Nether instead cost base x m ^ n with m = 3. Lowering k by 0.1 each: Sequence (S1275), Angel Perk 1, Dragon Set; Dragon's Breath also by 0.3 with Iron Flight (Dragon perk 2). Lowering m: Sequence 0.5, Angel Perk 1 0.3, Dragon Set 0.2. Which spells use the first rule: every spell the code flags as having tiers (23 of the 32 spell classes), so read the flag, do not hardcode a list. Not flagged: Tax Collection (Reap Interests and Share Benefits are its upgraded forms), Catalyst, Chaos Madness, and the event spells (Cannibalize, Hailstorm, Heatwave, Shadow Embrace, Wail of the Banshee). This matches what the user described. Share Benefits (Tax Collection with Round Table) and Twisting Nether use the second rule; their maximum tier count is unknown (Twisting Nether is fixed at 98 in the code). The tier count n in the rule is the number of that spell's tier upgrades owned (the user reports 5 tiers at most so far), plus 1 for each of several upgrades that add a tier to named spells (the Dragon Set's Set Bonus 2 adds one to six alignment spells; four more such upgrades are in the code and not yet identified by name). The tooltips of the four reducing items carry a note pointing to the Spells page.
5. **Unlocks page** (all mechanic unlocks): Fragment of a Titan Statue, Druidic Runestone, Octopus Shaped Spine, Passage to the Underworld (Misc upgrades, not exported yet) set the hidden Archeology Titan/Druid/Faceless/Underworld flags that gate those factions; the allegiance pages already name them as "Upgrade: ...".
   - **Research facility upgrades** (Mana Loom, Factory, Mythos, Vault, Athanor, Battlefield, Apeiron; their budget bonus is on the research page, the unlock belongs here): to be bought they need Reincarnation 180, the Forgotten Relic artifact, the facility's own artifact and at least 5000 research points already spent in that branch (Apeiron: Reincarnation 180, the Forgotten Relic and Apeiron artifacts). The code prices each at 1e45 of its branch's faction coins (Fairy, Elf, Angel, Goblin, Undead, Demon for the first six; Apeiron 1e50 Dwarven and Drow coins). Once owned, the budget bonus applies. Read from the code, not checked in game.
6. **Notes that point to pages that do not exist yet.** Faded notes in the tooltips send the reader to pages that have not been made, and we may not make one page per note, so they have to be edited when the page plan is settled (`NOTES` in `tools/build_upgrades_page.py`, `NOTES` in `tools/build_research_page.py`):
   - "Spells page, tier cost scaling": Sequence (S1275), Angel Perk 1, Iron Flight, Dragon Set.
   - "Buildings page, building cost multiplier": Biased Architecture (Dwarven challenge 2), Goblin Bloodline, Titan Perk 1, Bartering (E50), Bribing (E135), Discount (E13125).
   - "Excavations page, excavation cost multiplier": Surveyorship (E270), Discount (E13125).
   - "Royal Exchanges page, Royal Exchange cost multiplier": Advanced Civilization (Elven challenge 1), Titanomachy (Archon challenge 3), Intimidation (E1325), Discount (E13125).
7. **Verify the research page** (researches, formulas, requirements; built from code, checked so far only as listed under
   Resolved).
8. **Major mechanic: Legacies** (read from the code, not checked in game; Ascension 4 only, so the user has not seen it yet):
   - **Containers:** 4 Legacy Containers plus one free container, "Relativity's Legacy", which needs the research Relativity (Forbidden, 11750; needs 5500 Royal Exchanges). A container needs Ascension 4 and a faction. The Legacy chosen in a container is kept until you Abdicate.
   - **A Legacy** is one tier of one faction (Bronze, Silver, Gold, Diamond; upgrades 1-3, 4-6, 7-9, 10-12 of that faction). It can be any faction except your own line (your base, prestige and astral factions, and the prestige faction that matches your alignment). Owning the Legacy makes that faction's three upgrades of the tier available, replacing the usual tier requirement; the three upgrades are still bought at their own prices.
   - **The Legacy itself costs gold plus the faction's coins, rising with the container number n (the free container costs nothing).** Gold: 1e39 x 1000^(0.5 ((n+3)^2 - (n+3))) = 1e57, 1e69, 1e84, 1e102 for containers 1 to 4; coins: 1e21 x 1e9^(n-1) = 1e21, 1e30, 1e39, 1e48. Legacies of the prestige factions (Dwarf, Drow, Dragon) cost 1e118 base gold and 1e45 base coins instead (1e136 to 1e181 gold, 1e45 to 1e72 coins). Factions with no coins of their own pay in the coins of their two parent factions (Titan: Angel and Goblin; Druid: Elf and Demon; Faceless: Fairy and Undead; Dragon: Dwarf and Drow; Archon: Angel and Undead; Djinn: Fairy and Demon; Makers: Elf and Goblin), the full amount of each.
   - **Legacy Combos:** 15 effects, one per pair of the six base factions (Fairy, Elf, Angel, Goblin, Undead, Demon): Mystic Forest (Fairy+Elf), Twisting Nether (Fairy+Angel), Artifact Caveau (Fairy+Goblin), Dream Realm (Fairy+Undead), Brooding Abyss (Fairy+Demon), Sacred Glade (Elf+Angel), Greed Factory (Elf+Goblin), Swamp of Sorrows (Elf+Undead), Forbidden Grove (Elf+Demon), Golden Heaven (Angel+Goblin), Dark Sanctum (Angel+Undead), Eternal Battlefield (Angel+Demon), Homunculus Lab (Goblin+Undead), Corruption Zone (Goblin+Demon), Frozen Wastes (Undead+Demon). A combo needs Ascension 4, at least one Legacy, and an owned Legacy of each of its two factions. Only one combo can be bought before abdicating, two with the research Revelations (Forbidden, 12000; needs 1e33 Faction Coins found). A combo costs 1e72 gold and 1e33 of each of its two factions' coins.
   - **In the game's UI (from the code, not seen in game):** a container is an ordinary upgrade of the group LegacyContainer; clicking it opens a chooser window that lists the Legacies you do not own and may take, under a header per faction ("Fairy Upgrades"), each named "<Faction> <Tier> Legacy" with the names and texts of its three upgrades. Picking one buys it (gold and coins as above) and marks the container as used (`1Y` sets the clicked container as owned). The three upgrades then show in the normal upgrade list. The 15 combos have no container or chooser: they are ordinary upgrades of the group LegacyComboUpgrade that are available only when their conditions hold (the game stacks upgrades of one group into one icon).
   - **Trophies:** "Have 4 different factions involved in your Legacy upgrades" and the same with 5.
   - The effects of the 15 combos and their formulas are in the game text and the code (see `export_upgrades.py` for how they are read); they are not on any page yet.
9. **Event stuff** (not very important): not covered. Seasonal items found so far: Dragonblood (4.3.15, Halloween): the feat (game text: collect a stack of at least 720 Blood while having at least 3000 Dragon Pastures and at least 5 Dragon's Breath effects active; it unlocks the upgrade) and the upgrade (Maximum Mana x1.10 during any Seasonal Event). The feat is in `trophies.json`; the upgrade is not on any page yet.
10. **Anything left:** ask the user for whatever else is missing before calling the project done.

Accepted without further checking: the Ascension-penalty flags (which values are reduced and from which Ascension; from the game's own text and the code, impossible to verify in game; revisit if wiki users report a mismatch); the offline-time terms in Fusion and Gargantuaness (ignored, zero in normal play).

### Resolved (confirmed by the user; do not re-open)

- Misc upgrades as built so far (Reincarnation Powers 1-5 with every effect, range and formula, Gem Power and the Gem upgrades,
  Challenge Power, Ruby Power and its tiers, the clicking, offline and assistant series): confirmed by the user.
- Archaeology page as a whole (all lore and quest artifacts, requirements, hints, chances): checked by the user; only the 5
  earmarked items stay open (Lantern of Guidance, the three Fragment factors, Poison Vial's Drow Perk 4 term).
- Wall Fragment, Wall Chunk, Mathematician (building tier multipliers, tier counted from 1): Wall Fragment checked in game against four
  buildings (1 + 5 * (2 * (11 - T))^2.5, not the old wiki 3 * (2 * (11 - T))^3 %); Wall Chunk and Mathematician agree with the old wiki.
- Reverse Autocasting (from R40 = Ascension 1) and Tiered Autocasting (from R42) availability; the Mana Regeneration
  upgrades' Ascension limits (Mana Wave onward need Ascension 1, Mana Spring and Mana Falls need Ascension 2, the earlier
  ones none), as stated by the trophies themselves.

- Building upgrades: the series are removed from Ascension 3 on, the building count thresholds, and the Ascension penalties.

- Lore artifact chance formulas confirmed against the patch notes / old wiki apart from cleanup terms (0.5, +1), inputs
  confirmed: Excavated Mirage, Eye of the Dragon, Spark of Life, Primal Leaf, Dwarven Anvil, Factory, Battlefield, Mana Loom, Glowing Wing, Sylvan Mirror, Orc Fang Necklace, Ancestral Hourglass (and its upgrade formula), Ancient Heirloom (upgrade formula), Nightmare Figment, Raw Emerald, Branch of the Life Tree, Dragon Scale, Planetary Force, Mercenary Insignia, Solid Cloud, Blood Chalice, Frozen Lightning, The Blackest Ink, Beard Hair, Athanor, Demon Tail, Oil Lamp (artifact), Fossilized Wing, Dusty Coffin, Mythos, Wall Chunk, Apeiron, Stiletto Heel, Titan Helmet, Crystallized Lava, Silk Cloth, Spiked Whip (building count excludes "count as more" bonuses in the code), Poison Vial (base formula; the Drow Perk 4 term is open under item 1).

- Research availability by Ascension: Ascension 3 removes researches numbered 400 or lower and Ascension 4 those 5000 or lower
  (patch notes).

- Challenges page: fully confirmed by the user (all sixteen factions, including the review changes). Earlier notes: Versatile Combo, Overflowing Magic, the Mystic Maze bug, and the requirement changes with Ascension
  (Smuggled Jewels, Underground Foundations, Omnipresence).
- Secret upgrades: Future Linkin (last Era length), MAD Masks, Bloodstream and Art of the Crow formulas and variable meanings;
  the Ascension availability ranges of the Secret upgrades.

- Advanced Heritages start at Ascension 2: the faction Master trophies need Lineage level 30 and a Lineage cannot go above 25 x Ascension (the Lineage upgrade is not available at or above that level), confirmed by the user and by the code.
- The extra effect of the nine base-faction Unions (Fairies to Faceless) only works from Reincarnation 105 (the Union's text and the production code both test it); before that the Union only unlocks the faction's tier 4 upgrades. The Dwarven, Drow and Dragon Unions have no such gate (they need Reincarnation 115 to be bought).
- Mercenaries cannot be played at Ascension 2 and 4: Mercenary First Contract (the only way to become one) has no availability there (code), so the Mercenary faction's contracts, perks, unique buildings and quest are unavailable then too. The Mercenary Badge heritage and the Mercenary Set do not need the faction.
- Faction cell colours; Neutral has no tint; alignment-locked researches and the 11 locked ones.
- Home faction vs unlock faction (S300 Chain Lightning: unlock as Faceless, buy as Titan); the unlock flag persists.
- Mercenaries cannot unlock a research whose unlock faction is another faction (no hidden unlock path assumed).
- The prestige-unique-upgrade note on Metallurgy, Marketing, Poisons and the other prestige researches is correct as written.
- Folgoration (A12250) formula matches the patch notes; Manipulation (S3200) needs no formula; Estates (E3300) text change at Ascension 3.
- Veteran Figurine needs the Dragon challenge (Dracomet Vault); time-as-faction stats are all-time and never reset;
  building counts include "counts as more" bonuses; Dragon Soul needs spell tier 5.

## Corrected so far

| Was | Now | How it was caught |
|---|---|---|
| "Bloodline" for the prestige-faction field | "Prestige faction" / "No prestige faction" | User (plays the game) |
| Spell counter = "time active" | Number of **casts** | Game UI: "Cast This Era: %0, Total: %1" |
| `§#!!§.§!-§()` = "clicking reward" | **Number of assistants** (before multipliers) | User, from the 4.3.x patch notes; confirmed in code: Titan Sized Walls ("based on assistants owned") calls the wrapper `§&c§.§!-§()`, which calls it |
| "Neutral Order path" | "Order alignment" (a second alignment axis: Order/Chaos/Balance) | Contradiction with "Evil alignment" on the same artifact |
| "Make N excavations" | "N excavations" (the Excavation Reset wording was dropped) | Code: the counter `§1!5§` is zeroed by both kinds of Excavation Reset |

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
| `§@w§[i]` | stat `i` for previous Reincarnations (so 5!V + =y + @w = all-time, never reset, not even by Ascension) | **high** | code: only a full wipe zeroes it; user (patch notes and play): time-as-faction requirements span the whole playthrough |
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
| `§["&§` | Consecutive days logged in (UTC server days) | high | +1 when today = last day + 1, else reset to 1; user: patch notes say "consecutive days logged in" |
| `§1!#§[f]` | Lineage level of faction `f` | medium | Genealogist / Chemistry "total amount of Lineage levels" sum it |
| spell `§?j§`/`§<q§`/`§<!G§` | Spell activity time (s): this Era / earlier Eras / previous Reincarnations | high | UI "Active Time This Era / This Reincarnation" |
| spell `§`r§` | Tier the spell is currently **active** at, stored from 0 (shown as +1); raised on cast, reset to 0 when it ends | medium | setter/mutators in the spell class. The highest tier you can reach is the number of owned tier upgrades for that spell (up to 4, so displayed tier 5) plus +1 from a few upgrades (e.g. Absolute Hierarchy for Dragon's Breath); the spell panel's "Highest Tier Unlocked: x/5" counts only the standard series. Dragon Soul needs stored 4 = the standard top tier |
| upgrade `§?!6§` | Upgrade obtained at some point (challenge rewards persist) | medium | Veteran Figurine checks it on "Dracomet Vault" (icon `DragonChallenge6`); user: challenges grant permanent bonuses and Dracomet Vault should be a challenge |
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
| `§8G§.§%Z§(building)` | Buildings of that type owned, counting bonuses that make them count as more (Dwarf Challenge 5, Underground Foundations, ...); with `true`, the raw owned count | **high** | user: such "counts as more" bonuses apply to count-based artifacts unless stated otherwise |

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

## Code vs. patch-notes doc (4.3.11) constant factors (background for the artifact checks)

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

## Researches (page: research.html)

Source of truth is the game's own text where possible: the requirement text is the research's requirement
method evaluated with the research marked as owned (so it prints the target instead of "Progress: x/y");
descriptions are the game's description text with the "(+x%)" current-value readouts removed.

| Claim | Confidence | Evidence |
|---|---|---|
| Research number (`§%w§`) = research points of that branch you must have bought; branch icon + `Research<number>` sprite is how the game draws the cell | high | `§ !3§` compares the branch's research points with `%w`; the research grid sets its texture to "Research" + `%w` |
| Grid order = ascending research number (ties by the game's index `§"!U§`) | user-stated | the user's description of the in-game grid |
| `§^!C§` = faction the research needs (current faction or prestige faction) | high | `§ !3§` |
| Researches with number >= 5000 need Reincarnation 180 and the "Forgotten Relic" artifact | high | `§+!a§`; 3.7.0 changelog ("Forgotten Relic ... unlocks the 5000 research points cap") |
| "Cannot be bought in Ascension 3 / 4 or higher" for numbers below 405 / 5000 | medium | `§9!%§` returns false for those; Mercenary-only exceptions in some overrides are not shown |
| Stat 2 = Good time, 36 = Chaos time, 48 = Order time, 14 = Balance time, 45 = offline time, 97 = time with at least one spell active, 155 = Combo Strike counter max, 156 = Grand Balance targets max | medium | alignment-time helper maps alignment to these indices; research texts name the quantities |
| `§&c§.§&!y§(least, ...)` etc. | medium | description text of Mercy / Compassion |
| Research code = branch letter + research number (S, C, D, E, A, W; F for Forbidden is an assumption) | high / low for F | user's examples A200, C150, E300, S1 |
| Displayed percentages are reduced by Ascension: shown = ((1 + v/100)^(0.1^(A - a + 1)) - 1) * 100 from Ascension a on (a = 1 unless the text says otherwise; some use 2, 4 or 5) | **high** | `§&c§.§6!T§` calls `§#!!§.§#%§`; matches the user's S1 reading (29% at Ascension 1 with 5757 mana: v = 1.2*5757^0.8 = 1223%, 13.2^0.1 = 1.295) |
| Highest Ascension is 4 (the Ascend rule has one Reincarnation threshold for each of Ascension 0-3); the research page reads it from the code | high | `§8G§` Ascend function; user's guess agrees |
| A research is unavailable from Ascension 3 (number < 405) / 4 (number < 5000) on | medium | `§9!%§` of the research base class; user could not confirm yet |
| Description and requirement text change with the Ascension for 18 researches (e.g. Channeling S10: "by 160% per Heaven's Gate" at Ascension 0, "based on Heaven's Gates owned" from 1); the page evaluates the game's text at every Ascension | high | engine evaluation with the Ascension field set |
| Research page shows the base formula plus an "A" mark per power of the Ascension penalty (k = Ascension - start + 1); descriptions use the Ascension-0 wording because the "by 160% per Gate" -> "based on Gates" rewordings are the penalty showing through; Estates (E3300) is the only research whose meaning changes (Ascension 3: all Unique Buildings that match your alignments) | high | engine evaluation of the description at every Ascension |
| Only Dwarf (9), Drow (10) and Dragon (12) are prestige factions among those researches use (Archon 13 appears once in the code as a prestige value but no research needs it); every other faction research needs you to play as that faction. Condition: `faction == X or prestige faction == X`; the third affiliation does not count | high | code; user |
| Research cell colour = fill of the game's `<Faction>Trim` texture (Fairy pink, Angel light blue, ...) | high | `§99§.§5t§` per-faction textures, used by the research cell class |
| A research has two faction fields: the **home faction** (`§-!^§` of the research: the faction you must be playing to buy it; also the cell colour) and the **unlock faction** (`§^!C§`: the faction you must be playing/have as prestige to unlock it). They differ for 22 researches, e.g. Chain Lightning S300: unlock as Faceless (cast Brainwave 8 times), buy as Titan | **high** | user (S300), engine test, cell class uses `-!^` for the texture |
| Unlocking is checked live (`§-6§` = ` !3` of the research); the first moment it is true the game sets the persistent unlocked flag `§?!6§` (saved as `§3!c§`, cleared only by a full wipe), after which the unlock faction no longer matters. The unlock check has no Mercenary clause, so a Mercenary cannot unlock a research whose unlock faction is another faction | high from the code, not tested in game | `§4!S§` unlock loop in `§8G§`; `§&!_§` unlocked getter |
| Mercenaries are not subject to the home-faction lock; about 47 researches add their own condition (the faction's unique-building upgrade or spell); Bloodspring (A400) is blocked for them | high for the buy side | `§9!%§` overrides evaluated in the engine; the unlock side for Mercenaries is not decoded |
| Mercenary override of availability (`§9!%§` in about 75 researches) lets a Mercenary buy a faction-specific research when a related spell/upgrade is available, without the Ascension cut-off | medium | code only; not shown beyond "Mercenaries may be an exception" |
| Fusion (A105) = 0.7 * (ln(1 + F))^3, F = Faction Coins found this Era; Gargantuaness (C1500) = 0.75 * t^0.75, t = Neutral time this Reincarnation; Toxicity (A10875) = 1.3 * t^0.7, t = time as the faction opposite to your current one this Reincarnation; Backfire (W13500) = 0.75 * x^0.75 for six x values | **high** | code getters; user's old wiki / patch-notes formulas agree (A105 gave 41.9% at 1.66e7 coins at Ascension 1, user reads 41%) |
| `§#!!§.§2!P§ / 2` and `§#!!§. !O§ / 2` in those formulas are non-zero only while the game simulates offline progress (set and cleared in the offline-time function); omitted | medium | code |
| Manipulation (S3200) has no formula: "multiplicatively increase mana regen by 12% per active spell" | high | description text, user |

## Not decoded yet

Nothing blocking. Ten research formulas were once undecoded and are now all done except Manipulation, which has none by design.
