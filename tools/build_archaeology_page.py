"""Generate docs/archaeology.html from data/artifacts.json.

    python -I tools/build_archaeology_page.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
artifacts = json.load(open(os.path.join(ROOT, 'data', 'artifacts.json'), encoding='utf8'))
icons = json.load(open(os.path.join(ROOT, 'data', 'icons.json')))

# artifact icons are not referenced by entity data, so make sure they are exported
import shutil
sprites = json.load(open(os.path.join(ROOT, 'data', 'sprites.json')))
icon_dir = os.path.join(ROOT, 'docs', 'assets', 'icons')
os.makedirs(icon_dir, exist_ok=True)


def icon_file(a):
    n = a['icon']
    if not n: return None
    dst = os.path.basename(sprites[n][0]['file'])
    path = os.path.join(icon_dir, dst)
    if not os.path.exists(path):
        src = os.path.join(ROOT, sprites[n][0]['file'])
        if os.path.exists(src): shutil.copy(src, path)
    if not os.path.exists(path): return None
    icons[n] = dst
    return dst


def item(a):
    ch = a.get('chance', {})
    return {'n': a['name'], 'f': a['flavor'], 'h': a['hint'], 'q': a['requirements'],
            'x': a['undecoded_conditions'], 'i': icon_file(a),
            'c': ch.get('mode'), 'p': ch.get('percent'), 'l': ch.get('latex'), 'v': ch.get('vars')}


sections = []
for kind, label in (('quest', 'Quest Artifacts'), ('lore', 'Lore Artifacts')):
    its = sorted((a for a in artifacts if a['kind'] == kind), key=lambda a: a['order'])
    sections.append({'title': f'{len(its)} {label}', 'items': [item(a) for a in its]})

json.dump(icons, open(os.path.join(ROOT, 'data', 'icons.json'), 'w'), indent=0, sort_keys=True)
data = json.dumps(sections, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
total = sum(len(s['items']) for s in sections)

html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Realm Grinder Archaeology</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<style>
:root{--bg:#fbfaf7;--fg:#1f1c17;--muted:#6b655a;--line:#ddd6c8;--card:#fff;--cell:#f0eadc;--cellhi:#e4d8bd;--accent:#8a5a14;--shadow:0 6px 24px rgba(0,0,0,.18)}
@media (prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece6d8;--muted:#a39b8a;--line:#383229;--card:#201d18;--cell:#2b261f;--cellhi:#3a3328;--accent:#e0a64a;--shadow:0 6px 24px rgba(0,0,0,.6)}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:620px;margin:0 auto;padding:16px 16px 80px}
nav{display:flex;gap:14px;margin:0 0 18px;font-size:.95rem}
nav a{color:var(--muted);text-decoration:none}
nav a[aria-current]{color:var(--fg);font-weight:600;border-bottom:2px solid var(--accent)}
h1{margin:0 0 4px;font-size:1.7rem}
.sub{color:var(--muted);margin:0 0 20px}
section{margin:0 0 26px}
h2{font-size:1.05rem;margin:0 0 8px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}
.cell{aspect-ratio:1;border:1px solid var(--line);border-radius:8px;background:var(--cell);padding:3px;
  display:flex;align-items:center;justify-content:center;cursor:default;font:inherit;color:inherit}
.cell:hover,.cell:focus-visible{background:var(--cellhi);outline:2px solid var(--accent);outline-offset:-1px}
.cell img{max-width:100%;max-height:100%;image-rendering:pixelated;pointer-events:none}
#tip{position:fixed;z-index:50;width:min(400px,calc(100vw - 16px));padding:10px 12px;border-radius:8px;background:var(--card);
  border:1px solid var(--line);box-shadow:var(--shadow);pointer-events:none;display:none;font-size:.92rem}
#tip b{display:block;font-size:1rem}
#tip .lbl{display:block;color:var(--accent);font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;margin-top:8px}
#tip ul{margin:2px 0 0;padding-left:18px}
#tip .hint,#tip .more,#tip .chance{color:var(--muted)}
#tip ul.vars{list-style:none;padding-left:0;margin:4px 0}
#tip ul.vars li{margin:2px 0}
#tip .formula{padding:4px 0;overflow-wrap:anywhere}
#tip .flavor{font-style:italic;color:var(--muted)}
/*SEARCH_CSS*/
</style>
</head>
<body>
<main>
<nav><a href="index.html">Home</a><a href="trophies.html">Trophies</a><a href="archaeology.html" aria-current="page">Archaeology</a><a href="research.html">Research</a><a href="challenges.html">Challenges</a><a href="upgrades.html">Upgrades</a></nav>
<h1>Archaeology</h1>
<p class="sub">__TOTAL__ artifacts. Hover an icon to see its hint, unlock requirement, and the flavor text revealed once it is found.</p>
<!--SEARCH_BAR-->
<div id="root"></div>
</main>
<div id="tip" role="tooltip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var SECTIONS = JSON.parse(document.getElementById('data').textContent);
  var root=document.getElementById('root'), tip=document.getElementById('tip');
/*SEARCH_JS*/
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  function showTip(it, anchor){
    tip.textContent='';
    tip.appendChild(el('b',null,it.n));
    if(it.h){ tip.appendChild(el('span','lbl','Hint')); tip.appendChild(el('div','hint',it.h)); }
    if(it.q.length || it.x){
      tip.appendChild(el('span','lbl','Unlock requirement'));
      if(it.q.length){ var ul=el('ul'); it.q.forEach(function(q){ ul.appendChild(el('li',null,q)); }); tip.appendChild(ul); }
      if(it.x) tip.appendChild(el('div','more',(it.q.length?'Plus ':'')+'additional conditions not listed here.'));
    } else {
      tip.appendChild(el('span','lbl','Unlock requirement'));
      tip.appendChild(el('div','hint','None. It can be found on any excavation.'));
    }
    if(it.c){
      tip.appendChild(el('span','lbl','How it is found'));
      var pct = (it.p!=null) ? String(it.p) : '';
      var lead = (it.q.length || it.x) ? 'Meeting the requirements does not unlock it by itself. From then on, each excavation has ' : 'Each excavation has ';
      if(it.c==='guaranteed'){
        tip.appendChild(el('div','chance','Once the requirements are met, it is found on your next excavation.'));
      } else if(it.c==='fixed'){
        tip.appendChild(el('div','chance',lead+'a '+pct+'% chance to find it.'));
      } else if(it.l && it.v){
        tip.appendChild(el('div','chance',lead+'a chance to find it, which depends on:'));
        var ul2=el('ul','vars');
        it.v.forEach(function(v){ var li=el('li'); var b=el('b',null,v.symbol); if(window.katex){ try{ katex.render(v.symbol,b,{throwOnError:false}); }catch(e){} } li.appendChild(b); li.appendChild(document.createTextNode(' — '+v.text)); ul2.appendChild(li); });
        tip.appendChild(ul2);
        var f=el('div','formula');
        if(window.katex){ try{ katex.render('\\\\displaystyle '+it.l,f,{throwOnError:false,displayMode:false}); }catch(e){ f.textContent=it.l; } }
        else f.textContent=it.l;
        tip.appendChild(f);
        tip.appendChild(el('div','more','p is the percent chance per excavation.'));
      } else {
        tip.appendChild(el('div','chance',lead+'a chance to find it, which depends on your stats.'));
      }
    }
    if(it.f){ tip.appendChild(el('span','lbl','Flavor text')); tip.appendChild(el('div','flavor',it.f)); }
    tip.style.display='block';
    var a=anchor.getBoundingClientRect(), t=tip.getBoundingClientRect();
    var x=Math.min(Math.max(8,a.left+a.width/2-t.width/2), window.innerWidth-t.width-8);
    var y=a.top-t.height-8; if(y<8) y=a.bottom+8;
    if(y+t.height>window.innerHeight-8) y=Math.max(8,window.innerHeight-t.height-8);
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }
  function hideTip(){ tip.style.display='none'; }
  document.addEventListener('scroll',hideTip,true);
  document.addEventListener('click',function(e){ if(!e.target.closest('.cell')) hideTip(); });
  SECTIONS.forEach(function(s){
    var sec=el('section'); sec.appendChild(el('h2',null,s.title));
    var g=el('div','grid');
    s.items.forEach(function(it){
      var b=el('button','cell'); b.type='button';
      b.setAttribute('aria-label', it.n);
      b._s=normS([it.n,it.h,it.f].join(' '));
      if(it.i){ var img=el('img'); img.src='assets/icons/'+encodeURIComponent(it.i); img.alt=''; img.loading='lazy'; b.appendChild(img); }
      b.addEventListener('mouseenter',function(){ showTip(it,b); });
      b.addEventListener('mouseleave',hideTip);
      b.addEventListener('focus',function(){ showTip(it,b); });
      b.addEventListener('blur',hideTip);
      b.addEventListener('click',function(e){ e.stopPropagation(); showTip(it,b); });
      g.appendChild(b);
    });
    sec.appendChild(g); root.appendChild(sec);
  });
  searchInit(root);
})();
</script>
</body>
</html>
'''
import search_snippet
html = search_snippet.apply(html.replace('__DATA__', data).replace('__TOTAL__', str(total)),
                            'Search artifact names, hints and flavor text')
open(os.path.join(ROOT, 'docs', 'archaeology.html'), 'w', encoding='utf8').write(html)
print('docs/archaeology.html', len(html) // 1024, 'KB;', [s['title'] for s in sections])
