"""Search bar shared by the page builders: CSS, the input, and the JS that filters `.cell` buttons.

A page sets `cell._s` (lower-case, accent-free text of what the game shows for the item: name, hint, flavor
text, description) on every cell it wants searchable, then calls `searchInit(root)` once the cells exist.
`qmatch(text)` tells whether a normalised text matches the current query (used to filter stack popups).
"""

CSS = r'''
html.embed,html.embed body{background:transparent!important}
html.embed main,html.embed nav,html.embed #more,html.embed .gv,html.embed #bgfx{display:none!important}
html.embed body::before,html.embed body::after{display:none!important}
/* the game's icon frames, generated from the sprites by frame_css.py (plain borders and gradients, no images) */
/*FRAMES*/
.cell img,.cell img.ov{position:absolute;inset:auto;margin:0;left:50%;top:50%;transform:translate(-50%,-50%);width:calc(100% + 4px);height:calc(100% + 4px);
  max-width:none;max-height:none;object-fit:contain;image-rendering:pixelated}
.cell:hover,.cell:focus-visible,.cell.fac:hover{background:none;outline:none;box-shadow:none;filter:brightness(1.15)}
.cell.fac{background:none;border-color:transparent}
.cell.na{opacity:.35;filter:grayscale(1)}
.cell.na:hover{filter:grayscale(1) brightness(1.2)}
.badge{z-index:3}

/* section headers are dropdowns */
section.dd h2{display:flex;align-items:baseline;gap:8px;cursor:pointer;user-select:none}
section.dd h2:hover{color:var(--accent)}
section.dd h2 .chev{margin-left:auto;align-self:center;width:9px;height:9px;margin-right:6px;border-right:2px solid var(--muted);border-bottom:2px solid var(--muted);
  transform:translateY(-3px) rotate(45deg);transition:transform .3s ease}
section.dd.open h2 .chev{transform:translateY(2px) rotate(-135deg)}
.dd-body{display:grid;grid-template-rows:0fr;opacity:0;transition:grid-template-rows .45s ease,opacity .3s ease}
.dd.open .dd-body,body.searching .dd .dd-body{grid-template-rows:1fr;opacity:1}
.dd-in{overflow:hidden;min-height:0}
@keyframes ddcell{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:none}}      /* no slide: the folded body clips whatever leaves its box, which cut off the top frames */
.dd-in.casc .cell{animation:ddcell .34s ease both;animation-delay:calc(var(--i,0) * 9ms)}
/* the game's own fonts: Liony Bold for headings, names and labels, Liony Regular for everything else */
@font-face{font-family:"Liony";src:url(assets/fonts/Liony-Regular.ttf) format("truetype");font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"Liony";src:url(assets/fonts/Liony-Bold.ttf) format("truetype");font-weight:700;font-style:normal;font-display:swap}
html{font-size:30px}
body{font-family:"Liony",system-ui,-apple-system,"Segoe UI",sans-serif;font-size:1rem;line-height:1.12;letter-spacing:.01em}
main{max-width:780px}
#tip{width:min(620px,calc(100vw - 16px))}
#tip b.t,#tip>b:first-child{display:block;font-size:1.3em;line-height:1.1;margin-bottom:2px}
#pop h3,#more h3{font-size:1.25em}
#pop .card{width:min(620px,100%)}
#more .card{width:min(640px,100%)}
h1,h2,h3,b,strong,#tip b.t,#tip .lbl,#more .lbl,#tip .flabel,#more .flabel,#pop h3,#more h3,.subh,.bar b,nav a[aria-current],.mark{font-family:"Liony",system-ui,sans-serif;font-weight:700}
input,select,button,textarea,option,optgroup{font-family:"Liony",system-ui,sans-serif;font-size:1rem}
select option{font-family:"Liony",system-ui,sans-serif}
/* tighter tooltips and popups */
.katex{font-size:.9em}
#tip{padding:7px 12px;line-height:1.2}
#tip .lbl{margin-top:5px}
#tip p{margin:2px 0 0}
#tip ul{margin:1px 0 0}
#tip .faction{margin-top:3px}
#tip .formula{padding:1px 0}
#tip ul.vars{margin:2px 0}
#tip ul.vars li{margin:0}
#tip ul.vars b{display:inline;font-family:inherit;font-size:inherit}
#tip>span:not(.lbl){display:block;line-height:1.05}
#tip em{margin-top:1px;line-height:1.05}
#tip>b:first-child{margin-bottom:0}
#tip .flabel{margin-top:3px}
#tip .fsep{margin:4px 0 1px}
#tip .cost{margin-top:0}
#more .bonus{padding:5px 0}
#more .bonus p{margin:0 0 1px}
#more .formula{padding:0}
#more ul.vars{margin:1px 0}
#pop .card,#more .card{padding:10px 12px}
/* the Upgrades entry of the nav drops down to the four upgrade pages */
.dd-nav{position:relative;display:flex}
.dd-nav>a{display:block}
#tip>b+.more{margin-top:0;margin-bottom:2px}
/* dark scrollbars (the default one flashes white on hover) */
*{scrollbar-width:thin;scrollbar-color:#4a443a transparent}
::-webkit-scrollbar{width:10px;height:10px;background:transparent}
::-webkit-scrollbar-thumb{background:#4a443a;border-radius:5px}
::-webkit-scrollbar-thumb:hover{background:#6a6150}
::-webkit-scrollbar-track,::-webkit-scrollbar-corner{background:transparent}
.dd-nav .dd-menu{display:none;position:absolute;top:100%;left:-10px;z-index:70;min-width:210px;padding:6px;background:var(--card);
  border:1px solid var(--line);border-radius:10px;box-shadow:var(--shadow);flex-direction:column;gap:2px}
.dd-nav:hover .dd-menu,.dd-nav:focus-within .dd-menu,.dd-nav.open .dd-menu{display:flex}
.dd-nav .dd-menu a{padding:5px 10px;border:0;border-radius:6px;white-space:nowrap}
.dd-nav .dd-menu a:hover{background:var(--cell);color:var(--fg)}
.dd-nav .dd-menu a[aria-current]{background:var(--cellhi);border:0}
/* the game's tooltip border (black_SteelTrim, 9-slice 8 px) instead of rounded corners; used on one page so far */
body.steel #tip,body.steel #pop .card,body.steel #more .card{border:8px solid transparent;border-radius:0;background:none;box-shadow:none;
  border-image:url(assets/ui/trim/Steel.png) 8 fill / 8px / 0 stretch;image-rendering:pixelated;padding:0 6px;
  --fg:#ece6d8;--muted:#a39b8a;--accent:#e0a64a;--line:#4a443a;--card:#201d18;--cell:#2b261f;--cellhi:#3a3328;color:#ece6d8}
sup{font-size:.62em;line-height:0;vertical-align:.5em;font-family:inherit}
body.steel .pen-note,body.steel .search input{border:8px solid transparent;border-radius:0;background:none;
  border-image:url(assets/ui/trim/Steel.png) 8 fill / 8px / 0 stretch;image-rendering:pixelated;color:#ece6d8;
  --fg:#ece6d8;--muted:#a39b8a;--accent:#e0a64a}
body.steel .search input{padding:0 8px}
body.steel #tip{overflow:visible;line-height:1.15}
body.steel #more header{background:transparent;margin-top:0}
/* popups close by clicking outside them or with Escape: no Close button */
#pop button.x,#more button.x{display:none}
#pop .card.narrow{width:auto;max-width:min(330px,100%);margin:0 auto}
body.steel #pop .card.narrow{padding:0 12px 18px}
#pop .card.narrow header{margin-bottom:12px}
body.steel #tip .lbl{margin-top:3px}
body.steel #tip p{margin:1px 0 0}
body.steel .cs>button,body.steel .cs ul{border:8px solid transparent;border-radius:0;background:none;
  border-image:url(assets/ui/trim/Steel.png) 8 fill / 8px / 0 stretch;image-rendering:pixelated;color:#ece6d8;
  --fg:#ece6d8;--muted:#a39b8a;--cellhi:#3a3328}
body.steel .cs>button{padding:0 30px 0 6px}
body.steel .cs ul{box-shadow:none}
/* no bullets anywhere; the A marks on icons are small and in the game's font */
ul{list-style:none;padding-left:0}
li::marker{content:""}
.cell .pen{font-family:"Liony",system-ui,sans-serif;font-weight:700;font-size:.58rem;line-height:1;padding:1px 4px;border-radius:3px;letter-spacing:0;top:auto;bottom:3px;right:3px}
/* less vertical air everywhere */
main{padding-top:10px;padding-bottom:40px}
nav{margin:0 0 6px}
h1{margin:0 0 2px}
.sub{margin:0 0 6px;line-height:1.12}
.pen-note{margin:0 0 6px;padding:3px 8px;line-height:1.12}
.search{margin:0 0 6px}
.bar{padding:2px 16px;gap:0;margin-bottom:6px}
.bar .row{gap:2px 14px}
section{margin:0 0 10px}
h2{margin:0 0 3px;padding-bottom:2px}
.subh{margin:6px 0 3px}
.grid{gap:4px}
/* drop-downs drawn by the page, so that they use the game's font (the browser's own list does not) */
.cs{position:relative;display:inline-block}
.cs>button{font:inherit;color:var(--fg);background:var(--card);border:1px solid var(--line);border-radius:6px;padding:1px 28px 1px 10px;
  cursor:pointer;text-align:left;position:relative;min-width:3ch;line-height:1.2}
.cs>button::after{content:"";position:absolute;right:10px;top:50%;width:7px;height:7px;border-right:2px solid var(--muted);
  border-bottom:2px solid var(--muted);transform:translateY(-70%) rotate(45deg)}
.cs ul{position:absolute;z-index:80;left:0;top:100%;margin:2px 0 0;padding:4px;list-style:none;background:var(--card);
  border:1px solid var(--line);border-radius:8px;box-shadow:var(--shadow);max-height:55vh;overflow:auto;min-width:100%;display:none}
.cs.open ul{display:block}
.cs li{padding:1px 10px;border-radius:5px;cursor:pointer;white-space:nowrap;line-height:1.25}
.cs li:hover,.cs li.sel{background:var(--cellhi)}
.cs.dis>button{opacity:.5;cursor:default}
.search{margin:0 0 16px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.search input{flex:1 1 220px;min-width:0;font:inherit;color:var(--fg);background:var(--card);border:1px solid var(--line);border-radius:8px;padding:7px 10px}
.search input:focus{outline:2px solid var(--accent);outline-offset:-1px}
.search .qn{color:var(--muted);font-size:.9rem}
/* the search box is as wide as the notes box; the result count sits inside it */
.search{position:relative;display:block}
.search input{display:block;width:100%;box-sizing:border-box;padding-right:96px}
body.steel .search input{padding:0 96px 0 8px}
.search .qn{position:absolute;right:16px;top:50%;transform:translateY(-50%);pointer-events:none}
.sx{display:none!important}
'''
from frame_css import frame_css
CSS = CSS.replace('/*FRAMES*/', frame_css())

