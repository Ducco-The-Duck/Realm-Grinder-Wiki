"""Generate docs/research.html from data/research.json (+ data/research_meta.json).

    python -I tools/build_research_page.py
"""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
research = json.load(open(os.path.join(ROOT, 'data', 'research.json'), encoding='utf8'))
meta = json.load(open(os.path.join(ROOT, 'data', 'research_meta.json')))
sprites = json.load(open(os.path.join(ROOT, 'data', 'sprites.json')))
icons = json.load(open(os.path.join(ROOT, 'data', 'icons.json')))
icon_dir = os.path.join(ROOT, 'docs', 'assets', 'icons')
os.makedirs(icon_dir, exist_ok=True)


def icon_file(name):
    """Copy the sprite into docs/assets/icons if needed and return its file name."""
    if name not in sprites: return None
    dst = os.path.basename(sprites[name][0]['file'])
    path = os.path.join(icon_dir, dst)
    if not os.path.exists(path):
        src = os.path.join(ROOT, sprites[name][0]['file'])
        if os.path.exists(src): shutil.copy(src, path)
    if not os.path.exists(path): return None
    icons[name] = dst
    return dst


# where extra research slots come from (read from the game's slot function); branch index -> data
SLOT_UPGRADE = {0: 'Magician', 1: 'Artisan', 2: 'Demigod', 3: 'Businessman', 4: 'Apothecary', 5: 'Warlord'}
MERC_ALIGN = {0: 'Good', 2: 'Good', 3: 'Evil', 5: 'Evil', 1: 'Neutral', 4: 'Neutral'}
NEUTRAL_AFFINITY = {0: 'Faceless', 1: 'Titan', 2: 'Faceless', 3: 'Druid', 4: 'Druid', 5: 'Titan'}
BASE_FACTION = {0: 'Fairy', 1: 'Elf', 2: 'Angel', 3: 'Goblin', 4: 'Undead', 5: 'Demon'}


def slot_sources(b):
    """[delta, text, from Ascension, until Ascension (exclusive)]; the page keeps the rows of the chosen Ascension"""
    rows = [
        ['-1', 'Mercenary', 1, 2],
        ['+1', f'Secret Trophy: {SLOT_UPGRADE[b]}', 0, 2],
        ['+1', 'Reincarnation Power, R90+', 1, 2],
        ['+1', f'Reincarnation Power, R75+ ({MERC_ALIGN[b]} Mercenary)', 1, 2],
        ['+1', f'Ancient Device Power ({NEUTRAL_AFFINITY[b]})', 0, 2],
    ]
    if b == 1:
        rows.append(['+2', 'Legacy of the Dwarven Kings', 0, 2])
    if b == 5:
        rows.append(['+2', 'Dark Light of Bondelnar', 0, 2])
    # Dwarf is the prestige faction of the Good base factions, Drow of the Evil ones, so only one of the two applies
    rows.append(['+1', f"{'Legacy of the Dwarven Kings' if b < 3 else 'Dark Light of Bondelnar'} ({BASE_FACTION[b]})", 0, 2])
    rows.append(['+1 or more', 'Archon Bloodline', 2, 3])
    return rows


BRANCHES = []
for b in range(7):
    its = sorted((r for r in research if r['branch'] == b), key=lambda r: (r['number'], r['index']))
    if not its: continue
    name = its[0]['branch_name']
    bicon = icon_file('Research' + name)
    items = []
    for r in its:
        items.append({
            'n': r['name'], 'k': f"{r['code']} · {name} {r['number']:,}", 'i': icon_file(f"Research{r['number']}"), 'b': bicon,
            'd': r['description'], 'q': r['requirements'], 'h': r['hint'],
            'u': r['unavailable_from'], 'm': r['mercenary_exception'],
            'fn': r['faction_name'], 'fk': r['faction_kind'], 'fc': meta['faction_colors'].get(str(r['faction'])),
            'mn': r['mercenary_note'], 'al': r['alignment_lock'], 'an': r['alignment_not'],
            'ac': meta['alignment_colors'].get(r['alignment_lock'] or ''),
            'a': {k: {'d': v['description'], 'q': v['requirements']} for k, v in r['by_ascension'].items()},
            'f': [{'l': f['latex'], 'v': f['vars'], 's': f.get('scale'), 'lb': f.get('label')} for f in r['formulas']],
        })
    BRANCHES.append({'name': name, 'icon': bicon, 'items': items, 'sl': slot_sources(b) if b in SLOT_UPGRADE else None})

