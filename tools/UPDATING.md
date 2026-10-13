# After a game update

1. Put the new `RealmGrinderDesktop.swf` in `raw/` and extract: `sh tools/extract.sh`, then `python -I tools/parse_mo.py`.
2. `python -I tools/selfcheck.py` : did the obfuscated names move? Stop here if it says LOOK AT.
   - "names used by the tools ... gone" or "Ascension/Reincarnation fields are now ..." means the name mapping is stale.
   - New item ids are listed as new; an item whose id changed is reported as CHANGED ID.
3. Rebuild: `build_data.py`, `as3js.py`, `eval_formulas.py`, the `export_*.py` scripts, then the `build_*_page.py` scripts
   (the commands are in `data/GLOSSARY.md`).
4. `python -I tools/diff_data.py` (`-v` for old and new values): added, removed and changed items, plus hand-written
   overrides (formulas, notes, fixes in the exporters) whose item changed. Review that list, nothing else.
5. `python -I tools/selfcheck.py --update` once the new ids are accepted, then commit.
