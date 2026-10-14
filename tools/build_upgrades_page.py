"""Generate docs/upgrades.html from data/upgrade_pages.json.

    python -I tools/build_upgrades_page.py
"""
import json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
pages = json.load(open(os.path.join(ROOT, 'data', 'upgrade_pages.json'), encoding='utf8'))
meta = json.load(open(os.path.join(ROOT, 'data', 'research_meta.json'), encoding='utf8'))
icons = json.load(open(os.path.join(ROOT, 'data', 'icons.json')))
sprites = json.load(open(os.path.join(ROOT, 'data', 'sprites.json')))
icon_dir = os.path.join(ROOT, 'docs', 'assets', 'icons')
os.makedirs(icon_dir, exist_ok=True)


def icon_file(n):
    if not n or n not in sprites: return None
    dst = os.path.basename(sprites[n][0]['file'])
    path = os.path.join(icon_dir, dst)
    if not os.path.exists(path):
        src = os.path.join(ROOT, sprites[n][0]['file'])
        if os.path.exists(src): shutil.copy(src, path)
    if not os.path.exists(path): return None
    icons[n] = dst
    return dst


def effect_label(text):
    """short noun phrase naming what a paragraph's formula gives"""
    prefix = ''
    m = re.match(r'^([^:.]{1,20}): (.*)$', text)
    if m: prefix, text = m.group(1) + ': ', m.group(2)
    t = re.split(r' based on | for each |\. ', text)[0].rstrip('.')
    t = re.sub(r'^(?:[Mm]ultiplicatively )?(?:[Ii]ncreases?|[Gg]ain|[Gg]ive|[Rr]educe|[Ll]ower) ', '', t)
    t = re.sub(r'^the ', '', t)
    return prefix + t[:1].upper() + t[1:]


_SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
FNAME = {0: 'Fairy', 1: 'Elf', 2: 'Angel', 3: 'Goblin', 4: 'Undead', 5: 'Demon', 6: 'Titan', 7: 'Druid', 8: 'Faceless',
         9: 'Dwarf', 10: 'Drow', 11: 'Mercenary', 12: 'Dragon', 13: 'Archon', 14: 'Djinn', 15: 'Makers'}
# the name the search matches (the community codes map to these)
FSEARCH = {**FNAME, 1: 'Elven', 9: 'Dwarven'}
# base factions: alignment 1 Good, 2 Evil, 3 Neutral; axis 4 Order, 5 Chaos, 6 Balance
FACTIONS = [
    {'i': 0, 'n': 'Fairy', 'role': 'base', 'al': 1, 'ax': 5}, {'i': 1, 'n': 'Elf', 'role': 'base', 'al': 1, 'ax': 6},
    {'i': 2, 'n': 'Angel', 'role': 'base', 'al': 1, 'ax': 4}, {'i': 3, 'n': 'Goblin', 'role': 'base', 'al': 2, 'ax': 6},
    {'i': 4, 'n': 'Undead', 'role': 'base', 'al': 2, 'ax': 4}, {'i': 5, 'n': 'Demon', 'role': 'base', 'al': 2, 'ax': 5},
    {'i': 6, 'n': 'Titan', 'role': 'base', 'al': 3, 'ax': 4}, {'i': 7, 'n': 'Druid', 'role': 'base', 'al': 3, 'ax': 6},
    {'i': 8, 'n': 'Faceless', 'role': 'base', 'al': 3, 'ax': 5}, {'i': 11, 'n': 'Mercenary', 'role': 'merc'},
    {'i': 9, 'n': 'Dwarf', 'role': 'prestige', 'al': 1}, {'i': 10, 'n': 'Drow', 'role': 'prestige', 'al': 2},
    {'i': 12, 'n': 'Dragon', 'role': 'prestige', 'al': 3},
    {'i': 13, 'n': 'Archon', 'role': 'astral', 'ax': 4}, {'i': 14, 'n': 'Djinn', 'role': 'astral', 'ax': 5},
    {'i': 15, 'n': 'Makers', 'role': 'astral', 'ax': 6},
]
FORDER = [f['i'] for f in FACTIONS]


def fmt_num(n):
    n = float(n)
    if n < 1e6: return f'{int(round(n)):,}' if n == int(n) else f'{n:g}'
    m_, e_ = f'{n:.9e}'.split('e')
    mant, e = float(m_), int(e_)
    if abs(mant - round(mant)) < 1e-6: mant = round(mant)
    sup = str(e).translate(_SUP)
    return f'10{sup}' if mant == 1 else f'{mant:g} × 10{sup}'


UNION_ICON = {9: 'DwarvenUnion', 10: 'DrowUnion', 12: 'DragonUnion'}     # their icons exist per path (Order / Chaos / Balance)


