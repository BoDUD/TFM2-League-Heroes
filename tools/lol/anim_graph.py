#!/usr/bin/env python3
"""What League plays for a champion's clips: its animation graph, read from the local client.

    python tools/lol/anim_graph.py Yone [--grep run] [--lol D:\\WeGameApps\\lol]

Reads (never writes) data/characters/<champ>/animations/skin0.bin from <Champ>.wad.client with a minimal
reader of Riot's PROP bin format and prints every clip of the graph's mClipDataMap: its name (the key is an
FNV-1a hash; names are matched against common ones and the .anm file names), its class, and
  - for an AtomicClipData its .anm file, the clip's length and frame rate as the file gives them, and the
    graph's `mTickDuration` when set (the time a frame is played for: 1/30 by default, Yone's walk 1/35), so
    a cycle takes (frames - 1) x mTickDuration;
  - for a ParametricClipData / ConditionFloatClipData its children and their values (Ekko's `Run`:
    run_base from move speed 315, Run_Haste from 535), for a ConditionBoolClipData its true / false clips
    (Yone's `Run`: run_homeguard when the homeguard buff runs, run_base otherwise).
The move tag of a sprite is what `Run` plays at base move speed: follow it to `run_base` (Yone's is
Yone_Walk01, a walk; his Yone_Run01 is `run_fast`, not his move).
"""
import argparse
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from riot import Wad  # noqa: E402
import pose_ref as P  # noqa: E402


def fnv1a(s):
    h = 0x811C9DC5
    for b in s.lower().encode("utf-8"):
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


FIELDS = ["mClipDataMap", "mAnimationResourceData", "mAnimationFilePath", "mParametricPairDataList", "mClipName",
          "mValue", "mUpdaterType", "mConditionFloatPairDataList", "mTrueConditionClipName", "mFalseConditionClipName",
          "mTickDuration", "mFlags", "mStartFrame", "mEndFrame", "mChangeAnimationMidPlay", "mHoldAnimationToHigher",
          "mHoldAnimationToLower", "mMaskDataName", "mTrackDataName", "mSyncGroupDataName", "mEventDataMap",
          "mSelectorPairDataList", "mProbability", "mClipNameList"]
CLASSES = ["AtomicClipData", "ParametricClipData", "SelectorClipData", "SequencerClipData", "ConditionFloatClipData",
           "ConditionBoolClipData", "ParallelClipData", "AnimationResourceData", "ParametricPairData",
           "ConditionFloatPairData", "SelectorPairData", "IsHomeguardParametricUpdater", "MoveSpeedParametricUpdater",
           "IsMovingParametricUpdater", "AttackSpeedParametricUpdater", "TotalMoveSpeedParametricUpdater"]
NAMES = {fnv1a(n): n for n in FIELDS + CLASSES}
COMMON = ["run", "run_base", "run_fast", "run_slow", "run_haste", "run_homeguard", "walk", "idle1", "idle_base",
          "attack1", "attack2", "crit", "death", "dance", "joke", "laugh", "taunt", "recall", "channel",
          "spell1", "spell2", "spell3", "spell4"]
PRIM = {0: "", 1: "?", 2: "b", 3: "B", 4: "h", 5: "H", 6: "i", 7: "I", 8: "q", 9: "Q", 10: "f", 11: "2f", 12: "3f",
        13: "4f", 14: "16f", 15: "4B", 17: "I", 18: "Q", 19: "?"}


class Reader:
    def __init__(self, b):
        self.b, self.o = b, 0

    def u(self, fmt):
        v = struct.unpack_from("<" + fmt, self.b, self.o)
        self.o += struct.calcsize("<" + fmt)
        return v if len(v) > 1 else v[0]

    def string(self):
        n = self.u("H")
        s = self.b[self.o:self.o + n].decode("utf-8", "replace")
        self.o += n
        return s


