#!/usr/bin/env python3
"""Bring a career save's copies of our heroes up to the installed mods (the user, 2026-11-01: 「你帮我迁移存档英雄数据吧」).

    python -I tools/save/refresh_save_heroes.py SAVE [OUT] [--mods DIR] [--prefix league_ --prefix tft_]

Without OUT it only reports which copies are stale.

Why. A TFM2 career save keeps its own copies of every champion definition: one list per ruleset (seven in the career
started 2026-10-29), each a u64 count, then per champion the u64 tag b"1HCM", a u64 length and the champion as compact
JSON (the game's serialisation: every field, defaults included, no view_* tables). The game fills them from the loaded
mods when the career starts and adds a champion that appears later, but never reads a changed one again. So a fix in
a .data_champion (or in an add-on's override of one) does not reach a running career, while add-on code does
(league_addons.dll is loaded at every start). Checked on the 2026-10-29 career on 11-01: its Galio, Rumble, Kled,
Wukong, Tahm Kench, Sylas, Azir, Cho'Gath and Aurelion Sol were the versions of 10-28/29, and ten TFT heroes had no
basic attack in three of the seven lists.

What. The installed definition of a champion is its mod's champion/<id>.data_champion, or the file an "override"
entry of any mod's mod.override_info remaps it to (the add-ons' copies); the local mods folder only (the Workshop
copies of our mods are older and lose to it). For every champion whose id starts with a prefix, a copy that differs
from it (a value of the installed JSON the copy lacks or has otherwise, or a non-default value the copy has that the
installed JSON leaves out) becomes the installed JSON without view_projectiles / view_effects / view_buffs, with the
career's balance patches kept. Some rulesets are the career's unpatched start (checked on 11-01: their stat and growth
equal the 10-29 files for every hero), the others scale some stat / growth values (a hero's hp 1200 -> 1032). Such a
value becomes the installed one times the copy's over the unpatched ruleset's (Viego's hp went 980 -> 900 after the
career started: a patched 843 becomes 774). The game reorders the rulesets when it saves (11-01: the patched values
of Rumble and Aatrox moved between lists 3-6 across one save), so the unpatched one is not taken as the first list:
it is the list whose stat and growth equal the installed files for the most of our champions - after a refresh all
of them, and a patched list misses at least its patched champions (taking a patched Aatrox's 946 as the base would
make his unpatched 1100 into 1279). Everything else stays: other champions byte for byte, the rest of the body, the
header but for the gzip part's length and CRC32. OUT is read back and checked.

The game's other mentions of a champion are by id (athletes' proficiency, match history, news, each ruleset's table
of skill numbers): none points into a definition. Run it with the game closed and keep the original; the game also
keeps SAVE.bak (its previous save) and falls back to it when SAVE does not load. The save folder is synced by Steam
Cloud: if Steam reports a conflict at the next start, keep the local file.
"""
import argparse
import collections
import glob
import gzip
import json
import os
import re
import struct
import sys
import zlib

MODS = "D:/Steam/steamapps/common/Teamfight Manager2/mods"
TAG = b"1HCM"
VIEW = ("view_projectiles", "view_effects", "view_buffs")
PATCHED = ("stat", "growth")
START = re.compile(rb'\{"id":"([a-z][a-z0-9_]*)"')
# enum fields the game writes out at their first value, which our files leave out (checked on 11-01: the only one)
ENUM_DEFAULTS = {"attack_effect_type": "Target"}


def split(b):
    """(offset of the gzip part, the body): b"TFM2", version byte 5, u32 timestamp, u32 database version, u64 length
    of the gzip part (offset 13), u32 CRC32 of it (offset 21), preview metadata and logos, then one gzip member"""
    if b[:5] != b"TFM2\x05":
        sys.exit("not a TFM2 v5 file")
    glen = struct.unpack_from("<Q", b, 13)[0]
    off = len(b) - glen
    if not 25 <= off < len(b) or b[off:off + 3] != b"\x1f\x8b\x08":
        sys.exit("gzip part not where the header says")
    if zlib.crc32(b[off:]) != struct.unpack_from("<I", b, 21)[0]:
        sys.exit("CRC32 of the gzip part does not match the header")
    d = zlib.decompressobj(31)
    body = d.decompress(b[off:]) + d.flush()
    if d.unused_data or not d.eof:
        sys.exit("gzip part has trailing data / is cut")
    return off, body


