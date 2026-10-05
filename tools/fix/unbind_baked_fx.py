#!/usr/bin/env python3
"""Drop the caster pictures a hero's <hero>_bake.json draws into his own frames.

    python tools/fix/unbind_baked_fx.py --hero jhin [--check]

tools/art/import_native.py bakes the effect tags listed in assets/source/native/<hero>_bake.json into the hero's
action frames, which the client mirrors with his facing (a data effect picture it never mirrors, so a muzzle flash
drawn pointing right pointed right on the red side too: 「烬在红色方 ... 技能特效 伤口还是反的」, 2026-10-06). This
removes every CasterViewEffect playing one of those pictures and its view_effects entry, so the picture is not drawn
twice. Sounds and everything else stay. --check only reports what is left to remove.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "native")


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def strip(o, names, count):
    if isinstance(o, dict):
        for key, v in o.items():
            if isinstance(v, dict) and v.get("type") == "CasterViewEffect" and v.get("name") in names:
                count[v["name"]] = count.get(v["name"], 0) + 1
                o[key] = {"type": "Combine", "effects": []}     # a branch that played only the picture
                continue
            strip(v, names, count)
    elif isinstance(o, list):
        keep = []
        for v in o:
            if isinstance(v, dict) and v.get("type") == "CasterViewEffect" and v.get("name") in names:
                count[v["name"]] = count.get(v["name"], 0) + 1
                continue
            strip(v, names, count)
            keep.append(v)
        o[:] = keep


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    with open(os.path.join(SRC, f"{args.hero}_bake.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    kit = os.path.join(ROOT, "league", "champion", f"league_{args.hero}.data_champion")
    raw = open(lp(kit), "rb").read().decode("utf-8")
    k = json.loads(raw)
    anim = "asset/league/effects/" + cfg["fx"]
    tags = {e["tag"] for e in cfg["items"]}
    names = {v["name"] for v in k.get("view_effects", []) if v.get("anim") == anim and v.get("tag") in tags}
    missing = tags - {v["tag"] for v in k.get("view_effects", []) if v["name"] in names}
    count = {}
    strip({key: v for key, v in k.items() if key not in ("view_effects", "view_projectiles", "view_buffs")},
          names, count)
    if args.check:
        left = sorted(names)
        print(f"league_{args.hero}: " + (f"{len(left)} baked pictures still bound: {', '.join(left)}" if left
                                          else "every baked picture unbound"))
        sys.exit(1 if left else 0)
    if not names:
        sys.exit(f"league_{args.hero}: nothing to unbind" + (f" (tags not bound: {', '.join(sorted(missing))})"
                                                              if missing else ""))
    k["view_effects"] = [v for v in k["view_effects"] if v["name"] not in names]
    out = json.dumps(k, ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(kit), "wb").write(out.encode("utf-8"))
    for n in sorted(names):
        print(f"  {n}: {count.get(n, 0)} CasterViewEffect removed, binding removed")


if __name__ == "__main__":
    main()
