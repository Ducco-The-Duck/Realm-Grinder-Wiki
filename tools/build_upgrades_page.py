"""Generate docs/upgrades.html from data/upgrades_secret.json.

    python -I tools/build_upgrades_page.py
"""
import json, os, re, shutil
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
secret = json.load(open(os.path.join(ROOT, 'data', 'upgrades_secret.json'), encoding='utf8'))
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


def item(u):
    forms = []
    for p in u['description']:
        for f in p['formulas']:
            forms.append({'l': f['latex'], 'v': f['vars'], 'lb': effect_label(p['text']), 's': p['s']})
    if len(forms) == 1: forms[0]['lb'] = None
    return {
        'n': u['name'], 'i': icon_file(u['icon']),
        'd': [{'t': p['text'], 's': p['s']} for p in u['description']], 'f': forms,
        's': [f"{s['kind']}: {s['name']}" for s in u['sources']],
        'o': u['conditions'], 'lo': u['asc_min'], 'hi': u['asc_max'],
    }


secret_items = [item(u) for u in sorted(secret, key=lambda u: u['order'])]
sections = [
    {'id': 'allegiances', 'name': 'Allegiances Upgrades', 'items': None},
    {'id': 'misc', 'name': 'Misc Upgrades', 'items': None},
    {'id': 'magic', 'name': 'Magic Upgrades', 'items': None},
    {'id': 'buildings', 'name': 'Buildings Upgrades', 'items': None},
    {'id': 'secret', 'name': 'Secret Upgrades', 'items': secret_items},
]
json.dump(icons, open(os.path.join(ROOT, 'data', 'icons.json'), 'w'), indent=0, sort_keys=True)
data = json.dumps({'max': meta['max_ascension'], 'sections': sections}, ensure_ascii=False,
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
</style>
</head>
<body>
<main>
<nav><a href="index.html">Home</a><a href="trophies.html">Trophies</a><a href="archaeology.html">Archaeology</a><a href="research.html">Research</a><a href="challenges.html">Challenges</a><a href="upgrades.html" aria-current="page">Upgrades</a></nav>
<h1>Upgrades</h1>
<p class="sub">Hover an upgrade for what it does and what unlocks it. Only the Secret upgrades are filled in so far.</p>
<div class="pen-note"><b>Ascension penalty.</b> From Ascension 1 on, the game reduces the percentage effects of many upgrades. If an upgrade's
value is <i>v</i> (in %), the effect you get is <span id="pen-formula"></span>, where <i>k</i> is the number of <span class="mark">A</span>
marks on the upgrade: <span class="mark">A</span> is <i>k</i>&nbsp;=&nbsp;1 (exponent 0.1), <span class="mark">AA</span> is <i>k</i>&nbsp;=&nbsp;2
(exponent 0.01), <span class="mark">AAA</span> is <i>k</i>&nbsp;=&nbsp;3 (exponent 0.001), and so on, so more As means a harsher penalty.
The marks follow the Ascension chosen below. Most are reduced from Ascension 1, so <i>k</i> equals the Ascension number; some start later
and have fewer As, or none, at a given Ascension. Upgrades without a mark are not reduced. The formulas in the hover popups are always
the base values <i>v</i>.</div>
<div class="bar">
  <div class="row"><label for="asc"><b>Ascension</b></label><select id="asc"></select>
  <span class="hint">The A marks and the greyed-out upgrades (not available in it) follow the chosen Ascension.</span></div>
  <div class="row" id="filter"><b>Show</b></div>
</div>
<div id="root"></div>
</main>
<div id="tip" role="tooltip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var DATA = JSON.parse(document.getElementById('data').textContent);
  var SECTIONS = DATA.sections, MAXA = DATA.max, ASC = 0, cells = [];
  var root=document.getElementById('root'), tip=document.getElementById('tip'), filter=document.getElementById('filter'), sel=document.getElementById('asc');
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  function math(tex, host){
    if(window.katex){ try{ katex.render('\\displaystyle '+tex, host, {throwOnError:false}); return; }catch(e){} }
    host.textContent = tex;
  }
  function As(k){ return new Array(k+1).join('A'); }
  function penalty(it){
    var k=0; it.d.forEach(function(p){ if(p.s && ASC>=p.s) k=Math.max(k, ASC-p.s+1); });
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
          else suf=' · Ascension penalty (from Ascension '+f.s+')';
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
    if(it.o.length) tip.appendChild(el('div','faction','Can only be bought when '+it.o.join(' and ')+'.'));
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
    if(it.s.length){
      tip.appendChild(el('span','lbl','Unlock requirement'));
      var ul=el('ul'); it.s.forEach(function(s){ ul.appendChild(el('li',null,s)); }); tip.appendChild(ul);
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

  var saved={};
  try{ saved=JSON.parse(localStorage.getItem('upgrade-sections')||'{}')||{}; }catch(e){}
  SECTIONS.forEach(function(s){
    var on = s.items ? (saved[s.id]!==false) : false;
    var lab=el('label', s.items ? '' : 'off');
    var cb=el('input'); cb.type='checkbox'; cb.checked=on; cb.disabled=!s.items;
    lab.appendChild(cb);
    lab.appendChild(document.createTextNode(s.name.replace(' Upgrades','')+(s.items ? ' ('+s.items.length+')' : ' (not filled in yet)')));
    filter.appendChild(lab);
    if(!s.items) return;
    var sec=el('section'); sec.hidden=!on;
    var h=el('h2',null,s.name); h.appendChild(el('small',null,s.items.length+' upgrades')); sec.appendChild(h);
    var g=el('div','grid');
    s.items.forEach(function(it){
      var b=el('button','cell'); b.type='button'; b.setAttribute('aria-label', it.n);
      if(it.i){ var img=el('img'); img.src='assets/icons/'+encodeURIComponent(it.i); img.alt=''; img.loading='lazy'; b.appendChild(img); }
      b.addEventListener('mouseenter',function(){ showTip(it,b); });
      b.addEventListener('mouseleave',hideTip);
      b.addEventListener('focus',function(){ showTip(it,b); });
      b.addEventListener('blur',hideTip);
      b.addEventListener('click',function(e){ e.stopPropagation(); showTip(it,b); });
      g.appendChild(b); cells.push([b,it]);
    });
    sec.appendChild(g); root.appendChild(sec);
    cb.addEventListener('change',function(){
      sec.hidden=!cb.checked; hideTip();
      saved[s.id]=cb.checked;
      try{ localStorage.setItem('upgrade-sections', JSON.stringify(saved)); }catch(e){}
    });
  });
  function apply(){
    cells.forEach(function(p){
      var na=unavailable(p[1]), k=na?0:penalty(p[1]), b=p[0].querySelector('.pen');
      p[0].classList.toggle('na', na);
      if(k){ if(!b){ b=el('span','pen'); p[0].appendChild(b); } b.textContent=As(k); }
      else if(b){ b.remove(); }
    });
    hideTip();
  }
  for(var a=0;a<=MAXA;a++){ var o=el('option',null,String(a)); o.value=String(a); sel.appendChild(o); }
  try{ var sv=parseInt(localStorage.getItem('rg-ascension'),10); if(sv>=0 && sv<=MAXA) ASC=sv; }catch(e){}
  sel.value=String(ASC);
  sel.addEventListener('change',function(){ ASC=parseInt(sel.value,10); try{ localStorage.setItem('rg-ascension',String(ASC)); }catch(e){} apply(); });
  apply();
  document.addEventListener('DOMContentLoaded',function(){
    math('\\left(\\left(1+\\frac{v}{100}\\right)^{0.1^{k}}-1\\right)\\cdot 100\\,\\%', document.getElementById('pen-formula'));
  });
})();
</script>
</body>
</html>
'''
html = html.replace('__DATA__', data)
open(os.path.join(ROOT, 'docs', 'upgrades.html'), 'w', encoding='utf8').write(html)
print('docs/upgrades.html', len(html) // 1024, 'KB;', len(secret_items), 'secret upgrades;',
      sum(1 for i in secret_items if i['i']), 'with icon')
