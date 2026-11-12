
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
    function toggle(){ setOpen(!open, true); }
    sec._fold=function(o){ setOpen(o, false); };      // folds or unfolds without remembering it (a link that lands on one section folds the others)
    function setOpen(o, remember){
      if(o===open) return;
      open=o; sec.classList.toggle('open', open); h.setAttribute('aria-expanded', String(open));
      if(typeof hideTip==='function') hideTip();
      if(open){
        var cs=inner.querySelectorAll('.cell');
        for(var k=0;k<cs.length && k<90;k++) cs[k].style.setProperty('--i', k);
        inner.classList.add('casc'); setTimeout(function(){ inner.classList.remove('casc'); }, 1300);
      }
      if(remember){ store[key]=open;
        try{ localStorage.setItem(sk, JSON.stringify(store)); }catch(e){} }
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

  // ---- the popup of an upgrade as the upgrade pages show it (name, cost, requirements, text, formulas); asc is the chosen Ascension
  function upgMath(tex, host){
    if(window.katex){ try{ katex.render('\\displaystyle '+tex, host, {throwOnError:false}); return; }catch(e){} }
    host.textContent = tex;
  }
  function upgPred(p){
    return p.replace(/^not having /,'you do not have ').replace(/^not playing /,'you are not playing ').replace(/^following /,'you are following ')
            .replace(/^having /,'you have ').replace(/^playing /,'you are playing ').replace(/^using /,'you are using ')
            .replace(/^being able /,'you are able ').replace(/^being /,'you are ');
  }
  function upgAs(k){ return new Array(k+1).join('A'); }
  function upgPenalty(it, ASC){
    var k=0; it.d.forEach(function(p){ if(p.s && ASC>=p.s && !(p.np && ASC>=4)) k=Math.max(k, ASC-p.s+1); });
    if(it.m) it.m.forEach(function(p){ if(p.s && ASC>=p.s) k=Math.max(k, ASC-p.s+1); });
    return k;
  }
  function upgUnavailable(it, ASC){ return (it.lo!==null && ASC<it.lo) || (it.hi!==null && ASC>=it.hi) || !!(it.an && it.an.indexOf(ASC)>=0); }
  function upgFormulas(parent, list, title, ASC){
    var many=list.length>1, seen={};
    parent.appendChild(ce('span','lbl',title||(many?'Formulas':'Formula')));
    var anyScaled=many && list.some(function(f){ return f.s; });
    list.forEach(function(f,i){
      if(i>0) parent.appendChild(ce('div','fsep'));
      var vs=many?'v_{'+(i+1)+'}':'v';
      var own=/^([a-uw-zA-Z](?:_\{[^}]*\})?) = /.exec(f.l); if(own) vs=own[1];      // a formula for a named value (a, b, ...) keeps its own symbol
      if(f.lb){
        var lab=ce('div','flabel'); var lm=ce('span'); upgMath(vs,lm); lab.appendChild(lm);
        var suf='', badge=null;
        if(anyScaled){
          if(!f.s) suf='';
          else if(ASC>=f.s && !(f.np && ASC>=4)){ suf=' · '; badge=ce('span','mark',upgAs(ASC-f.s+1)); }
        }
        lab.appendChild(document.createTextNode(' — '+f.lb+suf)); if(badge) lab.appendChild(badge); parent.appendChild(lab);
      }
      var d=ce('div','formula'); var m=ce('span'); upgMath(f.l.replace(/^v(_\{\d+\})? = /, vs+' = '), m); d.appendChild(m); parent.appendChild(d);
      var ul=ce('ul','vars'), n=0;
      f.v.forEach(function(v){
        var k=v.symbol+'|'+v.text; if(seen[k]) return; seen[k]=1; n++;
        var li=ce('li'); var b=ce('b'); b.style.display='inline'; upgMath(v.symbol,b); li.appendChild(b);
        rich(li, ' — '+v.text); ul.appendChild(li);
      });
      if(n) parent.appendChild(ul);
    });
    if(list.some(function(f){ return f.s; })) parent.appendChild(ce('div','more','v is the base value, before any Ascension penalty.'));
  }
  function upgCostText(it, ASC, COINS){      // the game's "Cost: ..." for the chosen Ascension; nothing for an upgrade that cannot be bought then
    return upgUnavailable(it, ASC) ? null : upgCost(it, ASC, COINS);
  }
  function upgradeTip(it, anchor, ASC, COINS){
    var tip=document.getElementById('tip');
    tip.className='upg'; tip.textContent='';
    tip.appendChild(ce('b','t',it.n));
    var ct=upgCostText(it, ASC, COINS); if(ct) tip.appendChild(ce('div','cost',ct));      // right below the name, faded
    if(it.sub) tip.appendChild(ce('div','more',it.sub));
    if(it.m || it.bl || it.lg || it.lp || it.st || it.cb) tip.appendChild(ce('div','more','Click for more info'));
    if(it.o.length){
      var rs=[], os=[];
      var st=[];
      it.o.forEach(function(c){ var m=/^being at Reincarnation ([0-9]+) or higher$/.exec(c); if(m) rs.push('after Reincarnation '+m[1]); else if(c.indexOf('starting from')===0) st.push(c); else os.push(c); });
      var ps=os.map(upgPred), pj=ps.length>1 ? ps.slice(0,-1).join(', ')+' and '+ps[ps.length-1] : ps.join(''), txt;
      txt='Can only be bought'+(os.length?' when '+pj:'')+(rs.length?(os.length?' and ':' ')+rs.join(' and '):'')+(st.length?(os.length||rs.length?', ':' ')+st.join(' and '):'')+'.';
      if(it.ns && it.an) txt+=' Cannot be bought at Ascension '+it.an.slice(0,-1).join(', ')+(it.an.length>1?' and ':'')+it.an[it.an.length-1]+'.';
      tip.appendChild(ce('div','faction',txt));
    }
    if(upgUnavailable(it, ASC)){
      tip.appendChild(ce('span','lbl','Not available'));
      tip.appendChild(ce('div',null,'This upgrade is not available in Ascension '+ASC+'.'));
    }
    tip.appendChild(ce('span','lbl','What it does'));
    var noted=false;
    it.d.forEach(function(p){
      var e=ce('p',null,p.t);
      if(p.s && ASC>=p.s && !(p.np && ASC>=4)){ e.appendChild(document.createTextNode(' ')); e.appendChild(ce('span','mark',upgAs(ASC-p.s+1))); }
      tip.appendChild(e);
      if(it.nt && !noted && new RegExp(it.nr).test(p.t)){ tip.appendChild(ce('div','more',it.nt)); noted=true; }
    });
    if(it.f.length){
      upgFormulas(tip, it.f, null, ASC);
    }
    if(it.lc && !upgUnavailable(it, ASC)){      // a Lineage: what raising it a level costs
      var L=it.lc;
      var cf=[{l:'C = \\left(b \\cdot 10^{L/A}\\right)^{1 + \\left(c + \\frac{1}{2A} - r\\right)\\left\\lfloor L/'+L.ev+' \\right\\rfloor}', lb:null, v:[
          {symbol:'C', text:'the associated faction coins the next level costs'}, {symbol:'L', text:'current lineage level'}, {symbol:'A', text:'your Ascension value'},
          {symbol:'b', text:'base cost (changes with Ascensions, $'+ctex(L.b[ASC])+'$ at Ascension '+ASC+')'}, {symbol:'c', text:'base growth (changes with Ascensions, $'+L.c[ASC]+'$ at Ascension '+ASC+')'},
          {symbol:'r', text:'growth reduction term, $0$ without '+L.hg}]}];
      upgFormulas(tip, cf, 'Cost', ASC);
    }
    var rq=it.s.slice();
    if(it.ra){ var ra=it.ra[String(Math.min(Math.max(ASC, it.lo||1),4))]; if(ra) rq.unshift(ra); }      // before it unlocks: the numbers of the Ascension it unlocks in
    if(rq.length){
      tip.appendChild(ce('span','lbl','Unlock requirement'));
      var ul=ce('ul'); rq.forEach(function(s){ ul.appendChild(ce('li',null,s)); }); tip.appendChild(ul);
    }
    if(it.nt && !noted) tip.appendChild(ce('div','more',it.nt));
    placeTip(anchor, true);
  }

  // the perks of a Lineage in the #more popup of the page (the markup is on the Upgrades and Factions pages); keep(p) optionally picks the perks to show
  function upgPerks(it, ASC, keep){
    var more=document.getElementById('more'), body=document.getElementById('morebody'); document.getElementById('moretitle').textContent=it.n+' perks'; body.textContent='';
    it.lp.filter(function(p){ return !keep || keep(p); }).forEach(function(p){
      var blk=ce('div','bonus'), head=ce('p'), pi=p.it;
      head.appendChild(ce('b',null,pi ? pi.n : 'Perk '+p.n)); blk.appendChild(head);
      if(pi){
        var pn=false;
        pi.d.forEach(function(d){ blk.appendChild(ce('p',null,d.t)); if(pi.nt && !pn && new RegExp(pi.nr).test(d.t)){ blk.appendChild(ce('div','more',pi.nt)); pn=true; } });
        if(pi.f.length){ var fw=ce('div'); upgFormulas(fw, pi.f, null, ASC); blk.appendChild(fw); }
        if(pi.nt && !pn) blk.appendChild(ce('div','more',pi.nt));
      }
      blk.appendChild(ce('span','lbl','Unlock requirement'));
      blk.appendChild(ce('div',null,'Reincarnation '+p.reinc+', Lineage level '+p.level+(p.challenge ? ', '+p.challenge : '')));
      body.appendChild(blk);
    });
    more.classList.add('open'); document.getElementById('moreclose').focus();
  }
  function bindMore(){      // the close button, a click outside the card and Escape
    var more=document.getElementById('more');
    function close(){ more.classList.remove('open'); }
    document.getElementById('moreclose').addEventListener('click',close);
    more.addEventListener('click',function(e){ if(e.target===more) close(); });
    document.addEventListener('keydown',function(e){ if(e.key==='Escape') close(); });
  }

  // ---- an artifact {n: name, h: hint, q: unlock requirements, x: undecoded conditions, c: how it is found, p: percent, l: formula, v: its variables, f: flavor text, i: icon file}
  // as the Archaeology page shows it: the popup, and the cell that opens it
  function artifactTip(it, anchor){
    var tip=document.getElementById('tip');
    tip.className='art'; tip.textContent='';
    tip.appendChild(ce('b',null,it.n));
    if(it.h){ tip.appendChild(ce('span','lbl','Hint')); tip.appendChild(ce('div','hint',it.h)); }
    if(it.q.length || it.x){
      tip.appendChild(ce('span','lbl','Unlock requirement'));
      if(it.q.length){ var ul=ce('ul'); it.q.forEach(function(q){ ul.appendChild(ce('li',null,q)); }); tip.appendChild(ul); }
      if(it.x) tip.appendChild(ce('div','more',(it.q.length?'Plus ':'')+'additional conditions not listed here.'));
    } else {
      tip.appendChild(ce('span','lbl','Unlock requirement'));
      tip.appendChild(ce('div','hint','None. It can be found on any excavation.'));
    }
    if(it.c){
      tip.appendChild(ce('span','lbl','How it is found'));
      var pct = (it.p!=null) ? String(it.p) : '';
      var lead = (it.q.length || it.x) ? 'Meeting the requirements does not unlock it by itself. From then on, each excavation has ' : 'Each excavation has ';
      if(it.c==='guaranteed'){
        tip.appendChild(ce('div','chance','Once the requirements are met, it is found on your next excavation.'));
      } else if(it.c==='fixed'){
        tip.appendChild(ce('div','chance',lead+'a '+pct+'% chance to find it.'));
      } else if(it.l && it.v){
        tip.appendChild(ce('div','chance',lead+'a chance to find it, which depends on:'));
        var ul2=ce('ul','vars');
        it.v.forEach(function(v){ var li=ce('li'); var b=ce('b',null,v.symbol); if(window.katex){ try{ katex.render(v.symbol,b,{throwOnError:false}); }catch(e){} } li.appendChild(b); rich(li, ' — '+v.text); ul2.appendChild(li); });
        tip.appendChild(ul2);
        var f=ce('div','formula');
        if(window.katex){ try{ katex.render('\\displaystyle '+it.l,f,{throwOnError:false,displayMode:false}); }catch(e){ f.textContent=it.l; } }
        else f.textContent=it.l;
        tip.appendChild(f);
        tip.appendChild(ce('div','more','p is the percent chance per excavation.'));
      } else {
        tip.appendChild(ce('div','chance',lead+'a chance to find it, which depends on your stats.'));
      }
    }
    if(it.f){ tip.appendChild(ce('span','lbl','Flavor text')); tip.appendChild(ce('div','flavor',it.f)); }
    placeTip(anchor, true);
  }
  function artifactCell(it){
    var b=ce('button','cell'), tip=document.getElementById('tip'); b.type='button'; b.setAttribute('aria-label', it.n);
    if(it.i){ var im=ce('img'); im.src='assets/icons/'+encodeURIComponent(it.i); im.alt=''; im.loading='lazy'; b.appendChild(im); }
    function hide(){ tip.style.display='none'; }
    b.addEventListener('mouseenter',function(){ artifactTip(it,b); }); b.addEventListener('focus',function(){ artifactTip(it,b); });
    b.addEventListener('mouseleave',hide); b.addEventListener('blur',hide);
    return b;
  }

  // ---- an upgrade of the Upgrades pages' data ({n, i, d, f, s, o, lo, ...} as build_upgrades_page.item makes it) as a cell: the icon, the popup (upgradeTip), the A marks of the Ascension penalty,
  // greyed out when it is not available in asc; a click opens what the upgrade holds (the perks of a Lineage, the upgrades of a Legacy Combos / Bloodlines / Lineages / Artifact Sets container)
  var UPG_TRIM={Fairy:1,Elven:1,Angel:1,Goblin:1,Undead:1,Demon:1,Titan:1,Druid:1,Faceless:1,Dwarven:1,Drow:1,Mercenary:1,Dragon:1,Archon:1,Djinn:1,Makers:1};
  function upgItemCell(it, asc, coins){
    var b=ce('button','cell'), tip=document.getElementById('tip'); b.type='button'; b.setAttribute('aria-label',it.n);
    if(it.fn && UPG_TRIM[it.fn]) b.classList.add('t-'+it.fn);
    if(it.i){ var im=ce('img'); im.src='assets/icons/'+encodeURIComponent(it.i); im.alt=''; b.appendChild(im); }
    var na=upgUnavailable(it,asc), k=na?0:upgPenalty(it,asc);
    b.classList.toggle('na',na); if(k) b.appendChild(ce('span','pen',upgAs(k)));
    function hide(){ tip.style.display='none'; }
    b.addEventListener('mouseenter',function(){ upgradeTip(it,b,asc,coins); }); b.addEventListener('focus',function(){ upgradeTip(it,b,asc,coins); });
    b.addEventListener('mouseleave',hide); b.addEventListener('blur',hide);
    var group = it.cb ? ['Legacy Combos',it.cb] : it.bl ? ['Bloodlines',it.bl] : it.lg ? ['Lineages',it.lg] : it.st ? ['Artifact Sets',it.st] : null;
    if(it.lp) b.addEventListener('click',function(e){ e.stopPropagation(); hide(); upgPerks(it,asc); });
    else if(group) b.addEventListener('click',function(e){ e.stopPropagation(); hide(); openUpgGroup(group[0], group[1], asc, coins); });
    return b;
  }
  // the group popup (#pop, #poptitle, #popgrid, #popclose in the page): the upgrades in a grid of three columns
  function openUpgGroup(title, items, asc, coins){
    var pop=document.getElementById('pop'), grid=document.getElementById('popgrid');
    document.getElementById('poptitle').textContent=title; grid.textContent=''; grid.className='grid cols3';
    pop.querySelector('.card').classList.add('narrow');
    items.forEach(function(it){ if(it) grid.appendChild(upgItemCell(it,asc,coins)); });
    pop.classList.add('open'); document.getElementById('popclose').focus();
  }
  function bindPop(){
    var pop=document.getElementById('pop');
    function close(){ pop.classList.remove('open'); document.getElementById('tip').style.display='none'; }
    document.getElementById('popclose').addEventListener('click',close);
    pop.addEventListener('click',function(e){ if(e.target===pop) close(); });
    document.addEventListener('keydown',function(e){ if(e.key==='Escape') close(); });
  }

  // ---- a challenge (challenge_items.item) of a faction section {name, ...} as the Challenges page shows it: the popup, and the cell that opens it
  function chalFormulas(parent, list){
    var many=list.filter(function(f){ return /^v/.test(f.l); }).length>1, seen={}, vk=0;
    parent.appendChild(ce('span','lbl',many?'Formulas':'Formula'));
    list.forEach(function(f,i){
      if(i>0) parent.appendChild(ce('div','fsep'));
      var isy=!/^v/.test(f.l);
      var vs=isy?'y':many?'v_{'+(++vk)+'}':'v';
      if(f.lb){
        var lab=ce('div','flabel'); var lm=ce('span'); upgMath(vs,lm); lab.appendChild(lm);
        lab.appendChild(document.createTextNode(' — '+f.lb)); parent.appendChild(lab);
      }
      var d=ce('div','formula'); var m=ce('span'); upgMath(isy?f.l:f.l.replace(/^v(_\{\d+\})? = /, vs+' = '), m); d.appendChild(m); parent.appendChild(d);
      var ul=ce('ul','vars'), n=0;
      f.v.forEach(function(v){
        var k=v.symbol+'|'+v.text; if(seen[k]) return; seen[k]=1; n++;
        var li=ce('li'); var b=ce('b'); b.style.display='inline'; upgMath(v.symbol,b); li.appendChild(b);
        rich(li, ' — '+v.text); ul.appendChild(li);
      });
      if(n) parent.appendChild(ul);
    });
  }
  function challengeTip(sec, it, anchor){
    var tip=document.getElementById('tip');
    tip.className='chl'; tip.textContent='';
    tip.appendChild(ce('b','t',it.n));
    if(it.su){
      tip.appendChild(ce('span','kind','Permanent spell upgrade for '+sec.name));
    } else {
      tip.appendChild(ce('span','kind',sec.name+' challenge '+it.num));
      tip.appendChild(ce('span','lbl','Requirements'));
      var ul2=ce('ul'); it.q.forEach(function(q){ ul2.appendChild(ce('li',null,q)); }); tip.appendChild(ul2);
      tip.appendChild(ce('span','lbl','The challenge'));
      tip.appendChild(ce('div','chal',it.c));
    }
    tip.appendChild(ce('span','lbl',it.su ? 'Effect' : 'Reward'));
    it.r.forEach(function(t,i){ tip.appendChild(ce('p',null,t));
      it.rn.forEach(function(n){ if(n[0]===i) tip.appendChild(ce('div','more',n[1])); }); });
    if(it.f.length){
      chalFormulas(tip, it.f);
      if(it.nt) tip.appendChild(ce('div','more',it.nt));
      else if(it.sh) tip.appendChild(ce('div','more','v is the number the game shows for the reward.'));
    }
    if(it.a){
      tip.appendChild(ce('span','lbl','Reward can be used'));
      var a = it.a, txt;
      if(a.indexOf('any ')===0) txt = 'While playing with '+a+'.';
      else txt = 'Only while playing with the '+a+' faction.';
      tip.appendChild(ce('div',null,txt));
    }
    if(it.fl){ tip.appendChild(ce('span','lbl','Flavor text')); tip.appendChild(ce('div','flavor',it.fl)); }
    tip.style.width=''; tip.style.display='block';
    var need=0; tip.querySelectorAll('.formula').forEach(function(f){ need=Math.max(need, f.scrollWidth-f.clientWidth); });
    if(need>0) tip.style.width=Math.min(window.innerWidth-16, tip.getBoundingClientRect().width+need+8)+'px';
    placeTip(anchor, true);
  }
  function challengeCell(sec, it){
    var b=ce('button','cell'+(it.su?' su':'')), tip=document.getElementById('tip'); b.type='button'; b.setAttribute('aria-label',it.n);
    var tn=trimName(sec.name); if(tn) b.classList.add('t-'+tn);
    if(it.i){ var im=ce('img'); im.src='assets/icons/'+encodeURIComponent(it.i); im.alt=''; im.loading='lazy'; b.appendChild(im); }
    function hide(){ tip.style.display='none'; }
    b.addEventListener('mouseenter',function(){ challengeTip(sec,it,b); }); b.addEventListener('focus',function(){ challengeTip(sec,it,b); });
    b.addEventListener('mouseleave',hide); b.addEventListener('blur',hide);
    return b;
  }

  // ---- the chips of a spell or faction (Good, Order, ...) and the labels of a board
  function chips(s){
    var d=ce('div','tags');
    (s.tags||s).forEach(function(t){ d.appendChild(ce('span','chip c-'+t.replace(/\*$/,'').toLowerCase().replace(/[^a-z0-9]+/g,'-'),t)); });
    return d;
  }
  function chipLabel(text, r, c, cs, span){
    var d=ce('div','lab'); d.style.gridRow=String(r); d.style.gridColumn=span?c+' / span '+span:String(c);
    d.appendChild(ce('span','chip c-'+text.toLowerCase().replace(/[^a-z0-9]+/g,'-'),text)); return d;
  }
  function ce(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
