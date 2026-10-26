"""Draft tagger for the global effect search.

Reads every upgrade, research and challenge text, splits it into effects ("Increase X (based on Y)") and writes
data/effect_tags_draft.json: for each object a list of effects with the X tags, the Y tags, the mode (additive /
multiplicative) and the trigger.  Corrections go into data/effect_tags_fixes.json, which is applied on top.
The tags of an effect are whole paths (general stat first), so a search for a general stat finds the specific ones.
"""
import json, re, sys, collections
sys.stdout.reconfigure(encoding='utf8')
R = __file__.replace('\\', '/').rsplit('/tools/', 1)[0] + '/'
sys.path.insert(0, R + 'tools')
import availability

BUILD = json.load(open(R + 'data/buildings.json', encoding='utf8'))
SPELLS = json.load(open(R + 'data/spells.json', encoding='utf8'))
BNAMES = {}                          # lower-case plural / unique plural -> building name
for b in BUILD:
    pl = b.get('name_plural') or b['name']
    BNAMES[pl.lower()] = pl
    for v in (b.get('unique_names_plural_list') or {}).values():
        BNAMES[v.lower()] = pl
SNAMES = sorted({s['name'].lower() for s in SPELLS}, key=len, reverse=True)
ALIGN = ['good', 'neutral', 'evil', 'order', 'chaos', 'balance']
FACTIONS = ['fairy', 'fairies', 'elf', 'elves', 'elven', 'angel', 'goblin', 'undead', 'demon', 'titan', 'druid', 'faceless', 'dwarf',
            'dwarven', 'drow', 'dragon', 'archon', 'djinn', 'makers', 'mercenar']

SKIP = re.compile(r'^(Gain (?:a new spell|the \w+ faction spell)|Requirements?:|Requires|Enable|Unlock|Allows|Upgrade|Affiliating|Choosing|Only available|Hey|Khaire|Hello|We |Our |You |The (?:Good|Evil|Neutral))', re.I)
PREFIX = re.compile(r'^(?:Set Bonus \d+:|\d+[AP]M-\d+[AP]M:|(?:Good|Neutral|Evil):|[A-Z][a-z]+ path:|From Reincarnation \d+(?: up to \d+)?[:,]?|Also,?)\s*')
TRIG = re.compile(r'^(While|Whenever|When|Each time|Every time|If|Only while|During|After)\b(.*?),\s*(.*)$', re.I)
VERB = re.compile(r'^(?:(Multiplicatively|Additively)\s+)?(increases?|reduces?|gain|adds?|multiply|improve|generate)\b\s*(.*)$', re.I)


def mode_of(s):
    s = s.lower()
    if 'additively and multiplicatively' in s: return 'both'
    if 'multiplicatively' in s: return 'multiplicative'
    if 'additively' in s: return 'additive'
    return None


def clean(s):
    s = re.sub(r'\([^)]*\)', ' ', s)
    s = re.sub(r'\b(additively and multiplicatively|additively|multiplicatively)\b', ' ', s, flags=re.I)
    s = re.sub(r'^\s*(the|your|all of the|their)\s+', '', s.strip().lower())
    return re.sub(r'\s+', ' ', s).strip(' .,')


def spell_in(s):
    return [n for n in SNAMES if re.search(r'\b' + re.escape(n) + r"(?:'s)?\b", s)]