BAR = ('<div class="search"><input id="q" type="search" placeholder="__PLACEHOLDER__" autocomplete="off" '
       'aria-label="Search"><span class="qn" id="qn"></span></div>')

JS = r'''
  // (only used by the unfinished Effects page, see data/EFFECT_SEARCH_NOT_IN_USE.md)
  // embed mode (#embed): the Effects page loads this page in a hidden frame and asks for the tooltip of one object, so that it shows this
  // page's own tooltip. show(message, anchor) draws it (and says whether the object was found); setAsc(n) switches the Ascension.
  function embedInit(show, setAsc, cellOf){
    if(location.hash!=='#embed') return;
    document.documentElement.classList.add('embed');
    var t=document.getElementById('tip'), anchor=document.createElement('div');
    anchor.style.cssText='position:fixed;left:12px;top:12px;width:1px;height:1px'; document.body.appendChild(anchor);
    function say(o){ o.rg='tipsize'; parent.postMessage(o, location.origin); }
    window.addEventListener('message', function(ev){
      var m=ev.data;
      if(m && m.rg==='cells'){      // the cells (icons) of several objects, as drawn on this page at that Ascension
        var out={};
        try{ setAsc(m.asc); }catch(e){}
        m.items.forEach(function(i){ try{ var c=cellOf && cellOf(i); out[i.key]=c ? c.outerHTML : ''; }catch(e){ out[i.key]=''; } });
        parent.postMessage({rg:'cellsout', asc:m.asc, cells:out}, location.origin);
        return;
      }
      if(!m || m.rg!=='tip') return;
      if(m.hide){ t.style.display='none'; return; }
      var ok=false;
      try{ if(m.asc!=null) setAsc(m.asc); ok=show(m, anchor); }catch(e){ ok=false; }
      if(!ok){ say({id:m.id, ok:false}); return; }
      t.style.left='10px'; t.style.top='10px';
      var r=t.getBoundingClientRect(); say({id:m.id, ok:true, w:Math.ceil(r.width)+20, h:Math.ceil(r.height)+20});
    });
    window.addEventListener('load', function(){ parent.postMessage({rg:'tipready'}, location.origin); });
  }
  var QT = [];
  // community faction codes: a code typed as a whole word searches for the faction name
  var FCODES = {fr:'fairy',el:'elven',an:'angel',gb:'goblin',ud:'undead',dm:'demon',tt:'titan',dd:'druid',fc:'faceless',
                dn:'dwarven',dw:'drow',dg:'dragon',ar:'archon',dj:'djinn',mk:'makers',mc:'mercenary'};
  function normS(s){ return String(s==null?'':s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,''); }
  // lines (from a list of strings) that name a faction, so an item can be found by the faction it belongs to
  var FNAMES = Object.keys(FCODES).map(function(k){ return FCODES[k]; });
  function facLines(list){ return (list||[]).filter(function(l){ var n=normS(l); return FNAMES.some(function(f){ return n.indexOf(f)>=0; }); }).join(' '); }

  // ---- foldable sections (header = dropdown) and icon frames
  var TRIMF={Fairy:1,Elven:1,Angel:1,Goblin:1,Undead:1,Demon:1,Titan:1,Druid:1,Faceless:1,Dwarven:1,Drow:1,Mercenary:1,Dragon:1,Archon:1,Djinn:1,Makers:1};
  function trimName(n){ n={Elf:'Elven',Dwarf:'Dwarven',Angel:'Angel'}[n]||n; return TRIMF[n] ? n : null; }
  // text of a variable explanation: the parts between $ ... $ are formulas, drawn in the formula font (shared by every page)
  function rich(parent, txt){
    txt.split('$').forEach(function(s,i){
      if(i%2){
        var sp=document.createElement('span');
        if(window.katex){ try{ katex.render(s, sp, {throwOnError:false}); }catch(e){ sp.textContent=s; } } else sp.textContent=s;
        parent.appendChild(sp);
      } else if(s) parent.appendChild(document.createTextNode(s));
    });
  }
  function foldable(sec, h, inner, key){
    var store={}, sk='fold:'+location.pathname;
    try{ store=JSON.parse(localStorage.getItem(sk)||'{}')||{}; }catch(e){}
    var open = store[key]!==false;
    var chev=document.createElement('span'); chev.className='chev'; h.appendChild(chev);
    h.tabIndex=0; h.setAttribute('role','button'); h.setAttribute('aria-expanded', String(open));
    var body=document.createElement('div'); body.className='dd-body';
    inner.classList.add('dd-in'); body.appendChild(inner); sec.appendChild(body);
    sec.classList.add('dd'); if(open) sec.classList.add('open');
    function toggle(){
      open=!open; sec.classList.toggle('open', open); h.setAttribute('aria-expanded', String(open));
      if(typeof hideTip==='function') hideTip();
      if(open){
        var cs=inner.querySelectorAll('.cell');
        for(var k=0;k<cs.length && k<90;k++) cs[k].style.setProperty('--i', k);
        inner.classList.add('casc'); setTimeout(function(){ inner.classList.remove('casc'); }, 1300);
      }
      store[key]=open;
      try{ localStorage.setItem(sk, JSON.stringify(store)); }catch(e){}
    }
    h.addEventListener('click', toggle);
    h.addEventListener('keydown', function(e){ if(e.key==='Enter' || e.key===' '){ e.preventDefault(); toggle(); } });
  }
  function enhanceSelects(){
    var proto=Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value');
    document.querySelectorAll('select').forEach(function(sel){
      if(sel._cs) return; sel._cs=1;
      var wrap=document.createElement('span'); wrap.className='cs';
      var btn=document.createElement('button'); btn.type='button';
      var ul=document.createElement('ul'); ul.setAttribute('role','listbox');
      sel.parentNode.insertBefore(wrap,sel); wrap.appendChild(btn); wrap.appendChild(ul); wrap.appendChild(sel); sel.style.display='none';
      function sync(){
        ul.textContent='';
        var cur=sel.options[sel.selectedIndex];
        btn.textContent=cur ? cur.textContent : '';
        Array.prototype.forEach.call(sel.options,function(o){
          var li=document.createElement('li'); li.textContent=o.textContent; if(o.value===proto.get.call(sel)) li.className='sel';
          li.addEventListener('click',function(e){
            e.stopPropagation(); proto.set.call(sel,o.value); sync(); wrap.classList.remove('open');
            sel.dispatchEvent(new Event('change'));
          });
          ul.appendChild(li);
        });
        wrap.classList.toggle('dis',sel.disabled); btn.disabled=sel.disabled;
      }
      Object.defineProperty(sel,'value',{get:function(){ return proto.get.call(sel); }, set:function(v){ proto.set.call(sel,v); sync(); }, configurable:true});
      new MutationObserver(sync).observe(sel,{childList:true,attributes:true,attributeFilter:['disabled']});
      btn.addEventListener('click',function(e){
        e.stopPropagation();
        var was=wrap.classList.contains('open');
        document.querySelectorAll('.cs.open').forEach(function(w){ w.classList.remove('open'); });
        if(!was && !sel.disabled) wrap.classList.add('open');
      });
      sync();
    });
    document.addEventListener('click',function(e){
      document.querySelectorAll('.cs.open').forEach(function(w){ w.classList.remove('open'); });
      document.querySelectorAll('.dd-nav.open').forEach(function(w){ if(!w.contains(e.target)) w.classList.remove('open'); });
    });
    document.addEventListener('keydown',function(e){ if(e.key==='Escape') document.querySelectorAll('.cs.open').forEach(function(w){ w.classList.remove('open'); }); });
  }
  // exponents written as superscript characters (10\u2076, x\u207b\u00b2) become real <sup> elements, so they are drawn in the page font
  var SUPMAP={'\u2070':'0','\u00b9':'1','\u00b2':'2','\u00b3':'3','\u2074':'4','\u2075':'5','\u2076':'6','\u2077':'7','\u2078':'8','\u2079':'9','\u207b':'-'};
  var SUPRE=/[\u2070\u00b9\u00b2\u00b3\u2074-\u2079\u207b]+/;
  function supify(root){
    var w=document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null), todo=[], n;
    while((n=w.nextNode())){
      if(SUPRE.test(n.nodeValue) && !(n.parentNode.closest && n.parentNode.closest('.katex,script,style'))) todo.push(n);
    }
    todo.forEach(function(t){
      var frag=document.createDocumentFragment(), txt=t.nodeValue, re=new RegExp(SUPRE.source,'g'), last=0, m;
      while((m=re.exec(txt))){
        if(m.index>last) frag.appendChild(document.createTextNode(txt.slice(last,m.index)));
        var sp=document.createElement('sup'); sp.textContent=m[0].replace(/./g,function(c){ return SUPMAP[c]||c; });
        frag.appendChild(sp); last=m.index+m[0].length;
      }
      if(last<txt.length) frag.appendChild(document.createTextNode(txt.slice(last)));
      t.parentNode.replaceChild(frag,t);
    });
  }
  new MutationObserver(function(ms){
    ms.forEach(function(m){ m.addedNodes.forEach(function(n){ if(n.nodeType===1) supify(n); else if(n.nodeType===3 && n.parentNode) supify(n.parentNode); }); });
  }).observe(document.body,{childList:true,subtree:true});
  document.addEventListener('DOMContentLoaded',function(){ supify(document.body); });
  function qmatch(s){ return !QT.length || QT.every(function(t){ return s.indexOf(t)>=0; }); }
  function searchInit(root, after){
    enhanceSelects();
    var box=document.getElementById('q'), note=document.getElementById('qn');
    var hq=location.hash.match(/^#q=(.*)$/); if(hq){ try{ box.value=decodeURIComponent(hq[1]); }catch(e){} }      // a link from the Effects page
    function run(){
      QT = normS(box.value).split(/\s+/).filter(Boolean).map(function(t){ return FCODES.hasOwnProperty(t) ? FCODES[t] : t; });
      var shown=0;
      root.querySelectorAll('.cell').forEach(function(c){
        var ok = qmatch(c._s||'');
        c.classList.toggle('sx', !ok); if(ok && !(QT.length && c.hasAttribute('data-un'))) shown++;
      });
      root.querySelectorAll('.grid').forEach(function(g){
        var any = !QT.length || !!g.querySelector('.cell:not(.sx)');
        g.classList.toggle('sx', !any);
        var p=g.previousElementSibling; if(p && p.classList.contains('subh')) p.classList.toggle('sx', !any);
      });
      root.querySelectorAll('section').forEach(function(s){
        s.classList.toggle('sx', QT.length>0 && !s.querySelector('.cell:not(.sx)'));
      });
      note.textContent = QT.length ? shown+(shown===1?' match':' matches') : '';
      document.body.classList.toggle('searching', QT.length>0);
      if(after) after();
    }
    box.addEventListener('input', run);
    run();
    return run;
  }
'''


