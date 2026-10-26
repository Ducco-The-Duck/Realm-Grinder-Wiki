"""Generate docs/effects.html from data/effect_tags.json: a search over what every upgrade, research and challenge does.

    python -I tools/build_effects_page.py

Three boxes: the overall search (everything an effect says), X (what the effect changes) and Y (what it is based on).
The tags come from tools/effect_tags.py.
"""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
tags = json.load(open(os.path.join(ROOT, 'data', 'effect_tags.json'), encoding='utf8'))
sprites = json.load(open(os.path.join(ROOT, 'data', 'sprites.json')))
BUILD = json.load(open(os.path.join(ROOT, 'data', 'buildings.json'), encoding='utf8'))
icon_dir = os.path.join(ROOT, 'docs', 'assets', 'icons')
SRC = {'upgrade': 'Upgrade', 'research': 'Research', 'challenge': 'Challenge'}


def icon_file(n):
    if not n or n not in sprites: return None
    dst = os.path.basename(sprites[n][0]['file'])
    path = os.path.join(icon_dir, dst)
    if not os.path.exists(path):
        src = os.path.join(ROOT, sprites[n][0]['file'])
        if os.path.exists(src): shutil.copy(src, path)
    return dst if os.path.exists(path) else None


def clean_tags(lst):
    return [t.lstrip('?') for t in lst]


objs = []
for key, o in tags.items():
    if not o['effects']: continue
    mask = sum(1 << a for a in o['asc'])
    effs = [{'t': e['text'], 'x': clean_tags(e['x']), 'y': clean_tags(e['y']), 'm': e['mode'], 'g': e['trigger'], 'v': e['verb'],
             **({'sc': e['scope']} if e['scope'] else {}), **({'s': e['seconds']} if e['seconds'] else {})} for e in o['effects']]
    objs.append({'k': key, 'n': o['name'], 's': SRC[o['src']], 'i': icon_file(o['icon']), 'p': o['page'], 'a': mask, 'e': effs})