def xtags(raw):
    """-> (tags, building scope list)"""
    s = clean(raw)
    t, scope = [], []

    def add(*a): t.extend(x for x in a if x not in t)
    # production of buildings
    prod = re.search(r'production|assistants$|mercenaries$|dragons$', s)
    if s in ('production', 'total production'): add('production', 'total production')
    elif 'offline' in s and 'production' in s:
        add('offline production')
        if re.search(r'\bproduction and offline production|^production and', s): add('production', 'building production', 'all buildings production'); scope.append('all')
    elif 'production bonus from gems' in s: add('production bonus from gems', 'gems')
    elif 'production' in s and not re.search(r'mercenary production|overall production|assistants production|production of assistants', s) or re.search(r'production of (?:the )?(?:three|two) highest|highest (?:three|two)', s):
        base = s.startswith('base production') or ' base production' in s or s.startswith('the base production') or 'base production' in s
        head = 'base production' if base else 'production'
        sub = 'base building production' if base else 'building production'
        add(head, sub)
        sfx = ' base production' if base else ' production'
        found = False
        for n, full in BNAMES.items():
            if re.search(r'\b' + re.escape(n) + r'\b', s):
                add(full.lower() + sfx); scope.append('b:' + full); found = True
        for pat, tag, sc in (
                (r'non-unique', 'non-unique buildings', 'non-unique'), (r'(?<!non-)\bunique buildings', 'unique buildings', 'unique'),
                (r'all other buildings', 'all other buildings', 'other'),
                (r'(?:all|each|every) (?:building|buildings)|production of buildings|all buildings|each building', 'all buildings', 'all'),
                (r'\bgood buildings|good, ', 'good buildings', 'good'), (r'\bevil buildings', 'evil buildings', 'evil'),
                (r'(?<!non-)\bneutral buildings|non-neutral', 'neutral buildings', 'neutral'),
                (r'tier \d+ building', 'tier buildings of your alignment', 'alignment-tier'),
                (r'highest .*tiers?|highest three|highest two|three highest|two highest', 'highest building tiers', 'highest-tiers'),
                (r'even-tier', 'even-tier buildings', 'even-tier'), (r'tiers directly above or below', 'buildings next to unique', 'next-unique'),
                (r'mercenary buildings|non-neutral mercenary', 'mercenary buildings', 'mercenary')):
            if re.search(pat, s):
                add(tag + sfx); scope.append(sc); found = True
        if not found and 'buildings' in s: add('all buildings' + sfx); scope.append('all')
        if not found and 'buildings' not in s and not scope: add('?' + s)
    elif re.search(r'assistants|production of assistants', s) and 'production' in s: add('production', 'assistants production')
    elif 'mercenar' in s and 'production' in s: add('production', 'mercenary production')
    elif re.search(r'overall production', s):
        g = re.search(r'overall production of (.*)', s); add('production', 'faction production', (g.group(1) if g else '') + ' production')
    elif re.search(r'clicking reward|clicks gained|clicks per', s):
        add('clicking reward')
        if 'base' in s: add('base clicking reward')
        if 'offline' in s: add('offline clicks')
    elif re.search(r'offline gains of faction coins', s): add('faction coins', 'offline faction coins')
    elif re.search(r'faction coin', s):
        if 'find chance' in s or 'chance to find' in s or 'find' in s and 'chance' in s: add('faction coin find chance')
        if 'excavation' in s: add('faction coins found with excavations')
        if not t: add('faction coins')
    elif re.search(r'royal (exchange|market)', s) and 'cost' not in s:
        add('royal exchange')
        if 'ascension multiplier' in s: add('royal exchange ascension multiplier')
        elif 'bonus' in s: add('royal exchange bonus')
        elif 'production' in s: add('royal exchange bonus')
        else: add('?' + s)
    elif 'cost' in s:
        add('cost multiplier')
        if 'spell' in s: add('spell cost')
        elif 'excavation' in s: add('excavation cost multiplier')
        elif 'royal exchange' in s: add('royal exchange cost multiplier')
        elif 'lineage' in s: add('lineage upgrade cost')
        elif 'building' in s or 'farms' in s or 'halls' in s or any(n in s for n in BNAMES): add('building cost multiplier')
        else: add('?' + s)
        for n, full in BNAMES.items():
            if re.search(r'\b' + re.escape(n) + r'\b', s): add(full.lower() + ' cost multiplier')
    elif re.search(r'maximum mana|mana regeneration|mana produced', s):
        add('mana')
        if 'maximum mana' in s: add('maximum mana')
        if 'regeneration' in s: add('offline mana regeneration' if 'offline' in s else 'mana regeneration')
    elif re.search(r'duration|durations', s):
        add('spells', 'spell duration')
        for sp in spell_in(s): add(sp)
        if re.search(r'night time', s): add('night time')
    elif re.search(r'research (budget|slots?)', s):
        add('research', 'research budget' if 'budget' in s else 'research slots')
    elif 'tax collection' in s:
        add('tax collection', 'tax collection worth' if 'worth' in s else 'triggered tax collections')
    elif s.startswith('count of '): add(s[9:] + ' count')
    elif s in ('autoclicks', 'autoclick power'): add('autoclicks')
    elif s == 'offline bonus': add('offline production')
    elif s in ('assistant production', 'assistants production'): add('production', 'assistants production')
    elif s == 'advanced heritages powers': add('advanced heritage power')
    elif s == 'headstart time': add('spells', 'brainwave', 'headstart time')
    elif s in ('offline spells cast amount', 'offline spell casts', 'offline spells cast'): add('spells cast amount', 'offline spells cast amount')
    elif s in ('spells cast amount', 'spells cast'): add('spells cast amount')
    elif re.search(r'\btiers?$', s) and ('spell' in s or 'gain' in s): add('spell tier')
    elif 'gem power' in s or 'ruby power' in s: add('gem power' if 'gem' in s else 'ruby power')
    elif re.search(r'assistants?', s): add('assistants')
    elif 'set power' in s: add('set power')
    elif 'excavation' in s: add('excavation', s)
    else:
        sp = spell_in(s)
        if sp:
            add('spells'); [add(x) for x in sp]
            add(s)
        else: add('?' + s)
    return t, scope


