# Realm Grinder Wiki

A wiki for Realm Grinder whose pages are generated from the game's own code and text. Nothing on the pages is typed in
by hand: the numbers, requirements and formulas are read out of the decompiled game, and the few hand-written
corrections live in named tables inside the tools so they can be found and reviewed. The Codex (Mechanics, Unlocks, Spells and Buildings
pages) is the exception: its explanations are written by hand from the code, in `data/handwritten/unlocks.json`, `data/handwritten/spells_overview.json` and `data/handwritten/buildings.json`.

The site is served by GitHub Pages from `docs/`.

## Pages (`docs/`)

| Page | What it shows |
|---|---|
| `index.html` | Landing page |
| `upgrades-allegiance.html` | Faction upgrades, treaties, Unions, Heritages, Lineages, Bloodlines, Artifact Sets |
| `upgrades-magic.html` | Spell tiers and other magic upgrades |
| `upgrades-secret.html`, `upgrades-misc.html` | Artifact and secret upgrades, building series, Reincarnation Powers, Gem upgrades |
| `research.html` | The research tree, with formulas and Ascension marks |
| `challenges.html` | Faction challenges and their rewards |
| `archaeology.html` | Quest and lore artifacts, with find-chance formulas |
| `trophies.html` | Trophies and their requirements |
| `mechanics.html`, `unlocks-a0.html` to `unlocks-a4.html` | Codex: the mechanics, and what has to be unlocked at each Ascension (under construction) |
| `spells.html` | Codex: every spell with its overview, formulas, tiers and Ascension penalty (under construction) |
| `buildings.html` | Codex: the 11 base buildings; pick one for its base production and the cost of buying more (under construction) |

Each page is one self-contained HTML file with its data embedded.

## How it fits together

```
raw/<version>/RealmGrinderDesktop.swf     the game file (not in git)
        |   tools/extract.sh <version>    decompile with FFDec
        v
out/                                      decompiled code, strings, images (not in git; out/VERSION says which build)
        |   tools/extract/as3js.py, tools/export/build_data.py, tools/export/export_*.py
        v
data/generated/*.json                    the facts the pages show (committed)
        |   tools/pages/build_*_page.py   (with data/handwritten/*.json for the Codex)
        v
docs/*.html                               the site (committed)
```

- **`raw/`**: one folder per game version, for example `raw/4.3.14` and `raw/4.3.15`.
- **`out/`**: the build the tools and pages are made from. An older build can be extracted next to it
  (`sh tools/extract.sh 4.3.14 out_4.3.14`) to compare versions.
- **`data/`**, in four folders by what may be edited:
  `generated/` (the facts the pages show, written by the exporters and committed: do not edit, a rebuild overwrites them),
  `derived/` (intermediate files rebuilt from the game, not in git: the engine, strings, sprites, class data),
  `handwritten/` (written by hand from the code: `spells_overview.json`, `unlocks.json`, `buildings.json`; edit these) and
  `docs/` (the notes: `GLOSSARY.md` with the rebuild commands, `INFERENCES.md` for what the decompiled names mean and how sure we are,
  `STATUS.md` for the open items, `FORMULA_MISMATCHES.md` for every place the code differs from the last documented version).
- **`tools/`**: `update.py` (the one command for a game update), `extract.sh` and the preview server at the top, and the rest grouped by stage:
  `extract/` (decompile, texts, images, the formula engine), `export/` (the exporters that turn the decompiled game into `data/*.json`),
  `manual/` (the hand-written correction tables the exporters use), `pages/` (the page builders and the shared look; each page's HTML, CSS and JS is a file in
  `pages/templates/`, with the colours every page shares in `theme.css`) and `checks/` (`selfcheck.py`: did the game's scrambled names or numbers move?; `diff_data.py`: what
  changed after a rebuild; `verify_formulas.py`). `tools/UPDATING.md` has the steps for a game update.
- **`unused/`**: things that were dropped (the Effects search page and its tools and data, and the `eval_formulas.py` step); kept for reference, not built or checked.
- **Engine**: `tools/extract/as3js.py` turns the game's formulas into JavaScript (`data/derived/engine.js`), which is run with `quickjs` to
  evaluate formulas and to test what an upgrade does at each Ascension.

## Setup (to rebuild from a game file)

Only needed to regenerate the data; the committed `docs/` needs nothing but a browser. Everything here was set up and tested on Windows
with Python 3.10.

- **The game file:** your own copy of `RealmGrinderDesktop.swf` from the game folder, placed in `raw/<version>/`. The game itself is not in the repo.
- **FFDec** (JPEXS Free Flash Decompiler, command-line version): unpacked into `tools/ffdec/` so that `tools/ffdec/ffdec-cli.exe` exists. `extract.sh` calls it.
- **`sh`:** Git for Windows provides it (`update.py` looks for it).
- **Python packages**, installed next to the tools so nothing is installed system-wide:
  `pip install --target tools/pylib quickjs esprima pillow` (`tools/pylib/` is ignored by git). `quickjs` runs the formula engine, `esprima` parses
  the game's code and `pillow` slices the sprites.
- Then `python -I tools/update.py <version>` (see Rebuilding).

## Rebuilding

For a new game version: copy the swf to `raw/<version>/` and run `python -I tools/update.py <version>` (details in
`tools/UPDATING.md`). It extracts, checks the new build, rebuilds the data and every page, and prints what changed;
you then read the summary and commit. The summary is also saved in `update_report.txt` (not in git). The individual commands are in `data/docs/GLOSSARY.md`. To preview locally, serve
`docs/` (for example `python -m http.server 8123 --directory docs`).

## Conventions

- Facts come from the code: no constant, number or formula is meant to originate from us. Where a formula has to be written by hand (the spell details, the Mechanics page, a few upgrade and challenge tables), `tools/checks/verify_formulas.py` (run by `selfcheck.py`) checks that every number in it still appears in the game code it was read from.
- A meaning we guessed is recorded in `INFERENCES.md` until it is confirmed in game; `STATUS.md` lists what is still open.
- Something is a bug only when the maintainer has confirmed it; confirmed ones are in `KNOWN_BUGS.md` and shown as a note on the page.
- Values that differ from older documentation are logged in `FORMULA_MISMATCHES.md` (open) and `FORMULA_MISMATCHES_RESOLVED.md` (resolved), even when the code turns out to be right.
- Ascension penalty marks follow the game's own tooltip text, checked against the code (see the notes in `INFERENCES.md`).
