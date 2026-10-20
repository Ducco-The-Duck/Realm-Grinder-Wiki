# Realm Grinder Wiki

A wiki for Realm Grinder whose pages are generated from the game's own code and text. Nothing on the pages is typed in
by hand: the numbers, requirements and formulas are read out of the decompiled game, and the few hand-written
corrections live in named tables inside the tools so they can be found and reviewed.

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

Each page is one self-contained HTML file with its data embedded.

## How it fits together

```
raw/<version>/RealmGrinderDesktop.swf     the game file (not in git)
        |   tools/extract.sh <version>    decompile with FFDec
        v
out/                                      decompiled code, strings, images (not in git; out/VERSION says which build)
        |   tools/build_data.py, as3js.py, eval_formulas.py, export_*.py
        v
data/*.json                               the facts the pages show (committed)
        |   tools/build_*_page.py
        v
docs/*.html                               the site (committed)
```

- **`raw/`**: one folder per game version, for example `raw/4.3.14` and `raw/4.3.15`.
- **`out/`**: the build the tools and pages are made from. An older build can be extracted next to it
  (`sh tools/extract.sh 4.3.14 out_4.3.14`) to compare versions.
- **`data/`**: JSON files plus the notes: `GLOSSARY.md` (what each file is and the rebuild commands), `INFERENCES.md`
  (what the decompiled names mean, how sure we are, and the open items) and `FORMULA_MISMATCHES.md` (every place the
  code differs from the last documented version).
- **`tools/`**: the exporters, the page builders, the shared look (`search_snippet.py`, `frame_css.py`), and two guards:
  `selfcheck.py` (did the game's scrambled internal names move?) and `diff_data.py` (what changed after a rebuild, and
  which hand-written fixes sit on a changed item). `tools/UPDATING.md` has the steps for a game update.
- **Engine**: `as3js.py` turns the game's formulas into JavaScript (`data/engine.js`), which is run with `quickjs` to
  evaluate formulas and to test what an upgrade does at each Ascension.

## Rebuilding

See `data/GLOSSARY.md` for the commands and `tools/UPDATING.md` for a game update. In short: extract, run
`selfcheck.py`, rebuild data and pages, read the `diff_data.py` list, commit. To preview locally, serve `docs/` (for
example `python -m http.server 8123 --directory docs`).

## Conventions

- Facts come from the code. A meaning we guessed is recorded in `INFERENCES.md` until it is confirmed in game.
- Values that differ from older documentation are logged in `FORMULA_MISMATCHES.md`, even when the code turns out to be right.
- Ascension penalty marks follow the game's own tooltip text, checked against the code (see the notes in `INFERENCES.md`).