json.dump(icons, open(os.path.join(ROOT, 'data', 'icons.json'), 'w'), indent=0, sort_keys=True)
payload = {'max': meta['max_ascension'], 'branches': BRANCHES}
data = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
total = sum(len(b['items']) for b in BRANCHES)

html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/bg.css"><script src="assets/bg.js" defer></script>
<title>Realm Grinder Research</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<style>
:root{--bg:#fbfaf7;--fg:#1f1c17;--muted:#6b655a;--line:#ddd6c8;--card:#fff;--cell:#f0eadc;--cellhi:#e4d8bd;--accent:#8a5a14;--shadow:0 6px 24px rgba(0,0,0,.18)}
@media (prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece6d8;--muted:#a39b8a;--line:#383229;--card:#201d18;--cell:#2b261f;--cellhi:#3a3328;--accent:#e0a64a;--shadow:0 6px 24px rgba(0,0,0,.6)}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:760px;margin:0 auto;padding:16px 16px 80px}
nav{display:flex;gap:14px;margin:0 0 18px;font-size:.95rem}
nav a{color:var(--muted);text-decoration:none}
nav a[aria-current]{color:var(--fg);font-weight:600;border-bottom:2px solid var(--accent)}
h1{margin:0 0 4px;font-size:1.7rem}
.sub{color:var(--muted);margin:0 0 12px}
.asc{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:0 -16px 18px;padding:8px 16px;
  background:var(--bg);border-bottom:1px solid var(--line)}
.asc label{font-weight:600}
.asc select{font:inherit;color:var(--fg);background:var(--card);border:1px solid var(--line);border-radius:6px;padding:4px 8px}
.asc .hint{color:var(--muted);font-size:.85rem}
section{margin:0 0 26px}
h2{font-size:1.05rem;margin:0 0 8px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h2 small{font-weight:400;color:var(--muted);margin-left:8px}
.grid{display:grid;grid-template-columns:repeat(10,1fr);gap:4px}
.cell{position:relative;aspect-ratio:1;border:1px solid var(--line);border-radius:6px;background:var(--cell);padding:2px;
  display:flex;align-items:center;justify-content:center;cursor:default;font:inherit;color:inherit}
.cell.buy{grid-column:1 / span 2;grid-row:1 / span 2;aspect-ratio:auto;border-radius:10px;padding:6px}
.cell:hover,.cell:focus-visible{background:var(--cellhi);outline:2px solid var(--accent);outline-offset:-1px}
.cell img{max-width:100%;max-height:100%;image-rendering:pixelated;pointer-events:none}
.cell img.ov{position:absolute;inset:0;margin:auto;width:100%;height:100%;object-fit:contain}
.cell.na{opacity:.35;filter:grayscale(1)}
.cell.fac{background:var(--fc);border-color:rgba(255,255,255,.22)}
.cell.fac:hover,.cell.fac:focus-visible{background:var(--fc);filter:brightness(1.5)}
#tip .faction{margin-top:6px;display:flex;gap:6px;align-items:baseline;font-size:.88rem}
#tip .faction .sw{flex:none;width:10px;height:10px;border-radius:3px;border:1px solid var(--line)}
.cell .pen{position:absolute;z-index:2;top:1px;right:2px;font:700 .6rem/1 system-ui,sans-serif;letter-spacing:-.02em;color:#fff;
  background:#a3341f;padding:1px 3px;border-radius:4px;pointer-events:none}
.pen-note{margin:0 0 14px;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);font-size:.92rem}
.pen-note .mark{font-weight:700;color:#fff;background:#a3341f;padding:0 4px;border-radius:4px}
#tip{position:fixed;z-index:50;width:min(420px,calc(100vw - 16px));padding:10px 12px;border-radius:8px;background:var(--card);
  border:1px solid var(--line);box-shadow:var(--shadow);pointer-events:none;display:none;font-size:.92rem}
#tip b{display:block;font-size:1rem}
#tip .num{color:var(--muted);font-size:.8rem}
#tip .lbl{display:block;color:var(--accent);font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;margin-top:8px}
#tip .desc{white-space:pre-line}
#tip ul{margin:2px 0 0;padding-left:18px}
#tip .more,#tip .hint{color:var(--muted)}
#tip .mark{font-weight:700;color:#fff;background:#a3341f;padding:0 4px;border-radius:4px;font-size:.8em}
#tip .flabel{margin-top:6px;font-weight:600}
#tip ul.vars{list-style:none;padding-left:0;margin:4px 0}
#tip ul.vars li{margin:2px 0}
#tip .formula{padding:2px 0;overflow-wrap:anywhere}
#tip .fsep{border-top:1px solid var(--line);margin:8px 0 2px}
/*SEARCH_CSS*/
</style>
</head>
<body>
<main>
<nav><a href="index.html">Home</a><a href="trophies.html">Trophies</a><a href="archaeology.html">Archaeology</a><a href="research.html" aria-current="page">Research</a><a href="challenges.html">Challenges</a><a href="upgrades.html">Upgrades</a></nav>
<h1>Research</h1>
<p class="sub">__TOTAL__ researches in __BRANCHES__ branches, in the in-game order (by research number). Hover a research for what it does, its formula and its requirements. The large icon is where you buy research points for the branch.</p>
<div class="pen-note"><b>Ascension penalty.</b> From Ascension 1 on, the game reduces most percentage effects. If a research's formula
gives <i>v</i> (in %), the effect you get is <span id="pen-formula"></span>, where <i>k</i> is the number of <span class="mark">A</span>
marks on the research: <span class="mark">A</span> is <i>k</i>&nbsp;=&nbsp;1 (exponent 0.1), <span class="mark">AA</span> is <i>k</i>&nbsp;=&nbsp;2
(exponent 0.01), <span class="mark">AAA</span> is <i>k</i>&nbsp;=&nbsp;3 (exponent 0.001), and so on, so more As means a harsher penalty.
The marks follow the Ascension chosen below. Most researches are reduced from Ascension 1, so <i>k</i> equals the Ascension number; a few
start later and have fewer As, or none, at a given Ascension. Researches without a mark are not reduced. The formulas in the hover
popups are always the base values <i>v</i>.</div>
<div class="asc"><label for="asc">Ascension</label><select id="asc"></select>
<span class="hint">The A marks and the greyed-out researches (not available in it) follow the chosen Ascension.</span></div>
<!--SEARCH_BAR-->
<div id="root"></div>
</main>
<div id="tip" role="tooltip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var DATA = JSON.parse(document.getElementById('data').textContent);
  var BRANCHES = DATA.branches, MAXA = DATA.max;
  var root=document.getElementById('root'), tip=document.getElementById('tip'), sel=document.getElementById('asc');
  var ASC = 0, cells = [];
/*SEARCH_JS*/
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  function math(tex, node){
    if(window.katex){ try{ katex.render('\\displaystyle '+tex,node,{throwOnError:false,displayMode:false}); return; }catch(e){} }
    node.textContent=tex;
  }
  function penalty(it){
    var k=0; (it.f||[]).forEach(function(f){ if(f.s && ASC>=f.s) k=Math.max(k, ASC-f.s+1); });
    return k;
  }
  function unavailable(it){ return it.u!==null && it.u!==undefined && ASC>=it.u; }
  function textFor(it){
    var cur={d:it.d,q:it.q}, ks=Object.keys(it.a||{}).map(Number).sort(function(a,b){return a-b;});
    ks.forEach(function(k){ if(k<=ASC) cur=it.a[k]; });
    return cur;
  }
  function showTip(it, anchor){
    tip.textContent='';
    if(it.sl){
      if(ASC>=3){ hideTip(); return; }
      tip.appendChild(el('b',null,it.n+' research slots'));
      tip.appendChild(el('div',null,'Base: '+(ASC>=2?1:4)+(ASC>=2?' slot':' slots')));
      var rows=it.sl.filter(function(r){ return ASC>=r[2] && ASC<r[3]; });
      if(rows.length){
        var ulS=el('ul');
        rows.forEach(function(r){ var li=el('li'); li.appendChild(el('b',null,r[0]+' ')); li.appendChild(document.createTextNode(r[1])); ulS.appendChild(li); });
        tip.appendChild(ulS);
      }
      if(ASC===2) tip.appendChild(el('div','more','Faction researches do not count towards the slots.'));
      place(anchor); return;
    }
    tip.appendChild(el('b',null,it.n));
    if(it.k) tip.appendChild(el('div','num',it.k));
    if(it.al || it.an){
      var al=el('div','faction'), sw2=el('span','sw'); sw2.style.background=it.ac||'transparent'; al.appendChild(sw2);
      al.appendChild(document.createTextNode(it.al ? 'Can only be bought while your alignment is '+it.al+'.'
                                                   : 'Cannot be bought while your alignment is '+it.an+'.'));
      tip.appendChild(al);
    }
    if(it.fn){
      var fl=el('div','faction'), sw=el('span','sw'); sw.style.background=it.fc||'transparent'; fl.appendChild(sw);
      fl.appendChild(document.createTextNode(it.fn+' research. Can only be bought '+
        (it.fk==='prestige' ? 'when '+it.fn+' is your prestige faction.' : 'when playing as '+it.fn+'.')+
        (it.mn ? ' '+it.mn : '')));
      tip.appendChild(fl);
    }
    var t=textFor(it);
    if(it.nobuy){ place(anchor); return; }
    if(unavailable(it)){
      tip.appendChild(el('span','lbl','Not available'));
      tip.appendChild(el('div',null,'This research is not available in Ascension '+ASC+'.'+(it.m?' (Mercenaries may be an exception.)':'')));
      if(t.d){ tip.appendChild(el('span','lbl','What it does')); tip.appendChild(el('div','desc',t.d)); }
      place(anchor); return;
    }
    if(t.d){
      tip.appendChild(el('span','lbl','What it does'));
      var dd=el('div','desc',t.d), pk0=penalty(it);
      if(pk0 && it.f && it.f.length===1){ dd.appendChild(document.createTextNode(' ')); dd.appendChild(el('span','mark',new Array(pk0+1).join('A'))); }
      tip.appendChild(dd);
    }
    if(it.f && it.f.length){
      tip.appendChild(el('span','lbl',it.f.length>1?'Formulas':'Formula'));
      var anyScaled=it.f.length>1 && it.f.some(function(f){ return f.s; });
      it.f.forEach(function(f,i){
        if(i>0) tip.appendChild(el('div','fsep'));
        var vs = it.f.length>1 ? 'v_{'+(i+1)+'}' : 'v';
        var tex=f.l.replace(/^v = /, vs+' = ');
        if(f.lb){
          var lab=el('div','flabel'); var lm=el('span'); math(vs,lm); lab.appendChild(lm);
          var suf='', badge=null;
          if(anyScaled){
            if(!f.s) suf='';
            else if(ASC>=f.s){ suf=' · '; badge=el('span','mark',new Array(ASC-f.s+2).join('A')); }
          }
          lab.appendChild(document.createTextNode(' — '+f.lb+suf)); if(badge) lab.appendChild(badge); tip.appendChild(lab);
        }
        var d=el('div','formula'); var m=el('span'); math(tex,m); d.appendChild(m); tip.appendChild(d);
        var ul=el('ul','vars');
        f.v.forEach(function(v){ var li=el('li'); var b=el('b'); b.style.display='inline'; math(v.symbol,b); li.appendChild(b); li.appendChild(document.createTextNode(' — '+v.text)); ul.appendChild(li); });
        tip.appendChild(ul);
      });
      tip.appendChild(el('div','more','v is the base value, before any Ascension penalty.'));
    }
    if(it.h){ tip.appendChild(el('span','lbl','Hint')); tip.appendChild(el('div','hint',it.h)); }
    if(t.q && t.q.length){
      tip.appendChild(el('span','lbl','Unlock requirement'));
      var ul2=el('ul'); t.q.forEach(function(q){ ul2.appendChild(el('li',null,q)); }); tip.appendChild(ul2);
    }
    place(anchor);
  }
  function place(anchor){
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
  function cell(it, cls){
    var b=el('button','cell'+(cls?' '+cls:'')); b.type='button'; b.setAttribute('aria-label', it.n);
    if(it.d!=null){ var ds=[it.n,it.k,it.h,it.d,it.fn]; Object.keys(it.a||{}).forEach(function(k){ ds.push(it.a[k].d); }); b._s=normS(ds.join(' ')); }
    if(it.fc || it.ac){ b.classList.add('fac'); b.style.setProperty('--fc', it.fc || it.ac); }
    var tn=trimName(it.fn); if(tn) b.classList.add('t-'+tn);
    function add(file, c){ var img=el('img',c); img.src='assets/icons/'+encodeURIComponent(file); img.alt=''; img.loading='lazy'; b.appendChild(img); }
    if(it.b){ add(it.b); if(it.i) add(it.i,'ov'); } else if(it.i){ add(it.i); }
    function show(){ showTip(it,b); }
    b.addEventListener('mouseenter',show);
    b.addEventListener('mouseleave',hideTip);
    b.addEventListener('focus',show);
    b.addEventListener('blur',hideTip);
    b.addEventListener('click',function(e){ e.stopPropagation(); show(); });
    return b;
  }
  BRANCHES.forEach(function(br){
    var sec=el('section'); var h=el('h2',null,br.name); h.appendChild(el('small',null,br.items.length+' researches')); sec.appendChild(h);
    var g=el('div','grid');
    g.appendChild(cell({n:br.name, i:br.icon, nobuy:true, sl:br.sl},'buy'));
    br.items.forEach(function(it){ var c=cell(it,''); cells.push([c,it]); g.appendChild(c); });
    var inner=el('div'); inner.appendChild(g); foldable(sec, h, inner, br.name);
    root.appendChild(sec);
  });
  searchInit(root);
  function apply(){
    cells.forEach(function(p){
      var na=unavailable(p[1]), k=na?0:penalty(p[1]), b=p[0].querySelector('.pen');
      p[0].classList.toggle('na', na);
      if(k){ if(!b){ b=el('span','pen'); p[0].appendChild(b); } b.textContent=new Array(k+1).join('A'); }
      else if(b){ b.remove(); }
    });
    hideTip();
  }
  for(var a=0;a<=MAXA;a++){ var o=el('option',null,String(a)); o.value=String(a); sel.appendChild(o); }
  try{ var saved=parseInt(localStorage.getItem('rg-ascension'),10); if(saved>=0 && saved<=MAXA) ASC=saved; }catch(e){}
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
import search_snippet
html = html.replace('__DATA__', data).replace('__TOTAL__', str(total)).replace('__BRANCHES__', str(len(BRANCHES)))
html = search_snippet.apply(html, 'Search research names, hints and descriptions')
open(os.path.join(ROOT, 'docs', 'research.html'), 'w', encoding='utf8').write(html)
print('docs/research.html', len(html) // 1024, 'KB;', [(b['name'], len(b['items'])) for b in BRANCHES],
      'no icon:', sum(1 for b in BRANCHES for it in b['items'] if not it['i']), '| max Ascension', meta['max_ascension'])