def value(r, t):
    if t == 16:
        return r.string()
    if t in PRIM:
        return r.u(PRIM[t]) if PRIM[t] else None
    if t in (128, 129):                     # list, list2
        vt = r.u("B")
        _size, count = r.u("II")
        return [value(r, vt) for _ in range(count)]
    if t in (130, 131):                     # pointer, embed
        cls = r.u("I")
        if cls == 0:
            return None
        _size = r.u("I")
        fields = {}
        for _ in range(r.u("H")):
            name, ft = r.u("IB")
            fields[NAMES.get(name, f"#{name:08x}")] = value(r, ft)
        return {"__class": NAMES.get(cls, f"#{cls:08x}"), **fields}
    if t == 132:                            # link
        return r.u("I")
    if t == 133:                            # option
        vt = r.u("B")
        return value(r, vt) if r.u("B") else None
    if t == 134:                            # map
        kt, vt = r.u("BB")
        _size, count = r.u("II")
        return [(value(r, kt), value(r, vt)) for _ in range(count)]
    if t == 135:                            # flag
        return r.u("B")
    raise ValueError(f"unknown bin type {t} at byte {r.o}")


def parse_prop(b):
    r = Reader(b)
    r.o = 4
    if b[:4] == b"PTCH":
        r.o = 20
    elif b[:4] != b"PROP":
        raise ValueError("not a PROP bin")
    version = r.u("I")
    if version >= 2:
        for _ in range(r.u("I")):
            r.string()
    types = [r.u("I") for _ in range(r.u("I"))]
    entries = []
    for t in types:
        size = r.u("I")
        end = r.o + size
        r.u("I")                            # the entry's own key
        fields = {}
        for _ in range(r.u("H")):
            name, ft = r.u("IB")
            fields[NAMES.get(name, f"#{name:08x}")] = value(r, ft)
        r.o = end
        entries.append((NAMES.get(t, f"#{t:08x}"), fields))
    return entries


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("champ", help="the champion's WAD name, e.g. Yone, Ekko")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol", help="League install folder")
    ap.add_argument("--grep", default="", help="only clips whose line contains this (case-insensitive)")
    a = ap.parse_args()
    w = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", f"{a.champ}.wad.client"))
    b = w.read_path(f"data/characters/{a.champ.lower()}/animations/skin0.bin")
    anms = sorted(set(m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\.anm", b)))
    names = list(COMMON)
    for path in anms:
        stem = os.path.splitext(os.path.basename(path))[0]
        names.append(stem)
        if "_" in stem:
            names.append(stem.split("_", 1)[1])
    cands = {fnv1a(n): n for n in names}
    clipname = lambda h: cands.get(h, f"#{h:08x}") if isinstance(h, int) else str(h)
    lengths = {}
    for _cls, fields in parse_prop(b):
        for key, clip in fields.get("mClipDataMap") or []:
            c = clip or {}
            line = f"{clipname(key):28s} {c.get('__class', '?'):24s}"
            res = c.get("mAnimationResourceData")
            if isinstance(res, dict) and res.get("mAnimationFilePath"):
                path = res["mAnimationFilePath"]
                if path not in lengths:
                    try:
                        anim = P.read_anim(w.read_path(path.lower()))
                        lengths[path] = (anim["duration"], anim["fps"])
                    except Exception as e:  # noqa: BLE001
                        lengths[path] = (None, str(e))
                dur, fps = lengths[path]
                line += f" {os.path.basename(path)}"
                if dur is not None:
                    frames = round(dur * fps)
                    tick = c.get("mTickDuration") or 1.0 / fps
                    line += f"  {dur:.3f} s of clip at {fps:.0f} fps, a cycle {frames * tick:.3f} s"
                    if c.get("mTickDuration"):
                        line += f" (mTickDuration {c['mTickDuration']:.4f})"
            for lk in ("mParametricPairDataList", "mConditionFloatPairDataList", "mSelectorPairDataList"):
                if c.get(lk):
                    line += "  " + ", ".join(f"{clipname(p.get('mClipName'))}={p.get('mValue', p.get('mProbability'))}"
                                             for p in c[lk] if isinstance(p, dict))
            if "mTrueConditionClipName" in c:
                line += (f"  true: {clipname(c['mTrueConditionClipName'])}, "
                         f"false: {clipname(c.get('mFalseConditionClipName'))}")
            if a.grep and a.grep.lower() not in line.lower():
                continue
            print(line)


if __name__ == "__main__":
    main()
