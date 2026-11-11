#!/usr/bin/env python3
"""The game's effect types and the methods its AI estimates them with (the `EffectType` trait's vtables in the EXE).

    python -I tools/re/ai/re_ai.py index                      # once per EXE (the same --work)
    python -I tools/re/ai/effect_types.py                     # every effect type: struct size, the estimate methods
    python -I tools/re/ai/effect_types.py Combine Projectile  # only the types whose name holds one of the words
    python -I tools/re/ai/effect_types.py --slot 0x240        # which types override one vtable slot (grouped by function)

How the vtables are found (game 0.7.2, 2026-11-11; docs/native_ai.md has what the methods do): every runtime effect
struct (`CombineEffect`, `TargetProjectileEffect`, ... - built from the data's `DataEffectDef`) is a trait object; its
vtable is [drop, size, align 8, methods...]. The method at +0x18 writes the type's name (its serialize), so a qword
table whose +0x10 is 8 and whose +0x18 function points at a string `XxxEffect` is one of them. Slots that matter here:

    +0x30   expected damage (AD, AP) of the effect, from the caster's stats and current buffs
    +0x38   the same against one target, when the type has something to say about the target (an Option)
    +0x58   percent of the target's health it takes (the callers add target hp x this / 100)
    +0x60   expected damage against one target (what the DPS estimate calls on an action's effect)
    +0xb8   expected crowd-control time (an Option)
    +0x240  a mask: 0 for most, 0xff for CasterInvisibleEffect and ModEffect (a mod's Native effect), 2 / 4 / 8 for a
            few base ults; containers OR their children. Non-zero = the kit ledger does not cache the action.

The slot numbers move when the trait changes: check them against a type you know (CombineEffect sums its children at
+0x30) after a game update.
"""
import argparse
import collections
import os
import pickle
import re
import struct
import sys
import tempfile

import numpy as np

SLOTS = (("dmg", 0x30), ("vs_opt", 0x38), ("pct", 0x58), ("vs", 0x60), ("cc", 0xb8), ("mask", 0x240))


def load(work):
    d = pickle.load(open(os.path.join(work, "pe.pkl"), "rb"))
    src, tgt = np.load(os.path.join(work, "lea_src.npy")), np.load(os.path.join(work, "lea_tgt.npy"))
    order = np.argsort(src)
    return d, src[order], tgt[order]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("words", nargs="*")
    ap.add_argument("--work", default=os.path.join(tempfile.gettempdir(), "tfm2_ai_re"))
    ap.add_argument("--slot", help="hex offset: group the types by the function in that slot")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    d, src_s, tgt_s = load(a.work)
    base, secs, fns = d["base"], d["secs"], d["fns"]
    ends = {b: e for b, e in fns}
    text = next(s for s in secs if s[0] == ".text")
    t_lo, t_hi = text[1], text[1] + len(text[3])
    rdata = next(s for s in secs if s[0] == ".rdata")
    va, data = rdata[1], rdata[3]

    def at(rva, n):
        for _, v, _, dd in secs:
            if v <= rva < v + len(dd):
                return dd[rva - v: rva - v + n]
        return b""

    def q(rva):
        return struct.unpack("<Q", at(rva, 8))[0]

    pat = re.compile(rb"^([A-Z][A-Za-z0-9]{1,48}?Effect)")
    cache = {}

    def name_of(f):
        if f not in cache:
            out = None
            if f in ends and ends[f] - f < 8000:
                lo, hi = np.searchsorted(src_s, f), np.searchsorted(src_s, ends[f])
                for t in sorted(set(int(x) for x in tgt_s[lo:hi])):
                    m = pat.match(at(t, 60))
                    if m:
                        out = m.group(1).decode()
                        break
            cache[f] = out
        return cache[f]

    qs = np.frombuffer(data[: len(data) // 8 * 8], dtype="<u8")
    code = lambda v: t_lo <= int(v) - base < t_hi
    types = collections.defaultdict(list)
    for i in np.nonzero(qs == 8)[0]:
        p = int(i) - 2
        if p < 0 or p + 0x54 >= len(qs) or not (0 < int(qs[p + 1]) < 0x2000):
            continue
        if not all(code(qs[p + k]) for k in (3, 6, 12, 0x48)):
            continue
        nm = name_of(int(qs[p + 3]) - base)
        if nm:
            types[nm].append(va + 8 * p)
    fnsize = {b: e - b for b, e in fns}
    if a.slot:
        off = int(a.slot, 16)
        by = collections.defaultdict(set)
        for nm, vts in types.items():
            for vt in vts:
                by[q(vt + off) - base].add(nm)
        for f, ns in sorted(by.items(), key=lambda kv: -len(kv[1])):
            print(f"{f:#9x} ({fnsize.get(f, '?')} B, {at(f, 8).hex()}) x{len(ns)}: {', '.join(sorted(ns))}")
        return
    print(f"{len(types)} effect types, {sum(len(v) for v in types.values())} vtables")
    for nm in sorted(types):
        if a.words and not any(w in nm for w in a.words):
            continue
        vt = types[nm][0]
        cols = " ".join(f"{k} {q(vt + o) - base:#9x}({fnsize.get(q(vt + o) - base, '?')})" for k, o in SLOTS)
        print(f"{nm:38s} size {q(vt + 8):#6x} vt {vt:#x} x{len(types[nm])} {cols}")


if __name__ == "__main__":
    main()
