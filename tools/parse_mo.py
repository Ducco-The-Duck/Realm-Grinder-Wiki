"""Decompress + parse the gettext .mo catalogs embedded in the SWF into JSON (msgid -> {lang: msgstr})."""
import glob, json, re, struct, sys, zlib, os
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
out = {}
for f in sorted(glob.glob(os.path.join(root, 'out/binaryData/*_mo*.bin'))):
    lang = re.search(r'realmgrinder_([a-zA-Z_]+)_mo', os.path.basename(f)).group(1)
    d = zlib.decompress(open(f, 'rb').read())
    magic = struct.unpack('<I', d[:4])[0]
    e = '<' if magic == 0x950412de else '>'
    _, n, o_off, t_off = struct.unpack(e + '4I', d[4:20])
    for i in range(n):
        ol, oo = struct.unpack(e + '2I', d[o_off + 8*i:o_off + 8*i + 8])
        tl, to = struct.unpack(e + '2I', d[t_off + 8*i:t_off + 8*i + 8])
        k = d[oo:oo+ol].decode('utf8'); v = d[to:to+tl].decode('utf8')
        out.setdefault(k, {})[lang] = v
    print(lang, n, file=sys.stderr)
os.makedirs(os.path.join(root, 'data'), exist_ok=True)
json.dump(out, open(os.path.join(root, 'data/strings.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
print(len(out), 'msgids')
