"""Search bar shared by the page builders: CSS, the input, and the JS that filters `.cell` buttons.

A page sets `cell._s` (lower-case, accent-free text of what the game shows for the item: name, hint, flavor
text, description) on every cell it wants searchable, then calls `searchInit(root)` once the cells exist.
`qmatch(text)` tells whether a normalised text matches the current query (used to filter stack popups).
"""

CSS = r'''
/* the game's icon frames: gold by default, a colour of their own per faction (9-slice of the 20x20 sprites) */
.cell{position:relative;--tr:url(assets/ui/trim/Gold.png);--trh:url(assets/ui/trim/Gold_Hover.png);padding:0;border:6px solid transparent;border-radius:0;
  background:none;border-image-source:var(--tr);border-image-slice:5 fill;border-image-width:6px;border-image-repeat:stretch;image-rendering:pixelated}
.cell img,.cell img.ov{position:absolute;inset:auto;margin:0;left:50%;top:50%;transform:translate(-50%,-50%);width:calc(87.7% + 10.5px);height:calc(87.7% + 10.5px);
  max-width:none;max-height:none;object-fit:contain;image-rendering:pixelated}
.cell:hover,.cell:focus-visible,.cell.fac:hover{background:none;outline:none;box-shadow:none;border-image-source:var(--trh);filter:brightness(1.15)}
.cell.fac{background:none;border-color:transparent}
.cell.na{opacity:.35;filter:grayscale(1)}
.cell.na:hover{filter:grayscale(1) brightness(1.2)}
.badge{z-index:3}
.t-Fairy{--tr:url(assets/ui/trim/FairyTrim.png);--trh:url(assets/ui/trim/FairyTrim_Hover.png)}
.t-Elven{--tr:url(assets/ui/trim/ElvenTrim.png);--trh:url(assets/ui/trim/ElvenTrim_Hover.png)}
.t-Angel{--tr:url(assets/ui/trim/AngelTrim.png);--trh:url(assets/ui/trim/AngelTrim_Hover.png)}
.t-Goblin{--tr:url(assets/ui/trim/GoblinTrim.png);--trh:url(assets/ui/trim/GoblinTrim_Hover.png)}
.t-Undead{--tr:url(assets/ui/trim/UndeadTrim.png);--trh:url(assets/ui/trim/UndeadTrim_Hover.png)}
.t-Demon{--tr:url(assets/ui/trim/DemonTrim.png);--trh:url(assets/ui/trim/DemonTrim_Hover.png)}
.t-Titan{--tr:url(assets/ui/trim/TitanTrim.png);--trh:url(assets/ui/trim/TitanTrim_Hover.png)}
.t-Druid{--tr:url(assets/ui/trim/DruidTrim.png);--trh:url(assets/ui/trim/DruidTrim_Hover.png)}
.t-Faceless{--tr:url(assets/ui/trim/FacelessTrim.png);--trh:url(assets/ui/trim/FacelessTrim_Hover.png)}
.t-Dwarven{--tr:url(assets/ui/trim/DwarvenTrim.png);--trh:url(assets/ui/trim/DwarvenTrim_Hover.png)}
.t-Drow{--tr:url(assets/ui/trim/DrowTrim.png);--trh:url(assets/ui/trim/DrowTrim_Hover.png)}
.t-Mercenary{--tr:url(assets/ui/trim/MercenaryTrim.png);--trh:url(assets/ui/trim/MercenaryTrim_Hover.png)}
.t-Dragon{--tr:url(assets/ui/trim/DragonTrim.png);--trh:url(assets/ui/trim/DragonTrim_Hover.png)}
.t-Archon{--tr:url(assets/ui/trim/ArchonTrim.png);--trh:url(assets/ui/trim/ArchonTrim_Hover.png)}
.t-Djinn{--tr:url(assets/ui/trim/DjinnTrim.png);--trh:url(assets/ui/trim/DjinnTrim_Hover.png)}
.t-Makers{--tr:url(assets/ui/trim/MakersTrim.png);--trh:url(assets/ui/trim/MakersTrim_Hover.png)}
.t-Good{--tr:url(assets/ui/trim/GoodTrim.png);--trh:url(assets/ui/trim/GoodTrim_Hover.png)}
.t-Evil{--tr:url(assets/ui/trim/EvilTrim.png);--trh:url(assets/ui/trim/EvilTrim_Hover.png)}
.t-Order{--tr:url(assets/ui/trim/OrderTrim.png);--trh:url(assets/ui/trim/OrderTrim_Hover.png)}
.t-Chaos{--tr:url(assets/ui/trim/ChaosTrim.png);--trh:url(assets/ui/trim/ChaosTrim_Hover.png)}
.t-Balance{--tr:url(assets/ui/trim/BalanceTrim.png);--trh:url(assets/ui/trim/BalanceTrim_Hover.png)}.t-Silver{--tr:url(assets/ui/trim/Silver.png);--trh:url(assets/ui/trim/Silver.png)}

/* section headers are dropdowns */
section.dd h2{display:flex;align-items:baseline;gap:8px;cursor:pointer;user-select:none}
section.dd h2:hover{color:var(--accent)}
section.dd h2 .chev{margin-left:auto;align-self:center;width:9px;height:9px;margin-right:6px;border-right:2px solid var(--muted);border-bottom:2px solid var(--muted);
  transform:translateY(-3px) rotate(45deg);transition:transform .3s ease}
section.dd.open h2 .chev{transform:translateY(2px) rotate(-135deg)}
.dd-body{display:grid;grid-template-rows:0fr;opacity:0;transition:grid-template-rows .45s ease,opacity .3s ease}
.dd.open .dd-body,body.searching .dd .dd-body{grid-template-rows:1fr;opacity:1}
.dd-in{overflow:hidden;min-height:0;content-visibility:auto;contain-intrinsic-size:auto 700px}
@keyframes ddcell{from{opacity:0;transform:translateY(-10px) scale(.9)}to{opacity:1;transform:none}}
.dd-in.casc .cell{animation:ddcell .34s ease both;animation-delay:calc(var(--i,0) * 9ms)}
/* the game's own fonts: Liony Bold for headings, names and labels, Liony Regular for everything else */
@font-face{font-family:"Liony";src:url(assets/fonts/Liony-Regular.ttf) format("truetype");font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"Liony";src:url(assets/fonts/Liony-Bold.ttf) format("truetype");font-weight:700;font-style:normal;font-display:swap}
html{font-size:30px}
body{font-family:"Liony",system-ui,-apple-system,"Segoe UI",sans-serif;font-size:1rem;line-height:1.2;letter-spacing:.01em}
main{max-width:960px}
#tip{width:min(620px,calc(100vw - 16px))}
#pop .card{width:min(620px,100%)}
#more .card{width:min(640px,100%)}
h1,h2,h3,b,strong,#tip b.t,#tip .lbl,#tip .flabel,#pop h3,#more h3,.subh,.bar b,nav a[aria-current],.mark{font-family:"Liony",system-ui,sans-serif;font-weight:700}
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
#tip .flabel{margin-top:3px}
#tip .fsep{margin:4px 0 1px}
#tip .cost{margin-top:0}
#more .bonus{padding:5px 0}
#more .bonus p{margin:0 0 1px}
#more .formula{padding:0}
#more ul.vars{margin:1px 0}
#pop .card,#more .card{padding:10px 12px}
/* the Upgrades entry of the nav drops down to the four upgrade pages */
.dd-nav{position:relative;display:inline-block}
.dd-nav .dd-menu{display:none;position:absolute;top:100%;left:-10px;z-index:70;min-width:210px;padding:6px;background:var(--card);
  border:1px solid var(--line);border-radius:10px;box-shadow:var(--shadow);flex-direction:column;gap:2px}
.dd-nav:hover .dd-menu,.dd-nav:focus-within .dd-menu{display:flex}
.dd-nav .dd-menu a{padding:5px 10px;border:0;border-radius:6px;white-space:nowrap}
.dd-nav .dd-menu a:hover{background:var(--cell);color:var(--fg)}
.dd-nav .dd-menu a[aria-current]{background:var(--cellhi);border:0}
/* less vertical air everywhere */
main{padding-top:18px;padding-bottom:50px}
nav{margin:0 0 8px}
h1{margin:0 0 2px}
.sub{margin:0 0 8px;line-height:1.2}
.pen-note{margin:0 0 8px;padding:6px 10px;line-height:1.2}
.search{margin:0 0 8px}
.bar{padding:4px 16px;gap:2px;margin-bottom:8px}
.bar .row{gap:2px 14px}
section{margin:0 0 14px}
h2{margin:0 0 5px;padding-bottom:3px}
.subh{margin:8px 0 4px}
.grid{gap:5px}
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
.sx{display:none!important}
'''

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
    document.addEventListener('click',function(){ document.querySelectorAll('.cs.open').forEach(function(w){ w.classList.remove('open'); }); });
    document.addEventListener('keydown',function(e){ if(e.key==='Escape') document.querySelectorAll('.cs.open').forEach(function(w){ w.classList.remove('open'); }); });
  }
  function qmatch(s){ return !QT.length || QT.every(function(t){ return s.indexOf(t)>=0; }); }
  function searchInit(root, after){
    enhanceSelects();
    var box=document.getElementById('q'), note=document.getElementById('qn');
    function run(){
      QT = normS(box.value).split(/\s+/).filter(Boolean).map(function(t){ return FCODES.hasOwnProperty(t) ? FCODES[t] : t; });
      var shown=0;
      root.querySelectorAll('.cell').forEach(function(c){
        var ok = qmatch(c._s||'');
        c.classList.toggle('sx', !ok); if(ok) shown++;
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
    return ('<span class="dd-nav"><a href="upgrades.html"' + (' aria-current="page"' if parent_current else '') +
            '>Upgrades</a><span class="dd-menu">' + links + '</span></span>')


def apply(html, placeholder, current_file=None):
    """Fill the three markers of a page template: /*SEARCH_CSS*/, <!--SEARCH_BAR-->, /*SEARCH_JS*/."""
    html = html.replace('<a href="upgrades.html" aria-current="page">Upgrades</a>', upgrades_nav(current_file, True))
    html = html.replace('<a href="upgrades.html">Upgrades</a>', upgrades_nav(current_file, False))
    return (html.replace('/*SEARCH_CSS*/', CSS).replace('<!--SEARCH_BAR-->', BAR.replace('__PLACEHOLDER__', placeholder))
                .replace('/*SEARCH_JS*/', JS))
