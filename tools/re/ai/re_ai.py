#!/usr/bin/env python3
"""Reverse-engineering helper for the game's built-in match AI (the `game-ai` crate inside TeamfightManager2.exe).

    python -I tools/re/ai/re_ai.py index                  # once per EXE: sections, functions, lea / call indexes,
                                                          # game-ai panic locations -> functions (cached in --work)
    python -I tools/re/ai/re_ai.py files battle_common    # functions of the game-ai source files matching the text
    python -I tools/re/ai/re_ai.py str "FOCUS-SEL T"      # code that uses a string / a length-prefixed fmt template
    python -I tools/re/ai/re_ai.py fmt "DIVE T"           # the template's pieces (<c0> = an argument)
    python -I tools/re/ai/re_ai.py dis 0xed59b6 +0x80     # disassembly with strings / floats / call targets noted
    python -I tools/re/ai/re_ai.py callers 0x161d880      # E8 calls into a function (+ the game-ai files they sit in)
    python -I tools/re/ai/re_ai.py callees 0xed1610
    python -I tools/re/ai/re_ai.py ptr 0x9b7df0           # .rdata / .data slots holding a pointer (vtables, tables)
    python -I tools/re/ai/re_ai.py bundle list rlp        # bundle.game_data entries (type path size)
    python -I tools/re/ai/re_ai.py bundle get asset/base/setting/macro_weights macro_weights out.json
    python -I tools/re/ai/re_ai.py rlib select_tactic     # a function of the classic SDK 0.5.1 game_core rlib, which
                                                          # still carries symbols: relocations named
    python -I tools/re/ai/re_ai.py syms051 battle         # the 0.5.1 AI's function names (plan_legacy, goal_data, ...)

What it relies on (docs/native_ai.md has the findings): the EXE is a stripped Rust build, but every panic site keeps a
`core::panic::Location` {file, line, col} in .rdata, so `index` maps each function to the game-ai source files and
lines it panics from; format strings are length-prefixed templates (the lea points at the length byte); the asset
bundle is a plain list of (u32-length type, path, data). Needs `pip install capstone pefile numpy`.
"""
import argparse
import bisect
import collections
import mmap
import os
import pickle
import re
import struct
import sys
import tempfile

GAME = os.environ.get("TFM2_GAME_DIR", "D:/steam/steamapps/common/Teamfight Manager2")
RLIB = "D:/steam/steamapps/common/mod-sdk-0.5.1/deps/libgame_core-ca200d77d5c563ee.rlib"
args = None


def work(name):
    os.makedirs(args.work, exist_ok=True)
    return os.path.join(args.work, name)


# ---------------------------------------------------------------- the EXE

class Img:
    def __init__(self):
        cache = work("pe.pkl")
        if os.path.exists(cache) and os.path.getmtime(cache) >= os.path.getmtime(args.exe):
            d = pickle.load(open(cache, "rb"))
        else:
            import pefile
            pe = pefile.PE(args.exe, fast_load=True)
            pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            d = {"base": pe.OPTIONAL_HEADER.ImageBase,
                 "secs": [(s.Name.rstrip(b"\0").decode(), s.VirtualAddress, s.Misc_VirtualSize, s.get_data()) for s in pe.sections],
                 "fns": sorted((e.struct.BeginAddress, e.struct.EndAddress) for e in pe.DIRECTORY_ENTRY_EXCEPTION)}
            pickle.dump(d, open(cache, "wb"))
        self.base, self.secs, self.fns = d["base"], d["secs"], d["fns"]
        self.starts = [a for a, _ in self.fns]
        self.text = next(s for s in self.secs if s[0] == ".text")
        self.rdata = next(s for s in self.secs if s[0] == ".rdata")

    def sec_of(self, rva):
        for n, va, vs, data in self.secs:
            if va <= rva < va + max(vs, len(data)):
                return n, va, data
        return None

    def read(self, rva, n):
        s = self.sec_of(rva)
        return s[2][rva - s[1]: rva - s[1] + n] if s else b""

    def func_of(self, rva):
        i = bisect.bisect_right(self.starts, rva) - 1
        return self.fns[i] if i >= 0 and self.fns[i][0] <= rva < self.fns[i][1] else None