def ytags(raw):
    s = clean(raw)
    s = re.sub(r'\b(and )?unlocking more (unique )?perks for the building\b', ' ', s).strip(' ,')
    t = []

    def add(*a): t.extend(x for x in a if x not in t)
    R_ = lambda p: re.search(p, s)
    if R_(r'time spent|time of the day|least time|longest era|the time'):
        add('time spent')
        for a in ALIGN:
            if R_(r'\b' + a + r'\b'): add('time spent as ' + a)
        for f in FACTIONS:
            if R_(r'\b' + f): add('time spent as ' + f.rstrip('s'))
        if R_(r'offline'): add('time spent offline')
        if R_(r'\bonline'): add('time spent online')
        if R_(r'in this era'): add('time spent this era')
        if R_(r'longest era'): add('longest era')
        if R_(r'time of the day'): add('time of the day')
    if R_(r'mana statistics'): add('mana statistics')
    elif R_(r'mana produced'): add('mana produced')
    if R_(r'maximum mana|max mana'): add('maximum mana')
    if R_(r'mana regeneration'): add('mana regeneration')
    if R_(r'spell tier'): add('spell tier')
    elif R_(r'^(?:their |its )?tier$|building tiers? hit'): add('building tier')
    if R_(r'^(?:their |its )?(?:quantity|amount)$|buildings of the same type'): add('building quantity')
    if R_(r'assistants'): add('assistants owned')
    if R_(r'faction coin|coins found|(?:fairy|elven|angel|goblin|undead|demon|titan|druid|faceless|dwarven|drow|dragon|archon|djinn|makers) coins'):
        add('faction coins found')
        if R_(r'find chance'): add('faction coin find chance')
    if R_(r'buildings? (built|owned|you build)|built|owned') and not R_(r'assistants|gems|gold'): add('buildings built')
    if R_(r'gems'): add('gems owned')
    if R_(r'\bgold\b|amount of coins|coins you gained'): add('gold owned')
    if R_(r'clicks made|clicks'): add('clicks made')
    if R_(r'autoclick'): add('autoclicks')
    if R_(r'reincarnations (made|you made)|times you reincarnated|reincarnations'): add('reincarnations made')
    if R_(r'trophies'): add('trophies unlocked')
    if R_(r'artifacts'): add('artifacts found')
    if R_(r'lineage level|lineage levels|level of the lineage'): add('lineage level')
    if R_(r'research points|research budget'): add('research points')
    if R_(r'researches selected'): add('researches selected')
    if R_(r'royal exchanges'): add('royal exchanges made')
    if R_(r'royal exchange bonus'): add('royal exchange bonus')
    if R_(r'excavation'): add('excavation depth' if 'depth' in s else 'excavations made')
    if R_(r'tax collection'): add('tax collections cast')
    if R_(r'grand balance targets'): add('grand balance targets')
    if R_(r'combo strike (counter|bonus)'): add('combo strike counter')
    if R_(r'upgrades purchased'): add('upgrades purchased')
    if R_(r'production'): add('production')
    if R_(r'rubies'): add('rubies collected')
    if R_(r'spells (cast|you cast)|spells cast|casts|hellfire blasts cast'): add('spells cast')
    if R_(r'active spells|spell effects|dragon.s breath effects'): add('active spells')
    if R_(r'activity time|activity'): add('spell activity time')
    if R_(r'duration'): add('spell duration')
    for sp in spell_in(s): add(sp)
    if R_(r'factions? involved|different factions|factions in your legacies|faction upgrades different'): add('different factions')
    if R_(r'in this era'): add('this era')
    if R_(r'this reincarnation|in this reinc'): add('this reincarnation')
    if R_(r'all-time|across all reincarnations|all time'): add('all-time')
    if R_(r'single era'): add('single era')
    if R_(r'previous era|last era'): add('previous era')
    if R_(r'highest|maximum|deepest'): add('highest')
    if R_(r'least|lowest'): add('lowest')
    if R_(r'sum |combined|total'): add('sum')
    if not t: add('?' + s)
    return t


