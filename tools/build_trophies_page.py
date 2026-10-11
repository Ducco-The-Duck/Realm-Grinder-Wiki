"""Generate docs/trophies.html (self-contained, data embedded) from data/trophies.json.

    python -I tools/build_trophies_page.py
"""
import json, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
trophies = json.load(open(os.path.join(ROOT, 'data', 'trophies.json'), encoding='utf8'))
icons = json.load(open(os.path.join(ROOT, 'data', 'icons.json')))


def pretty(t):
    if not t: return 'Other'
    t = re.sub(r'\d+$', '', t)
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', t)


rows = []
for t in trophies:
    rows.append({
        'n': t['name'], 'r': t['requirement'], 'i': icons.get(t['icon']) if t['icon'] else None,
        'a': t['alignment'], 't': pretty(t['type']), 'g': t['group'], 'o': t['order'],
    })
data = json.dumps(rows, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
listed = sum(1 for r in rows if r['g'] == 'trophy')

html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Realm Grinder Trophies</title>
<style>
:root{--bg:#fbfaf7;--fg:#1f1c17;--muted:#6b655a;--line:#ddd6c8;--card:#fff;--accent:#8a5a14;--chip:#f0eadc}
@media (prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece6d8;--muted:#a39b8a;--line:#383229;--card:#201d18;--accent:#e0a64a;--chip:#2b261f}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 16px 64px}
h1{margin:0 0 4px;font-size:1.7rem}
.sub{color:var(--muted);margin:0 0 18px}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:12px}
input[type=search],select{font:inherit;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg)}
input[type=search]{flex:1 1 240px;min-width:0}
label.chk{display:flex;gap:6px;align-items:center;color:var(--muted);font-size:.92rem}
.count{color:var(--muted);font-size:.92rem;margin:6px 0 10px}
.list{border:1px solid var(--line);border-radius:10px;background:var(--card);overflow:hidden}
.row{display:grid;grid-template-columns:56px 1fr;gap:12px;padding:10px 14px;border-top:1px solid var(--line);align-items:center}
.row:first-child{border-top:0}
.ico{width:48px;height:48px;display:flex;align-items:center;justify-content:center}
.ico img{max-width:48px;max-height:48px;image-rendering:pixelated}
.name{font-weight:600}
.req{color:var(--muted);white-space:pre-line}
.tags{margin-top:4px;display:flex;gap:6px;flex-wrap:wrap}
.tag{font-size:.75rem;background:var(--chip);border-radius:999px;padding:1px 8px;color:var(--muted)}
.tag.a1{color:#2f7a3e}.tag.a2{color:#a8322a}.tag.a3{color:#6a4e9a}
.empty{padding:24px;text-align:center;color:var(--muted)}
@media (max-width:520px){.row{grid-template-columns:44px 1fr;padding:10px}}
</style>
</head>
<body>
<main>
<h1>Trophies</h1>
<p class="sub">__LISTED__ trophies and how to unlock each one. Extracted from the game files.</p>
<div class="controls">
  <input id="q" type="search" placeholder="Search name or requirement…" aria-label="Search trophies">
  <select id="align" aria-label="Alignment">
    <option value="">Any alignment</option><option value="1">Good</option><option value="2">Evil</option><option value="3">Neutral</option><option value="0">No alignment</option>
  </select>
  <select id="type" aria-label="Type"><option value="">All types</option></select>
  <label class="chk"><input id="extra" type="checkbox"> Include event &amp; special entries</label>
</div>
<div class="count" id="count"></div>
<div class="list" id="list"></div>
</main>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var ALL = JSON.parse(document.getElementById('data').textContent);
  var qEl=document.getElementById('q'), aEl=document.getElementById('align'), tEl=document.getElementById('type'),
      xEl=document.getElementById('extra'), list=document.getElementById('list'), count=document.getElementById('count');
  var GROUP={special:'Special',seasonal:'Seasonal event',excavation:'Excavation find','event-quest':'Event quest step'};
  var ALIGN={1:'Good',2:'Evil',3:'Neutral'};
  var types={};
  ALL.forEach(function(r){ if(r.g==='trophy') types[r.t]=(types[r.t]||0)+1; });
  Object.keys(types).sort().forEach(function(t){
    var o=document.createElement('option'); o.value=t; o.textContent=t+' ('+types[t]+')'; tEl.appendChild(o);
  });
  function esc(s){ return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); }
  function render(){
    var q=qEl.value.trim().toLowerCase(), al=aEl.value, ty=tEl.value, ex=xEl.checked;
    var rows=ALL.filter(function(r){
      if(r.g!=='trophy' && !ex) return false;
      if(al!=='' && String(r.a)!==al) return false;
      if(ty && r.t!==ty) return false;
      if(q && (r.n+' '+r.r).toLowerCase().indexOf(q)<0) return false;
      return true;
    });
    count.textContent = rows.length+' shown';
    if(!rows.length){ list.innerHTML='<div class="empty">No trophies match.</div>'; return; }
    list.innerHTML = rows.map(function(r){
      var img = r.i ? '<img loading="lazy" src="assets/icons/'+encodeURIComponent(r.i)+'" alt="">' : '';
      var tags = [];
      if(ALIGN[r.a]) tags.push('<span class="tag a'+r.a+'">'+ALIGN[r.a]+'</span>');
      if(r.g!=='trophy') tags.push('<span class="tag">'+esc(GROUP[r.g]||r.g)+'</span>');
      else tags.push('<span class="tag">'+esc(r.t)+'</span>');
      return '<div class="row"><div class="ico">'+img+'</div><div><div class="name">'+esc(r.n)+'</div>'+
             '<div class="req">'+esc(r.r||'(no requirement text)')+'</div><div class="tags">'+tags.join('')+'</div></div></div>';
    }).join('');
  }
  [qEl,aEl,tEl,xEl].forEach(function(el){ el.addEventListener('input',render); el.addEventListener('change',render); });
  render();
})();
</script>
</body>
</html>
'''
html = html.replace('__DATA__', data).replace('__LISTED__', str(listed))
os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
open(os.path.join(ROOT, 'docs', 'trophies.html'), 'w', encoding='utf8').write(html)
print('docs/trophies.html', len(html) // 1024, 'KB,', len(rows), 'rows')
