"""Which Ascensions (0-4) an upgrade, research or challenge is available at.
One place for the rules, so the pages and the global effect search cannot disagree."""
import json

# the highest research number a branch can reach, per Ascension (see data/INFERENCES.md, "Highest research number you can reach")
MAXNUM = [780, 4950, 4999, 7000, 14000]
ASCENSIONS = range(5)


def upgrade_asc(u):
    """asc_min: first Ascension it exists at; asc_max: first Ascension it is gone at; asc_not: Ascensions it is missing at"""
    lo, hi, no = u.get('asc_min'), u.get('asc_max'), u.get('asc_not') or []
    return [a for a in ASCENSIONS if not ((lo is not None and a < lo) or (hi is not None and a >= hi) or a in no)]


def research_asc(r):
    """unavailable_from: first Ascension it is removed at; number: needs a facility level of that size"""
    uf = r.get('unavailable_from')
    return [a for a in ASCENSIONS if not ((uf is not None and a >= uf) or r['number'] > MAXNUM[a])]


def challenge_asc(c):
    return list(ASCENSIONS)      # nothing in the code limits a challenge by Ascension that we know of
