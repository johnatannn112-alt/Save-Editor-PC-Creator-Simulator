"""Minimal MS-NRBF (.NET BinaryFormatter) reader that records file offsets of primitive values."""
import struct

PRIM = {1:('?',1),2:('B',1),3:('<H',2),4:('<d',8) ,5:None,6:('<d',8),7:('<h',2),8:('<i',4),9:('<q',8),
        10:('<b',1),11:('<f',4),14:('<H',2),15:('<I',4),16:('<Q',8)}
# PrimitiveType enum: 1 Boolean,2 Byte,3 Char,5 Decimal,6 Double,7 Int16,8 Int32,9 Int64,10 SByte,11 Single,12 TimeSpan,13 DateTime,14 UInt16,15 UInt32,16 UInt64,18 String
FMT = {1:'?',2:'B',6:'<d',7:'<h',8:'<i',9:'<q',10:'<b',11:'<f',14:'<H',15:'<I',16:'<Q',12:'<q',13:'<q'}
SIZE = {1:1,2:1,3:None,5:None,6:8,7:2,8:4,9:8,10:1,11:4,12:8,13:8,14:2,15:4,16:8,18:None}

class Reader:
    def __init__(s, data):
        s.d = data; s.p = 0
        s.classes = {}   # object id -> (name, members, types, extra)
        s.fields = []    # (path, offset, fmt) for primitive values
        s.objs = {}
    def u8(s): v = s.d[s.p]; s.p += 1; return v
    def i32(s): v = struct.unpack_from('<i', s.d, s.p)[0]; s.p += 4; return v
    def lps(s):
        n = 0; shift = 0
        while True:
            b = s.u8(); n |= (b & 0x7f) << shift
            if not b & 0x80: break
            shift += 7
        v = s.d[s.p:s.p+n].decode('utf-8'); s.p += n; return v
    def prim(s, t, path):
        if t == 18: return s.lps()
        if t == 3:  # char (utf8)
            b = s.d[s.p]; n = 1 if b < 0x80 else 2 if b < 0xE0 else 3 if b < 0xF0 else 4
            v = s.d[s.p:s.p+n].decode('utf-8'); s.p += n; return v
        if t == 5: return s.lps()
        f = FMT[t]; off = s.p
        v = struct.unpack_from(f, s.d, s.p)[0]; s.p += SIZE[t]
        s.fields.append((path, off, f, v)); return v
    def read_classinfo(s):
        oid = s.i32(); name = s.lps(); n = s.i32()
        members = [s.lps() for _ in range(n)]
        return oid, name, members
    def read_types(s, n):
        bt = [s.u8() for _ in range(n)]; extra = []
        for t in bt:
            if t in (0, 7): extra.append(s.u8())
            elif t == 3: extra.append(s.lps())
            elif t == 4: extra.append((s.lps(), s.i32()))
            else: extra.append(None)
        return bt, extra
    def read_members(s, oid, name, members, bt, extra, path):
        vals = {}
        owner = f'{name}#{oid}'
        for m, t, e in zip(members, bt, extra):
            vals[m] = s.read_value(t, e, f'{owner}.{m}')
        s.objs[oid] = (name, vals); return ('obj', oid)
    def read_value(s, t, e, path):
        if t == 0: return s.prim(e, path)
        if t == 1: return s.record(path)  # String
        return s.record(path)
    def record(s, path='root'):
        rt = s.u8()
        if rt == 0: s.p += 16; return None
        if rt == 11: return 'END'
        if rt == 12: s.i32(); s.lps(); return s.record(path)
        if rt in (3, 5, 2, 4):
            oid, name, members = s.read_classinfo()
            if rt in (4, 5): bt, extra = s.read_types(len(members))
            else: bt = extra = None
            if rt in (3, 5): s.i32()  # library id
            if rt in (2, 3): raise NotImplementedError('class without types')
            s.classes[oid] = (name, members, bt, extra)
            return s.read_members(oid, name, members, bt, extra, path)
        if rt == 1:
            oid = s.i32(); ref = s.i32(); name, members, bt, extra = s.classes[ref]
            s.classes[oid] = s.classes[ref]
            return s.read_members(oid, name, members, bt, extra, path)
        if rt == 6:
            oid = s.i32(); v = s.lps(); s.objs[oid] = ('str', v); return v
        if rt == 8:
            t = s.u8(); return s.prim(t, path)
        if rt == 9: return ('ref', s.i32())
        if rt == 10: return None
        if rt == 13: s.u8(); return None
        if rt == 14: s.i32(); return None
        if rt == 15:
            oid = s.i32(); n = s.i32(); t = s.u8(); arr = []
            for i in range(n): arr.append(s.prim(t, f'{path}[{i}]'))
            s.objs[oid] = ('arr', arr); return ('obj', oid)
        if rt in (16, 17):
            oid = s.i32(); n = s.i32(); arr = []; i = 0
            while i < n:
                p0 = s.p; rt2 = s.d[s.p]
                if rt2 == 13: s.p += 1; k = s.u8(); arr += [None]*k; i += k; continue
                if rt2 == 14: s.p += 1; k = s.i32(); arr += [None]*k; i += k; continue
                arr.append(s.record(f'{path}[{i}]')); i += 1
            s.objs[oid] = ('arr', arr); return ('obj', oid)
        if rt == 7:
            oid = s.i32(); at = s.u8(); rank = s.i32()
            lens = [s.i32() for _ in range(rank)]
            if at in (3, 4, 5): [s.i32() for _ in range(rank)]
            t = s.u8(); e = None
            if t in (0, 7): e = s.u8()
            elif t == 3: e = s.lps()
            elif t == 4: e = (s.lps(), s.i32())
            total = 1
            for l in lens: total *= l
            arr = []; i = 0
            while i < total:
                if t == 0: arr.append(s.prim(e, f'{path}[{i}]')); i += 1; continue
                rt2 = s.d[s.p]
                if rt2 == 13: s.p += 1; k = s.u8(); arr += [None]*k; i += k; continue
                if rt2 == 14: s.p += 1; k = s.i32(); arr += [None]*k; i += k; continue
                arr.append(s.record(f'{path}[{i}]')); i += 1
            s.objs[oid] = ('arr', arr); return ('obj', oid)
        raise ValueError(f'unknown record type {rt} at {s.p-1}')
    def parse(s):
        assert s.u8() == 0; s.p += 16
        while True:
            r = s.record('root')
            if r == 'END': break
        return s

def load(path):
    d = open(path, 'rb').read(); r = Reader(d).parse(); return d, r
