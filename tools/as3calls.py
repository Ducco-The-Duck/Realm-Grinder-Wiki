import re

_RE_MSG = re.compile(r'\b_\("((?:[^"\\]|\\.)*)"')


def find_msg_calls(body):
    """Yield (msgid, [arg strings]) for each _("...", args...) call, balanced-paren aware."""
    for m in _RE_MSG.finditer(body):
        i = m.end(); depth = 1; args = []; cur = ''; instr = None
        while i < len(body) and depth > 0:
            ch = body[i]
            if instr:
                cur += ch
                if ch == '\\':
                    cur += body[i + 1]; i += 1
                elif ch == instr:
                    instr = None
            elif ch == '§':
                j = body.find('§', i + 1)
                j = j if j > 0 else i
                cur += body[i:j + 1]; i = j
            elif ch in ('"', "'"):
                instr = ch; cur += ch
            elif ch in '([{':
                depth += 1; cur += ch
            elif ch in ')]}':
                depth -= 1
                if depth > 0: cur += ch
            elif ch == ',' and depth == 1:
                args.append(cur.strip()); cur = ''
            else:
                cur += ch
            i += 1
        if cur.strip(): args.append(cur.strip())
        yield m.group(1), [a for a in args if a]
