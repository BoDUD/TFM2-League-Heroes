#!/usr/bin/env python3
"""Armed ults: the unused-window refund reads the arm flag 3 ticks before the window ends, not on its last tick.

    python tools/fix/arm_refund_read.py [--check]

An armed ult's slot only raises a caster flag (r_arm / r_armed, n ticks) and a poll fires the real ult; unused, a
`Delayed` of n ticks reads the flag and gives the cooldown back (a 3-tick buff with `ult_cooldown_mult`). But a flag of
n ticks is seen on n - 1 of them (champion-data.md section 8; classic-SDK probe 2026-11-05, lr1105/fix_j/probe.py: seen
148 of 148 times at every offset up to n - 1, never at n), so the read on tick n always found it gone and a lapsed
window cost the full cooldown (league_sion traced: lapse-to-rearm 3558 ticks, 877 once read at n - 3). The generated
kits carry the fix in tools/kit/build_<hero>.py (`delayed(p["r_arm"] - 3, ...)`); this script moves the same read for
the kits whose shipped JSON is hand-kept or post-processed after the generator, so a rebuild would not reproduce it:
  league_aatrox, league_blitzcrank, league_evelynn, league_fiora, league_riven, league_taric, league_twistedfate,
  league_kayle, league_zilean (these two read at n - 1)
      hand-kept (no tools/kit generator)
  league_alistar, league_lissandra, league_tryndamere
      generated, then baked (CasterAnimation / view entries; Tryndamere's bake table lives in assets/, absent from a
      sparse checkout): build_alistar.py, build_lissandra.py and build_tryndamere.py carry the -3 too
A read at n - 1 is not enough either: league_wukong's (n - 1) refunded 46 of 53 lapsed windows in 48 traced games, the
other 7 found the flag gone - every kit reads at n - 3 now, which refunded 177 of 177 (league_anivia).
For each hero's ult: a `Delayed` reading the n-tick arm flag (a `SwitchByBuff` on it with a cooldown-multiplier caster
buff inside) later than n - 3 goes to n - 3. Idempotent (--check: exit 1 while any read is later). With file paths as
arguments it patches those files instead (an add-on's copy whose make_override.py cannot run here).
tools/kit/check_arm_refund.py is the guard that reports any such read in the shipped data. Add-on copies made from
these files are rebuilt after this (league_aatrox_chain, league_executes, league_fiora_duel, league_lowhp:
make_override.py).
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEROES = ["league_aatrox", "league_alistar", "league_blitzcrank", "league_evelynn", "league_fiora", "league_lissandra",
          "league_riven", "league_taric", "league_twistedfate", "league_tryndamere", "league_kayle",
          "league_zilean"]
MARGIN = 3


def lp(path):
    path = os.path.abspath(path)
    return path if not os.name == "nt" or path.startswith("\\\\?\\") else "\\\\?\\" + path


def flags(node, out, tick=0):
    """Caster flags set in the tree: name -> longest duration at tick 0 (the cast)."""
    if isinstance(node, list):
        for x in node:
            flags(x, out, tick)
    elif isinstance(node, dict):
        t = node.get("type")
        if t == "Delayed":
            tick += int(node.get("tick", 0))
        if t == "AddCasterBuff" and tick == 0:
            st = node["buff_state"]
            if isinstance(st.get("duration"), dict) and "Time" in st["duration"]:
                out[st["name"]] = max(out.get(st["name"], 0), int(st["duration"]["Time"]["tick"]))
        if t == "AddCasted":
            return
        for k, v in node.items():
            if isinstance(v, (dict, list)) and k not in ("applied_effects", "end_effects"):
                flags(v, out, tick)


def refund_read(node):
    """The arm flag a `SwitchByBuff` chain under a Delayed reads for a cooldown-multiplier buff, or None."""
    if isinstance(node, list):
        for x in node:
            r = refund_read(x)
            if r:
                return r
        return None
    if not isinstance(node, dict):
        return None
    t = node.get("type")
    if t == "SwitchByBuff":
        if has_mult(node.get("effect_buff")):
            return node["buff_name"]
        return None
    if t in ("Combine", "RangeEffect"):
        return refund_read(node.get("effects"))
    return None


def has_mult(node):
    if isinstance(node, list):
        return any(has_mult(x) for x in node)
    if not isinstance(node, dict):
        return False
    if node.get("type") == "AddCasterBuff":
        return any(k.endswith("cooldown_mult") for k in node["buff_state"])
    return any(has_mult(v) for v in node.values() if isinstance(v, (dict, list)))


def reads(node, arm, out, tick=0):
    """Every Delayed (at cumulative tick) reading one of the arm flags for a refund: (node, flag, tick before it)."""
    if isinstance(node, list):
        for x in node:
            reads(x, arm, out, tick)
    elif isinstance(node, dict):
        t = node.get("type")
        if t == "Delayed":
            name = refund_read(node.get("effects"))
            if name in arm:
                out.append((node, name, tick))
            tick += int(node.get("tick", 0))
        if t == "AddCasted":
            return
        for k, v in node.items():
            if isinstance(v, (dict, list)) and k not in ("applied_effects", "end_effects"):
                reads(v, arm, out, tick)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("files", nargs="*", help="kit files to patch instead of the main pack's list")
    a = ap.parse_args()
    todo = 0
    paths = a.files or [os.path.join(ROOT, "league", "champion", f"{hero}.data_champion") for hero in HEROES]
    for path in paths:
        hero = os.path.basename(path).split(".")[0]
        with open(lp(path), "rb") as f:
            raw = f.read().decode("utf-8-sig")
        d = json.loads(raw)
        ult = d["ult"].get("effect", d["ult"].get("effects"))
        arm = {}
        flags(ult, arm)
        arm = {k: n for k, n in arm.items() if k.endswith(("_r_arm", "_r_armed"))}
        found = []
        reads(ult, arm, found)
        if not arm or not found:
            sys.exit(f"{hero}: no armed-ult refund read found ({arm}) - the kit changed, look again")
        late = [(node, name) for node, name, before in found if before + node["tick"] > arm[name] - MARGIN]
        done = [(node, name) for node, name, before in found if before + node["tick"] == arm[name] - MARGIN]
        todo += len(late)
        if a.check:
            print(f"{hero}: {len(found)} refund reads, {len(late)} later than n - {MARGIN}, {len(done)} at n - {MARGIN}")
            continue
        for node, name in late:
            node["tick"] = arm[name] - MARGIN
        if late:
            nl = "\r\n" if "\r\n" in raw else "\n"
            text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl
            with open(lp(path), "w", encoding="utf-8", newline="") as f:
                f.write(text)
        print(f"{hero}: {len(late)} of {len(found)} refund reads moved to n - {MARGIN}" + "".join(
            f" ({name} {arm[name]} ticks -> read at {arm[name] - MARGIN})" for _, name in late))
    if a.check:
        sys.exit(1 if todo else 0)


if __name__ == "__main__":
    main()
