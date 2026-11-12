  // ---- the tray: the left side of every page, where objects of the wiki are pinned (sections and subsections, each with its own Ascension).
  // State lives in localStorage ("rg-tray"): {open, w, last, secs:[{id, name, asc, shut, items:[reference], subs:[{id, name, asc, shut, items}]}]}.
  // Objects are dragged with the mouse (pointer events, not the browser's drag and drop, which does not start on a button in Firefox); on a touch screen a long press
  // pins an object (to the newest section) or removes it from the tray. The objects of the tray are drawn by objectFor from the catalogue, without their click.
  (function(){
    var KEY='rg-tray', MAXOBJ=200, MAXSEC=30, NAMELEN=24, MAXA=__MAXA__, DEFW=300, MINW=200;
    var T, tray, body, toast, narrow=window.matchMedia('(max-width:700px)'), undoState=null, toastTimer=null;
    function uid(){ return 'k'+Date.now().toString(36)+Math.random().toString(36).slice(2,6); }
    function globalAsc(){ try{ var a=parseInt(localStorage.getItem('rg-ascension'),10); if(a>=0 && a<=MAXA) return a; }catch(e){} return 0; }
    function cleanName(s, d){ s=String(s==null?'':s).replace(/\s+/g,' ').trim().slice(0,NAMELEN).trim(); return s||d; }
    function cleanList(l){ return Array.isArray(l) ? l.filter(function(x){ return typeof x==='string' && PINNABLE.indexOf(x.split('|')[0])>=0; }) : []; }
    function cleanSec(s, sub){
      var o={id:typeof s.id==='string'?s.id:uid(), name:cleanName(s.name,'Section'), asc:(s.asc>=0 && s.asc<=MAXA)?(s.asc|0):globalAsc(), shut:!!s.shut, items:cleanList(s.items)};
      if(!sub) o.subs=(Array.isArray(s.subs)?s.subs:[]).map(function(x){ return cleanSec(x,true); });
      return o;
    }
    function fresh(){ var s=cleanSec({name:'General'}); return {open:!narrow.matches, w:DEFW, last:s.id, secs:[s]}; }
    function load(){
      try{
        var o=JSON.parse(localStorage.getItem(KEY)||'null');
        if(o && Array.isArray(o.secs)){
          var t={open:o.open!==false, w:Math.min(Math.max(+o.w||DEFW,MINW),900), last:o.last, secs:o.secs.map(function(x){ return cleanSec(x); })};
          return t;
        }
      }catch(e){}
      return fresh();
    }
    function save(){ try{ localStorage.setItem(KEY, JSON.stringify(T)); }catch(e){} }
    function countObjects(){ var n=0; T.secs.forEach(function(s){ n+=s.items.length; s.subs.forEach(function(u){ n+=u.items.length; }); }); return n; }
    function countSecs(){ var n=0; T.secs.forEach(function(s){ n+=1+s.subs.length; }); return n; }
    function find(id){      // {sec, sub|null, parent|null}
      for(var i=0;i<T.secs.length;i++){
        var s=T.secs[i]; if(s.id===id) return {sec:s, parent:null, list:T.secs, i:i};
        for(var j=0;j<s.subs.length;j++) if(s.subs[j].id===id) return {sec:s.subs[j], parent:s, list:s.subs, i:j};
      }
      return null;
    }
    function newest(){ var f=T.last && find(T.last); if(f) return f.sec; return T.secs[T.secs.length-1] || null; }

    // ---- messages
    function say(text, undo){
      if(!toast) return;
      toast.textContent=''; toast.appendChild(document.createTextNode(text+(undo?' ':'')));
      if(undo){ var u=ce('button',null,'Undo'); u.type='button'; u.addEventListener('click',function(){ T=undo(); save(); render(); toast.classList.remove('on'); }); toast.appendChild(u); }
      toast.classList.add('on'); clearTimeout(toastTimer); toastTimer=setTimeout(function(){ toast.classList.remove('on'); }, 5000);
    }
    function snapshot(){ var j=JSON.stringify(T); return function(){ return JSON.parse(j); }; }

    // ---- changes (each saves and redraws)
    function pin(ref, sec, index){
      if(countObjects()>=MAXOBJ){ say('The tray holds up to '+MAXOBJ+' objects.'); return false; }
      if(!sec){ sec=newest(); if(!sec){ sec=cleanSec({name:'General'}); T.secs.push(sec); } }
      if(index==null || index>sec.items.length) index=sec.items.length;
      sec.items.splice(index,0,ref); save(); render(); return true;
    }
    function addSection(parentId){
      if(countSecs()>=MAXSEC){ say('The tray holds up to '+MAXSEC+' sections and subsections.'); return; }
      var parent=parentId && find(parentId), s;
      if(parent){ s=cleanSec({name:'Subsection', asc:parent.sec.asc}, true); parent.sec.subs.push(s); parent.sec.shut=false; }
      else { s=cleanSec({name:'Section', asc:globalAsc()}); T.secs.push(s); }
      T.last=s.id; save(); render(); rename(s.id);
    }
    function remove(id){
      var f=find(id); if(!f) return;
      var n=f.sec.items.length + (f.sec.subs||[]).reduce(function(a,u){ return a+u.items.length; },0);
      if(n && !window.confirm('Delete "'+f.sec.name+'" and the '+n+' object'+(n===1?'':'s')+' in it?')) return;
      var back=snapshot(); f.list.splice(f.i,1); save(); render(); say('Deleted "'+f.sec.name+'".', back);
    }
    function unpin(secId, i){
      var f=find(secId); if(!f) return; var back=snapshot(); f.sec.items.splice(i,1); save(); render(); say('Removed.', back);
    }
    function move(from, to, index){      // from {id, i}; to: section id; index in it
      var a=find(from.id), b=find(to); if(!a || !b) return;
      var ref=a.sec.items.splice(from.i,1)[0];
      if(a.sec===b.sec && index>from.i) index--;
      if(index==null || index>b.sec.items.length) index=b.sec.items.length;
      b.sec.items.splice(index,0,ref); save(); render();
    }
    function rename(id){
      var el=tray.querySelector('.ts[data-id="'+id+'"] > .ts-h .ts-name'); if(!el) return;
      var f=find(id), inp=ce('input','ts-in'); inp.type='text'; inp.maxLength=NAMELEN; inp.value=f.sec.name; inp.setAttribute('aria-label','Section name');
      el.replaceWith(inp); inp.focus(); inp.select();
      var done=false;
      function end(ok){ if(done) return; done=true; if(ok){ f.sec.name=cleanName(inp.value, f.sec.name); save(); } render(); }
      inp.addEventListener('keydown',function(e){ if(e.key==='Enter') end(true); else if(e.key==='Escape') end(false); e.stopPropagation(); });
      inp.addEventListener('blur',function(){ end(true); });
    }

    // ---- drawing
    function ensureKatex(){
      if(window.katex || document.getElementById('tray-katex')) return;
      var l=document.createElement('link'); l.rel='stylesheet'; l.href='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css'; document.head.appendChild(l);
      var s=document.createElement('script'); s.id='tray-katex'; s.src='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js'; document.head.appendChild(s);
    }
    function ascSelect(sec){
      var s=ce('select','ts-asc'); s.title='Ascension of the objects in this section'; s.setAttribute('aria-label','Ascension');
      for(var a=0;a<=MAXA;a++){ var o=ce('option',null,'Asc '+a); o.value=String(a); s.appendChild(o); }
      s.value=String(sec.asc);
      s.addEventListener('change',function(){ sec.asc=parseInt(s.value,10); save(); render(); });
      var w=ce('span','ts-sel'); w.appendChild(s); return w;      // enhanceSelects (after each redraw) turns it into the page's own drop-down
    }
    function section(sec, sub, parentAsc){      // a subsection shows its objects at the Ascension of its section
      var box=ce('div','ts'+(sub?' tsub':'')+(sec.shut?' shut':'')); box.setAttribute('data-id',sec.id);
      var h=ce('div','ts-h'), chev=ce('span','chev'), nm=ce('span','ts-name',sec.name), click=null;
      h.appendChild(chev); nm.title='Double-click to rename'; h.appendChild(nm);
      if(!sub){ var add=ce('button','ts-b2 ts-plus','+'); add.type='button'; add.title='Add a subsection'; add.setAttribute('aria-label','Add a subsection'); add.addEventListener('click',function(e){ e.stopPropagation(); addSection(sec.id); }); h.appendChild(add); }
      var x=ce('button','ts-b2 ts-x','×'); x.type='button'; x.title='Delete'; x.setAttribute('aria-label','Delete '+sec.name); x.addEventListener('click',function(e){ e.stopPropagation(); remove(sec.id); }); h.appendChild(x);
      h.addEventListener('click',function(e){      // a click folds; a double click on the name renames (so the fold waits a moment)
        if(e.target.closest('select,button,input')) return;
        clearTimeout(click); click=setTimeout(function(){ sec.shut=!sec.shut; save(); box.classList.toggle('shut',sec.shut); }, 230);
      });
      nm.addEventListener('dblclick',function(e){ clearTimeout(click); e.stopPropagation(); rename(sec.id); });
      box.appendChild(h);
      if(!sub){ var ar=ce('div','ts-ar'); ar.appendChild(ascSelect(sec)); box.appendChild(ar); }      // under the name, so that the name keeps its room on a narrow screen
      var outer=ce('div','ts-b'), b=ce('div','ts-bi'), g=ce('div','tgrid'); outer.appendChild(b); b.appendChild(g);
      sec.items.forEach(function(ref,i){
        var ph=ce('span','cell ph'); ph.setAttribute('data-i',String(i)); g.appendChild(ph);
        objectFor(ref, sub ? parentAsc : sec.asc).then(function(c){
          c.setAttribute('data-i',String(i));
          var px=ce('span','px','×'); px.title='Remove'; px.addEventListener('click',function(e){ e.stopPropagation(); e.preventDefault(); unpin(sec.id,i); }); c.appendChild(px);
          ph.replaceWith(c);
        });
      });
      var empty=!sec.items.length && !(sec.subs||[]).some(function(u){ return u.items.length; });
      if(empty) b.appendChild(ce('p','tray-empty','Drag an object from the wiki here to pin it'));
      (sec.subs||[]).forEach(function(u){ b.appendChild(section(u,true,sec.asc)); });
      box.appendChild(outer);
      return box;
    }
    function render(){
      if(!tray) return;
      var host=tray.querySelector('.tray-body'); host.textContent='';
      T.secs.forEach(function(s){ host.appendChild(section(s,false)); });
      if(!T.secs.length) host.appendChild(ce('p','tray-empty','Drag an object from the wiki here to pin it'));
      var more=ce('div','tray-addrow'); more.title='Add a section'; more.setAttribute('role','button'); more.setAttribute('aria-label','Add a section'); more.tabIndex=0;
      more.addEventListener('click',function(){ addSection(null); }); more.addEventListener('keydown',function(e){ if(e.key==='Enter' || e.key===' '){ e.preventDefault(); addSection(null); } });
      host.appendChild(more);
      if(countObjects()) ensureKatex();
      enhanceSelects();
      layout();
    }
    function layout(){
      var open=T.open;
      document.documentElement.style.setProperty('--tray-w', T.w+'px');
      tray.classList.toggle('closed', !open); body.classList.toggle('tray-open', open);
      var arrow=tray.querySelector('.tray-close'); arrow.title=open ? 'Hide the tray' : 'Show the tray'; arrow.setAttribute('aria-label', arrow.title);
    }
    function setOpen(o){ T.open=o; save(); layout(); }

    // ---- the shell: arrow, heading, resize edge, messages
    function build(){
      body=document.body;
      tray=ce('aside'); tray.id='tray'; tray.setAttribute('aria-label','Pinned objects');
      var close=ce('button','tray-close'); close.type='button'; close.title='Hide the tray'; close.setAttribute('aria-label','Hide the tray'); close.addEventListener('click',function(){ setOpen(!T.open); });
      tray.appendChild(close);
      tray.appendChild(ce('h2','tray-title','Pins'));      // the heading of the tray
      tray.appendChild(ce('div','tray-body'));
      var rz=ce('div','tray-rz'); rz.title='Drag to resize'; tray.appendChild(rz);
      rz.addEventListener('pointerdown',function(e){
        e.preventDefault(); rz.setPointerCapture(e.pointerId); body.classList.add('tray-resizing');
        function mv(ev){ T.w=Math.round(Math.min(Math.max(ev.clientX, MINW), Math.min(900, window.innerWidth*0.7))); document.documentElement.style.setProperty('--tray-w', T.w+'px'); }
        function up(){ rz.removeEventListener('pointermove',mv); rz.removeEventListener('pointerup',up); rz.removeEventListener('pointercancel',up); body.classList.remove('tray-resizing'); save(); }
        rz.addEventListener('pointermove',mv); rz.addEventListener('pointerup',up); rz.addEventListener('pointercancel',up);
      });
      toast=ce('div'); toast.id='tray-toast'; toast.setAttribute('role','status');
      body.appendChild(tray); body.appendChild(toast);
      if(!document.getElementById('tip')){ var t=ce('div'); t.id='tip'; t.setAttribute('role','tooltip'); t.setAttribute('data-own',''); body.appendChild(t); }      // a page without popups of its own
    }

    // ---- dragging (mouse and pen) and the long press (touch)
    var drag=null, ghost=null, hold=null, lastTouch=false;
    function inCatalog(ref){      // a Promise: is the object in the catalogue of its type?
      var p=ref.split('|'), type=p[0], name=p[p.length-1];
      return loadCatalog(type).then(function(cat){ return type==='challenge' ? !!(cat.sections[p[1]] && cat.sections[p[1]].items[name]) : !!cat.items[name]; }).catch(function(){ return false; });
    }
    function pinChecked(ref, sec, index){      // pin once the catalogue says the object can be drawn; otherwise say so
      return inCatalog(ref).then(function(ok){
        if(!ok){ say('This object cannot be pinned.'); return false; }
        var s=sec && find(sec.id); return pin(ref, s ? s.sec : null, index);
      });
    }
    function pinnableCell(t){
      var c=t && t.closest && t.closest('button.cell[data-obj], span.cell[data-obj]'); if(!c) return null;
      var type=c.getAttribute('data-obj').split('|')[0];
      if(PINNABLE.indexOf(type)<0) return null;
      if(!c.closest('#tray') && (document.body.getAttribute('data-nopin')||'').split(' ').indexOf(type)>=0) return null;      // a page can say which types of its own objects are not pinnable (data-nopin on the body); the objects already in the tray still move
      return c;
    }
    function where(x, y){      // the container under the pointer: {id, index} in the tray, or null
      var el=document.elementFromPoint(x,y), box=el && el.closest && el.closest('#tray .ts');
      if(!box){
        if(el && el.closest && el.closest('#tray .tray-body')) return {id:null, index:null};
        return null;
      }
      var c=el.closest('.cell[data-i]'), idx=null;
      if(c && box.contains(c) && c.closest('.ts')===box){ idx=parseInt(c.getAttribute('data-i'),10); var r=c.getBoundingClientRect(); if(x>r.left+r.width/2) idx++; }
      return {id:box.getAttribute('data-id'), index:idx, cell:c};
    }
    function clearMarks(){ tray.querySelectorAll('.drop,.ins-b,.ins-a').forEach(function(e){ e.classList.remove('drop','ins-b','ins-a'); }); }
    function startDrag(e){
      drag.on=true; ghost=drag.c.cloneNode(true); ghost.removeAttribute('data-obj'); ghost.removeAttribute('id'); ghost.classList.add('ghost');
      var r=drag.c.getBoundingClientRect(); ghost.style.width=r.width+'px'; ghost.style.height=r.height+'px'; document.body.appendChild(ghost);
      document.getElementById('tip').style.display='none'; body.classList.add('tray-dragging'); if(window.getSelection) window.getSelection().removeAllRanges();
      if(!drag.fromTray && !T.open) setOpen(true);
    }
    function dragMove(e){
      ghost.style.left=(e.clientX-ghost.offsetWidth/2)+'px'; ghost.style.top=(e.clientY-ghost.offsetHeight/2)+'px';
      clearMarks(); var w=where(e.clientX,e.clientY);
      ghost.classList.toggle('out', !w && drag.fromTray);      // let go outside the tray: removes it
      if(w && w.id){
        var box=tray.querySelector('.ts[data-id="'+w.id+'"]'); if(box) box.classList.add('drop');
        if(w.cell && w.index!=null){ var i=parseInt(w.cell.getAttribute('data-i'),10); w.cell.classList.add(w.index>i ? 'ins-a' : 'ins-b'); }
      }
    }
    function dragEnd(e, cancel){
      var w=cancel ? null : where(e.clientX,e.clientY), d=drag;
      clearMarks(); if(ghost) ghost.remove(); ghost=null; body.classList.remove('tray-dragging'); drag=null;
      if(cancel) return;
      var swallow=function(ev){ ev.stopPropagation(); ev.preventDefault(); }; window.addEventListener('click',swallow,true); setTimeout(function(){ window.removeEventListener('click',swallow,true); },60);      // the click that ends a drag is not a click
      if(!w){ if(d.fromTray) unpin(d.src.id, d.src.i); return; }
      if(!w.id && T.secs.length) return;      // the empty space below the last section is not a section
      var sec=w.id && find(w.id); if(w.id && !sec) return;
      if(d.fromTray){ if(w.id) move(d.src, w.id, w.index); }
      else pinChecked(d.ref, sec && sec.sec, w.index);
    }
    function onDown(e){
      var c=pinnableCell(e.target); if(!c || e.button>0) return;
      var ref=c.getAttribute('data-obj'), inTray=!!c.closest('#tray'), src=null;
      if(inTray){ var box=c.closest('.ts'); src={id:box.getAttribute('data-id'), i:parseInt(c.getAttribute('data-i'),10)}; }
      if(e.pointerType==='touch'){
        lastTouch=true; var x0=e.clientX, y0=e.clientY;
        hold={c:c, timer:setTimeout(function(){
          var h=hold; hold=null; if(!h) return; h.done=true;
          document.getElementById('tip').style.display='none';
          var swallow=function(ev){ ev.stopPropagation(); ev.preventDefault(); }; window.addEventListener('click',swallow,true); setTimeout(function(){ window.removeEventListener('click',swallow,true); },700);
          if(inTray) unpin(src.id, src.i);
          else { var s=newest(); pinChecked(ref, s).then(function(ok){ if(ok) say('Pinned to "'+newest().name+'".'); }); }
        }, 550), x:x0, y:y0};
        return;
      }
      drag={c:c, ref:ref, fromTray:inTray, src:src, x:e.clientX, y:e.clientY, on:false, ok:true};
      if(!inTray){ var d0=drag; inCatalog(ref).then(function(ok){ d0.ok=ok; }); }
    }
    document.addEventListener('pointerdown', onDown, true);
    document.addEventListener('pointermove',function(e){
      if(hold && Math.hypot(e.clientX-hold.x, e.clientY-hold.y)>8){ clearTimeout(hold.timer); hold=null; }
      if(!drag) return;
      if(!drag.on){ if(Math.hypot(e.clientX-drag.x, e.clientY-drag.y)<6) return; if(!drag.ok){ drag=null; return; } startDrag(e); }
      dragMove(e);
    }, true);
    function up(e){ if(hold){ clearTimeout(hold.timer); hold=null; } if(drag){ if(drag.on) dragEnd(e,false); else drag=null; } }
    document.addEventListener('pointerup', up, true);
    document.addEventListener('pointercancel', function(e){ if(hold){ clearTimeout(hold.timer); hold=null; } if(drag){ if(drag.on) dragEnd(e,true); else drag=null; } }, true);
    document.addEventListener('keydown',function(e){ if(e.key==='Escape' && drag && drag.on) dragEnd(e,true); });
    document.addEventListener('contextmenu',function(e){ if(lastTouch && pinnableCell(e.target)) e.preventDefault(); });      // no menu from a long press on an object
    document.addEventListener('dragstart',function(e){ if(drag && e.target.closest && e.target.closest('.cell')) e.preventDefault(); }, true);
    window.addEventListener('storage',function(e){ if(e.key===KEY && tray){ T=load(); render(); } });

    function init(){
      T=load(); build(); render();
    }
    if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', init); else init();
  })();

