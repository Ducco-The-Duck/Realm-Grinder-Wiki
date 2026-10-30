"""Generate docs/spells.html from data/spells.json and data/spells_overview.json (descriptions, tags): every spell as an icon with a hover tooltip.

    python -I tools/build_spells_page.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
spells = json.load(open(os.path.join(ROOT, 'data', 'spells.json'), encoding='utf8'))
ov = json.load(open(os.path.join(ROOT, 'data', 'spells_overview.json'), encoding='utf8'))['spells']
data = json.dumps([{'name': s['name'], 'icon': s['icon'] + '.png', 'cost': s.get('cost'), 'ticks': s.get('duration'),
                    'desc': ov[s['name']]['description'], 'tags': ov[s['name']]['tags'], 'detail': ov[s['name']].get('detail', {})} for s in spells],
                  ensure_ascii=False, separators=(',', ':')).replace('</', '<\/')

html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/bg.css"><script src="assets/bg.js" defer></script>
<title>Realm Grinder Spells</title>
<style>
:root{--bg:#fbfaf7;--fg:#1f1c17;--muted:#6b655a;--line:#ddd6c8;--card:#fff;--cell:#f0eadc;--cellhi:#e4d8bd;--accent:#8a5a14;--shadow:0 6px 24px rgba(0,0,0,.18)}
@media (prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece6d8;--muted:#a39b8a;--line:#383229;--card:#201d18;--cell:#2b261f;--cellhi:#3a3328;--accent:#e0a64a;--shadow:0 6px 24px rgba(0,0,0,.6)}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:780px;margin:0 auto;padding:16px 16px 80px}
.sub{color:var(--muted);margin:0 0 18px}
.grid{display:flex;flex-wrap:wrap;gap:10px}
.cell{width:89px;height:89px;border:1px solid var(--line);border-radius:8px;background:var(--cell);padding:3px;
  display:flex;align-items:center;justify-content:center;cursor:default;font:inherit;color:inherit}
.cell:hover,.cell:focus-visible{background:var(--cellhi);outline:2px solid var(--accent);outline-offset:-1px}
.cell img{max-width:100%;max-height:100%;image-rendering:pixelated;pointer-events:none}
#tip{position:fixed;z-index:50;width:min(340px,calc(100vw - 16px));padding:10px 12px;border-radius:8px;background:var(--card);
  border:1px solid var(--line);box-shadow:var(--shadow);pointer-events:none;display:none;font-size:.92rem}
#tip b{display:block;font-size:1rem}
#tip p{margin:4px 0 0}
.tags{display:flex;gap:4px;flex-wrap:wrap;align-items:flex-start;margin-top:4px}
.chip{font-size:.72em;height:1.5em;line-height:1.5em;box-sizing:border-box;white-space:nowrap;padding:0 .5em;border-radius:9px;border:1px solid var(--line);background:var(--cell);color:var(--muted)}
.chip{border-color:transparent}
.chip.c-tax-collection{background:#c9a227;color:#2a1f00}
.chip.c-common{background:#8b5a2b;color:#fff}
.chip.c-pseudo-faction{background:repeating-linear-gradient(45deg,#7a35b0 0 6px,#141414 6px 12px);color:#fff;text-shadow:0 0 2px #000,0 0 2px #000}
.chip.c-alignment{background:#141414;color:#eee;border-color:#555}
.chip.c-good{background:#8fd0ff;color:#0a2a40}
.chip.c-evil{background:#c0392b;color:#fff}
.chip.c-neutral{background:#9a9a9a;color:#111}
.chip.c-order{background:#f4f4f4;color:#222}
.chip.c-chaos{background:#8ee68e;color:#0d3a0d}
.chip.c-balance{background:#fff3a0;color:#4a3f00}
.chip.c-faction{background:#8e44ad;color:#fff}
.chip.c-seasonal{background:#ff9ec7;color:#5a0a2e}
#detail .chip{font-size:.8em}
#detail .note{color:var(--muted);opacity:.8;font-size:.9rem;margin:6px 0 0}
#detail h3{margin:16px 0 0;color:var(--accent)}
#tip .hint{color:var(--muted);opacity:.75;font-size:.8rem;margin-top:8px}
#detail{margin-top:22px;scroll-margin-top:12px}
#detail h2{margin:0 0 4px;color:var(--accent)}
#detail .empty{color:var(--muted)}
/*SEARCH_CSS*/
</style>
</head>
<body>
<main>
<nav><a href="index.html">Home</a><a href="spells.html" aria-current="page">Spells</a></nav>
<h1>Spells</h1>
<p>Pseudo-Faction spells count as Faction spells for stats, but are not affected by effects that affect Faction spells.</p>
<p class="sub">Hover a spell for an overview, click it for the details.</p>
<div class="grid" id="root"></div>
<section id="detail" hidden></section>
</main>
<div id="tip" role="tooltip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var SPELLS = JSON.parse(document.getElementById('data').textContent), root=document.getElementById('root'), tip=document.getElementById('tip');
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  function chips(s){
    var d=el('div','tags');
    (s.tags||s).forEach(function(t){ d.appendChild(el('span','chip c-'+t.replace(/\*$/,'').toLowerCase().replace(/[^a-z0-9]+/g,'-'),t)); });
    return d;
  }
  function dur(ticks){      // durations are stored in ticks, 30 per second
    var s=Math.round(ticks/30), m=Math.floor(s/60), r=s%60, out=[];
    function u(n,w){ return n+' '+w+(n===1?'':'s'); }
    if(m) out.push(u(m,'minute'));
    if(r||!m) out.push(u(r,'second'));
    return out.join(' ');
  }
  var detail=document.getElementById('detail');
  function showDetail(s){
    detail.hidden=false; detail.textContent=''; detail.appendChild(el('h2',null,s.name));
    if(s.tags.length) detail.appendChild(chips(s));
    var dd=s.detail||{};
    if(dd.note) detail.appendChild(el('p','note',dd.note));
    (dd.sections||[]).forEach(function(c){ detail.appendChild(el('h3',null,c.title)); if(c.tags) detail.appendChild(chips(c.tags)); });
    if(!dd.sections) detail.appendChild(el('p','empty','No detailed information has been written yet.'));
    detail.scrollIntoView({behavior:'smooth',block:'nearest'});
  }
  function hideTip(){ tip.style.display='none'; }
  function showTip(s, anchor){
    tip.textContent=''; tip.appendChild(el('b',null,s.name));
    if(s.tags.length) tip.appendChild(chips(s));
    tip.appendChild(el('p',null,s.desc));
    if(s.cost!=null) tip.appendChild(el('p',null,'Base mana cost: '+s.cost.toLocaleString('en-US')));
    if(s.ticks!=null) tip.appendChild(el('p',null,'Base duration: '+dur(s.ticks)));
    tip.appendChild(el('p','hint','Click the spell icon to show detailed information.'));
    tip.style.display='block';
    var a=anchor.getBoundingClientRect(), t=tip.getBoundingClientRect();
    var x=Math.min(Math.max(8,a.left+a.width/2-t.width/2),innerWidth-t.width-8);
    var up=a.top-t.height-8>=8;
    tip.style.left=x+'px'; tip.style.top=(up?a.top-t.height-8:a.bottom+8)+'px';
  }
  window.addEventListener('scroll',hideTip,{passive:true});
  SPELLS.forEach(function(s){
    var c=el('button','cell'), im=el('img'); c.type='button'; im.src='assets/icons/'+s.icon; im.alt=s.name; c.appendChild(im);
    c.addEventListener('mouseenter',function(){ showTip(s,c); }); c.addEventListener('focus',function(){ showTip(s,c); });
    c.addEventListener('click',function(){ hideTip(); showDetail(s); });
    c.addEventListener('mouseleave',hideTip); c.addEventListener('blur',hideTip);
    root.appendChild(c);
  });
/*SEARCH_JS*/
})();
</script>
</body>
</html>
'''
import search_snippet
page = search_snippet.apply(html.replace('__DATA__', data), '', 'spells.html')
open(os.path.join(ROOT, 'docs', 'spells.html'), 'w', encoding='utf8').write(page)
print('docs/spells.html', len(page) // 1024, 'KB;', len(spells), 'spells')
