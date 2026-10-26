# Effect vocabulary (draft for review)

For the global effect search. An effect is "Increase X (based on Y)". Each upgrade, research and challenge gets a list of effects, each with its own X tags and Y tags.
Unlocks, requirements and "Enable/Unlock/Allows" effects are not part of this. A stat is counted when the effect increases or reduces a number.

Every tag list stores the whole path, so a search for a general stat also finds the specific ones ("production" finds "farms production"). The searches are plain text, all typed words must appear.

Drawn from the 2,275 texts of the wiki (1,147 sentences start with "Increase", 288 different "based on" phrases). About 20 stats cover nearly every X.

## X (the stat that is changed)

Format: `stat > specific stat`. A specific stat is listed once the general one cannot say it.

| Stat | Specific parts (examples from the texts) |
|---|---|
| production | all buildings; unique / non-unique buildings; good / neutral / evil buildings; other buildings; tier groups (three highest tiers, even tiers, the tier 7 building of your alignment); one building (28 of them: farms ... ancient pyramids, halls of legends); assistants; mercenary buildings; faction groups (vanilla / neutral / prestige / astral factions, one faction); production bonus from gems; offline production |
| base production | the same buildings as above, for the effects that say "base production" |
| clicking reward | base clicking reward; offline clicks; autoclicks |
| mana | maximum mana; mana regeneration; offline mana regeneration |
| spells | spell duration (all spells, faction spells, one spell); spell cost (all, faction spells); higher tier cost scaling; spell-specific numbers (lightning strike multiplier, brainwave multiplier, combo strike counter, grand balance duration, elven luck chance, night time duration ...) |
| faction coin find chance | with excavations; offline gains of faction coins |
| assistants | assistants gained (count) |
| tax collection | tax collection worth; triggered tax collections |
| Royal Exchange | Royal Exchange bonus; Ascension multiplier; cost multiplier |
| cost multiplier | building cost multiplier (all, non-unique, one building); excavation cost multiplier; Royal Exchange cost multiplier; lineage upgrade cost |
| research | research budget; research slots |
| set power | |
| excavation | free excavation reset requirement |

## Y (the stat the effect is based on)

Y is a base stat plus qualifiers. The tags store the base stat, and the qualified version.

Base stats: `time spent`, `mana produced`, `maximum mana`, `mana regeneration`, `spells cast`, `active spells`, `spell activity time`, `spell tier`, `spell duration`, `assistants owned`, `buildings built`, `buildings owned`, `faction coins found`, `gems owned`, `gold / coins`, `clicks`, `autoclicks`, `reincarnations made`, `trophies unlocked`, `artifacts found`, `lineage level`, `research points`, `researches selected`, `Royal Exchanges made`, `excavation depth`, `excavation resets`, `tax collections cast`, `grand balance targets`, `combo strike counter`, `upgrades purchased`, `production` (total production, offline production bonus), `mana statistics`.

Qualifiers (stored as extra tags, so "this era" or "highest" is searchable):

- **Period:** this era; this reincarnation; all-time; a single era (highest); a previous era; longest era.
- **Aggregate:** highest / maximum; least used; lowest; sum / combined; difference.
- **Parameter:** an alignment (good, neutral, evil, order, chaos, balance), a faction (including mercenaries), a spell, a building, a building tier, offline versus online.

Some of the tails need a decision (see the questions below), such as "how long their beard is (it grows over time!)", "time of the day", "mysterious events".

## Decisions

1. "base production" is its own stat, separate from "production".
2. "offline production" is its own stat, separate from "production".
3. Per-spell numbers: open (see the chat).
4. The unique Y values (beard length, time of the day, mysterious events, "your past choices") are standalone stats with no hierarchy.
5. Additive / multiplicative is a tag on the effect, searchable in the overall box and in the X box (not in the Y box).
6. Triggers ("While X is active", "When you cast X", "Each time ...") are part of the effect and searchable in the overall box only. About 80 of the 2,503 sentences have one.