def entries(body):
    """[(start of the tag, end, id)] for every tagged, length-prefixed champion JSON whose length ends on its brace"""
    out = []
    for m in START.finditer(body):
        p = m.start()
        if p < 16 or body[p - 16:p - 8] != TAG + b"\0" * 4:
            continue
        ln = struct.unpack_from("<Q", body, p - 8)[0]
        if not 2 <= ln <= 1 << 26 or p + ln > len(body) or body[p + ln - 1:p + ln] != b"}":
            continue
        try:
            d = json.loads(body[p:p + ln])
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("id") == m.group(1).decode():
            out.append((p - 16, p + ln, d["id"]))
    return out


def lists(body):
    """[[entries]] for runs of entries that follow each other byte for byte, each run's u64 count checked"""
    runs = []
    for e in entries(body):
        if runs and e[0] == runs[-1][-1][1]:
            runs[-1].append(e)
        else:
            runs.append([e])
    for r in runs:
        n = struct.unpack_from("<Q", body, r[0][0] - 8)[0]
        if n != len(r):
            sys.exit(f"list at {r[0][0] - 8}: count field {n} != {len(r)} parsed entries")
    return runs


def installed(mods):
    """{id: (file, JSON)}: each mod's champion files, an override remapping of one replacing it"""
    files = {}
    for p in glob.glob(f"{mods}/*/champion/*.data_champion"):
        files.setdefault(os.path.basename(p).split(".")[0], []).append(p)
    over = collections.defaultdict(list)
    for info in glob.glob(f"{mods}/*/mod.override_info"):
        for asset, v in json.loads(open(info, encoding="utf-8-sig").read()).items():
            if v.get("type") != "override" or "/champion/" not in asset:
                continue
            hits = glob.glob(os.path.join(mods, *v["remapping"].split("/")[1:]) + ".data_champion")
            if len(hits) != 1:
                sys.exit(f"{info}: {asset} remaps to {v['remapping']}, found {hits}")
            over[asset.rsplit("/", 1)[1]].append(hits[0])
    out = {}
    for cid in set(files) | set(over):
        pick = over.get(cid) or files.get(cid)
        if len(pick) != 1:
            sys.exit(f"{cid}: {len(pick)} candidate definitions: {pick}")
        out[cid] = (pick[0], json.loads(open(pick[0], "rb").read().decode("utf-8-sig")))
    return out


def is_default(v, key=None):
    return key in ENUM_DEFAULTS and v == ENUM_DEFAULTS[key] or v in (0, False, "", None, [], {}) or \
        isinstance(v, dict) and all(is_default(x, k) for k, x in v.items())


def differs(new, copy):
    """does the copy (the game's full serialisation) say anything the new compact JSON does not?"""
    if isinstance(new, dict) and isinstance(copy, dict):
        return any(k not in copy or differs(v, copy[k]) for k, v in new.items()) or \
            any(not is_default(v, k) for k, v in copy.items() if k not in new)
    if isinstance(new, list) and isinstance(copy, list):
        return len(new) != len(copy) or any(differs(a, b) for a, b in zip(new, copy))
    return new != copy


def patched(now, first, copy):
    """the installed section with each value the career patched (copy != the unpatched ruleset) scaled the same way"""
    out = dict(now)
    for k, c in copy.items():
        c0 = first.get(k, 0)
        if c == c0 or not isinstance(c, int) or not isinstance(c0, int):
            continue
        f = now.get(k, 0)
        out[k] = round(f * c / c0) if c0 else f + c - c0
    return out