PROOF_OF = {'Proof of Good Deed': {'al': 1}, 'Proof of Evil Deed': {'al': 2}, 'Proof of Neutrality': {'al': 3},
            'Proof of Order': {'ax': 4}, 'Proof of Chaos': {'ax': 5}, 'Proof of Balance': {'ax': 6}}
KIND_ORDER = {'proof': 0, 'bloodline_c': 1, 'bloodline': 9, 'tier': 2, 'perk': 3, 'heritage': 4, 'exchange': 5, 'spell': 6, 'unique': 7}


def item(u):
    forms = []
    for p in u['description']:
        for f in p['formulas']:
            forms.append({'l': f['latex'], 'v': f['vars'], 'lb': f.get('label') or effect_label(p['text']), 's': p['s']})
    if len(forms) == 1: forms[0]['lb'] = None
    return {
        'n': u['name'], 'i': icon_file(u['icon']),
        'd': [{'t': p['text'], 's': p['s']} for p in u['description']], 'f': forms,
        's': [f"{s['kind']}: {s['name']}" for s in u['sources']] + u['requirements'],
        'o': u['conditions'], 'lo': u['asc_min'], 'hi': u['asc_max'],
        'm': [{'t': b['text'], 's': b['s'], 'f': [{'l': f['latex'], 'v': f['vars']} for f in b['formulas']]}
              for b in u['more']] if u.get('more') else None,
        'mn': u.get('more_note'),
        **({'ra': u['unlock_by_asc'], 'sp': u['spell']} if u.get('unlock_by_asc') else {}),
        **({'fa': u['faction'], 'fn': FSEARCH.get(u['faction']), 'ak': u['akind']} if 'faction' in u else {}),
        **({'pr': PROOF_OF[u['name']]} if u.get('akind') == 'proof' else {}),
        **({'ia': {str(ax): icon_file(f"{UNION_ICON[u['faction']]}{nm}") for ax, nm in ((4, 'Order'), (5, 'Chaos'), (6, 'Balance'))}}
           if u.get('tier_no') == 4 and u.get('faction') in UNION_ICON else {}),
    }


GROUP_TITLES = {
    'HallOfLegendsProduction': 'Hall of Legends production upgrades',
    'HallOfLegendsPrestige': 'Hall of Legends base production upgrades',
    'NeutralProduction': 'Neutral buildings production upgrades',
    'GoodProduction': 'Good buildings production upgrades',
    'EvilProduction': 'Evil buildings production upgrades',
    'TrophyUpgrade': 'Trophy upgrades',
    'ManaProduction': 'Mana Regeneration upgrades',
    'RubyUpgrade': 'Ruby Power tiers',
    'ClickingBase': 'Base clicking reward upgrades',
    'ClickingProduction': 'Clicking reward and production upgrades',
    'ClickingTotalProduction': 'Production added to base clicking reward upgrades',
    'OfflineUpgrade': 'Offline production upgrades',
    'AssistantUpgrade': 'Production per assistant upgrades',
}
NOT_CONSOLIDATED = {'Autocast', 'ReincarnationPowerUpgrade', 'GemUpgrade'}      # listed one by one


def entries(items):
    """the game's grouping: upgrades of one group become one stacked icon (at the first member's position)"""
    out, pos = [], {}
    for u in sorted(items, key=lambda u: u['order']):
        g = u['group']
        if not g or g in NOT_CONSOLIDATED or u['name'] == 'Ruby Power':
            out.append({'g': None, 'items': [item(u)]}); continue
        if g not in pos:
            pos[g] = len(out)
            title = GROUP_TITLES.get(g) or (f"{u['building']} production upgrades" if u.get('building') else
                                            f"{u['spell']} spell tiers" if u.get('spell') else g)
            out.append({'g': title, 'items': []})
        out[pos[g]]['items'].append(item(u))
    for e in out:
        if e['g'] and len(e['items']) == 1: e['g'] = None
    return out


def section(sid, name, items):
    es = entries(items) if items is not None else None
    return {'id': sid, 'name': name, 'entries': es, 'count': sum(len(e['items']) for e in es) if es else 0}


def alleg_section():
    def key(u):
        sub = u['tier_no'] or u['perk'] or 0
        if u['akind'] == 'heritage': sub = 1 if u['name'].startswith('Advanced') else 0
        if u['akind'] == 'unique': sub = (u['name'][:-6] if u['name'].endswith(' Quest') else u['name'], 1 if not u['name'].endswith(' Quest') else 0)
        return (-1 if u['faction'] == -1 else FORDER.index(u['faction']), KIND_ORDER[u['akind']], sub, u['name'])
    allu = sorted(pages['allegiances'], key=key)
    blood = [item(u) for u in allu if u['akind'] == 'bloodline']
    es = []
    for u in allu:
        if u['akind'] == 'bloodline': continue
        it = item(u)
        if u['akind'] == 'bloodline_c': it['bl'] = blood
        es.append({'g': None, 'items': [it]})
    return {'id': 'allegiances', 'name': 'Allegiances Upgrades', 'entries': es, 'count': len(es), 'alleg': True}