bnames = sorted({(b.get('name_plural') or b['name']).lower() for b in BUILD})
data = json.dumps({'objs': objs, 'buildings': bnames}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/bg.css"><script src="assets/bg.js" defer></script>
<title>Realm Grinder Effects</title>
<style>
:root{--bg:#fbfaf7;--fg:#1f1c17;--muted:#6b655a;--line:#ddd6c8;--card:#fff;--cell:#f0eadc;--cellhi:#e4d8bd;--accent:#8a5a14;--shadow:0 6px 24px rgba(0,0,0,.18)}
@media (prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece6d8;--muted:#a39b8a;--line:#383229;--card:#201d18;--cell:#2b261f;--cellhi:#3a3328;--accent:#e0a64a;--shadow:0 6px 24px rgba(0,0,0,.6)}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:760px;margin:0 auto;padding:16px 16px 80px}
nav{display:flex;gap:14px;flex-wrap:wrap;margin:0 0 18px;font-size:.95rem}
nav a{color:var(--muted);text-decoration:none}
nav a[aria-current]{color:var(--fg);font-weight:600;border-bottom:2px solid var(--accent)}
h1{margin:0 0 4px;font-size:1.7rem}
.asc{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:0 0 12px}
.asc label{font-weight:600}
.asc select{font:inherit;color:var(--fg);background:var(--card);border:1px solid var(--line);border-radius:6px;padding:4px 8px}
.asc .hint{color:var(--muted);font-size:.85rem}
.boxes{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0 0 6px}
.boxes .full{grid-column:1/-1}
.boxes label{display:block;font-size:.78rem;color:var(--muted);margin:0 0 2px}
.boxes input{width:100%;font:inherit;color:var(--fg);background:var(--card);border:1px solid var(--line);border-radius:6px;padding:7px 10px}
.types{display:flex;gap:14px;flex-wrap:wrap;margin:6px 0 12px;font-size:.9rem}
.count{color:var(--muted);font-size:.9rem;margin:0 0 10px}
.res{display:flex;gap:10px;padding:9px 10px;margin:0 0 6px;border:1px solid var(--line);border-radius:8px;background:var(--card);cursor:pointer;color:inherit;text-decoration:none}
.res:hover,.res:focus-visible{background:var(--cellhi);outline:none}
.res .ic{flex:none;width:44px;height:44px;border:1px solid var(--line);border-radius:8px;background:var(--cell);display:flex;align-items:center;justify-content:center}
.res .ic img{max-width:100%;max-height:100%;image-rendering:pixelated}
.res .body{min-width:0;flex:1}
.res .nm{font-weight:600}
.res .src{color:var(--muted);font-size:.8rem;margin-left:8px;font-weight:400}
.res .fx{margin:3px 0 0;font-size:.9rem}
.res .fx .tags{display:flex;gap:4px;flex-wrap:wrap;margin-top:2px}
.chip{font-size:.72rem;padding:0 6px;border-radius:9px;border:1px solid var(--line);background:var(--cell);color:var(--muted)}
.chip.x{border-color:var(--accent);color:var(--accent)}
.chip.y{border-color:#4a7ea8;color:#4a7ea8}
.chip.m{border-style:dashed}
.res .more{color:var(--muted);font-size:.8rem;margin-top:3px}
.res.na{opacity:.4}
#tip{position:fixed;z-index:50;width:min(460px,calc(100vw - 16px));padding:10px 12px;border-radius:8px;background:var(--card);
  border:1px solid var(--line);box-shadow:var(--shadow);pointer-events:none;display:none;font-size:.92rem}
#tip b.t{display:block;font-size:1rem}
#tip .kind{display:block;color:var(--muted);font-size:.82rem}
#tip .e{margin:7px 0 0;padding-top:6px;border-top:1px solid var(--line)}
#tip .e.hit{border-left:3px solid var(--accent);padding-left:7px}
#tip .tags{display:flex;gap:4px;flex-wrap:wrap;margin-top:3px}
#tip .more{color:var(--muted);margin-top:8px;font-size:.85rem}
/*SEARCH_CSS*/
</style>
</head>
<body>
<main>
<nav><a href="index.html">Home</a><a href="trophies.html">Trophies</a><a href="archaeology.html">Archaeology</a><a href="research.html">Research</a><a href="challenges.html">Challenges</a><a href="upgrades.html">Upgrades</a><a href="effects.html" aria-current="page">Effects</a></nav>
<h1>Effects</h1>
<div class="asc"><label for="asc">Ascension</label><select id="asc"></select>
<span class="hint">Only what is available in the chosen Ascension is listed.</span></div>
<div class="boxes">
  <div class="full"><label for="qa">Search everything</label><input id="qa" type="search" placeholder="Any word of an effect, its stat, what it is based on, or its name" autocomplete="off"></div>
  <div><label for="qx">Changes (X)</label><input id="qx" type="search" placeholder="e.g. faction coin find chance" autocomplete="off"></div>
  <div><label for="qy">Based on (Y)</label><input id="qy" type="search" placeholder="e.g. assistants owned" autocomplete="off"></div>
</div>
<div class="types"><label><input type="checkbox" id="tu" checked> Upgrades</label><label><input type="checkbox" id="tr" checked> Research</label><label><input type="checkbox" id="tc" checked> Challenges</label></div>
<div class="count" id="count"></div>
<div id="root"></div>
</main>
<div id="tip" role="tooltip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var DATA = JSON.parse(document.getElementById('data').textContent);
  var root=document.getElementById('root'), tip=document.getElementById('tip'), sel=document.getElementById('asc'), count=document.getElementById('count');
  var ASC = 0, LIMIT = 150;
/*SEARCH_JS*/
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  var BL = DATA.buildings.join(' ');
  var MODE = {additive:'additive additively', multiplicative:'multiplicative multiplicatively'};
  // what each box looks at in an effect (lower case, no accents); built once
  DATA.objs.forEach(function(o){
    o.nm = normS(o.n);
    o.e.forEach(function(e){
      var hasAll = (e.sc||[]).some(function(s){ return s==='all' || s==='other'; });
      e.hx = normS(e.x.join(' ') + ' ' + (MODE[e.m]||'') + ' ' + (e.v==='reduce'?'reduce':'increase') + (hasAll ? ' ' + BL : ''));     // an effect on all buildings is also found by one building's name
      e.hy = normS(e.y.join(' '));
      e.ha = normS(o.n + ' ' + e.t + ' ' + e.x.join(' ') + ' ' + e.y.join(' ') + ' ' + (e.g||'') + ' ' + (MODE[e.m]||''));
    });
  });
  function terms(s){ return normS(s).split(/\s+/).filter(Boolean).map(function(t){ return FCODES.hasOwnProperty(t) ? FCODES[t] : t; }); }
  function all(h, T){ return T.every(function(t){ return h.indexOf(t)>=0; }); }
  function chips(parent, e){
    var d=el('div','tags');
    e.x.forEach(function(t){ d.appendChild(el('span','chip x',t)); });
    e.y.forEach(function(t){ d.appendChild(el('span','chip y',t)); });
    if(e.m) d.appendChild(el('span','chip m',e.m));
    parent.appendChild(d);
  }
  // the simple tooltip: used while the page's own tooltip is not ready (see below)
  function showTip(o, hits, anchor){
    tip.textContent='';
    tip.appendChild(el('b','t',o.n)); tip.appendChild(el('span','kind',o.s + ' · ' + o.p.replace('.html','').replace('upgrades-','upgrades: ')));
    var av=[]; for(var a=0;a<=4;a++) if(o.a>>a&1) av.push(a);
    o.e.forEach(function(e){
      var d=el('div','e'+(hits.indexOf(e)>=0?' hit':'')); d.appendChild(el('div',null,e.t)); chips(d,e); tip.appendChild(d);
    });
    tip.appendChild(el('div','more',(av.length===5 ? 'Available in every Ascension' : 'Available in Ascension ' + av.join(', ')) + '. Click to open it on its page.'));
    tip.style.display='block';
    var r=anchor.getBoundingClientRect(), t=tip.getBoundingClientRect();
    var x=Math.min(Math.max(8,r.left+30), window.innerWidth-t.width-8);
    var y=r.bottom+6; if(y+t.height>window.innerHeight-8) y=Math.max(8,r.top-t.height-6);
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }
  // the page's own tooltip: the page of the object is loaded in a hidden frame (in its embed mode, see embedInit in search_snippet.py) and asked
  // to draw the tooltip of that object; the frame is then shown next to the result. The frames load when first needed.
  var FR={}, cur=null, seq=0;
  function frameFor(page){
    if(FR[page]) return FR[page];
    var f=document.createElement('iframe'); f.src=page+'#embed'; f.setAttribute('aria-hidden','true'); f.tabIndex=-1; f.title='';
    f.style.cssText='position:fixed;left:-9999px;top:0;width:520px;height:1100px;border:0;background:transparent;pointer-events:none;z-index:60';
    document.body.appendChild(f);
    return FR[page]={f:f, ready:false};
  }
  function hideAll(){
    tip.style.display='none';
    Object.keys(FR).forEach(function(k){ FR[k].f.style.left='-9999px'; if(FR[k].ready) FR[k].f.contentWindow.postMessage({rg:'tip', hide:true}, location.origin); });
  }
  function ask(){
    var c=cur, fr=FR[c.o.p];
    fr.f.contentWindow.postMessage({rg:'tip', id:c.id, key:c.o.k, name:c.o.n, asc:ASC}, location.origin);
  }
  window.addEventListener('message', function(ev){
    var m=ev.data; if(!m) return;
    if(m.rg==='tipready'){
      Object.keys(FR).forEach(function(k){ if(FR[k].f.contentWindow===ev.source) FR[k].ready=true; });
      if(cur && FR[cur.o.p].ready && !cur.shown) ask();
    } else if(m.rg==='tipsize' && cur && m.id===cur.id){
      var fr=FR[cur.o.p];
      if(!m.ok){ showTip(cur.o, cur.hits, cur.a); return; }
      tip.style.display='none';
      fr.f.style.width=m.w+'px'; fr.f.style.height=m.h+'px';
      var r=cur.a.getBoundingClientRect();
      var x=Math.min(Math.max(0,r.left+20), window.innerWidth-m.w);
      var y=r.bottom-2; if(y+m.h>window.innerHeight) y=Math.max(0,r.top-m.h+2);
      fr.f.style.left=x+'px'; fr.f.style.top=y+'px'; cur.shown=true;
    }
  });
  function hover(o, hits, a){
    hideAll();
    cur={o:o, hits:hits, a:a, id:++seq, shown:false};
    var fr=frameFor(o.p);
    if(fr.ready) ask(); else showTip(o, hits, a);      // not loaded yet: the simple tooltip meanwhile
  }
  function hideTip(){ cur=null; hideAll(); }
  var qa=document.getElementById('qa'), qx=document.getElementById('qx'), qy=document.getElementById('qy');
  var tu=document.getElementById('tu'), tr=document.getElementById('tr'), tc=document.getElementById('tc');
  function render(){
    var A=terms(qa.value), X=terms(qx.value), Y=terms(qy.value);
    root.textContent=''; hideTip();
    var types={Upgrade:tu.checked, Research:tr.checked, Challenge:tc.checked};
    var found=[];
    DATA.objs.forEach(function(o){
      if(!types[o.s] || !(o.a>>ASC&1)) return;
      var hits=o.e.filter(function(e){ return (!A.length || all(e.ha,A)) && (!X.length || all(e.hx,X)) && (!Y.length || (e.y.length && all(e.hy,Y))); });
      if(hits.length) found.push([o,hits]);
    });
    if(!A.length && !X.length && !Y.length){ count.textContent = found.length+' upgrades, researches and challenges with an effect in Ascension '+ASC+'. Type in a box above to narrow them down.'; }
    else count.textContent = found.length + (found.length===1?' result':' results') + (found.length>LIMIT?' (the first '+LIMIT+' are shown)':'');
    found.slice(0,LIMIT).forEach(function(f){
      var o=f[0], hits=f[1];
      var a=el('a','res'); a.href=o.p+'#q='+encodeURIComponent(o.n);
      var ic=el('div','ic'); if(o.i){ var img=el('img'); img.src='assets/icons/'+encodeURIComponent(o.i); img.alt=''; img.loading='lazy'; ic.appendChild(img); }
      a.appendChild(ic);
      var b=el('div','body'), nm=el('div','nm',o.n); nm.appendChild(el('span','src',o.s)); b.appendChild(nm);
      hits.slice(0,3).forEach(function(e){ var d=el('div','fx'); d.appendChild(el('div',null,e.t)); chips(d,e); b.appendChild(d); });
      if(hits.length>3) b.appendChild(el('div','more','and '+(hits.length-3)+' more matching effects'));
      a.appendChild(b);
      a.addEventListener('mouseenter',function(){ hover(o,hits,a); }); a.addEventListener('mouseleave',hideTip);
      a.addEventListener('focus',function(){ hover(o,hits,a); }); a.addEventListener('blur',hideTip);
      root.appendChild(a);
    });
  }
  for(var i=0;i<=4;i++){ var op=el('option',null,String(i)); op.value=String(i); sel.appendChild(op); }
  try{ var saved=parseInt(localStorage.getItem('rg-ascension'),10); if(saved>=0 && saved<=4) ASC=saved; }catch(e){}
  sel.value=String(ASC);
  enhanceSelects();
  sel.addEventListener('change',function(){ ASC=parseInt(sel.value,10); try{ localStorage.setItem('rg-ascension',String(ASC)); }catch(e){} render(); });
  [qa,qx,qy,tu,tr,tc].forEach(function(n){ n.addEventListener(n.type==='checkbox'?'change':'input', render); });
  var h=location.hash.match(/^#(qa|qx|qy)=(.*)$/); if(h) document.getElementById(h[1]).value=decodeURIComponent(h[2]);
  render();
})();
</script>
</body>
</html>
'''
import search_snippet
html = html.replace('__DATA__', data)
html = search_snippet.apply(html, '', 'effects.html').replace('<div class="search"><input id="q" type="search" placeholder="" autocomplete="off" aria-label="Search"><span class="qn" id="qn"></span></div>', '')
open(os.path.join(ROOT, 'docs', 'effects.html'), 'w', encoding='utf8').write(html)
print('docs/effects.html', len(html) // 1024, 'KB;', len(objs), 'objects,', sum(len(o['e']) for o in objs), 'effects')
