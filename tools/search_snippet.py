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
.dd-in{overflow:hidden;min-height:0}
@keyframes ddcell{from{opacity:0;transform:translateY(-10px) scale(.9)}to{opacity:1;transform:none}}
.dd-in.casc .cell{animation:ddcell .34s ease both;animation-delay:calc(var(--i,0) * 9ms)}
/* the game's own fonts: Liony Bold for headings, names and labels, Liony Regular for everything else */
@font-face{font-family:"Liony";src:url(assets/fonts/Liony-Regular.ttf) format("truetype");font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"Liony";src:url(assets/fonts/Liony-Bold.ttf) format("truetype");font-weight:700;font-style:normal;font-display:swap}
body{font-family:"Liony",system-ui,-apple-system,"Segoe UI",sans-serif;font-size:17px;line-height:1.5;letter-spacing:.01em}
main{max-width:780px}
h1,h2,h3,b,strong,#tip b.t,#tip .lbl,#tip .flabel,#pop h3,#more h3,.subh,.bar b,nav a[aria-current],.mark{font-family:"Liony",system-ui,sans-serif;font-weight:700}
input,select,button,textarea{font-family:inherit}
#tip,#pop,#more{font-size:17px}
/* formulas: KaTeX keeps its own fonts for symbols and brackets (their sizes are baked into its layout);
   letters and digits take the game's font */
.katex .mathnormal,.katex .mathit,.katex .mathrm,.katex .mord:not(.mop):not(.mspace):not(.delimsizing):not(.sizing){font-family:"Liony",KaTeX_Main,serif}
.katex .mathnormal,.katex .mathit{font-style:normal}
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
  function qmatch(s){ return !QT.length || QT.every(function(t){ return s.indexOf(t)>=0; }); }
  function searchInit(root, after){
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


def apply(html, placeholder):
    """Fill the three markers of a page template: /*SEARCH_CSS*/, <!--SEARCH_BAR-->, /*SEARCH_JS*/."""
    return (html.replace('/*SEARCH_CSS*/', CSS).replace('<!--SEARCH_BAR-->', BAR.replace('__PLACEHOLDER__', placeholder))
                .replace('/*SEARCH_JS*/', JS))