def base_list(runs, body, defs, prefixes):
    """(index, matches, champions): the unpatched ruleset - the list whose stat and growth equal the installed
    definitions' for the most of our champions (a tie: the first of them)"""
    best, champions = (0, -1), 0
    for li, run in enumerate(runs):
        n = champions = 0
        for s, e, cid in run:
            if not cid.startswith(prefixes) or cid not in defs:
                continue
            champions += 1
            copy, defn = json.loads(body[s + 16:e]), defs[cid][1]
            if all(isinstance(copy.get(sec), dict) and
                   all(copy[sec].get(k, 0) == v for k, v in (defn.get(sec) or {}).items()) for sec in PATCHED):
                n += 1
        if n > best[1]:
            best = (li, n)
    return best[0], max(best[1], 0), champions


def refreshed(defn, first, copy):
    new = {k: v for k, v in defn.items() if k not in VIEW}
    for sec in PATCHED:
        if isinstance(copy.get(sec), dict) and isinstance(first.get(sec), dict):
            new[sec] = patched(new.get(sec, {}), first[sec], copy[sec])
    return new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("save")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--mods", default=MODS)
    ap.add_argument("--prefix", action="append", default=None, help="champion id prefixes (default league_, tft_)")
    a = ap.parse_args()
    prefixes = tuple(a.prefix or ("league_", "tft_"))
    b = open(a.save, "rb").read()
    off, body = split(b)
    runs = lists(body)
    if not runs:
        sys.exit("no champion definition lists in the body")
    defs = installed(a.mods)
    bi, matched, champions = base_list(runs, body, defs, prefixes)
    first = {e[2]: json.loads(body[e[0] + 16:e[1]]) for e in runs[bi]}
    repl, report, missing = {}, collections.defaultdict(list), set()
    for li, run in enumerate(runs):
        for s, e, cid in run:
            if not cid.startswith(prefixes):
                continue
            if cid not in defs:
                missing.add(cid)
                continue
            copy = json.loads(body[s + 16:e])
            new = refreshed(defs[cid][1], first.get(cid, copy), copy)
            if differs(new, copy):
                repl[s] = (e, json.dumps(new, separators=(",", ":"), ensure_ascii=True).encode())
                report[cid].append(li)
    print(f"{a.save}: {len(runs)} lists of {[len(r) for r in runs]} champions; {len(repl)} stale copies of "
          f"{len(report)} champions")
    print(f"  unpatched ruleset: list {bi} (stat and growth equal the installed files for {matched} of {champions} "
          f"of ours)")
    for cid in sorted(report):
        print(f"  {cid}: lists {report[cid]}  <- {os.path.relpath(defs[cid][0], a.mods)}")
    if missing:
        print(f"  not installed (left as they are): {' '.join(sorted(missing))}")
    if not a.out or not repl:
        return
    parts, prev = [], 0
    for s in sorted(repl):
        e, js = repl[s]
        parts += [body[prev:s], TAG + b"\0" * 4, struct.pack("<Q", len(js)), js]
        prev = e
    parts.append(body[prev:])
    new_body = b"".join(parts)
    gz = gzip.compress(new_body, compresslevel=6, mtime=0)
    out = b[:13] + struct.pack("<QI", len(gz), zlib.crc32(gz)) + b[25:off] + gz
    with open(a.out, "wb") as f:
        f.write(out)
    # read back: the same lists, the replaced copies as written, everything else byte for byte
    rb = open(a.out, "rb").read()
    roff, rbody = split(rb)
    if rb[:13] != b[:13] or rb[25:roff] != b[25:off] or rbody != new_body:
        sys.exit(f"{a.out}: read-back differs")
    rruns = lists(rbody)
    if [[x[2] for x in r] for r in rruns] != [[x[2] for x in r] for r in runs]:
        sys.exit(f"{a.out}: the lists' champions changed")
    olds = [x for r in runs for x in r]
    for (s, e, cid), (rs, re_, _) in zip(olds, [x for r in rruns for x in r]):
        if s in repl:
            if rbody[rs + 16:re_] != repl[s][1]:
                sys.exit(f"{a.out}: {cid} at {s} not as written")
        elif rbody[rs:re_] != body[s:e]:
            sys.exit(f"{a.out}: {cid} at {s} changed")
    print(f"{a.save} -> {a.out}: {len(repl)} copies rewritten; body {len(body)} -> {len(rbody)}, file {len(b)} -> "
          f"{len(rb)}; read back and checked")


if __name__ == "__main__":
    main()
