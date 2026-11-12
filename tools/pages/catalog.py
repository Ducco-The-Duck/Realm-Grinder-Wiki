"""The object catalogue: for each type of object that can be pinned in the tray (upgrade, artifact, challenge, research, spell) one file
docs/assets/data/catalog-<type>.json that holds everything needed to draw the object and its popup on any page. The page builders call `write`
with the same data they embed in their own page; the tray loads the file of a type only when it holds an object of that type.

A reference of an object is "type|name" ("challenge|faction|name" for a challenge). `objectFor` in tools/pages/templates/shared.js looks it up.
"""
import json, os
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
DIR = os.path.join(ROOT, 'docs', 'assets', 'data')


def unique(kind, pairs):
    """{name: object} from (name, object) pairs; the same name twice with different data would make a reference ambiguous, so the build stops"""
    out = {}
    for name, obj in pairs:
        if name in out and out[name] != obj:
            raise SystemExit(f'catalogue {kind}: two different objects are called {name!r}; a reference "{kind}|name" would be ambiguous')
        out[name] = obj
    return out


def write(kind, data):
    os.makedirs(DIR, exist_ok=True)
    path = os.path.join(DIR, f'catalog-{kind}.json')
    with open(path, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    return os.path.getsize(path) // 1024