UPGRADE_PAGES = [('upgrades-allegiance.html', 'Allegiance'), ('upgrades-magic.html', 'Magic'),
                 ('upgrades-secret.html', 'Secret'), ('upgrades-misc.html', 'Miscellaneous')]
CODEX = 'codex.html'      # key of the Codex tab (it has no page of its own)
CODEX_PAGES = [('mechanics.html', 'Mechanics')] + [(f'unlocks-a{a}.html', f'Unlocks (Ascension {a})') for a in range(5)]
DROPDOWNS = {'upgrades.html': UPGRADE_PAGES, CODEX: CODEX_PAGES}      # tab key -> its pages


def mech_slug(name):
    import re as _re
    return _re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def mechanics_list():
    """the mechanics of data/unlocks.json as (name, href): a mechanic with its own page ("page") links there, the others to their section of the Mechanics page"""
    import json, os
    d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'unlocks.json'), encoding='utf8'))
    return [(m['name'], m.get('page') or 'mechanics.html#' + mech_slug(m['name'])) for m in d['mechanics']]


HAT = '''<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 17.5h18v2.2H3z" fill="#f2b705" stroke="#3a2a00" stroke-width="1.1" stroke-linejoin="round"/><path d="M5 17.5a7 7 0 0 1 14 0z" fill="#f2b705" stroke="#3a2a00" stroke-width="1.1" stroke-linejoin="round"/><path d="M10.5 10.5V6.8h3v3.7z" fill="#d99a00" stroke="#3a2a00" stroke-width="1" stroke-linejoin="round"/></svg>'''      # the Under construction icon (a hard hat)
UNDER_CONSTRUCTION = '<div class="bugs"><p><b>Under construction:</b> this page is still being written and is not finished yet.</p></div>'


