"""Generate docs/mechanics.html (every mechanic, one section each) and docs/unlocks-a0.html ... unlocks-a4.html (what is unlocked at each Ascension)
from data/unlocks.json (hand-written).

    python -I tools/build_unlocks_page.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
d = json.load(open(os.path.join(ROOT, 'data', 'unlocks.json'), encoding='utf8'))
MAXA = d['max_ascension']

html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/bg.css"><script src="assets/bg.js" defer></script>
<title>__TITLE__</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<style>
:root{--bg:#fbfaf7;--fg:#1f1c17;--muted:#6b655a;--line:#ddd6c8;--card:#fff;--cell:#f0eadc;--cellhi:#e4d8bd;--accent:#8a5a14;--shadow:0 6px 24px rgba(0,0,0,.18)}
@media (prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece6d8;--muted:#a39b8a;--line:#383229;--card:#201d18;--cell:#2b261f;--cellhi:#3a3328;--accent:#e0a64a;--shadow:0 6px 24px rgba(0,0,0,.6)}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:780px;margin:0 auto;padding:16px 16px 80px}
.sub{color:var(--muted);margin:0 0 18px}
.mech{margin:0 0 26px}
.mech h2{margin:0 0 4px}
.mech .unl{color:var(--muted);margin:0 0 6px}
.mech a,ul.items a{color:var(--accent)}
.mech h3{margin:10px 0 2px;color:var(--accent)}
.cell{position:relative;float:right;width:89px;height:89px;margin:0 0 8px 14px;border:1px solid var(--line);border-radius:8px;background:var(--cell);padding:3px;
  display:flex;align-items:center;justify-content:center;cursor:default;font:inherit;color:inherit}
.cell:hover,.cell:focus-visible{background:var(--cellhi);outline:2px solid var(--accent);outline-offset:-1px}
.cell img{max-width:100%;max-height:100%;image-rendering:pixelated;pointer-events:none}
@media (max-width:700px){.cell{float:none;margin:0 0 8px}}
#tip{position:fixed;z-index:50;width:min(400px,calc(100vw - 16px));padding:10px 12px;border-radius:8px;background:var(--card);
  border:1px solid var(--line);box-shadow:var(--shadow);pointer-events:none;display:none;font-size:.92rem}
#tip b{display:block;font-size:1rem}
#tip p{margin:2px 0 0;white-space:pre-line}
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
<nav><a href="index.html">Home</a><a href="__FILE__" aria-current="page">Codex</a></nav>
<h1>__TITLE__</h1>
<p class="sub">__SUB__</p>
<div id="root"></div>
</main>
<div id="tip" role="tooltip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var DATA = JSON.parse(document.getElementById('data').textContent), ASC = __ASC__, MODE = '__MODE__';
  var root=document.getElementById('root');
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  function math(tex, node){
    if(window.katex){ try{ katex.render('\\displaystyle '+tex,node,{throwOnError:false,displayMode:false}); return; }catch(e){} }
    node.textContent=tex;
  }
  var tip=document.getElementById('tip');
  function hideTip(){ tip.style.display='none'; }
  function showTip(card, anchor){
    tip.textContent=''; tip.appendChild(el('b',null,card.name)); tip.appendChild(el('p',null,card.text));
    tip.style.display='block';
    var a=anchor.getBoundingClientRect(), t=tip.getBoundingClientRect();
    var x=Math.min(Math.max(8,a.left+a.width/2-t.width/2),innerWidth-t.width-8);
    var up=a.top-t.height-8>=8, y=up?a.top-t.height-8:a.bottom+8;
    tip.className=up?'above':'below'; tip.style.setProperty('--ax',Math.min(Math.max(a.left+a.width/2-x,24),t.width-24)+'px');
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }
  window.addEventListener('scroll',hideTip,{passive:true});
  function apply(){
    root.textContent='';
    if(MODE==='unlocks'){
      var ul0=el('ul','items');
      DATA.mechanics.filter(function(m){ return m.asc===ASC; }).forEach(function(m){
        var li=el('li'), a=el('a',null,m.name); a.href=m.href; li.appendChild(a);
        if(m.unlock && m.unlock.length) li.appendChild(document.createTextNode(' — '+m.unlock[0]));
        ul0.appendChild(li);
      });
      if(!ul0.children.length) root.appendChild(el('p','empty','No mechanics have been added for Ascension '+ASC+' yet.')); else root.appendChild(ul0);
      return;
    }
    var list=DATA.mechanics;
    list.forEach(function(m){
      var s=el('section','mech'), h=el('h2',null,m.name), inner=el('div'); s.id=m.id;
      s.appendChild(h);
      if(m.card){
        var c=el('button','cell'), im=el('img'); c.type='button'; im.src='assets/icons/'+m.card.icon; im.alt=m.card.name; c.appendChild(im);
        c.addEventListener('mouseenter',function(){ showTip(m.card,c); }); c.addEventListener('focus',function(){ showTip(m.card,c); });
        c.addEventListener('mouseleave',hideTip); c.addEventListener('blur',hideTip);
        inner.appendChild(c);
      }
      (m.unlock||[]).forEach(function(u){ inner.appendChild(el('p','unl',u)); });
      (m.sections||[]).forEach(function(c){
        if(c.title) inner.appendChild(el('h3',null,c.title));
        if(c.text) inner.appendChild(el('p',null,c.text));
        (c.formulas||[]).forEach(function(f){
          var d=el('div','formula'); math(f.latex,d); inner.appendChild(d);
          if(f.vars){ var ul=el('ul','vars'); f.vars.forEach(function(v){ var li=el('li'), b=el('b'); math(v[0],b); li.appendChild(b); li.appendChild(document.createTextNode(' — '+v[1])); ul.appendChild(li); }); inner.appendChild(ul); }
        });
        if(c.link){ var lp=el('p'), la=el('a',null,c.link.text); la.href=c.link.href; lp.appendChild(la); inner.appendChild(lp); }
        if(c.after) inner.appendChild(el('p',null,c.after));
        (c.lists||[]).forEach(function(l){
          if(l.title) inner.appendChild(el('p',null,l.title));
          var ul=el('ul','items'); l.items.forEach(function(t){ ul.appendChild(el('li',null,t)); }); inner.appendChild(ul);
        });
      });
      s.appendChild(inner); root.appendChild(s);
      foldable(s, h, inner, m.name);
    });
    var tgt=location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));      // a link to a mechanic opens its section
    if(tgt){ if(!tgt.classList.contains('open')) tgt.querySelector('h2').click(); tgt.scrollIntoView(); }
  }
  apply();
  window.addEventListener('load', apply);
/*SEARCH_JS*/
})();
</script>
</body>
</html>
'''
import search_snippet
hrefs = dict(search_snippet.mechanics_list())
for m in d['mechanics']:
    m['id'] = search_snippet.mech_slug(m['name'])
    m['href'] = hrefs[m['name']]


def write(fn, title, sub, mode, asc, mechs):
    data = json.dumps({'mechanics': mechs}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\/')
    page = html.replace('__DATA__', data).replace('__TITLE__', title).replace('__SUB__', sub).replace('__FILE__', fn).replace('__MODE__', mode).replace('__ASC__', str(asc))
    page = search_snippet.apply(page, '', fn).replace('<title>' + title + '</title>', '<title>Realm Grinder ' + title + '</title>')
    open(os.path.join(ROOT, 'docs', fn), 'w', encoding='utf8').write(page)


write('mechanics.html', 'Mechanics', 'How the game mechanics work. Under each name is when it becomes available.', 'mechanics', 0, d['mechanics'])
for a in range(MAXA + 1):
    write(f'unlocks-a{a}.html', f'Unlocks (Ascension {a})', f'What is unlocked at Ascension {a}.', 'unlocks', a, d['mechanics'])
print(f'docs/mechanics.html, docs/unlocks-a0..a{MAXA}.html;', len(d['mechanics']), 'mechanics')
