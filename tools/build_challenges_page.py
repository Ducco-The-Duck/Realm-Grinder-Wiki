"""Generate docs/challenges.html from data/challenges.json.

    python -I tools/build_challenges_page.py
"""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
factions = json.load(open(os.path.join(ROOT, 'data', 'challenges.json'), encoding='utf8'))
icons = json.load(open(os.path.join(ROOT, 'data', 'icons.json')))
sprites = json.load(open(os.path.join(ROOT, 'data', 'sprites.json')))
icon_dir = os.path.join(ROOT, 'docs', 'assets', 'icons')
os.makedirs(icon_dir, exist_ok=True)


def icon_file(n):
    if not n or n not in sprites: return None
    dst = os.path.basename(sprites[n][0]['file'])
    path = os.path.join(icon_dir, dst)
    if not os.path.exists(path):
        src = os.path.join(ROOT, sprites[n][0]['file'])
        if os.path.exists(src): shutil.copy(src, path)
    if not os.path.exists(path): return None
    icons[n] = dst
    return dst


def item(f, it):
    return {'n': it['name'], 'i': icon_file(it['icon']), 'su': it['spell_upgrade'], 'num': it['number'],
            'fl': it['flavor'], 'q': it['requirements'], 'c': it['challenge'], 'r': it['rewards'],
            'f': [{'l': g['latex'], 'v': g['vars'], 'lb': g['label']} for g in it['formulas']], 'a': it['applies_to'], 'sh': any(g['shown'] for g in it['formulas']), 'nt': it['note'],
            'g': it['game_name']}


sections = [{'id': f['id'], 'name': f['name'], 'kind': f['kind'], 'items': [item(f, it) for it in f['items']]}
            for f in factions]