# the nav is the game's tab column laid out in a row: 72x62 button with the icon, the red ribbon (126x34) with the name on it
TABS = [('index.html', 'Home', 'UiBuildings', 0), ('upgrades.html', 'Upgrades', 'UiUpgrades', 0), ('trophies.html', 'Trophies', 'UiTrophies', -6),
        ('archaeology.html', 'Archaeology', 'UiExcavation', -6), ('research.html', 'Research', 'UiResearch', -3), ('challenges.html', 'Challenges', 'UiChallenges', -3), ('codex.html', 'Codex', 'UICrystalBall', 0)]

SMALL = ('UiUpgrades', 'UICrystalBall')

NAV_CSS = r'''/*NAVCSS*/
nav.tabs{display:flex;flex-wrap:wrap;justify-content:center;align-items:flex-start;gap:0;margin:0 0 12px;--s:1.15;border:0;padding:0}
nav.tabs .tab{position:relative;display:block;width:calc(92px*var(--s));height:calc(78px*var(--s));padding:0;border:0;margin:0;color:#fff;text-decoration:none;
  cursor:pointer;image-rendering:pixelated;font-weight:400;-webkit-tap-highlight-color:transparent}
/* the frame (the wiki's steel trim; gold for the open page), then the icon, then the ribbon with the name */
nav.tabs .tab::before{content:"";position:absolute;left:0;top:0;width:100%;height:calc(76px*var(--s));box-sizing:border-box;
  border:calc(8px*var(--s)) solid transparent;border-image:url(assets/ui/trim/Steel.png) 8 fill / calc(8px*var(--s)) / 0 stretch;image-rendering:pixelated}
nav.tabs .tab[aria-current]::before{border-image-source:url(assets/ui/trim/Gold.png)}
nav.tabs .tab:hover::before{border-image-source:url(assets/ui/trim/Gold_Hover.png)}
nav.tabs .tab::after{content:"";position:absolute;z-index:2;left:0;top:calc(44px*var(--s));width:100%;height:calc(34px*var(--s));
  box-sizing:border-box;border:solid transparent;border-width:0 calc(14px*var(--s));border-image:url(assets/ui/nav/redRibbon.png) 0 14 fill / 0 calc(14px*var(--s)) / 0 stretch;image-rendering:pixelated}
nav.tabs .tab.long::after{left:calc(-9px*var(--s));width:calc(100% + 18px*var(--s))}
nav.tabs .tab.long span.n{left:calc(-9px*var(--s));right:calc(-9px*var(--s))}
nav.tabs .tab[aria-current]::after{border-image-source:url(assets/ui/nav/redRibbon_Selected.png)}
nav.tabs .tab img{position:absolute;z-index:1;left:calc(14px*var(--s));top:calc((var(--y) + 2)*var(--s)*1px);width:calc(64px*var(--s));height:calc(64px*var(--s));image-rendering:pixelated;transform:scale(var(--z,1))}
nav.tabs .tab span.n{position:absolute;z-index:3;left:0;right:0;top:calc(48px*var(--s));height:calc(24px*var(--s));display:flex;align-items:center;justify-content:center;
  font-family:"Liony",system-ui,sans-serif;font-weight:700;font-size:calc(14px*var(--s));line-height:1;text-shadow:1px 1px 0 #3a1a14;white-space:nowrap}
nav.tabs .tab:hover img,nav.tabs .tab:focus-visible img{filter:brightness(1.25)}
nav.tabs .tab:hover::after{filter:brightness(1.2)}
nav.tabs .dd-nav{display:block;position:relative}
nav.tabs .dd-menu{display:none;position:absolute;z-index:70;flex-direction:column}
nav.tabs .dd-nav:hover .dd-menu,nav.tabs .dd-nav:focus-within .dd-menu,nav.tabs .dd-nav.open .dd-menu{display:flex}
nav.tabs .dd-nav .dd-menu{top:calc(78px*var(--s));left:50%;transform:translateX(-50%);min-width:0;border:8px solid transparent;border-radius:0;background:none;box-shadow:none;
  border-image:url(assets/ui/trim/Steel.png) 8 fill / 8px / 0 stretch;image-rendering:pixelated;padding:0 4px;gap:0;color:#ece6d8;--cell:#2b261f;--cellhi:#3a3328;--fg:#ece6d8}
nav.tabs .dd-item{position:relative;display:block}
nav.tabs .dd-nav .dd-menu .dd-item>a{display:flex;align-items:center;justify-content:space-between}
nav.tabs .dd-item>a::after{content:"";flex:none;margin-left:14px;border:5px solid transparent;border-left-color:currentColor;border-right-width:0;opacity:.7}
nav.tabs .dd-sub{display:none;position:absolute;left:calc(100% + 12px);top:-10px;flex-direction:column;padding:0 4px;border:8px solid transparent;
  border-image:url(assets/ui/trim/Steel.png) 8 fill / 8px / 0 stretch;image-rendering:pixelated}
nav.tabs .dd-sub::before{content:"";position:absolute;left:-26px;top:-8px;bottom:-8px;width:26px}      /* keeps the hover while the pointer crosses the menu's frame */
nav.tabs .dd-item:hover .dd-sub,nav.tabs .dd-item:focus-within .dd-sub{display:flex}
nav.tabs .dd-nav .dd-menu a{display:block;color:#ece6d8;font-size:1rem;padding:2px 12px;border-radius:4px;text-decoration:none;white-space:nowrap}
@media (max-width:700px){nav.tabs{display:grid;grid-template-columns:repeat(3,1fr);justify-items:center;--s:.85;gap:0}}
nav.tabs .tab .uc{position:absolute;z-index:4;right:calc(2px*var(--s));top:calc(2px*var(--s));width:calc(24px*var(--s));height:calc(24px*var(--s));pointer-events:none;filter:drop-shadow(0 1px 1px rgba(0,0,0,.7))}
nav.tabs .tab .uc svg{display:block;width:100%;height:100%}
nav.tabs .dd-menu .uc-note{display:flex;align-items:center;gap:8px;padding:2px 12px 4px;margin-bottom:2px;border-bottom:1px solid rgba(236,230,216,.25);color:#f2b705;font-size:.8rem;white-space:nowrap}
nav.tabs .dd-menu .uc-note svg{width:1.3em;height:1.3em}
.bugs p{margin:0 0 20px;padding:8px 12px;border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:6px;background:var(--card);font-size:.92rem}
/*ENDNAVCSS*/'''


