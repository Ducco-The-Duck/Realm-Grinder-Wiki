# The global Effects search: not in use

An unfinished idea, potentially scrapped: one page to search every upgrade, research and challenge by what it changes (X) and what it is based on (Y),
with tags picked from suggestions, an Ascension filter, and the pages' own tooltips and icons. It was dropped because the search boxes of the Research,
Challenges and Upgrades pages already narrow things down enough. It still builds, but nothing links to it and the update tools do not run it.

## Files (moved here from the wiki; the paths inside them still point at the old places)
- `tools/effect_tags.py` (the tagger), `tools/effect_review.py` (the review list), `tools/build_effects_page.py` (the page)
- `data/effect_tags.json`, `data/effect_tags_fixes.json`, `data/effect_tags_review.md`, `data/EFFECT_VOCABULARY.md`
- `docs/effects.html` (the built page)
- removed from the wiki's code: the embed mode used for its tooltips and icons (`embedInit` in `tools/search_snippet.py`, its `html.embed` CSS and the
  `embedInit(...)` calls in `build_research_page.py`, `build_challenges_page.py` and `build_upgrades_page.py`); see the git history before the commit that
  created the `unused` folder

To bring it back: move the files to their old places, restore the embed code from the git history, link the page in the nav and the home page, add
`effect_tags` and `build_effects_page` to `STEPS` in `update.py`, the effect tag file to `FILES` in `diff_data.py`, and a stale-corrections check to `selfcheck.py`.

## Kept because they are useful on their own
- `tools/availability.py`: the Ascension rules (research number cap, Ascension start Reincarnations, upgrade and challenge availability); the Research page uses it
- the Ascension a Lineage perk exists from (`export_upgrades.py`), the `#q=` link into a page's search box (`search_snippet.py`)
- the research fixes made while checking: unique building names and the Mercenary notes (`export_research.py`)