json.dump(icons, open(os.path.join(ROOT, 'data', 'icons.json'), 'w'), indent=0, sort_keys=True)
data = json.dumps(sections, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
import html as _html
bugs = [(it['name'], it['bug']) for f in factions for it in f['items'] if it.get('bug')]
bug_html = ''.join(f'<p><b>Known bug, {_html.escape(n)}:</b> {_html.escape(t)}</p>' for n, t in bugs)
n_ch = sum(1 for f in factions for it in f['items'] if not it['spell_upgrade'])

html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/bg.css"><script src="assets/bg.js" defer></script>
<title>Realm Grinder Challenges</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<style>
:root{--bg:#fbfaf7;--fg:#1f1c17;--muted:#6b655a;--line:#ddd6c8;--card:#fff;--cell:#f0eadc;--cellhi:#e4d8bd;--accent:#8a5a14;--shadow:0 6px 24px rgba(0,0,0,.18)}
@media (prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece6d8;--muted:#a39b8a;--line:#383229;--card:#201d18;--cell:#2b261f;--cellhi:#3a3328;--accent:#e0a64a;--shadow:0 6px 24px rgba(0,0,0,.6)}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:620px;margin:0 auto;padding:16px 16px 80px}
nav{display:flex;gap:14px;flex-wrap:wrap;margin:0 0 18px;font-size:.95rem}
nav a{color:var(--muted);text-decoration:none}
nav a[aria-current]{color:var(--fg);font-weight:600;border-bottom:2px solid var(--accent)}
h1{margin:0 0 4px;font-size:1.7rem}
.sub{color:var(--muted);margin:0 0 20px}
.bugs p{margin:0 0 20px;padding:8px 12px;border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:6px;background:var(--card);font-size:.92rem}
section{margin:0 0 26px}
h2{font-size:1.05rem;margin:0 0 8px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h2 small{font-weight:400;color:var(--muted);margin-left:8px}
.grid{display:grid;grid-template-columns:repeat(7,minmax(0,70px));justify-content:start;gap:6px}
.cell{aspect-ratio:1;border:1px solid var(--line);border-radius:8px;background:var(--cell);padding:3px;
  display:flex;align-items:center;justify-content:center;cursor:default;font:inherit;color:inherit}
.cell.su{border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent)}
.cell:hover,.cell:focus-visible{background:var(--cellhi);outline:2px solid var(--accent);outline-offset:-1px}
.cell img{max-width:100%;max-height:100%;image-rendering:pixelated;pointer-events:none}
#tip{position:fixed;z-index:50;width:min(420px,calc(100vw - 16px));padding:10px 12px;border-radius:8px;background:var(--card);
  border:1px solid var(--line);box-shadow:var(--shadow);pointer-events:none;display:none;font-size:.92rem}
#tip b.t{display:block;font-size:1rem}
#tip .kind{display:block;color:var(--muted);font-size:.82rem}
#tip .lbl{display:block;color:var(--accent);font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;margin-top:8px}
#tip ul{margin:2px 0 0;padding-left:18px}
#tip p{margin:3px 0 0}
#tip .chal{font-weight:600}
#tip .muted,#tip .more{color:var(--muted)}
#tip ul.vars{list-style:none;padding-left:0;margin:4px 0}
#tip ul.vars li{margin:2px 0}
#tip .formula{padding:4px 0;overflow-wrap:anywhere}
#tip .flabel{margin-top:6px;font-weight:600}
#tip .fsep{border-top:1px solid var(--line);margin:8px 0 2px}
#tip .flavor{font-style:italic;color:var(--muted)}
#tip .al{margin-top:6px}
#tip .al b{color:var(--fg)}
/*SEARCH_CSS*/
</style>
</head>
<body>
<main>
<nav><a href="index.html">Home</a><a href="trophies.html">Trophies</a><a href="archaeology.html">Archaeology</a><a href="research.html">Research</a><a href="challenges.html" aria-current="page">Challenges</a><a href="upgrades.html">Upgrades</a></nav>
<h1>Challenges</h1>
<p class="sub">__TOTAL__ challenges. The first square of each faction is the permanent spell upgrade you get for completing all of that faction's challenges. Hover an icon for the requirements, the challenge itself, the reward and its formula. Everything from the Mercenary section on is read from the game code and has not been checked in the game.</p>
<!--SEARCH_BAR-->
<div class="bugs">__BUGS__</div>
<div id="root"></div>
</main>
<div id="tip" role="tooltip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var SECTIONS = JSON.parse(document.getElementById('data').textContent);
  var root=document.getElementById('root'), tip=document.getElementById('tip');
/*SEARCH_JS*/
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  function math(tex, host){
    if(window.katex){ try{ katex.render('\\displaystyle '+tex, host, {throwOnError:false}); return; }catch(e){} }
    host.textContent = tex;
  }
  function formulas(parent, list){
    var many=list.length>1, seen={};
    parent.appendChild(el('span','lbl',many?'Formulas':'Formula'));
    list.forEach(function(f,i){
      if(i>0) parent.appendChild(el('div','fsep'));
      var vs=many?'v_{'+(i+1)+'}':'v';
      if(f.lb){
        var lab=el('div','flabel'); var lm=el('span'); math(vs,lm); lab.appendChild(lm);
        lab.appendChild(document.createTextNode(' — '+f.lb)); parent.appendChild(lab);
      }
      var d=el('div','formula'); var m=el('span'); math(f.l.replace(/^v(_\{\d+\})? = /, vs+' = '), m); d.appendChild(m); parent.appendChild(d);
      var ul=el('ul','vars'), n=0;
      f.v.forEach(function(v){
        var k=v.symbol+'|'+v.text; if(seen[k]) return; seen[k]=1; n++;
        var li=el('li'); var b=el('b'); b.style.display='inline'; math(v.symbol,b); li.appendChild(b);
        li.appendChild(document.createTextNode(' — '+v.text)); ul.appendChild(li);
      });
      if(n) parent.appendChild(ul);
    });
  }
  function showTip(sec, it, anchor){
    tip.textContent='';
    tip.appendChild(el('b','t',it.n));
    if(it.su){
      tip.appendChild(el('span','kind','Permanent spell upgrade for '+sec.name));
    } else {
      tip.appendChild(el('span','kind',sec.name+' challenge '+it.num));
      tip.appendChild(el('span','lbl','Requirements'));
      var ul2=el('ul'); it.q.forEach(function(q){ ul2.appendChild(el('li',null,q)); }); tip.appendChild(ul2);
      tip.appendChild(el('span','lbl','The challenge'));
      tip.appendChild(el('div','chal',it.c));
    }
    tip.appendChild(el('span','lbl',it.su ? 'Effect' : 'Reward'));
    it.r.forEach(function(t){ tip.appendChild(el('p',null,t)); });
    if(it.f.length){
      formulas(tip, it.f);
      if(it.nt) tip.appendChild(el('div','more',it.nt));
      else if(it.sh) tip.appendChild(el('div','more','v is the number the game shows for the reward.'));
    }
    if(it.a){
      tip.appendChild(el('span','lbl','Reward can be used'));
      var a = it.a, txt;
      if(a.indexOf('any ')===0) txt = 'While playing with '+a+'.';
      else txt = 'Only while playing with the '+a+' faction.';
      tip.appendChild(el('div',null,txt));
    }
    if(it.fl){ tip.appendChild(el('span','lbl','Flavor text')); tip.appendChild(el('div','flavor',it.fl)); }
    tip.style.display='block';
    var r=anchor.getBoundingClientRect(), t=tip.getBoundingClientRect();
    var x=Math.min(Math.max(8,r.left+r.width/2-t.width/2), window.innerWidth-t.width-8);
    var y=r.top-t.height-8; if(y<8) y=r.bottom+8;
    if(y+t.height>window.innerHeight-8) y=Math.max(8,window.innerHeight-t.height-8);
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }
  function hideTip(){ tip.style.display='none'; }
  document.addEventListener('scroll',hideTip,true);
  document.addEventListener('click',function(e){ if(!e.target.closest('.cell')) hideTip(); });
  SECTIONS.forEach(function(s){
    var sec=el('section'); var h=el('h2',null,s.name); h.appendChild(el('small',null,s.kind)); sec.appendChild(h);
    var g=el('div','grid');
    s.items.forEach(function(it){
      var b=el('button','cell'+(it.su?' su':'')); b.type='button';
      var tn=trimName(s.name); if(tn) b.classList.add('t-'+tn);
      b.setAttribute('aria-label', it.n);
      b._s=normS([it.n,it.fl,it.c,it.r.join(' '),s.name,it.a].join(' '));
      if(it.i){ var img=el('img'); img.src='assets/icons/'+encodeURIComponent(it.i); img.alt=''; img.loading='lazy'; b.appendChild(img); }
      b.addEventListener('mouseenter',function(){ showTip(s,it,b); });
      b.addEventListener('mouseleave',hideTip);
      b.addEventListener('focus',function(){ showTip(s,it,b); });
      b.addEventListener('blur',hideTip);
      b.addEventListener('click',function(e){ e.stopPropagation(); showTip(s,it,b); });
      g.appendChild(b);
    });
    sec.appendChild(g); root.appendChild(sec);
  });
  searchInit(root);
})();
</script>
</body>
</html>
'''
import search_snippet
html = html.replace('__BUGS__', bug_html).replace('__DATA__', data).replace('__TOTAL__', str(n_ch))
html = search_snippet.apply(html, 'Search challenge names, flavor text, challenge and reward descriptions')
open(os.path.join(ROOT, 'docs', 'challenges.html'), 'w', encoding='utf8').write(html)
print('docs/challenges.html', len(html) // 1024, 'KB;', [s['name'] for s in sections])