def game_nav(current=None, current_file=None):
    """the nav: `current` is the href of the open page (an upgrade page counts as upgrades.html), `current_file` the upgrade page"""
    out = []
    for href, label, ic, y in TABS:
        cur = ' aria-current="page"' if href == current else ''
        lg = ' long' if len(label) > 10 else ''      # a longer name gets a ribbon a little wider than the frame
        z = ';--z:.84' if ic in SMALL else ''      # sprites that fill their whole square are drawn a little smaller so they stay inside the frame
        inner = f'<img src="assets/ui/nav/{ic}.png" alt="" style="--y:{4 + y}{z}"><span class="n">{label}</span>'
        if href == CODEX:      # the Codex is still being written
            inner += '<span class="uc">'+HAT+'</span>'
        if href in DROPDOWNS:
            def link(f, n):
                own = {h for _, h in mechanics_list() if '#' not in h}      # the pages of mechanics that have their own
                cur_ = f == current_file or (f == 'mechanics.html' and current_file in own)
                return f'<a href="{f}"' + (' aria-current="page"' if cur_ else '') + f'>{n}</a>'
            links = ''
            for f, n in DROPDOWNS[href]:
                if f == 'mechanics.html':      # hovering Mechanics opens the list of the mechanics
                    sub = ''.join(f'<a href="{h}">{mn}</a>' for mn, h in mechanics_list())
                    links += f'<span class="dd-item">{link(f, n)}<span class="dd-sub">{sub}</span></span>'
                else:
                    links += link(f, n)
            q = "'"
            if href == CODEX: links = '<span class="uc-note">'+HAT+'Under construction</span>' + links
            out.append(f'<span class="dd-nav"><a class="tab{lg}" role="button" tabindex="0"{cur} onclick="this.parentNode.classList.toggle({q}open{q})">{inner}</a>'
                       f'<span class="dd-menu">{links}</span></span>')
        else:
            out.append(f'<a class="tab{lg}" href="{href}"{cur}>{inner}</a>')
    return '<nav class="tabs">' + ''.join(out) + '</nav>'


