"""Search bar shared by the page builders: CSS, the input, and the JS that filters `.cell` buttons.

A page sets `cell._s` (lower-case, accent-free text of what the game shows for the item: name, hint, flavor
text, description) on every cell it wants searchable, then calls `searchInit(root)` once the cells exist.
`qmatch(text)` tells whether a normalised text matches the current query (used to filter stack popups).
"""

CSS = r'''
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
main{max-width:680px}
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


def upgrades_nav(current_file=None, parent_current=False):
    """the nav entry "Upgrades" with its drop-down of the four upgrade pages"""
    links = ''.join(f'<a href="{f}"' + (' aria-current="page"' if f == current_file else '') + f'>{n}</a>' for f, n in UPGRADE_PAGES)
    return ('<span class="dd-nav"><a role="button" tabindex="0" style="cursor:pointer"' + (' aria-current="page"' if parent_current else '') +
            " onclick=\"this.parentNode.classList.toggle('open')\">Upgrades</a><span class=\"dd-menu\">" + links + '</span></span>')


GV_CSS = '.gv{margin-top:36px;text-align:center;font-size:14px;color:var(--muted);opacity:.7}'


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
    html = html.replace('<a href="upgrades.html" aria-current="page">Upgrades</a>', upgrades_nav(current_file, True))
    html = html.replace('<a href="upgrades.html">Upgrades</a>', upgrades_nav(current_file, False))
    html = stamp(html)
    return (html.replace('/*SEARCH_CSS*/', CSS).replace('<!--SEARCH_BAR-->', BAR.replace('__PLACEHOLDER__', placeholder))
                .replace('/*SEARCH_JS*/', JS))
