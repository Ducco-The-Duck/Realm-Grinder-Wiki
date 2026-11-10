
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
            e.stopPropagation(); e.preventDefault();      // preventDefault: inside a <label>, a click on the list would otherwise be passed on to the button and open it again
            proto.set.call(sel,o.value); sync(); wrap.classList.remove('open');
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
    var hq=location.hash.match(/^#q=(.*)$/); if(hq){ try{ box.value=decodeURIComponent(hq[1]); }catch(e){} }      // a link with #q=... opens the page with that search
    function run(){
      QT = normS(box.value).split(/\s+/).filter(Boolean).map(function(t){ return FCODES.hasOwnProperty(t) ? FCODES[t] : t; });
      var shown=0;
      root.querySelectorAll('.cell').forEach(function(c){
        var ok = c._m ? c._m() : qmatch(c._s||'');
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

  // ---- upgrade cells and their hover popup (the upgrade pages and every page that shows an upgrade); the popup rules are in shared.css
  var SUPD='⁰¹²³⁴⁵⁶⁷⁸⁹';
  function cnum(x){      // the game's number format: the mantissa to 4 significant digits (3 after the point), without trailing zeros; 145000000 -> 1.45 × 10⁸
    if(x<1e6) return Math.floor(x).toLocaleString('en-US');
    var e=Math.floor(Math.log10(x)), m=x/Math.pow(10,e), s;
    if(m>=9.999){ s='1'; e++; } else { s=m.toPrecision(4); if(s.indexOf('.')>=0) s=s.replace(/\.?0+$/,''); }
    return s+' × 10'+String(e).split('').map(function(c){ return SUPD[+c]; }).join('');
  }
  function ctex(x){      // the same number for a formula ($...$)
    if(x<1e6) return String(x);
    var e=Math.floor(Math.log10(x)), m=x/Math.pow(10,e), s;
    if(m>=9.999){ s='1'; e++; } else { s=m.toPrecision(4); if(s.indexOf('.')>=0) s=s.replace(/\.?0+$/,''); }
    return s+' \\times 10^{'+e+'}';
  }
  function upgCost(u, asc, coins){      // the game's "Cost: ..." at an Ascension: the coins of that Ascension, then Faction Coins (u.c[asc] = [coins, [[faction, amount], ...]], or null)
    var c=u.c && u.c[asc]; if(!c) return null;
    var parts=[];
    if(c[0]>0) parts.push(cnum(c[0])+' '+coins[0][asc]);
    c[1].forEach(function(f){ parts.push(cnum(f[1])+' '+coins[1][f[0]]+(f[1]===1 ? ' Coin' : ' Coins')); });
    return 'Cost: '+(parts.length ? parts.join(', ') : 'Free');
  }
  function placeTip(anchor, clamp){      // show #tip above the anchor (below when there is no room), its arrow under the anchor; clamp: also keep it inside the window at the bottom
    var tip=document.getElementById('tip');
    tip.style.display='block';
    var r=anchor.getBoundingClientRect(), t=tip.getBoundingClientRect();
    var x=Math.min(Math.max(8,r.left+r.width/2-t.width/2), window.innerWidth-t.width-8);
    var up=r.top-t.height-8>=8, y=up ? r.top-t.height-8 : r.bottom+8;
    if(clamp && y+t.height>window.innerHeight-8) y=Math.max(8,window.innerHeight-t.height-8);
    tip.classList.remove('above','below'); tip.classList.add(up?'above':'below');
    tip.style.setProperty('--ax', Math.min(Math.max(r.left+r.width/2-x, 24), t.width-24)+'px');
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }
  // an upgrade of a card {n: name, i: icon file, d: [description paragraphs], s: [unlock requirement lines], c: costs per Ascension}: its cell, and the popup with name, cost and text
  function upgradeCell(u, asc, coins){
    var tip=document.getElementById('tip'), b=document.createElement('button'), im=document.createElement('img');
    b.className='cell'; b.type='button'; b.setAttribute('aria-label', u.n);
    im.src='assets/icons/'+encodeURIComponent(u.i); im.alt=''; b.appendChild(im);
    function add(tag, cls, text, to){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; (to||tip).appendChild(e); return e; }
    function show(){
      tip.className='upg'; tip.textContent='';
      add('b','t',u.n);
      var ct=upgCost(u, asc, coins); if(ct) add('div','cost',ct);
      add('span','lbl','What it does');
      u.d.forEach(function(t){ add('p',null,t); });
      if(u.s && u.s.length){ add('span','lbl','Unlock requirement'); var ul=add('ul'); u.s.forEach(function(s){ add('li',null,s,ul); }); }
      placeTip(b, true);
    }
    function hide(){ tip.style.display='none'; }
    b.addEventListener('mouseenter',show); b.addEventListener('focus',show); b.addEventListener('mouseleave',hide); b.addEventListener('blur',hide);
    return b;
  }