def put_nav(html, current_file=None):
    """replace the page's `<nav>` by the game-style one (the open page is read from the old nav)"""
    import re as _re
    old = html[html.find('<nav'):html.find('</nav>')] if '<nav' in html else ''
    m = _re.search(r'<a (?:class="tab" )?href="([^"]+)"[^>]*aria-current="page"', old) or _re.search(r'<a [^>]*role="button"[^>]*(aria-current)', old)
    cur = (m.group(1) if m.group(1) != 'aria-current' else 'upgrades.html') if m else None
    if cur and (cur in [f for f, _ in CODEX_PAGES] or cur in [h for _, h in mechanics_list()]): cur, current_file = CODEX, current_file or cur      # the Codex pages
    return _re.sub(r'<nav[^>]*>.*?</nav>', lambda _: game_nav(cur, current_file), html, count=1, flags=_re.S)


GV_CSS = '.gv{margin-top:36px;text-align:center;font-size:18px;color:var(--muted);opacity:.7}'


def game_version():
    """the game build the pages were made from (out/VERSION, written by tools/extract.sh)"""
    import os
    try:
        return open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out', 'VERSION')).read().strip()
    except OSError:
        return ''


def stamp(html):
    """a small, faint "Game version X" line at the bottom of the page (replaces an earlier one)"""
    import re as _re
    v = game_version()
    html = _re.sub(r'<div class="gv">.*?</div>', '', html)
    html = _re.sub(r'\.gv\{[^}]*\}', '', html)
    if not v: return html
    if GV_CSS not in html: html = html.replace('</style>', GV_CSS + '</style>', 1)
    return html.replace('</main>', '<div class="gv">Game version ' + v + '</div></main>', 1)


