"""Which Ascensions (0-4) an upgrade, research or challenge is available at.
One place for the rules, so the pages and the global effect search cannot disagree."""
import json, re

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


# the Reincarnation each Ascension starts at: the save loader clamps the Ascension level by the Reincarnation count (>= 220 for 4, >= 160 for 3,
# >= 100 for 2, >= 40 for 1; out/script/scripts/§8G§.as), and the Ascension button shows from Reincarnation 39 on while at Ascension 0
ASC_START_REINC = [0, 40, 100, 160, 220]


def asc_for_reincarnation(n):
    """the first Ascension at which Reincarnation n can be reached"""
    return next(a for a in ASCENSIONS if a == 4 or n < ASC_START_REINC[a + 1])


def challenge_reinc(c):
    return max([int(m) for q in c.get('requirements') or [] for m in re.findall(r'Reincarnation (\d+)', q)] or [0])


def challenge_asc(c, faction_floor=0):
    """a challenge needs the Reincarnation of its unlock requirement, which only exists from a certain Ascension on
    (Dragon challenges: Reincarnation 53, from Ascension 1; Astral: from 2; Mercenary: from 3). The faction's first challenge
    has no requirement of its own and is given by the faction's last challenge, so it follows the highest one of its faction."""
    lo = max(asc_for_reincarnation(challenge_reinc(c)), faction_floor)
    return [a for a in ASCENSIONS if a >= lo]


def faction_floor(items):
    return max(asc_for_reincarnation(challenge_reinc(i)) for i in items)
