"""Generate docs/unlocks.html from data/unlocks.json (hand-written): the game's mechanics, shown at the Ascension they are unlocked at.

    python -I tools/build_unlocks_page.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
d = json.load(open(os.path.join(ROOT, 'data', 'unlocks.json'), encoding='utf8'))
data = json.dumps({'max': d['max_ascension'], 'mechanics': d['mechanics']}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\/')

html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/bg.css"><script src="assets/bg.js" defer></script>
<title>Realm Grinder Unlocks</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<style>
:root{--bg:#fbfaf7;--fg:#1f1c17;--muted:#6b655a;--line:#ddd6c8;--card:#fff;--cell:#f0eadc;--cellhi:#e4d8bd;--accent:#8a5a14;--shadow:0 6px 24px rgba(0,0,0,.18)}
@media (prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece6d8;--muted:#a39b8a;--line:#383229;--card:#201d18;--cell:#2b261f;--cellhi:#3a3328;--accent:#e0a64a;--shadow:0 6px 24px rgba(0,0,0,.6)}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:780px;margin:0 auto;padding:16px 16px 80px}
.asc{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:0 -16px 18px;padding:8px 16px;
  background:var(--bg);border-bottom:1px solid var(--line)}
.asc label{font-weight:600}
.asc select{font:inherit;color:var(--fg);background:var(--card);border:1px solid var(--line);border-radius:6px;padding:4px 8px}
.asc .hint{color:var(--muted);font-size:.85rem}
.mech{margin:0 0 26px}
.mech h2{margin:0 0 4px}
.mech .unl{color:var(--muted);margin:0 0 6px}
.mech h3{margin:10px 0 2px;color:var(--accent)}
.tcard{float:right;width:min(270px,100%);margin:0 0 8px 14px;border:8px solid transparent;border-image:url(assets/ui/trim/Steel.png) 8 fill / 8px / 0 stretch;image-rendering:pixelated;padding:2px 6px;color:#ece6d8}
.tcard .top{display:flex;align-items:center;gap:8px}
.tcard img{width:50px;height:50px;image-rendering:pixelated}
.tcard p{margin:4px 0 0}
@media (max-width:700px){.tcard{float:none;margin:0 0 8px;width:100%}}
.mech p{margin:0 0 6px;white-space:pre-line}
.mech ul.items{margin:0 0 6px;padding-left:0}
.mech ul.items li{margin:0 0 2px;padding-left:16px;position:relative}
.mech ul.items li::before{content:"";position:absolute;left:3px;top:.62em;width:5px;height:5px;border-radius:50%;background:currentColor;opacity:.7}
.mech .formula{padding:2px 0;overflow-wrap:anywhere}
.mech ul.vars{margin:2px 0 6px}
.mech ul.vars li{margin:0}
.mech ul.vars b{display:inline;font-family:inherit;font-size:inherit}
.empty{color:var(--muted)}
/*SEARCH_CSS*/
</style>
</head>
<body>
<main>
<nav><a href="index.html">Home</a><a href="unlocks.html" aria-current="page">Unlocks</a></nav>
<h1>Unlocks</h1>
<div class="asc"><label for="asc">Ascension</label><select id="asc"></select>
<span class="hint">The mechanics that are unlocked at the chosen Ascension.</span></div>
<div id="root"></div>
</main>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var DATA = JSON.parse(document.getElementById('data').textContent), MAXA = DATA.max;
  var root=document.getElementById('root'), sel=document.getElementById('asc'), ASC=0;
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  function math(tex, node){
    if(window.katex){ try{ katex.render('\\displaystyle '+tex,node,{throwOnError:false,displayMode:false}); return; }catch(e){} }
    node.textContent=tex;
  }
  function apply(){
    root.textContent='';
    var list=DATA.mechanics.filter(function(m){ return m.asc===ASC; });
    if(!list.length){ root.appendChild(el('p','empty','No mechanics have been added for Ascension '+ASC+' yet.')); return; }
    list.forEach(function(m){
      var s=el('section','mech'), h=el('h2',null,m.name), inner=el('div');
      s.appendChild(h);
      if(m.card){
        var c=el('div','tcard'), top=el('div','top'), im=el('img'); im.src='assets/icons/'+m.card.icon; im.alt='';
        top.appendChild(im); top.appendChild(el('b',null,m.card.name)); c.appendChild(top); c.appendChild(el('p',null,m.card.text)); inner.appendChild(c);
      }
      (m.unlock||[]).forEach(function(u){ inner.appendChild(el('p','unl',u)); });
      (m.sections||[]).forEach(function(c){
        if(c.title) inner.appendChild(el('h3',null,c.title));
        if(c.text) inner.appendChild(el('p',null,c.text));
        (c.formulas||[]).forEach(function(f){
          var d=el('div','formula'); math(f.latex,d); inner.appendChild(d);
          if(f.vars){ var ul=el('ul','vars'); f.vars.forEach(function(v){ var li=el('li'), b=el('b'); math(v[0],b); li.appendChild(b); li.appendChild(document.createTextNode(' — '+v[1])); ul.appendChild(li); }); inner.appendChild(ul); }
        });
        if(c.after) inner.appendChild(el('p',null,c.after));
        (c.lists||[]).forEach(function(l){
          if(l.title) inner.appendChild(el('p',null,l.title));
          var ul=el('ul','items'); l.items.forEach(function(t){ ul.appendChild(el('li',null,t)); }); inner.appendChild(ul);
        });
      });
      s.appendChild(inner); root.appendChild(s);
      foldable(s, h, inner, m.name);
    });
  }
  for(var a=0;a<=MAXA;a++){ var o=el('option',null,String(a)); o.value=String(a); sel.appendChild(o); }
  try{ var saved=parseInt(localStorage.getItem('rg-unlocks-ascension'),10); if(saved>=0 && saved<=MAXA) ASC=saved; }catch(e){}
  sel.value=String(ASC);
  sel.addEventListener('change',function(){ ASC=parseInt(sel.value,10); try{ localStorage.setItem('rg-unlocks-ascension',String(ASC)); }catch(e){} apply(); });
  enhanceSelects();      // the game-font drop-down of the shared snippet
  apply();
  window.addEventListener('load', apply);
/*SEARCH_JS*/
})();
</script>
</body>
</html>
'''
import search_snippet
html = search_snippet.apply(html.replace('__DATA__', data), '')
open(os.path.join(ROOT, 'docs', 'unlocks.html'), 'w', encoding='utf8').write(html)
print('docs/unlocks.html', len(html) // 1024, 'KB;', len(d['mechanics']), 'mechanics')
