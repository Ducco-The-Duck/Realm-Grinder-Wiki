"""Generate docs/trophies.html (self-contained, data embedded) from data/trophies.json.

Layout mirrors the in-game trophy screen: sections by category, 7-column icon grid, tiers of the
same trophy type collapsed into one cell (click for a popup of every tier), tooltips on hover.

    python -I tools/build_trophies_page.py
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT =os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
trophies = json.load(open(os.path.join(ROOT, 'data', 'trophies.json'), encoding='utf8'))
icons = json.load(open(os.path.join(ROOT, 'data', 'icons.json')))

CATEGORIES = {0: 'Allegiances', 1: 'Miscellaneous', 2: 'Magic', 3: 'Building', 4: 'Secret'}
# 'special' entries (56) are internal: 53 have no icon and mirror upgrades, so they are not shown. Event trophies
# ('seasonal') are left out on purpose; so are the excavation finds, which live on the Archaeology page.


def pretty(t):
    t = re.sub(r'\d+$', '', t or '')
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', t)


_BLD = {re.sub(r"[^a-z]", '', b['name'].lower()): b.get('name_plural') or b['name']
        for b in json.load(open(os.path.join(ROOT, 'data', 'buildings.json'), encoding='utf8'))}
STACK_TITLES = {'Gain Coin': 'Coins', 'Gain Coin Clicking': 'Coins from Clicks', 'Click Treasure': 'Clicks',
                'Find Faction Coin': 'Faction Coins', 'Have Assistants': 'Assistants', 'Find Artifact': 'Artifacts',
                'Gain Gem': 'Gems', 'Gain Ruby': 'Rubies', 'Purchase Upgrade': 'Upgrades', 'Gain Reincarnate': 'Reincarnations',
                'Spend Mana': 'Mana', 'Cast Spell': 'Spells', 'Unlock Spell Tier': 'Arcane Brilliance',
                'Build Building': 'Buildings'}


def stack_title(t):
    """the name shown for a stack of tiers: what the trophies count, e.g. Coins, Spells, Farms"""
    p = pretty(t)
    if p in STACK_TITLES: return STACK_TITLES[p]
    if p.startswith('Build '):
        return _BLD.get(re.sub(r"[^a-z]", '', p[6:].lower()), p[6:] + 's')
    return p


def item(t):
    return {'n': t['name'], 'r': t['requirement'], 'i': icons.get(t['icon']) if t['icon'] else None}


def cells(items):
    """Group by trophy type (non-empty), keeping first-appearance order; tiers by registry order."""
    out, by_type = [], {}
    for t in sorted(items, key=lambda t: t['order']):
        if t['type']:
            if t['type'] not in by_type:
                by_type[t['type']] = {'title': stack_title(t['type']), 'items': []}
                out.append(by_type[t['type']])
            by_type[t['type']]['items'].append(item(t))
        else:
            out.append({'items': [item(t)]})
    return out


sections = []
listed = [t for t in trophies if t['listed']]
for cat, title in CATEGORIES.items():
    its = [t for t in listed if t['category'] == cat]
    sections.append({'title': f'{title} Trophies', 'n': len(its), 'cells': cells(its)})
assert sum(sum(len(c['items']) for c in s['cells']) for s in sections) == len(listed)
data = json.dumps(sections, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/bg.css"><script src="assets/bg.js" defer></script>
<title>Realm Grinder Trophies</title>
<style>
:root{--bg:#fbfaf7;--fg:#1f1c17;--muted:#6b655a;--line:#ddd6c8;--card:#fff;--cell:#f0eadc;--cellhi:#e4d8bd;--accent:#8a5a14;--shadow:0 6px 24px rgba(0,0,0,.18)}
@media (prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece6d8;--muted:#a39b8a;--line:#383229;--card:#201d18;--cell:#2b261f;--cellhi:#3a3328;--accent:#e0a64a;--shadow:0 6px 24px rgba(0,0,0,.6)}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:620px;margin:0 auto;padding:24px 16px 80px}
nav{display:flex;gap:14px;margin:0 0 18px;font-size:.95rem}
nav a{color:var(--muted);text-decoration:none}
nav a[aria-current]{color:var(--fg);font-weight:600;border-bottom:2px solid var(--accent)}
h1{margin:0 0 4px;font-size:1.7rem}
.sub{color:var(--muted);margin:0 0 20px}
section{margin:0 0 26px}
h2{font-size:1.05rem;margin:0 0 8px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h2 small{font-weight:400;color:var(--muted);margin-left:8px}
.subh small{font-weight:400;margin-left:8px}
.subh{font-size:.9rem;color:var(--muted);margin:14px 0 6px;font-weight:600}
.grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}
.cell{position:relative;aspect-ratio:1;border:1px solid var(--line);border-radius:8px;background:var(--cell);padding:3px;
  display:flex;align-items:center;justify-content:center;cursor:default;font:inherit;color:inherit}
.cell.group{cursor:pointer}
.cell:hover,.cell:focus-visible{background:var(--cellhi);outline:2px solid var(--accent);outline-offset:-1px}
.cell img{max-width:100%;max-height:100%;image-rendering:pixelated;pointer-events:none}
.cell .noimg{font-size:.7rem;color:var(--muted)}
.badge{position:absolute;right:2px;bottom:2px;font-size:.62rem;line-height:1;padding:2px 4px;border-radius:6px;background:var(--accent);color:var(--bg);font-weight:700;pointer-events:none}
#tip{position:fixed;z-index:50;max-width:min(320px,calc(100vw - 16px));padding:8px 10px;border-radius:8px;background:var(--card);
  border:1px solid var(--line);box-shadow:var(--shadow);pointer-events:none;display:none}
#tip b{display:block}
#tip span{display:block;color:var(--fg);white-space:pre-line;font-size:.92rem;line-height:1.05}
#tip em{display:block;color:var(--accent);font-style:normal;font-size:.8rem;margin-top:4px}
#pop{position:fixed;inset:0;z-index:40;background:rgba(0,0,0,.45);display:none;align-items:center;justify-content:center;padding:16px}
#pop.open{display:flex}
#pop .card{background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);width:min(460px,100%);max-height:90vh;overflow:auto;padding:14px}
#pop header{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:10px}
#pop h3{margin:0;font-size:1.05rem}
#pop button.x{font:inherit;border:1px solid var(--line);background:var(--cell);color:var(--fg);border-radius:8px;padding:2px 10px;cursor:pointer}
/*SEARCH_CSS*/
</style>
</head>
<body>
<main>
<nav><a href="index.html">Home</a><a href="trophies.html" aria-current="page">Trophies</a><a href="archaeology.html">Archaeology</a><a href="research.html">Research</a><a href="challenges.html">Challenges</a><a href="upgrades.html">Upgrades</a></nav>
<h1>Trophies</h1>
<p class="sub">__TOTAL__ trophies, arranged as in the game. Hover an icon to see its name and requirement; click a stacked icon to see every tier.</p>
<!--SEARCH_BAR-->
<div id="root"></div>
</main>
<div id="tip" role="tooltip"></div>
<div id="pop" role="dialog" aria-modal="true" aria-labelledby="poptitle"><div class="card">
  <header><h3 id="poptitle"></h3><button class="x" type="button" id="popclose">Close</button></header>
  <div class="grid" id="popgrid"></div>
</div></div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var SECTIONS = JSON.parse(document.getElementById('data').textContent);
  var root=document.getElementById('root'), tip=document.getElementById('tip'),
      pop=document.getElementById('pop'), popgrid=document.getElementById('popgrid'), poptitle=document.getElementById('poptitle');
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
/*SEARCH_JS*/
  function sOf(it){ return normS(it.n+' '+(it.r||'')); }
  function icon(it){
    if(it.i){ var img=el('img'); img.src='assets/icons/'+encodeURIComponent(it.i); img.alt=''; img.loading='lazy'; return img; }
    return el('span','noimg','?');
  }
  function showTip(it, anchor, hint){
    tip.textContent='';
    tip.appendChild(el('b',null,it.n));
    if(it.r) tip.appendChild(el('span',null,it.r.replace(/\n{2,}/g,'\\n').trim()));
    if(hint) tip.appendChild(el('em',null,hint));
    tip.style.display='block';
    var a=anchor.getBoundingClientRect(), t=tip.getBoundingClientRect();
    var x=Math.min(Math.max(8,a.left+a.width/2-t.width/2), window.innerWidth-t.width-8);
    var y=a.top-t.height-8; if(y<8) y=a.bottom+8;
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }
  function hideTip(){ tip.style.display='none'; }
  function bindTip(node, it, hint){
    node.addEventListener('mouseenter',function(){ showTip(it,node,hint); });
    node.addEventListener('mouseleave',hideTip);
    node.addEventListener('focus',function(){ showTip(it,node,hint); });
    node.addEventListener('blur',hideTip);
  }
  function cellButton(it, extraClass){
    var b=el('button','cell'+(extraClass?' '+extraClass:'')); b.type='button';
    b.setAttribute('aria-label', it.n+(it.r?': '+it.r:''));
    b.appendChild(icon(it));
    return b;
  }
  function openGroup(c){
    poptitle.textContent=c.title+' ('+c.items.length+' tiers)';
    popgrid.textContent='';
    c.items.forEach(function(it){
      if(!qmatch(sOf(it))) return;
      var b=cellButton(it); bindTip(b,it); b.addEventListener('click',function(e){ e.stopPropagation(); showTip(it,b); });
      popgrid.appendChild(b);
    });
    hideTip(); pop.classList.add('open'); document.getElementById('popclose').focus();
  }
  function closePop(){ pop.classList.remove('open'); hideTip(); }
  document.getElementById('popclose').addEventListener('click',closePop);
  pop.addEventListener('click',function(e){ if(e.target===pop) closePop(); });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape') closePop(); });
  document.addEventListener('scroll',hideTip,true);

  function grid(cells){
    var g=el('div','grid');
    cells.forEach(function(c){
      if(c.items.length===1){
        var it=c.items[0], b=cellButton(it); bindTip(b,it);
        b._s=sOf(it);
        b.addEventListener('click',function(){ showTip(it,b); });
        g.appendChild(b);
      } else {
        var first=c.items[0], last=c.items[c.items.length-1];
        var b=cellButton(first,'group');
        b.setAttribute('aria-label', c.title+', '+c.items.length+' tiers');
        b._s=normS(c.title)+' '+c.items.map(sOf).join(' ');
        b.appendChild(el('span','badge','\\u00d7'+c.items.length));
        var summary={n:c.title,r:first.n+' \\u2192 '+last.n};
        bindTip(b,summary,c.items.length+' tiers \\u2014 click to view');
        b.addEventListener('click',function(){ openGroup(c); });
        g.appendChild(b);
      }
    });
    return g;
  }
  SECTIONS.forEach(function(s){
    var sec=el('section'); var h=el('h2',null,s.title); h.appendChild(el('small',null,s.n+' trophies')); sec.appendChild(h);
    var inner=el('div');
    if(s.subs){ s.subs.forEach(function(sub){ var sh=el('h3','subh',sub.title); sh.appendChild(el('small',null,sub.n+' trophies')); inner.appendChild(sh); inner.appendChild(grid(sub.cells)); }); }
    else inner.appendChild(grid(s.cells));
    foldable(sec, h, inner, s.title);
    root.appendChild(sec);
  });
  searchInit(root);
})();
</script>
</body>
</html>
'''
import search_snippet
html = search_snippet.apply(html.replace('__DATA__', data).replace('__TOTAL__', str(len(listed))),
                            'Search trophy names and requirements')
os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
open(os.path.join(ROOT, 'docs', 'trophies.html'), 'w', encoding='utf8').write(html)
print('docs/trophies.html', len(html) // 1024, 'KB')
for s in sections:
    subs_ = s.get('subs') or [s]
    print(' ', s['title'], '->', sum(len(x['cells']) for x in subs_), 'cells')
