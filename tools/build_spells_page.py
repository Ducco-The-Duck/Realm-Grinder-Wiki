"""Generate docs/spells.html from data/spells.json: every spell as an icon with a hover tooltip.

    python -I tools/build_spells_page.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
spells = json.load(open(os.path.join(ROOT, 'data', 'spells.json'), encoding='utf8'))
data = json.dumps([{'name': s['name'], 'icon': s['icon'] + '.png', 'cost': s.get('cost')} for s in spells],
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
#tip{position:fixed;z-index:50;width:min(300px,calc(100vw - 16px));padding:10px 12px;border-radius:8px;background:var(--card);
  border:1px solid var(--line);box-shadow:var(--shadow);pointer-events:none;display:none;font-size:.92rem}
#tip b{display:block;font-size:1rem}
#tip p{margin:2px 0 0}
/*SEARCH_CSS*/
</style>
</head>
<body>
<main>
<nav><a href="index.html">Home</a><a href="spells.html" aria-current="page">Spells</a></nav>
<h1>Spells</h1>
<p class="sub">Hover a spell for its details.</p>
<div class="grid" id="root"></div>
</main>
<div id="tip" role="tooltip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var SPELLS = JSON.parse(document.getElementById('data').textContent), root=document.getElementById('root'), tip=document.getElementById('tip');
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  function hideTip(){ tip.style.display='none'; }
  function showTip(s, anchor){
    tip.textContent=''; tip.appendChild(el('b',null,s.name));
    if(s.cost!=null) tip.appendChild(el('p',null,'Base mana cost: '+s.cost.toLocaleString('en-US')));
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