sections = [
    alleg_section(),
    section('misc', 'Misc Upgrades', pages['misc']),
    section('magic', 'Magic Upgrades', pages['magic']),
    section('buildings', 'Buildings Upgrades', pages['buildings']),
    section('secret', 'Secret Upgrades', pages['secret']),
]
json.dump(icons, open(os.path.join(ROOT, 'data', 'icons.json'), 'w'), indent=0, sort_keys=True)
data = json.dumps({'max': meta['max_ascension'], 'sections': sections, 'factions': FACTIONS}, ensure_ascii=False,
                  separators=(',', ':')).replace('</', '<\\/')

html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Realm Grinder Upgrades</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<style>
:root{--bg:#fbfaf7;--fg:#1f1c17;--muted:#6b655a;--line:#ddd6c8;--card:#fff;--cell:#f0eadc;--cellhi:#e4d8bd;--accent:#8a5a14;--shadow:0 6px 24px rgba(0,0,0,.18)}
@media (prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece6d8;--muted:#a39b8a;--line:#383229;--card:#201d18;--cell:#2b261f;--cellhi:#3a3328;--accent:#e0a64a;--shadow:0 6px 24px rgba(0,0,0,.6)}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:620px;margin:0 auto;padding:16px 16px 80px}
nav{display:flex;gap:14px;flex-wrap:wrap;margin:0 0 18px;font-size:.95rem}
nav a{color:var(--muted);text-decoration:none}
nav a[aria-current]{color:var(--fg);font-weight:600;border-bottom:2px solid var(--accent)}
h1{margin:0 0 4px;font-size:1.7rem}
.sub{color:var(--muted);margin:0 0 12px}
.bar{position:sticky;top:0;z-index:40;margin:0 -16px 18px;padding:8px 16px;background:var(--bg);border-bottom:1px solid var(--line);
  display:flex;flex-direction:column;gap:6px;font-size:.92rem}
.bar .row{display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center}
.bar b{font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:var(--accent)}
.bar label{display:inline-flex;gap:6px;align-items:center;cursor:pointer}
.bar label.off{color:var(--muted);cursor:default}
.bar select{font:inherit;color:var(--fg);background:var(--card);border:1px solid var(--line);border-radius:6px;padding:4px 8px}
.bar .hint{color:var(--muted);font-size:.85rem}
.bar .row[hidden]{display:none}
.subh{margin:14px 0 6px;font-size:.92rem;color:var(--muted)}
.pen-note{margin:0 0 14px;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);font-size:.92rem}
.mark{font-weight:700;color:#fff;background:#a3341f;padding:0 4px;border-radius:4px;font-size:.8em}
section{margin:0 0 26px}
h2{font-size:1.05rem;margin:0 0 8px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h2 small{font-weight:400;color:var(--muted);margin-left:8px}
.grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}
.cell{position:relative;aspect-ratio:1;border:1px solid var(--line);border-radius:8px;background:var(--cell);padding:3px;
  display:flex;align-items:center;justify-content:center;cursor:default;font:inherit;color:inherit}
.cell:hover,.cell:focus-visible{background:var(--cellhi);outline:2px solid var(--accent);outline-offset:-1px}
.cell.na{opacity:.35;filter:grayscale(1)}
.cell img{max-width:100%;max-height:100%;image-rendering:pixelated;pointer-events:none}
.cell .pen{position:absolute;z-index:2;top:1px;right:2px;font:700 .6rem/1 system-ui,sans-serif;letter-spacing:-.02em;color:#fff;
  background:#a3341f;padding:1px 3px;border-radius:4px;pointer-events:none}
.cell.group{cursor:pointer}
.badge{position:absolute;right:2px;bottom:2px;font-size:.62rem;line-height:1;padding:2px 4px;border-radius:6px;background:var(--accent);color:var(--bg);font-weight:700;pointer-events:none}
#pop{position:fixed;inset:0;z-index:45;background:rgba(0,0,0,.45);display:none;align-items:center;justify-content:center;padding:16px}
#pop.open{display:flex}
#pop .card{background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);width:min(460px,100%);max-height:90vh;overflow:auto;padding:14px}
#pop header{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:10px}
#pop h3{margin:0;font-size:1.05rem}
#more{position:fixed;inset:0;z-index:46;background:rgba(0,0,0,.45);display:none;align-items:center;justify-content:center;padding:16px}
#more.open{display:flex}
#more .card{background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);width:min(480px,100%);max-height:90vh;overflow:auto;padding:12px 14px}
#more header{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:6px;position:sticky;top:-14px;background:var(--card);padding:6px 0}
#more h3{margin:0;font-size:1.1rem}
#more .bonus{border-top:1px solid var(--line);padding:8px 0}
#more .bonus p{margin:0 0 2px}
#more .formula{padding:2px 0;overflow-wrap:anywhere}
#more ul.vars{list-style:none;padding-left:0;margin:2px 0;color:var(--muted);font-size:.9rem}
#more .more{color:var(--muted);margin-top:10px}
#pop button.x,#more button.x{font:inherit;border:1px solid var(--line);background:var(--cell);color:var(--fg);border-radius:8px;padding:2px 10px;cursor:pointer}
#tip{position:fixed;z-index:50;width:min(420px,calc(100vw - 16px));padding:10px 12px;border-radius:8px;background:var(--card);
  border:1px solid var(--line);box-shadow:var(--shadow);pointer-events:none;display:none;font-size:.92rem}
#tip b.t{display:block;font-size:1rem}
#tip .lbl{display:block;color:var(--accent);font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;margin-top:8px}
#tip .faction{margin-top:6px;font-size:.88rem}
#tip ul{margin:2px 0 0;padding-left:18px}
#tip p{margin:3px 0 0}
#tip .more{color:var(--muted)}
#tip ul.vars{list-style:none;padding-left:0;margin:4px 0}
#tip ul.vars li{margin:2px 0}
#tip .formula{padding:4px 0;overflow-wrap:anywhere}
#tip .flabel{margin-top:6px;font-weight:600}
#tip .fsep{border-top:1px solid var(--line);margin:8px 0 2px}
/*SEARCH_CSS*/
</style>
</head>
<body>
<main>
<nav><a href="index.html">Home</a><a href="trophies.html">Trophies</a><a href="archaeology.html">Archaeology</a><a href="research.html">Research</a><a href="challenges.html">Challenges</a><a href="upgrades.html" aria-current="page">Upgrades</a></nav>
<h1>Upgrades</h1>
<p class="sub">Hover an upgrade for what it does and what unlocks it. Magic (with the spell tiers), Buildings and Secret upgrades are filled in so far; Misc has the Gem, Reincarnation, Ruby and Challenge powers and the clicking, offline and assistant series so far; Allegiances has the treaty tiers and the twelve faction upgrades of every faction so far (bloodlines, lineages, heritages, sets and legacies are still to come).</p>
<div class="pen-note"><b>Ascension penalty.</b> From Ascension 1 on, the game reduces the percentage effects of many upgrades. If an upgrade's
value is <i>v</i> (in %), the effect you get is <span id="pen-formula"></span>, where <i>k</i> is the number of <span class="mark">A</span>
marks on the upgrade: <span class="mark">A</span> is <i>k</i>&nbsp;=&nbsp;1 (exponent 0.1), <span class="mark">AA</span> is <i>k</i>&nbsp;=&nbsp;2
(exponent 0.01), <span class="mark">AAA</span> is <i>k</i>&nbsp;=&nbsp;3 (exponent 0.001), and so on, so more As means a harsher penalty.
The marks follow the Ascension chosen below. Most are reduced from Ascension 1, so <i>k</i> equals the Ascension number; some start later
and have fewer As, or none, at a given Ascension. Upgrades without a mark are not reduced. The formulas in the hover popups are always
the base values <i>v</i>.</div>
<!--SEARCH_BAR-->
<div class="bar">
  <div class="row"><label for="asc"><b>Ascension</b></label><select id="asc"></select>
  <span class="hint">The A marks and the greyed-out upgrades (not available in it) follow the chosen Ascension.</span></div>
  <div class="row" id="filter"><b>Show</b></div>
  <div class="row" id="alleg-row" hidden><b>Factions</b>
    <label>Base <select id="pk-b"></select></label>
    <label>Prestige <select id="pk-p"></select></label>
    <label>Astral <select id="pk-a"></select></label>
    <span class="hint" id="pk-h"></span></div>
</div>
<div id="root"></div>
</main>
<div id="tip" role="tooltip"></div>
<div id="pop" role="dialog" aria-modal="true" aria-labelledby="poptitle"><div class="card">
  <header><h3 id="poptitle"></h3><button class="x" type="button" id="popclose">Close</button></header>
  <div class="grid" id="popgrid"></div>
</div></div>
<div id="more" role="dialog" aria-modal="true" aria-labelledby="moretitle"><div class="card">
  <header><h3 id="moretitle"></h3><button class="x" type="button" id="moreclose">Close</button></header>
  <div id="morebody"></div>
</div></div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var DATA = JSON.parse(document.getElementById('data').textContent);
  var SECTIONS = DATA.sections, MAXA = DATA.max, ASC = 0, cells = [], gcells = [], FACS = DATA.factions;
  var PICK = {b:-1, p:-1, a:-1}, allegBox = null, allegItems = {}, runSearch = null;
  var root=document.getElementById('root'), tip=document.getElementById('tip'), filter=document.getElementById('filter'), sel=document.getElementById('asc');
/*SEARCH_JS*/
  function sOf(it){ return it._s || (it._s = normS([it.n,it.fn||'',Object.values(it.ra||{}).join(' '),facLines(it.o),facLines(it.s)].concat(it.d.map(function(p){ return p.t; })).join(' '))); }
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  function math(tex, host){
    if(window.katex){ try{ katex.render('\\displaystyle '+tex, host, {throwOnError:false}); return; }catch(e){} }
    host.textContent = tex;
  }
  function pred(p){
    return p.replace(/^not having /,'you do not have ').replace(/^not playing /,'you are not playing ').replace(/^following /,'you are following ')
            .replace(/^having /,'you have ').replace(/^playing /,'you are playing ').replace(/^using /,'you are using ')
            .replace(/^being able /,'you are able ').replace(/^being /,'you are ');
  }
  function As(k){ return new Array(k+1).join('A'); }
  function penalty(it){
    var k=0; it.d.forEach(function(p){ if(p.s && ASC>=p.s) k=Math.max(k, ASC-p.s+1); });
    if(it.m) it.m.forEach(function(p){ if(p.s && ASC>=p.s) k=Math.max(k, ASC-p.s+1); });
    return k;
  }
  function unavailable(it){ return (it.lo!==null && ASC<it.lo) || (it.hi!==null && ASC>=it.hi); }
  function formulas(parent, list){
    var many=list.length>1, seen={};
    parent.appendChild(el('span','lbl',many?'Formulas':'Formula'));
    var anyScaled=many && list.some(function(f){ return f.s; });
    list.forEach(function(f,i){
      if(i>0) parent.appendChild(el('div','fsep'));
      var vs=many?'v_{'+(i+1)+'}':'v';
      if(f.lb){
        var lab=el('div','flabel'); var lm=el('span'); math(vs,lm); lab.appendChild(lm);
        var suf='', badge=null;
        if(anyScaled){
          if(!f.s) suf='';
          else if(ASC>=f.s){ suf=' · '; badge=el('span','mark',As(ASC-f.s+1)); }
        }
        lab.appendChild(document.createTextNode(' — '+f.lb+suf)); if(badge) lab.appendChild(badge); parent.appendChild(lab);
      }
      var d=el('div','formula'); var m=el('span'); math(f.l.replace(/^v(_\{\d+\})? = /, vs+' = '), m); d.appendChild(m); parent.appendChild(d);
      var ul=el('ul','vars'), n=0;
      f.v.forEach(function(v){
        var k=v.symbol+'|'+v.text; if(seen[k]) return; seen[k]=1; n++;
        var li=el('li'); var b=el('b'); b.style.display='inline'; math(v.symbol,b); li.appendChild(b);
        li.appendChild(document.createTextNode(' — '+v.text)); ul.appendChild(li);
      });
      if(n) parent.appendChild(ul);
    });
    if(list.some(function(f){ return f.s; })) parent.appendChild(el('div','more','v is the base value, before any Ascension penalty.'));
  }
  function showTip(it, anchor){
    tip.textContent='';
    tip.appendChild(el('b','t',it.n));
    if(it.o.length) tip.appendChild(el('div','faction',(it.o[0].indexOf('starting from')===0 ? 'Can only be bought '+it.o[0]+'.' : 'Can only be bought when '+it.o.map(pred).join(' and ')+'.')));
    if(unavailable(it)){
      tip.appendChild(el('span','lbl','Not available'));
      tip.appendChild(el('div',null,'This upgrade is not available in Ascension '+ASC+'.'));
    }
    tip.appendChild(el('span','lbl','What it does'));
    it.d.forEach(function(p){
      var e=el('p',null,p.t);
      if(p.s && ASC>=p.s){ e.appendChild(document.createTextNode(' ')); e.appendChild(el('span','mark',As(ASC-p.s+1))); }
      tip.appendChild(e);
    });
    if(it.f.length){
      formulas(tip, it.f);
    }
    if(it.m || it.bl) tip.appendChild(el('div','more','Click for more info'));
    var rq=it.s.slice();
    if(it.ra && ASC>=1){ var ra=it.ra[String(Math.min(ASC,4))]; if(ra) rq.unshift(ra); }
    if(rq.length){
      tip.appendChild(el('span','lbl','Unlock requirement'));
      var ul=el('ul'); rq.forEach(function(s){ ul.appendChild(el('li',null,s)); }); tip.appendChild(ul);
    }
    tip.style.display='block';
    var r=anchor.getBoundingClientRect(), t=tip.getBoundingClientRect();
    var x=Math.min(Math.max(8,r.left+r.width/2-t.width/2), window.innerWidth-t.width-8);
    var y=r.top-t.height-8; if(y<8) y=r.bottom+8;
    if(y+t.height>window.innerHeight-8) y=Math.max(8,window.innerHeight-t.height-8);
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }
  function hideTip(){ tip.style.display='none'; }
  document.addEventListener('scroll',hideTip,true);
  document.addEventListener('click',function(e){ if(!e.target.closest('.cell')) hideTip(); });

  function itemCell(it, plain){
    var b=el('button','cell'); b.type='button'; b.setAttribute('aria-label', it.n);
    if(it.i){ var img=el('img'); img.src='assets/icons/'+encodeURIComponent(it.i); img.alt=''; img.loading='lazy'; b.appendChild(img); }
    if(!plain){
      b.addEventListener('mouseenter',function(){ showTip(it,b); });
      b.addEventListener('focus',function(){ showTip(it,b); });
      b.addEventListener('click',function(e){ e.stopPropagation(); if(it.m) openMore(it); else if(it.bl) openGroup({g:'Bloodlines', items:it.bl}); else showTip(it,b); });
    }
    b.addEventListener('mouseleave',hideTip);
    b.addEventListener('blur',hideTip);
    return b;
  }
  function decorate(b, it){
    var na=unavailable(it), k=na?0:penalty(it), m=b.querySelector('.pen');
    b.classList.toggle('na', na);
    if(k){ if(!m){ m=el('span','pen'); b.appendChild(m); } m.textContent=As(k); }
    else if(m){ m.remove(); }
  }
  function showGroupTip(sm, anchor){
    tip.textContent='';
    tip.appendChild(el('b','t',sm.n));
    tip.appendChild(el('div','more',sm.summary));
    tip.style.display='block';
    var r=anchor.getBoundingClientRect(), t=tip.getBoundingClientRect();
    var x=Math.min(Math.max(8,r.left+r.width/2-t.width/2), window.innerWidth-t.width-8);
    var y=r.top-t.height-8; if(y<8) y=r.bottom+8;
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }
  var pop=document.getElementById('pop'), popgrid=document.getElementById('popgrid'), poptitle=document.getElementById('poptitle');
  function openGroup(en){
    poptitle.textContent=en.g+' ('+en.items.length+' upgrades)';
    popgrid.textContent='';
    en.items.forEach(function(it){ if(!qmatch(sOf(it))) return; var b=itemCell(it); decorate(b,it); popgrid.appendChild(b); });
    hideTip(); pop.classList.add('open'); document.getElementById('popclose').focus();
  }
  function closePop(){ pop.classList.remove('open'); hideTip(); }
  document.getElementById('popclose').addEventListener('click',closePop);
  pop.addEventListener('click',function(e){ if(e.target===pop) closePop(); });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape') closePop(); });

  var more=document.getElementById('more'), morebody=document.getElementById('morebody'), moretitle=document.getElementById('moretitle');
  function openMore(it){
    moretitle.textContent=it.n; morebody.textContent='';
    var seen={}, scaled=false;
    it.m.forEach(function(b){
      var blk=el('div','bonus'), p=el('p',null,b.t);
      if(b.s){ scaled=true; if(ASC>=b.s){ p.appendChild(document.createTextNode(' ')); p.appendChild(el('span','mark',As(ASC-b.s+1))); } }
      blk.appendChild(p);
      var vars=[];
      b.f.forEach(function(f){
        var d=el('div','formula'), m=el('span'); math(f.l, m); d.appendChild(m); blk.appendChild(d);
        f.v.forEach(function(v){ var k=v.symbol+'|'+v.text; if(!seen[k]){ seen[k]=1; vars.push(v); } });
      });
      if(vars.length){
        var ul=el('ul','vars');
        vars.forEach(function(v){ var li=el('li'), bb=el('b'); bb.style.display='inline'; math(v.symbol, bb); li.appendChild(bb);
          li.appendChild(document.createTextNode(' — '+v.text)); ul.appendChild(li); });
        blk.appendChild(ul);
      }
      morebody.appendChild(blk);
    });
    if(scaled) morebody.appendChild(el('div','more','v is the base value, before any Ascension penalty.'));
    if(it.mn) morebody.appendChild(el('div','more',it.mn));
    hideTip(); more.classList.add('open'); document.getElementById('moreclose').focus();
  }
  function closeMore(){ more.classList.remove('open'); }
  document.getElementById('moreclose').addEventListener('click',closeMore);
  more.addEventListener('click',function(e){ if(e.target===more) closeMore(); });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape') closeMore(); });

  var saved={};
  try{ saved=JSON.parse(localStorage.getItem('upgrade-sections')||'{}')||{}; }catch(e){}
  SECTIONS.forEach(function(s){
    var on = s.entries ? (saved[s.id]!==false) : false;
    var lab=el('label', s.entries ? '' : 'off');
    var cb=el('input'); cb.type='checkbox'; cb.checked=on; cb.disabled=!s.entries;
    lab.appendChild(cb);
    lab.appendChild(document.createTextNode(s.name.replace(' Upgrades','')+(s.entries ? ' ('+s.count+')' : ' (not filled in yet)')));
    filter.appendChild(lab);
    if(!s.entries) return;
    var sec=el('section'); sec.hidden=!on;
    var h=el('h2',null,s.name); h.appendChild(el('small',null,s.count+' upgrades')); sec.appendChild(h);
    if(s.alleg){
      s.entries.forEach(function(en){ var it=en.items[0]; (allegItems[it.fa]=allegItems[it.fa]||[]).push(it); });
      allegBox=el('div'); sec.appendChild(allegBox); root.appendChild(sec);
      document.getElementById('alleg-row').hidden=!on;
      cb.addEventListener('change',function(){
        sec.hidden=!cb.checked; hideTip(); document.getElementById('alleg-row').hidden=!cb.checked;
        saved[s.id]=cb.checked;
        try{ localStorage.setItem('upgrade-sections', JSON.stringify(saved)); }catch(e){}
      });
      return;
    }
    var g=el('div','grid');
    s.entries.forEach(function(en){
      if(en.items.length===1){
        var it=en.items[0], b=itemCell(it);
        b._s=sOf(it); g.appendChild(b); cells.push([b,it]);
      } else {
        var gb=itemCell(en.items[0],true);
        gb.classList.add('group');
        gb.setAttribute('aria-label', en.g+', '+en.items.length+' upgrades');
        gb.appendChild(el('span','badge','\u00d7'+en.items.length));
        var summary={n:en.g, summary:en.items.length+' upgrades \u2014 click to view'};
        gb.addEventListener('mouseenter',function(){ showGroupTip(summary, gb); });
        gb.addEventListener('focus',function(){ showGroupTip(summary, gb); });
        gb.addEventListener('click',function(e){ e.stopPropagation(); openGroup(en); });
        gb._s=normS(en.g)+' '+en.items.map(sOf).join(' ');
        g.appendChild(gb); gcells.push([gb,en]);
      }
    });
    sec.appendChild(g); root.appendChild(sec);
    cb.addEventListener('change',function(){
      sec.hidden=!cb.checked; hideTip();
      saved[s.id]=cb.checked;
      try{ localStorage.setItem('upgrade-sections', JSON.stringify(saved)); }catch(e){}
    });
  });
  // ---- Allegiances: the base / prestige / astral faction picker
  var ROLE_TXT={base:'base faction', merc:'base faction', prestige:'prestige faction', astral:'astral faction'};
  function facOf(i){ for(var k=0;k<FACS.length;k++) if(FACS[k].i===i) return FACS[k]; return null; }
  function fillSel(sel, opts, val, disabled){
    sel.textContent='';
    opts.forEach(function(o){ var op=el('option',null,o[1]); op.value=String(o[0]); sel.appendChild(op); });
    sel.value=String(val); sel.disabled=!!disabled;
  }
  function syncPick(){
    var base=facOf(PICK.b), hint='';
    var bo=[[-1,'All factions']]; FACS.forEach(function(f){ if(f.role==='base'||f.role==='merc') bo.push([f.i,f.n]); });
    fillSel(document.getElementById('pk-b'), bo, PICK.b, false);
    // prestige: the one whose alignment matches the base faction (Mercenaries have none)
    var po=[[-1,'None']];
    if(base && base.role==='base') FACS.forEach(function(f){ if(f.role==='prestige' && f.al===base.al) po.push([f.i,f.n]); });
    else PICK.p=-1;
    if(PICK.p>=0 && !po.some(function(o){ return o[0]===PICK.p; })) PICK.p=-1;
    fillSel(document.getElementById('pk-p'), po, PICK.p, po.length<2);
    // astral: from Ascension 2, needs a prestige faction, and has to follow the same path (Order / Chaos / Balance)
    var ao=[[-1,'None']];
    if(base && base.role==='base' && PICK.p>=0 && ASC>=2) FACS.forEach(function(f){ if(f.role==='astral' && f.ax===base.ax) ao.push([f.i,f.n]); });
    else PICK.a=-1;
    if(PICK.a>=0 && !ao.some(function(o){ return o[0]===PICK.a; })) PICK.a=-1;
    fillSel(document.getElementById('pk-a'), ao, PICK.a, ao.length<2);
    if(!base) hint='Pick a base faction to see its upgrades together with those of a prestige and an astral faction.';
    else if(base.role==='merc') hint='Mercenaries cannot take a prestige or an astral faction.';
    else if(PICK.p<0) hint='Prestige factions need the Alliance upgrade of the base faction; the prestige faction has to match its alignment.';
    else if(ASC<2) hint='Astral factions are available from Ascension 2.';
    else if(PICK.a<0) hint='Astral factions need a prestige faction and follow the same path as the base faction (Order, Chaos or Balance).';
    document.getElementById('pk-h').textContent=hint;
  }
  function renderAlleg(){
    if(!allegBox) return;
    allegBox.textContent='';
    allegCells=[]; allegGroups=[];
    var bf=facOf(PICK.b), ax=String(bf && bf.ax ? bf.ax : 4);
    Object.keys(allegItems).forEach(function(k){ allegItems[k].forEach(function(it){ if(it.ia) it.i=it.ia[ax]; }); });
    var picked = PICK.b<0 ? null : [PICK.b].concat(PICK.p>=0?[PICK.p]:[], PICK.a>=0?[PICK.a]:[]);
    var g=el('div','grid');
    if(!picked){
      [{i:-1,n:'General'}].concat(FACS).forEach(function(f){
        var its=allegItems[f.i]||[]; if(!its.length) return;
        var en={g:f.n+' upgrades', items:its}, gb=itemCell(its[0],true);
        gb.classList.add('group');
        gb.setAttribute('aria-label', en.g+', '+its.length+' upgrades');
        gb.appendChild(el('span','badge','\u00d7'+its.length));
        var summary={n:en.g, summary:its.length+' upgrades \u2014 click to view'};
        gb.addEventListener('mouseenter',function(){ showGroupTip(summary, gb); });
        gb.addEventListener('focus',function(){ showGroupTip(summary, gb); });
        gb.addEventListener('click',function(e){ e.stopPropagation(); openGroup(en); });
        gb._s=normS(en.g)+' '+its.map(sOf).join(' ');
        g.appendChild(gb); allegGroups.push([gb,en]);
      });
      allegBox.appendChild(g);
    } else {
      [-1].concat(picked).forEach(function(fi){
        var f=fi<0 ? {n:'General',role:'gen'} : facOf(fi), its=allegItems[fi]||[];
        if(fi<0) its=its.filter(function(it){ return !it.pr || !bf || bf.role==='merc' || it.pr.al===bf.al || it.pr.ax===bf.ax; });
        if(!its.length) return;
        allegBox.appendChild(el('div','subh',fi<0 ? 'General (the alignment and path of your base faction)' : f.n+' ('+ROLE_TXT[f.role]+', '+its.length+' upgrades)'));
        var gg=el('div','grid');
        its.forEach(function(it){ var b=itemCell(it); b._s=sOf(it); gg.appendChild(b); allegCells.push([b,it]); });
        allegBox.appendChild(gg);
      });
    }
    decorateAlleg();
    if(runSearch) runSearch();
  }
  var allegCells=[], allegGroups=[];
  function decorateAlleg(){
    allegCells.forEach(function(p){ decorate(p[0], p[1]); });
    allegGroups.forEach(function(p){ p[0].classList.toggle('na', p[1].items.every(unavailable)); });
  }
  function bindPick(id, key){
    document.getElementById(id).addEventListener('change',function(){
      PICK[key]=parseInt(this.value,10);
      if(key==='b'){ PICK.p=-1; PICK.a=-1; }
      if(key==='p'){ PICK.a=-1; }
      savePick(); syncPick(); renderAlleg();
    });
  }
  function savePick(){ try{ localStorage.setItem('alleg-pick', JSON.stringify(PICK)); }catch(e){} }
  try{ var sp=JSON.parse(localStorage.getItem('alleg-pick')||'null'); if(sp && typeof sp.b==='number') PICK={b:sp.b|0, p:sp.p|0, a:sp.a|0}; }catch(e){}
  bindPick('pk-b','b'); bindPick('pk-p','p'); bindPick('pk-a','a');

  function apply(){
    cells.forEach(function(p){ decorate(p[0], p[1]); });
    syncPick(); renderAlleg();
    gcells.forEach(function(p){ p[0].classList.toggle('na', p[1].items.every(unavailable)); });
    hideTip();
  }
  for(var a=0;a<=MAXA;a++){ var o=el('option',null,String(a)); o.value=String(a); sel.appendChild(o); }
  try{ var sv=parseInt(localStorage.getItem('rg-ascension'),10); if(sv>=0 && sv<=MAXA) ASC=sv; }catch(e){}
  sel.value=String(ASC);
  sel.addEventListener('change',function(){ ASC=parseInt(sel.value,10); try{ localStorage.setItem('rg-ascension',String(ASC)); }catch(e){} apply(); });
  apply();
  runSearch=searchInit(root);
  document.addEventListener('DOMContentLoaded',function(){
    math('\\left(\\left(1+\\frac{v}{100}\\right)^{0.1^{k}}-1\\right)\\cdot 100\\,\\%', document.getElementById('pen-formula'));
  });
})();
</script>
</body>
</html>
'''
import search_snippet
html = html.replace('__DATA__', data)
html = search_snippet.apply(html, 'Search upgrade names and descriptions')
open(os.path.join(ROOT, 'docs', 'upgrades.html'), 'w', encoding='utf8').write(html)
print('docs/upgrades.html', len(html) // 1024, 'KB;', [(x['id'], x['count']) for x in sections])
