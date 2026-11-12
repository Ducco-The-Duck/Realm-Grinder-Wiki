// Proves that a change to popup code or CSS changed nothing visible. Paste into the browser pane (javascript_tool) of a served wiki (python tools/serve_docs.py).
// 1. before changing anything:  git show HEAD:docs/<page>.html > docs/_before_<page>.html
// 2. change the code, rebuild the page
// 3. paste this file, then run:  await snapCompare('_before_research.html', 'research.html', [0,2,3,4])   (the Ascensions to hover at; [0] for a page without a selector)
// 4. delete docs/_before_<page>.html
// It hovers every object of both pages and compares the text, the computed style of every element and the position of each popup (the popup's own class is ignored,
// since a change like that is what moves popup code into the shared script). "different: 0" means the same popups.
async function snapPage(page, ascs){
  const f=document.createElement('iframe'); f.style.cssText='width:1200px;height:900px;position:fixed;left:0;top:0;opacity:0;pointer-events:none';
  f.src='/'+page+'?v='+Date.now(); document.body.appendChild(f); await new Promise(r=>{f.onload=r}); await new Promise(r=>setTimeout(r,1500));
  const d=f.contentDocument, w=f.contentWindow, out=[];
  const P=['font-size','font-family','font-weight','color','background-color','margin-top','margin-bottom','padding-left','padding-top','display','border-top-width','text-transform','white-space','line-height','width','left','top'];
  for(const a of ascs){
    const sel=d.getElementById('asc');
    if(sel){ sel.value=String(a); sel.dispatchEvent(new Event('change',{bubbles:true})); await new Promise(r=>setTimeout(r,300)); }
    for(const c of d.querySelectorAll('button.cell')){
      c.dispatchEvent(new MouseEvent('mouseenter',{bubbles:false}));
      const t=d.getElementById('tip'); let s='';
      if(t && t.style.display!=='none'){
        const walk=(e,depth)=>{ const cs=w.getComputedStyle(e); s+=depth+e.tagName+(depth?'.'+e.className:'')+'['+(e.children.length?'':e.textContent)+']'+P.map(p=>cs.getPropertyValue(p)).join('|')+';'; [...e.children].forEach(x=>walk(x,depth+1)); };
        walk(t,0);
      }
      c.dispatchEvent(new MouseEvent('mouseleave',{bubbles:false}));
      out.push(a+':'+(c.dataset.obj||c.getAttribute('aria-label'))+'=>'+s);
    }
  }
  f.remove(); return out;
}
async function snapCompare(before, after, ascs){
  const B=await snapPage(before, ascs), A=await snapPage(after, ascs), bad=[];
  B.forEach((x,i)=>{ if(x.replace(/^[^=]*=>/,'')!==(A[i]||'').replace(/^[^=]*=>/,'')) bad.push(i); });
  return {objects:B.length, after:A.length, different:bad.length, first:bad.slice(0,3).map(i=>B[i].split('=>')[0])};
}