def special(s, trigger):
    """the wordings that are not 'Increase X based on Y'"""
    m = re.match(r'^(?:your )?(.+?)\s+(?:is|are)\s+(increased|reduced|multiplied)\b[^.]*?(?:\s+based on\s+([^.]*))?$', s, re.I)
    if m:
        return [{'verb': 'increase' if m.group(2).lower() != 'reduced' else 'reduce', 'x_raw': m.group(1), 'y_raw': m.group(3), 'mode': None, 'trigger': trigger}]
    m = re.match(r'^(?:also )?makes?\s+(.+?)\s+counts? more(?:\s+based on\s+(.*?))?(?:\s+when .*)?$', s, re.I)
    if m:
        return [{'verb': 'count', 'x_raw': 'count of ' + m.group(1), 'y_raw': m.group(2) or 'spell tier', 'mode': None, 'trigger': trigger}]
    m = re.match(r'^(?:also )?(.+?)\s+counts?\s+(?:\d+%\s+)?more(?:\s+(?:based on|when)\s+(.+?))?(?:\s+for every level)?$', s, re.I)
    if m and not s.lower().startswith('makes'):
        return [{'verb': 'count', 'x_raw': 'count of ' + m.group(1), 'y_raw': m.group(2), 'mode': None, 'trigger': trigger}]
    m = re.match(r"^([A-Z][\w' ]+?)\s+(?:(multiplicatively|additively)\s+)?(increases|reduces)\s+(.+?)(?:\s+(?:based on|progressively over)\s+(.+?))?$", s)
    if m and not re.match(r'^(?:The |Our |Your )?(?:production|mana)', m.group(1)) and re.search(r'\b[A-Z]', m.group(1)):
        y = m.group(5)
        if y and re.match(r'^its ', y): y = m.group(1) + ' ' + y[4:]
        return [{'verb': 'increase' if m.group(3) == 'increases' else 'reduce', 'x_raw': m.group(4), 'y_raw': y, 'mode': (m.group(2) or '').lower() or None, 'trigger': trigger}]
    m = re.match(r'^(.+?)\s+counts?\s+\d+%\s+more$', s, re.I)
    if m: return [{'verb': 'count', 'x_raw': 'count of ' + m.group(1), 'y_raw': None, 'mode': None, 'trigger': trigger}]
    m = re.match(r'^(.+?)\s+is added to\s+(.+)$', s, re.I)
    if m: return [{'verb': 'increase', 'x_raw': m.group(2), 'y_raw': re.sub(r'^\d+%\s+of\s+', '', m.group(1)), 'mode': None, 'trigger': trigger}]
    m = re.match(r'^(?:also,? )?(?:while ([^,]+), )?autoclicks?\b(?:.*?based on\s+(.*?))?[.]?$', s, re.I)
    if m: return [{'verb': 'increase', 'x_raw': 'autoclicks', 'y_raw': m.group(2), 'mode': None, 'trigger': trigger or (m.group(1) and 'While ' + m.group(1))}]
    m = re.match(r'^(.*?)\s*(?:is|are) worth more seconds based on\s+(.+?)$', s, re.I)
    if m: return [{'verb': 'increase', 'x_raw': 'tax collection worth', 'y_raw': m.group(2), 'mode': None, 'trigger': trigger}]
    m = re.match(r'^(.+?\bspells?|call to arms|[\w\' ]+?)\s+gains?\s+\d+\s+tiers?(?:\s+per .*)?$', s, re.I)
    if m: return [{'verb': 'increase', 'x_raw': 'spell tier', 'y_raw': None, 'mode': None, 'trigger': trigger}]
    m = re.match(r'^lower\s+(.+?)\s+based on\s+(.+?)$', s, re.I)
    if m: return [{'verb': 'reduce', 'x_raw': m.group(1), 'y_raw': m.group(2), 'mode': None, 'trigger': trigger}]
    return None


