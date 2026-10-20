# After a game update

**Quick way:** put the new `RealmGrinderDesktop.swf` in `raw/<version>/` and run `python -I tools/update.py <version>`.
It extracts, compares with the current build, runs the selfcheck, makes the new build current (the old one is kept as
`out_<old version>/`), rebuilds all data and pages, and prints what changed. Add `--dry-run` to only extract and compare.
It needs a clean git tree, never commits or pushes, and `git checkout -- data docs` undoes a rebuild. It cannot decode new
kinds of items or write formulas and notes: read its summary, then handle what is new. Whenever a new page or exporter is
added, add it to `STEPS` in `tools/update.py`. The manual steps it replaces:

1. Put the new `RealmGrinderDesktop.swf` in `raw/<version>/` (one folder per version) and extract it: `sh tools/extract.sh <version> out_<version>` first,
   compare it with `out/` (same file names = the scrambled names did not move), then make it current (rename `out` to `out_<old version>`, the new folder to `out`)
   and run `python -I tools/parse_mo.py`. `sh tools/extract.sh <version>` with no destination writes straight to `out/`. `out/VERSION` says which build `out/` is.
2. `python -I tools/selfcheck.py` : did the obfuscated names move? Stop here if it says LOOK AT.
   - "names used by the tools ... gone" or "Ascension/Reincarnation fields are now ..." means the name mapping is stale.
   - New item ids are listed as new; an item whose id changed is reported as CHANGED ID.
3. Rebuild: `build_data.py`, `as3js.py`, `eval_formulas.py`, the `export_*.py` scripts, then the `build_*_page.py` scripts and `build_index.py` (stamps the game version on the home page)
   (the commands are in `data/GLOSSARY.md`).
4. `python -I tools/diff_data.py` (`-v` for old and new values): added, removed and changed items, plus hand-written
   overrides (formulas, notes, fixes in the exporters) whose item changed. Review that list, nothing else.
5. `python -I tools/selfcheck.py --update` once the new ids are accepted, then commit.

# If the obfuscated names change (design note, not built)

`tools/selfcheck.py` says "names ... gone from the code" or "fields are now ...". Then the table of what each obfuscated
name means (`helper_calls.py`, `chance_latex.py`, `export_*.py`) points at names that no longer exist. Idea: re-derive
the mapping by matching the old build to the new one by *shape*, the way BinDiff / Diaphora match functions between two
versions of a program. Needs both builds side by side (keep the old `out/script` when updating).

1. **Items by id.** Every item class has a numeric id (`§6!Z§ = 177`) that also appears in saves, plus its display name
   and icon name. Match classes old to new through (id, name). This gives the class mapping for free.
2. **Save writer by position.** The save routine (`writeShort(58)` ... `writeUnsignedInt(id)`) writes fields in a fixed
   order; align the old and new sequences (a diff, not an index, since a field may be added). Each fields' old name has a
   known meaning, so its new name inherits it. Covers the saved scalars and the stat arrays (their indexes are plain numbers).
3. **Functions and members by fingerprint.** For each method keep: the numeric literals, string literals (`_("...")`),
   the number of calls and which already-matched names it reads. Match old to new by the highest overlap, then iterate:
   every newly matched name makes its neighbours' fingerprints more specific. This is what recovers the helpers
   (assistants, mana, building counts, the Ascension penalty, item getters such as the availability check `§-6§`).
4. **Report, don't guess.** Write `data/name_map.json` (old name -> new name, with the evidence), list everything that
   matched ambiguously or not at all, and only apply the map to the exporters when the unmatched list is short.
5. **Check with the canaries** in `selfcheck.py` (Ascension thresholds 40/100/160/220, save version, item ids) before
   trusting the new names.

Limits: a method whose body changed a lot in the update will not match (that is exactly what `diff_data.py` then flags
for review); only one old/new pair of builds can validate it, so build it when a second version exists.

**Variable explanations** (the text after a variable's symbol under a formula) may contain formulas between dollar signs, e.g. `Decimal digits of $x$` or `$\lfloor 1.25 \cdot y \rfloor$`; every page draws those parts in the formula font (`rich()` in `tools/search_snippet.py`). Use it whenever an explanation mentions another variable or an expression, and keep using it for new pages.
