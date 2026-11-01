"""Generate docs/spells.html from data/spells.json and data/spells_overview.json (descriptions, tags): every spell as an icon with a hover tooltip.

    python -I tools/build_spells_page.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
spells = json.load(open(os.path.join(ROOT, 'data', 'spells.json'), encoding='utf8'))
ov = json.load(open(os.path.join(ROOT, 'data', 'spells_overview.json'), encoding='utf8'))['spells']
tier_up = {}      # spell -> its tier upgrades (Magic upgrades), from the upgrade pages' data
for u in json.load(open(os.path.join(ROOT, 'data', 'upgrade_pages.json'), encoding='utf8'))['magic']:
    if u.get('spell'): tier_up.setdefault(u['spell'], []).append(u)

# formulas shared by all spells ("@name" in data/spells_overview.json)
SHARED = {
    'penalty': [
        {'latex': r'p = 1 \quad (A = 0)'},
        {'latex': r'p = \dfrac{0.1}{A} \quad (A \ge 1,\ \text{no tier unlocked})'},
        {'latex': r'p = \dfrac{0.5}{A} \cdot 0.5^{\,w\,(A - T + 1)} \quad (A \ge 1,\ \text{tiers unlocked})',
         'vars': [['A', 'your Ascension number'], ['T', 'the tier the spell is cast at (1 for a spell cast once)'],
                  ['w', '$1$ if T - 1 is not above A, otherwise $1/2$']]}],
}

import re as _re


def _num(t):
    """'2h cumulative evil spells activity ...' -> (7200, 'cumulative evil spells activity ...', True): the amount (seconds for a time), the label, whether it is a time"""
    m = _re.match(r'^(\d+(?:\.\d+)?(?:e\+?\d+)?)(%)?\s*(h|m|s)?\s+(?:of\s+)?(.*)$', t)
    if not m: return None
    v, pct, u, lab = float(m.group(1)), bool(m.group(2)), m.group(3), m.group(4)
    lab = lab.replace(' in this Reincarnation', ' (this Reincarnation)')
    if 'activity' in lab and 'activity time' not in lab: lab = lab.replace('activity', 'activity time', 1)
    return v * {'h': 3600, 'm': 60, 's': 1}.get(u, 1), lab, bool(u), pct


def _fit(vals):
    """vals: {tier: amount}; the amount as a formula in n: k(n-1) or a + bn, else None"""
    ns = sorted(vals)
    k = vals[ns[0]] / (ns[0] - 1)
    if all(abs(vals[n] - k * (n - 1)) < 1e-9 for n in ns): return ('prop', k)
    b = (vals[ns[1]] - vals[ns[0]]) / (ns[1] - ns[0]); a = vals[ns[0]] - b * ns[0]
    if all(abs(vals[n] - (a + b * n)) < 1e-9 for n in ns): return ('lin', a, b)
    r = vals[ns[1]] / vals[ns[0]]      # a geometric series: a r^(n-1)
    if all(abs(vals[n] / vals[ns[0]] / r ** (n - ns[0]) - 1) < 1e-3 for n in ns): return ('geo', vals[ns[0]] / r ** (ns[0] - 1), r)
    return None


def _g(x):
    """a number for a formula: digits, or a power of ten when it is a large one"""
    import math
    if x < 1e9: return str(int(x)) if x == int(x) else f'{x:g}'
    e = round(math.log10(x))
    if abs(x - 10 ** e) < 1e-6 * x: return f'10^{{{e}}}'
    e = math.floor(math.log10(x))
    return f'{x / 10 ** e:g} \cdot 10^{{{e}}}'


def tier_requirement_list(ups, name=''):
    """the unlock requirements of the tier upgrades as lines in the tier n ($...$ is set as a formula), and a note naming amounts that depend on the Ascension"""
    out, note = [], ''
    out.append('Ascension $n - 1$' if all(u['asc_min'] == u['spell_tier'] - 1 for u in ups) else 'Ascension $1$')
    parts = {}      # part index -> tier -> Ascension -> text
    for u in ups:
        for a, t in u['unlock_by_asc'].items():
            ps = t.removeprefix('To unlock, you need to have at least ').rstrip('.').split(' and have at least ')
            for i, x in enumerate(ps): parts.setdefault(i, {}).setdefault(u['spell_tier'], {})[a] = x
    for i in sorted(parts):
        tiers = parts[i]
        asc = sorted(next(iter(tiers.values())))
        parsed = {n: {a: _num(x) for a, x in v.items()} for n, v in tiers.items()}
        first = next(iter(next(iter(parsed.values())).values()))
        if any(q is None for v in parsed.values() for q in v.values()):
            out.append(next(iter(tiers.values()))[asc[0]]); continue
        lab = (' seconds ' if first[2] else ' ') + first[1]
        same = all(len({parsed[n][a][0] for a in asc}) == 1 for n in parsed)
        if same:
            f = _fit({n: parsed[n][asc[0]][0] for n in parsed})
            if f is None: out.append(first[1]); continue
            if f[0] == 'prop': rhs = _g(f[1]) + r'\,(n - 1)'
            elif f[0] == 'lin': rhs = _g(f[2]) + r'\,n + ' + _g(f[1])
            else:
                import math
                ea, er = round(math.log10(f[1]), 2), round(math.log10(f[2]), 2)
                rhs = f'10^{{{_g(er)}\,n}}' if ea == er else f'10^{{{_g(ea)}}} \cdot 10^{{{_g(er)}\,(n - 1)}}'
            out.append('$' + rhs + (r'\%' if first[3] else '') + '$' + lab)
        else:      # the amount depends on the Ascension: k (n - 1) with a k per Ascension
            ks = {}
            for a in asc:
                f = _fit({n: parsed[n][a][0] for n in parsed})
                if f is None or f[0] != 'prop': ks = None; break
                ks[a] = f[1]
            if ks is None: out.append(first[1]); continue
            out.append(r'$k\,(n - 1)$' + lab)
            note = '$k$ is ' + ', '.join(f'{_g(v)} at Ascension {a}' for a, v in ks.items()) + '.'
            if name == 'Call to Arms': note = '$k$ is $60000 / A$ below Ascension 4 and $10000 / A$ from Ascension 4, with $A$ your Ascension number.'
    return out, note


def tier_sections(name, hand):
    """the generated sections of a spell with tiers: the tier requirements, the cost of higher tiers, the bonus at higher tiers and the offline bonus"""
    ups = sorted(tier_up.get(name, []), key=lambda u: u['spell_tier'])
    if not ups: return []
    req = tier_requirement_list(ups, name)
    out = [{'title': 'Spell tiers',
            'text': 'Casting the spell again while it is active raises its tier by one, up to the highest tier you have unlocked. Higher tiers are unlocked by a magic upgrade with the following requirements:',
            'lists': [{'title': 'Tier $n$:', 'items': req[0]}], 'after': req[1]},
           {'title': 'Cost of higher tiers',
            'text': 'The first cast costs the normal mana cost. Casting again at a higher tier costs more:',
            'formulas': [{'latex': r'C = c^{\,1 + (0.6 - R)\,T}',
                          'vars': [['C', 'the mana cost of the cast'], ['c', "the spell's mana cost after all reductions"],
                                   ['R', 'the reduction of the tier cost scaling, for example 0.1 from Sequence (S1275)'],
                                   ['T', "the spell's current tier (1 after the first cast)"]]}]}]
    bonus = [dict(b) for b in hand]
    if any('Offline' in t['text'] for t in ups[0]['description']):      # the offline production bonus every tier adds
        bonus.append({'title': 'Offline production',
                      'text': 'Each unlocked tier also increases offline production:',
                      'formulas': [{'latex': r'v = \left( x^{\frac{2}{\max(3,\,A)}} + y^{\frac{2}{\max(3,\,A)}} \right)^{0.4}',
                                    'vars': [['v', 'the offline production bonus of a tier, in %'], ['x', 'your mana regeneration per second'],
                                             ['y', 'your Maximum Mana'], ['A', 'your Ascension number']]}],
                      'after': 'This bonus is affected by the regular Ascension penalty, which starts at Ascension $N$ for tier $N$.'})
    return out + bonus


def spell_detail(name):
    dt = dict(ov[name].get('detail', {}))
    secs = []
    for sec in dt.get('sections', []):
        sec = dict(sec)
        if 'formulas' in sec:
            fs = []
            for f in sec['formulas']:
                fs += SHARED[f[1:]] if isinstance(f, str) else [f]
            sec['formulas'] = fs
        secs.append(sec)
    secs += tier_sections(name, dt.get('tier_sections', []))
    out = {'sections': secs}
    if 'note' in dt: out['note'] = dt['note']
    return out


data = json.dumps([{'name': s['name'], 'icon': s['icon'] + '.png', 'cost': s.get('cost'), 'ticks': s.get('duration'),
                    'desc': ov[s['name']]['description'], 'tags': ov[s['name']]['tags'], 'detail': spell_detail(s['name'])} for s in spells],
                  ensure_ascii=False, separators=(',', ':')).replace('</', '<\/')

html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/bg.css"><script src="assets/bg.js" defer></script>
<title>Realm Grinder Spells</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<style>
:root{--bg:#fbfaf7;--fg:#1f1c17;--muted:#6b655a;--line:#ddd6c8;--card:#fff;--cell:#f0eadc;--cellhi:#e4d8bd;--accent:#8a5a14;--shadow:0 6px 24px rgba(0,0,0,.18)}
@media (prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece6d8;--muted:#a39b8a;--line:#383229;--card:#201d18;--cell:#2b261f;--cellhi:#3a3328;--accent:#e0a64a;--shadow:0 6px 24px rgba(0,0,0,.6)}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:780px;margin:0 auto;padding:16px 16px 80px}
.sub{color:var(--muted);margin:0 0 18px}
.grid{display:flex;flex-wrap:wrap;gap:10px}
.cell{width:89px;height:89px;border:1px solid var(--line);border-radius:8px;background:var(--cell);padding:3px;
  display:flex;align-items:center;justify-content:center;cursor:default;font:inherit;color:inherit}
.cell:hover,.cell:focus-visible{background:var(--cellhi);outline:2px solid var(--accent);outline-offset:-1px}
.cell img{max-width:100%;max-height:100%;image-rendering:pixelated;pointer-events:none}
#tip{position:fixed;z-index:50;width:min(340px,calc(100vw - 16px));padding:10px 12px;border-radius:8px;background:var(--card);
  border:1px solid var(--line);box-shadow:var(--shadow);pointer-events:none;display:none;font-size:.92rem}
#tip b{display:block;font-size:1rem}
#tip p{margin:4px 0 0}
.tags{display:flex;gap:4px;flex-wrap:wrap;align-items:flex-start;margin-top:4px}
.chip{font-size:.72em;height:1.2em;line-height:1em;box-sizing:border-box;white-space:nowrap;padding:0 .5em;border-radius:9px;border:1px solid var(--line);background:var(--cell);color:var(--muted)}
.chip{border-color:transparent}
.chip.c-tax-collection{background:#c9a227;color:#2a1f00}
.chip.c-common{background:#8b5a2b;color:#fff}
.chip.c-pseudo-faction{background:repeating-linear-gradient(45deg,#7a35b0 0 6px,#141414 6px 12px);color:#fff;text-shadow:0 0 2px #000,0 0 2px #000}
.chip.c-alignment{background:#141414;color:#eee;border-color:#555}
.chip.c-good{background:#8fd0ff;color:#0a2a40}
.chip.c-evil{background:#c0392b;color:#fff}
.chip.c-neutral{background:#9a9a9a;color:#111}
.chip.c-order{background:#f4f4f4;color:#222}
.chip.c-chaos{background:#8ee68e;color:#0d3a0d}
.chip.c-balance{background:#fff3a0;color:#4a3f00}
.chip.c-faction{background:#8e44ad;color:#fff}
.chip.c-event{background:#ff9ec7;color:#5a0a2e}
#detail .chip{font-size:.8em}
#detail .note{color:var(--muted);opacity:.8;font-size:.9rem;margin:6px 0 0}
#detail h3{margin:16px 0 0;color:var(--accent)}
#tip .hint{color:var(--muted);opacity:.75;font-size:.8rem;margin-top:8px}
#detail{margin-top:22px;scroll-margin-top:12px}
#detail h2{margin:0 0 4px;color:var(--accent)}
#detail .empty{color:var(--muted)}
#detail p.stats{margin:4px 0 0;font-weight:600;display:flex;flex-wrap:wrap;gap:0 20px}
#detail .mana{color:#1f6fbf}
#detail .dur{color:#4a4438}
@media (prefers-color-scheme:dark){#detail .mana{color:#6cb4ff}#detail .dur{color:#ece6d8}}
#detail p{margin:4px 0}
#detail .ltitle{margin:8px 0 0;font-weight:600}
#detail ul.items{margin:2px 0 6px;padding-left:0;list-style:none}
#detail ul.items li{margin:0 0 2px;padding-left:16px;position:relative}
#detail ul.items li::before{content:"";position:absolute;left:3px;top:.62em;width:5px;height:5px;border-radius:50%;background:currentColor;opacity:.7}
#detail hr.fsep{border:0;border-top:1px solid var(--line);margin:10px 0}
#detail .formula{padding:2px 0;overflow-x:auto;overflow-y:hidden}
#detail ul.vars{margin:2px 0 6px;padding-left:20px}
#detail ul.vars li{margin:0}
#detail ul.vars b{display:inline;font-family:inherit;font-size:inherit}
/*SEARCH_CSS*/
</style>
</head>
<body>
<main>
<nav><a href="index.html">Home</a><a href="spells.html" aria-current="page">Spells</a></nav>
<h1>Spells</h1>
<p>Pseudo-Faction spells count as Faction spells for stats, but are not affected by effects that affect Faction spells.</p>
<p class="sub">Hover a spell for an overview, click it for the details.</p>
<div class="grid" id="root"></div>
<section id="detail" hidden></section>
</main>
<div id="tip" role="tooltip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var SPELLS = JSON.parse(document.getElementById('data').textContent), root=document.getElementById('root'), tip=document.getElementById('tip');
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  function chips(s){
    var d=el('div','tags');
    (s.tags||s).forEach(function(t){ d.appendChild(el('span','chip c-'+t.replace(/\*$/,'').toLowerCase().replace(/[^a-z0-9]+/g,'-'),t)); });
    return d;
  }
  function dur(ticks){      // durations are stored in ticks, 30 per second
    var s=Math.round(ticks/30), m=Math.floor(s/60), r=s%60, out=[];
    function u(n,w){ return n+' '+w+(n===1?'':'s'); }
    if(m) out.push(u(m,'minute'));
    if(r||!m) out.push(u(r,'second'));
    return out.join(' ');
  }
  var detail=document.getElementById('detail');
  function showDetail(s){
    detail.hidden=false; detail.textContent=''; detail.appendChild(el('h2',null,s.name));
    if(s.tags.length) detail.appendChild(chips(s));
    var st=el('p','stats');
    if(s.cost!=null) st.appendChild(el('span','mana','Base Mana Cost: '+s.cost.toLocaleString('en-US')));
    if(s.ticks!=null) st.appendChild(el('span','dur','Base Duration: '+dur(s.ticks)));
    if(st.children.length) detail.appendChild(st);
    var dd=s.detail||{};
    if(dd.note) detail.appendChild(el('p','note',dd.note));
    (dd.sections||[]).forEach(function(c){
      detail.appendChild(el('h3',null,c.title));
      if(c.tags) detail.appendChild(chips(c.tags));
      if(c.text) detail.appendChild(richText('p',null,c.text));
      (c.lists||[]).forEach(function(l){
        if(l.title) detail.appendChild(richText('p','ltitle',l.title));
        var ul=el('ul','items'); l.items.forEach(function(t){ ul.appendChild(richText('li',null,t)); }); detail.appendChild(ul);
      });
      (c.formulas||[]).forEach(function(f,fi,fa){
        var d=el('div','formula'); math(f.latex,d); detail.appendChild(d);
        if(f.vars){ var ul=el('ul','vars'); f.vars.forEach(function(v){ var li=el('li'), b=el('b'); math(v[0],b); li.appendChild(b); li.appendChild(document.createTextNode(' — ')); li.appendChild(richText('span',null,v[1])); ul.appendChild(li); }); detail.appendChild(ul); }
        if(f.vars && fi<fa.length-1) detail.appendChild(el('hr','fsep'));      // a line between formulas that each come with their variables
      });
      if(c.after) detail.appendChild(richText('p',null,c.after));
    });
    if(!(dd.sections||[]).length) detail.appendChild(el('p','empty','No detailed information has been written yet.'));
    detail.scrollIntoView({behavior:'smooth',block:'nearest'});
  }
  function math(tex, node){
    if(window.katex){ try{ katex.render('\\displaystyle '+tex,node,{throwOnError:false,displayMode:false}); return; }catch(e){} }
    node.textContent=tex;
  }
  function richText(tag, cls, text){      // text with $formula$ parts set as formulas
    var e=el(tag,cls);
    text.split('$').forEach(function(part,i){
      if(i%2===0){ if(part) e.appendChild(document.createTextNode(part)); return; }
      var m=el('span'); e.appendChild(m);
      if(window.katex){ try{ katex.render(part,m,{throwOnError:false}); return; }catch(x){} }
      m.textContent=part;
    });
    return e;
  }
  function hideTip(){ tip.style.display='none'; }
  function showTip(s, anchor){
    tip.textContent=''; tip.appendChild(el('b',null,s.name));
    if(s.tags.length) tip.appendChild(chips(s));
    tip.appendChild(el('p',null,s.desc));
    if(s.cost!=null) tip.appendChild(el('p',null,'Base mana cost: '+s.cost.toLocaleString('en-US')));
    if(s.ticks!=null) tip.appendChild(el('p',null,'Base duration: '+dur(s.ticks)));
    tip.appendChild(el('p','hint','Click the spell icon to show detailed information.'));
    tip.style.display='block';
    var a=anchor.getBoundingClientRect(), t=tip.getBoundingClientRect();
    var x=Math.min(Math.max(8,a.left+a.width/2-t.width/2),innerWidth-t.width-8);
    var up=a.top-t.height-8>=8;
    tip.style.left=x+'px'; tip.style.top=(up?a.top-t.height-8:a.bottom+8)+'px';
  }
  window.addEventListener('scroll',hideTip,{passive:true});
  SPELLS.forEach(function(s){
    var c=el('button','cell'), im=el('img'); c.type='button'; im.src='assets/icons/'+s.icon; im.alt=s.name; c.appendChild(im);
    c.addEventListener('mouseenter',function(){ showTip(s,c); }); c.addEventListener('focus',function(){ showTip(s,c); });
    c.addEventListener('click',function(){ hideTip(); showDetail(s); });
    c.addEventListener('mouseleave',hideTip); c.addEventListener('blur',hideTip);
    root.appendChild(c);
  });
/*SEARCH_JS*/
})();
</script>
</body>
</html>
'''
import search_snippet
page = search_snippet.apply(html.replace('__DATA__', data), '', 'spells.html')
open(os.path.join(ROOT, 'docs', 'spells.html'), 'w', encoding='utf8').write(page)
print('docs/spells.html', len(page) // 1024, 'KB;', len(spells), 'spells')