def split_effects(sent):
    """a sentence -> list of effect dicts (may be empty)"""
    s = PREFIX.sub('', sent.strip()).strip()
    trigger = None
    m = TRIG.match(s)
    if m: trigger = (m.group(1) + m.group(2)).strip(); s = m.group(3).strip()
    if SKIP.match(s): return []
    s2 = re.sub(r'^(Also,?\s*)', '', s).rstrip('. ')
    dur = re.search(r'for (\d+) seconds', s2)
    sp = special(s2, trigger)
    if sp is not None: return sp
    m = VERB.match(s2)
    if not m: return None
    mode = m.group(1).lower() if m.group(1) else None
    verb = m.group(2).lower()
    rest = m.group(3)
    if mode is None: mode = mode_of(rest)
    if verb in ('adds', 'add', 'gain') and not re.search(r'assistant|spell|research|coins|tax|clicks|click', rest, re.I): return None
    parts = re.split(r'\s+and (?:(?:multiplicatively|additively)\s+)?(?=(?:increase|reduce)\b)', rest, flags=re.I)
    out = []
    ylast = None
    for p in parts:
        p = re.sub(r'^(?:increase|reduce)\s+', '', p, flags=re.I)
        mm = re.split(r'\s+based on\s+', p, maxsplit=1)
        xr = re.split(r'\s+by\s+(?=[\d(+-])|\s+to\s+\d|\.\s|\s+every\s|\s+for\s+\d', mm[0])[0]
        y = mm[1] if len(mm) > 1 else None
        if y: y = re.split(r'\.(?:\s|$)| for \d+ seconds', y)[0]
        out.append({'verb': verb if len(out) == 0 else ('reduce' if 'reduce' in p.lower() else verb), 'x_raw': xr, 'y_raw': y, 'mode': mode, 'trigger': trigger})
    if len(out) > 1 and out[-1]['y_raw'] and not out[0]['y_raw']:
        for o in out[:-1]: o['y_raw'] = out[-1]['y_raw']
    return out


def paras_of(obj):
    return obj


# tags that do not name a stat but qualify one (the Effects page combines tags of different kinds with AND and tags of one kind with OR)
QUALIFIERS = {'multiplicative': 'mode',
              'this era': 'period', 'this reincarnation': 'period', 'all-time': 'period', 'single era': 'period', 'previous era': 'period', 'longest era': 'period',
              'highest': 'aggregate', 'lowest': 'aggregate', 'sum': 'aggregate'}


UPAGE = {'allegiances': 'upgrades-allegiance.html', 'magic': 'upgrades-magic.html', 'secret': 'upgrades-secret.html', 'misc': 'upgrades-misc.html',
         'buildings': 'upgrades-misc.html'}      # the page each kind of upgrade is shown on (see build_upgrades_page.py)