def apply(html, placeholder, current_file=None):
    """Fill the markers of a page template: /*SEARCH_CSS*/, <!--SEARCH_BAR-->, /*SEARCH_JS*/ (and the nav)."""
    import re as _re
    # every page's tooltip placement: remember the side and where the object is, 
    html = _re.sub(r"var y=(\w)\.top-t\.height-8; if\(y<8\) y=\1\.bottom\+8;",
                   lambda m: ("var up=%(a)s.top-t.height-8>=8, y=up?%(a)s.top-t.height-8:%(a)s.bottom+8; "
                              "tip.className=up?'above':'below'; "
                              "tip.style.setProperty('--ax', Math.min(Math.max(%(a)s.left+%(a)s.width/2-x,24),t.width-24)+'px');")
                   % {'a': m.group(1)}, html)
    html = _re.sub(r'<p class="sub">.*?</p>\n?', '', html, flags=_re.S)      # no explanation under the page header
    html = html.replace('<body>', '<body class="steel">', 1)
    html = put_nav(html, current_file)
    html = stamp(html)
    return (html.replace('/*SEARCH_CSS*/', CSS + NAV_CSS).replace('<!--SEARCH_BAR-->', BAR.replace('__PLACEHOLDER__', placeholder))
                .replace('/*SEARCH_JS*/', JS))
