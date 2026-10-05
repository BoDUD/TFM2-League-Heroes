#!/usr/bin/env python3
"""Make effect pictures left-right symmetric: each frame drawn over its own mirror image.

    python tools/fix/mirror_union_fx.py --hero fiora --name league_fiora_v_ms_fx [--name ...]
    python tools/fix/mirror_union_fx.py --hero fiora --check

The client never mirrors a data effect picture (champion-data.md section 6). A caster picture that plays while the hero
is free to walk and turn - a buff's aura replayed every second (league_tristana's Rapid Fire wisp, league_masteryi's
Highlander, league_kaisa's E), one played when a projectile hits (league_jinx's Get Excited, league_varus's rage) - cannot
be drawn into one of his actions (tools/fix/bake_caster_fx.py leaves it), so it is made the same both ways: every
frame of its tag is composited over its mirror image (the picture keeps its pixels, its mirror fills in under them),
written to league/effects/league_<hero>_sym (one sheet per hero, a tag per picture, same name and durations), and the
picture's view_effects entry points there. Rerun after the source sheet changes. --check lists pictures whose sym tag
no longer matches its source.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402
import tfm2_ase  # noqa: E402

MOD = os.path.join(ROOT, "league")
SRC_KEY = "source"


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def union(frame):
    a = Image.fromarray(frame)
    m = a.transpose(Image.FLIP_LEFT_RIGHT)
    return np.asarray(Image.alpha_composite(m, a))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--name", action="append", default=[])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    hero = args.hero
    kit_path = os.path.join(MOD, "champion", f"league_{hero}.data_champion")
    raw = open(lp(kit_path), "rb").read().decode("utf-8")
    kit = json.loads(raw)
    sym = f"league_{hero}_sym"
    sym_anim = f"asset/league/effects/{sym}"
    sym_stem = os.path.join(MOD, "effects", sym)
    meta_path = os.path.join(ROOT, "assets", "source", "native", f"{hero}_sym.json")
    meta = json.load(open(meta_path, encoding="utf-8")) if os.path.exists(meta_path) else {}
    views = {v["name"]: v for v in kit.get("view_effects", [])}
    for n in args.name:
        v = views.get(n)
        if v is None:
            sys.exit(f"league_{hero}: no view_effects entry {n}")
        if v["anim"] != sym_anim:
            meta[n] = {"anim": v["anim"], "tag": v.get("tag") or v.get("loop_tag")}
    tags = {}
    stale = []
    for n, src in sorted(meta.items()):
        sp = tfm2_ase.load_sprite(os.path.join(MOD, src["anim"].split("asset/league/")[1] + "#sheet.png"))
        ids = sp.tag_frames(src["tag"])
        if not ids:
            sys.exit(f"{src['anim']} has no tag {src['tag']}")
        tags[n.replace(f"league_{hero}_", "")] = [(union(np.asarray(sp.frames[i])), sp.durations[i]) for i in ids]
    if args.check:
        if os.path.exists(lp(sym_stem + "#sheet.png")):
            have = tfm2_ase.load_sprite(sym_stem + "#sheet.png")
            for tag, frames in tags.items():
                ids = have.tag_frames(tag)
                if len(ids) != len(frames) or any(not np.array_equal(np.asarray(have.frames[i]), f)
                                                  for i, (f, _) in zip(ids, frames)):
                    stale.append(tag)
        print(f"league_{hero}: " + (f"stale: {', '.join(stale)}" if stale else f"{len(tags)} symmetric pictures up to date"))
        sys.exit(1 if stale else 0)
    if not tags:
        sys.exit(f"league_{hero}: nothing to do")
    w, h = G.write_sheet(sym_stem, tags)
    for n in meta:
        v = views[n]
        v["anim"] = sym_anim
        v["loop_tag" if "loop_tag" in v else "tag"] = n.replace(f"league_{hero}_", "")
    out = json.dumps(kit, ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(kit_path), "wb").write(out.encode("utf-8"))
    with open(meta_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(meta, ensure_ascii=False, indent=1) + "\n")
    print(f"league/effects/{sym}#sheet.png {w}x{h}: {', '.join(tags)}")


if __name__ == "__main__":
    main()
