#!/usr/bin/env python3
"""Save editor for the mining-simulator game (v3.dat, .NET BinaryFormatter, no encryption).
Usage:
  python3 save_editor.py v3.dat                      # show editable Player fields
  python3 save_editor.py v3.dat Money=999999 Level=20 -o v3_edited.dat
Only same-size primitive values (int/float/bool) are patched in place, so the file stays valid."""
import sys, struct, shutil, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nrbf

def main(argv):
    out = None; sets = {}; path = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '-o': out = argv[i+1]; i += 2; continue
        if '=' in a: k, v = a.split('=', 1); sets[k] = v
        else: path = a
        i += 1
    if not path: print(__doc__); return 1
    data, r = nrbf.load(path)
    # find the Player object's own primitive fields
    pid = next(k for k, v in r.objs.items() if v[0] == 'Player')
    pref = f'Player#{pid}.'
    fields = {p[len(pref):]: (off, f, v) for p, off, f, v in r.fields if p.startswith(pref)}
    if not sets:
        for k, (off, f, v) in fields.items(): print(f'{k:28} {v!r}')
        return 0
    XP = [0, 1000, 2000, 3200, 4800, 6400, 9000, 12400, 16100, 20000, 30000]
    if 'Level' in sets and not 1 <= int(sets['Level']) <= 10:
        print('! Level harus 1 sampai 10 (di luar itu progres tidak terbaca di game)'); return 2
    if 'Level' in sets and 'Experience' not in sets:
        sets['Experience'] = '0'; print('i Experience diatur ke 0 karena Level diubah')
    if 'Experience' in sets and int(sets['Experience']) < 0:
        print('! Experience tidak boleh negatif'); return 2
    buf = bytearray(data)
    for k, val in sets.items():
        if k not in fields: print(f'! field not found: {k}'); return 2
        off, f, old = fields[k]
        if f == '?': new = val.lower() in ('1', 'true', 'yes')
        elif f in ('<f', '<d'): new = float(val)
        else: new = int(val)
        struct.pack_into(f, buf, off, new)
        print(f'{k}: {old!r} -> {new!r}')
    out = out or path + '.edited'
    open(out, 'wb').write(buf); print('saved', out)

if __name__ == '__main__': sys.exit(main(sys.argv[1:]))