def load_index():
    import numpy as np
    d = {k: np.load(work(k + ".npy")) for k in ("lea_src", "lea_tgt", "call_src", "call_tgt")}
    d["locs"] = pickle.load(open(work("ai_locs.pkl"), "rb"))
    return d


def cmd_index():
    import numpy as np
    im = Img()
    _, tva, _, tdata = im.text
    a = np.frombuffer(tdata, np.uint8)
    n = len(a) - 7

    def rel32(idx, at):
        d = sum(a[idx + at + k].astype(np.int64) << (8 * k) for k in range(4))
        return np.where(d >= 2 ** 31, d - 2 ** 32, d)
    # lea r64, [rip + disp32]
    m = ((a[:n] == 0x48) | (a[:n] == 0x4C)) & (a[1:n + 1] == 0x8D) & ((a[2:n + 2] & 0xC7) == 0x05)
    idx = np.nonzero(m)[0]
    tgt = tva + idx + 7 + rel32(idx, 3)
    keep = np.zeros(len(tgt), bool)
    for name in (".rdata", ".data"):
        s = next(x for x in im.secs if x[0] == name)
        keep |= (tgt >= s[1]) & (tgt < s[1] + max(s[2], len(s[3])))
    src, tgt = (tva + idx)[keep], tgt[keep]
    o = np.argsort(tgt, kind="stable")
    np.save(work("lea_src.npy"), src[o])
    np.save(work("lea_tgt.npy"), tgt[o])
    # call rel32 into a function start
    idx = np.nonzero(a[:len(a) - 5] == 0xE8)[0]
    tgt = tva + idx + 5 + rel32(idx, 1)
    ok = np.isin(tgt, np.array(im.starts, dtype=np.int64))
    src, tgt = (tva + idx)[ok], tgt[ok]
    o = np.argsort(tgt, kind="stable")
    np.save(work("call_src.npy"), src[o])
    np.save(work("call_tgt.npy"), tgt[o])
    # game-ai panic locations -> functions
    rd, r0 = im.rdata[3], im.rdata[1]
    paths = {r0 + mm.start(): mm.group().decode() for mm in re.finditer(rb"game-ai.src.[!-~]+?[.]rs", rd)}
    q = np.frombuffer(rd[: len(rd) // 8 * 8], np.uint64)
    want = {im.base + r: p for r, p in paths.items()}
    locs = {}
    for h in np.nonzero(np.isin(q, np.array(sorted(want), dtype=np.uint64)))[0]:
        p = want[int(q[h])]
        if h + 2 < len(q) and int(q[h + 1]) == len(p):
            locs[r0 + int(h) * 8] = (p[len("game-ai") + 5:], int(q[h + 2]) & 0xFFFFFFFF)
    ls, lt = np.load(work("lea_src.npy")), np.load(work("lea_tgt.npy"))
    func_locs = collections.defaultdict(list)
    for la, pl in locs.items():
        for s in ls[np.searchsorted(lt, la): np.searchsorted(lt, la, side="right")]:
            f = im.func_of(int(s))
            if f:
                func_locs[f[0]].append(pl)
    pickle.dump(dict(func_locs), open(work("ai_locs.pkl"), "wb"))
    print(f"functions {len(im.fns)}, lea refs {len(ls)}, game-ai files {len(paths)}, "
          f"panic locations {len(locs)}, functions with game-ai locations {len(func_locs)} -> {args.work}")


def describe(im, ix, f):
    if not f:
        return "?"
    files = collections.Counter(p for p, _ in ix["locs"].get(f[0], []))
    return f"fn {f[0]:#x} ({f[1] - f[0]} B) " + ",".join(p for p, _ in files.most_common(3))


def cmd_files(subs):
    im, ix = Img(), load_index()
    for sub in subs:
        rows = []
        for f, locs in ix["locs"].items():
            mine = sorted(set(line for p, line in locs if sub in p))
            if mine:
                fn = im.func_of(f)
                others = sorted(set(p.split("\\")[-1] for p, _ in locs if sub not in p))
                rows.append((f, fn[1] - fn[0], mine, others))
        print(f"== {sub}: {len(rows)} functions, {sum(r[1] for r in rows)} bytes")
        for f, size, lines, others in sorted(rows, key=lambda r: r[2][0]):
            more = "..." if len(lines) > 12 else ""
            print(f"  {f:#x} {size:6d} B lines {lines[:12]}{more}" + (f"  +{','.join(others[:4])}" if others else ""))


def cmd_str(texts):
    import numpy as np
    im, ix = Img(), load_index()
    rd, r0 = im.rdata[3], im.rdata[1]
    ls, lt = ix["lea_src"], ix["lea_tgt"]
    for t in texts:
        i = rd.find(t.encode())
        while i >= 0:
            rva = r0 + i
            print(f"'{t}' at {rva:#x}")
            # a plain string or a fmt template: refs to it or to the length byte(s) before it
            for k in range(np.searchsorted(lt, rva - 32), np.searchsorted(lt, rva, side="right")):
                print(f"   lea {int(ls[k]):#x} -> {int(lt[k]):#x} (-{rva - int(lt[k])}) {describe(im, ix, im.func_of(int(ls[k])))}")
            i = rd.find(t.encode(), i + 1)


def template(im, rva, n=400):
    b, out, i = im.read(rva, n), [], 0
    while i < len(b) and b[i]:
        c = b[i]
        if c < 0x80 and i + 1 + c <= len(b) and all(32 <= x < 127 for x in b[i + 1:i + 1 + c]):
            out.append(b[i + 1:i + 1 + c].decode())
            i += 1 + c
        else:
            out.append(f"<{c:02x}>")
            i += 1
    return "".join(out)


def cmd_fmt(texts):
    im = Img()
    rd, r0 = im.rdata[3], im.rdata[1]
    for t in texts:
        i = rd.find(t.encode())
        print(f"{t} -> {template(im, r0 + i - 1) if i > 0 else 'not found'}")


def note(im, t, labels):
    if t in labels:
        return labels[t]
    s = im.sec_of(t)
    if not s:
        return ""
    n, va, data = s
    if n == ".rdata":
        b = data[t - va: t - va + 48]
        txt = b[1:1 + b[0]] if 0 < b[0] < 48 and all(32 <= c < 127 for c in b[1:1 + b[0]]) else b
        txt = bytes(c if 32 <= c < 127 else 46 for c in txt[:40]).decode()
        f32 = struct.unpack("<f", b[:4])[0] if len(b) >= 4 else 0
        f64 = struct.unpack("<d", b[:8])[0] if len(b) >= 8 else 0
        return f"'{txt}' f32={f32:.6g} f64={f64:.6g}"
    if n == ".text":
        f = im.func_of(t)
        return f"fn {f[0]:#x}" + (f"+{t - f[0]:#x}" if t != f[0] else "") if f else ""
    return n


def cmd_dis(start, end):
    from capstone import CS_ARCH_X86, CS_MODE_64, Cs
    im = Img()
    labels = {}
    if args.labels and os.path.exists(args.labels):
        for ln in open(args.labels, encoding="utf-8"):
            p = ln.split(None, 1)
            if len(p) == 2:
                labels[int(p[0], 16)] = p[1].strip()
    a = int(start, 16)
    if end:
        e = a + int(end[1:], 16) if end.startswith("+") else int(end, 16)
    else:
        f = im.func_of(a)
        e = f[1] if f else a + 0x200
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    for ins in md.disasm(im.read(a, e - a), a):
        s = f"{ins.address:#x}: {ins.mnemonic} {ins.op_str}"
        m = re.search(r"\[rip ([+-]) (0x[0-9a-f]+)\]", ins.op_str)
        t = None
        if m:
            t = ins.address + ins.size + int(m.group(2), 16) * (1 if m.group(1) == "+" else -1)
        elif ins.mnemonic in ("call", "jmp") and ins.op_str.startswith("0x"):
            t = int(ins.op_str, 16)
            if ins.mnemonic == "jmp" and im.func_of(t) == im.func_of(ins.address):
                t = None
        if t is not None:
            s += f"    ; {t:#x} {note(im, t, labels)}"
        print(s)


def cmd_calls(rvas, out):
    import numpy as np
    im, ix = Img(), load_index()
    cs, ct = ix["call_src"], ix["call_tgt"]
    for s in rvas:
        t = int(s, 16)
        if out:
            f = im.func_of(t)
            m = (cs >= f[0]) & (cs < f[1])
            print(f"== callees of {describe(im, ix, f)}")
            for c, k in collections.Counter(int(x) for x in ct[m]).most_common():
                print(f"   x{k} {describe(im, ix, im.func_of(c))}")
        else:
            lo, hi = np.searchsorted(ct, t), np.searchsorted(ct, t, side="right")
            print(f"== callers of {t:#x}: {hi - lo}")
            for x in cs[lo:hi][:60]:
                print(f"   {int(x):#x} in {describe(im, ix, im.func_of(int(x)))}")


def cmd_ptr(rvas):
    import numpy as np
    im = Img()
    for s in rvas:
        t = int(s, 16) + im.base
        for n, va, _, data in im.secs:
            if n not in (".rdata", ".data"):
                continue
            q = np.frombuffer(data[: len(data) // 8 * 8], np.uint64)
            for h in np.nonzero(q == t)[0]:
                print(f"{s} in {n} slot {va + int(h) * 8:#x}")
                for k in range(-4, 6):
                    if 0 <= h + k < len(q):
                        v = int(q[h + k]) - im.base
                        print(f"   [{k:+d}] {note(im, v, {}) if 0 <= v < 0x8000000 else hex(int(q[h + k]))}")


# ---------------------------------------------------------------- the asset bundle

def bundle_entries():
    f = open(os.path.join(GAME, "bundle.game_data"), "rb")
    m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    n, o = struct.unpack_from("<I", m, 0)[0], 4
    for _ in range(n):
        out = []
        for _k in range(2):
            ln = struct.unpack_from("<I", m, o)[0]
            out.append(m[o + 4:o + 4 + ln].decode())
            o += 4 + ln
        ln = struct.unpack_from("<I", m, o)[0]
        yield out[0], out[1], o + 4, ln, m
        o += 4 + ln


def cmd_bundle(rest):
    if rest[0] == "list":
        kinds = collections.Counter()
        for t, p, _, ln, _ in bundle_entries():
            kinds[t] += 1
            if len(rest) > 1 and rest[1] in f"{t} {p}":
                print(t, p, ln)
        if len(rest) == 1:
            for t, k in kinds.most_common():
                print(k, t)
    elif rest[0] == "get":
        for t, p, off, ln, m in bundle_entries():
            if p == rest[1] and t == rest[2]:
                open(rest[3], "wb").write(m[off:off + ln])
                print("wrote", ln, "bytes")
                return
        print("not found")


# ---------------------------------------------------------------- the classic SDK's symbolized game_core

def rlib_objects():
    cache = work("rlib051.pkl")
    if os.path.exists(cache):
        return pickle.load(open(cache, "rb"))
    data, objs, o, longnames = open(RLIB, "rb").read(), [], 8, b""
    while o + 60 <= len(data):
        h = data[o:o + 60]
        name, size = h[:16].decode().strip(), int(h[48:58].decode().strip())
        body = data[o + 60:o + 60 + size]
        if name == "//":
            longnames = body
        elif name.startswith("/") and name[1:].isdigit():
            st = int(name[1:])
            name = longnames[st:longnames.find(b"/\n", st)].decode()
        if ".rcgu." in name and struct.unpack_from("<H", body, 0)[0] == 0x8664:
            objs.append((name, coff(body)))
        o += 60 + size + (size & 1)
    pickle.dump(objs, open(cache, "wb"))
    return objs


def coff(body):
    _, nsec, _, symoff, nsym, opt, _ = struct.unpack_from("<HHIIIHH", body, 0)
    strtab = body[symoff + nsym * 18:]

    def sname(raw):
        if raw[:4] == b"\0\0\0\0":
            off = struct.unpack_from("<I", raw, 4)[0]
            return strtab[off:strtab.find(b"\0", off)].decode("utf-8", "replace")
        return raw.rstrip(b"\0").decode("utf-8", "replace")
    secs = []
    for i in range(nsec):
        s = body[20 + opt + i * 40: 20 + opt + (i + 1) * 40]
        _, _, rsz, rptr, relptr, _, nrel, _, _ = struct.unpack_from("<IIIIIIHHI", s, 8)
        secs.append((sname(s[:8]), body[rptr:rptr + rsz] if rptr else b"",
                     [struct.unpack_from("<IIH", body, relptr + k * 10) for k in range(nrel)]))
    syms, i = [], 0
    while i < nsym:
        raw = body[symoff + i * 18: symoff + (i + 1) * 18]
        val, secn, _, cls, naux = struct.unpack_from("<IhHBB", raw, 8)
        syms.append((sname(raw[:8]), val, secn, cls))
        syms.extend([None] * naux)
        i += 1 + naux
    return secs, syms


def demangle(s):
    """Rust v0 / legacy names, roughly: the identifiers in order."""
    toks, j = [], 0
    while j < len(s):
        mm = re.match(r"\d+", s[j:])
        if mm:
            k = j + len(mm.group())
            toks.append(s[k:k + int(mm.group())])
            j = k + int(mm.group())
        else:
            j += 1
    return "::".join(t for t in toks if t and not (t.startswith("h") and len(t) == 17))


def cmd_rlib(pat, count):
    from capstone import CS_ARCH_X86, CS_MODE_64, Cs
    md, done = Cs(CS_ARCH_X86, CS_MODE_64), 0
    for oname, (secs, syms) in rlib_objects():
        for s in syms:
            if not s or s[2] <= 0 or s[3] != 2 or pat not in s[0] or not secs[s[2] - 1][0].startswith(".text"):
                continue
            code, rel = secs[s[2] - 1][1], {r[0]: r for r in secs[s[2] - 1][2]}
            print(f"==== {demangle(s[0])}  [{len(code)} B]")
            for ins in md.disasm(code, 0):
                extra = ""
                for off in range(ins.address, ins.address + ins.size):
                    if off in rel and syms[rel[off][1]]:
                        tn, _, tsec, tcls = syms[rel[off][1]]
                        if tsec > 0 and secs[tsec - 1][0].startswith(".rdata") and tcls == 3:
                            d = secs[tsec - 1][1]
                            tn = "rdata:'" + bytes(c if 32 <= c < 127 else 46 for c in d[:48]).decode() + "'"
                        else:
                            tn = demangle(tn) if tn.startswith(("_R", "_ZN")) else tn
                        extra = f"  ; {tn}"
                        break
                print(f"  {ins.address:5x}: {ins.mnemonic} {ins.op_str}{extra}")
            done += 1
            if done >= count:
                return


def cmd_syms051(pat):
    names = set()
    for _, (_, syms) in rlib_objects():
        for s in syms:
            if s and s[3] == 2 and "aos_ver_hamster" in s[0]:
                d = demangle(s[0])
                d = d[d.find("aos_ver_hamster") + len("aos_ver_hamster::"):]
                if not pat or pat in d:
                    names.add(d)
    for n in sorted(names):
        print(n)


def main():
    global args
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd")
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--exe", default=os.path.join(GAME, "TeamfightManager2.exe"))
    ap.add_argument("--work", default=os.path.join(tempfile.gettempdir(), "tfm2_ai_re"))
    ap.add_argument("--labels", help="rva name lines, used by dis")
    ap.add_argument("-n", type=int, default=1, help="rlib: how many matching functions")
    args = ap.parse_args()
    r = args.rest
    {"index": lambda: cmd_index(),
     "files": lambda: cmd_files(r),
     "str": lambda: cmd_str(r),
     "fmt": lambda: cmd_fmt(r),
     "dis": lambda: cmd_dis(r[0], r[1] if len(r) > 1 else None),
     "callers": lambda: cmd_calls(r, False),
     "callees": lambda: cmd_calls(r, True),
     "ptr": lambda: cmd_ptr(r),
     "bundle": lambda: cmd_bundle(r),
     "rlib": lambda: cmd_rlib(r[0], args.n),
     "syms051": lambda: cmd_syms051(r[0] if r else ""),
     }.get(args.cmd, lambda: sys.exit(f"unknown command {args.cmd}"))()


if __name__ == "__main__":
    main()