def collect():
    objs = []
    d = json.load(open(R + 'data/upgrade_pages.json', encoding='utf8'))
    for page, v in d.items():
        for u in v:
            ps = list(u['description']) + list(u.get('more') or [])
            objs.append({'src': 'upgrade', 'key': page + '/' + u['name'], 'name': u['name'], 'icon': u.get('icon'), 'page': UPAGE.get(page), 'asc': availability.upgrade_asc(u), 'texts': [p['text'] for p in ps]})
            for c in u.get('combos') or []:
                objs.append({'src': 'upgrade', 'key': page + '/' + u['name'] + '/' + c['name'], 'name': c['name'], 'icon': c.get('icon'), 'page': UPAGE.get(page), 'asc': availability.upgrade_asc(c), 'texts': [p['text'] for p in c['description']]})
    for x in json.load(open(R + 'data/research.json', encoding='utf8')):
        objs.append({'src': 'research', 'key': x['code'], 'name': x['name'], 'icon': x.get('icon'), 'page': 'research.html', 'asc': availability.research_asc(x), 'texts': [x['description']]})
    for f in json.load(open(R + 'data/challenges.json', encoding='utf8')):
        floor = availability.faction_floor(f['items'])
        for it in f['items']:
            objs.append({'src': 'challenge', 'key': f['name'] + '/' + it['name'], 'name': it['name'], 'icon': it.get('icon'), 'page': 'challenges.html', 'asc': availability.challenge_asc(it, floor), 'texts': list(it['rewards'])})
    return objs


def load_fixes():
    try: return json.load(open(R + 'data/effect_tags_fixes.json', encoding='utf8')).get('fixes', [])
    except FileNotFoundError: return []


def apply_fixes(res, unsplit, fixes):
    """Hand corrections are tied to the sentence they were made for. If an update changes the sentence (or the object is gone),
    the correction is not applied silently; it is returned as stale so it gets looked at again."""
    stale = []
    for f in fixes:
        o = res.get(f['key'])
        ok = False
        if o is not None:
            hit = [e for e in o['effects'] if e['text'] == f['text']]
            if f.get('add'):
                if (f['key'], f['text']) in unsplit and not hit:
                    o['effects'].append({'text': f['text'], 'verb': f['set'].get('verb', 'increase'), 'mode': f['set'].get('mode'), 'trigger': f['set'].get('trigger'),
                                         'x': f['set'].get('x', []), 'scope': [], 'y': f['set'].get('y', []), 'seconds': f['set'].get('seconds'), 'fixed': True})
                    ok = True
            elif hit:
                n = f.get('n')       # which of several effects made from the same sentence, when it is not all of them
                for i, e in enumerate(hit):
                    if n is not None and i != n: continue
                    if f.get('skip'): o['effects'].remove(e)
                    else: e.update(f['set']); e['fixed'] = True
                ok = True
        if not ok: stale.append(f)
    return stale


def tag_all(fixes=True):
    res, unsplit = {}, []
    for o in collect():
        effs = []
        for t in o['texts']:
            for q in re.split(r'(?<=[.!?])\s+(?=[A-Z(])', t.replace('\n', ' ')):
                r = split_effects(q)
                if r is None:
                    unsplit.append((o['key'], q)); continue
                for e in r:
                    xt, sc = xtags(e['x_raw'])
                    yt = ytags(e['y_raw']) if e['y_raw'] else []
                    dur = re.search(r'for (\d+) seconds', q)
                    for md in (['additive', 'multiplicative'] if e['mode'] == 'both' else [e['mode']]):     # 'additively and multiplicatively' is two effects
                        md = 'multiplicative' if md in ('multiplicative', 'multiplicatively') else None      # only multiplicative is a mode: a plain effect is additive
                        effs.append({'text': q, 'verb': e['verb'], 'mode': md, 'trigger': e['trigger'], 'x': xt, 'scope': sc, 'y': yt,
                                     'seconds': int(dur.group(1)) if dur else None})
        res[o['key']] = {'src': o['src'], 'name': o['name'], 'icon': o['icon'], 'page': o['page'], 'asc': o['asc'], 'effects': effs}
    stale = apply_fixes(res, set(unsplit), load_fixes()) if fixes else []
    return res, unsplit, stale


if __name__ == '__main__':
    res, unsplit, stale = tag_all()
    json.dump(res, open(R + 'data/effect_tags.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    n = sum(len(v['effects']) for v in res.values())
    bad = [(k, e) for k, v in res.items() for e in v['effects'] if any(x.startswith('?') for x in e['x'] + e['y'])]
    print('objects', len(res), 'effects', n, 'with ? tags', len(bad), 'unsplit sentences', len(unsplit), 'stale hand corrections', len(stale))
