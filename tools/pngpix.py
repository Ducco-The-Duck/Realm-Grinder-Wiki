"""Minimal PNG reader (no third-party libraries): pixels(path) -> (width, height, rows of (r, g, b, a))."""
import struct
import zlib


def pixels(path):
    data = open(path, 'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    pos, idat, plte, trns = 8, b'', None, None
    while pos < len(data):
        n, typ = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if typ == b'IHDR': w, h, depth, ctype = struct.unpack('>IIBB', body[:10])
        elif typ == b'PLTE': plte = body
        elif typ == b'tRNS': trns = body
        elif typ == b'IDAT': idat += body
    assert depth == 8 and ctype in (0, 2, 3, 4, 6), (depth, ctype)
    ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    raw = zlib.decompress(idat)
    stride, out, prev = w * ch, [], bytearray(w * ch)
    i = 0
    for _ in range(h):
        f = raw[i]; line = bytearray(raw[i + 1:i + 1 + stride]); i += 1 + stride
        for x in range(stride):
            a = line[x - ch] if x >= ch else 0
            b = prev[x]
            c = prev[x - ch] if x >= ch else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + ((a + b) >> 1)) & 255
            elif f == 4:
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        out.append(line); prev = line
    rows = []
    for line in out:
        row = []
        for x in range(w):
            if ctype == 6: row.append(tuple(line[x * 4:x * 4 + 4]))
            elif ctype == 2: row.append((*line[x * 3:x * 3 + 3], 255))
            elif ctype == 0: row.append((line[x], line[x], line[x], 255))
            elif ctype == 4: row.append((line[x * 2], line[x * 2], line[x * 2], line[x * 2 + 1]))
            else:
                k = line[x]; row.append((*plte[k * 3:k * 3 + 3], trns[k] if trns and k < len(trns) else 255))
        rows.append(row)
    return w, h, rows
