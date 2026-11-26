#!/usr/bin/env python3
"""Camille's R arena floor, one tag a frame: `r_zone_<k>` / `hd_r_zone_<k>` in league_camille_big for the add-on's pieces.

    python tools/fix/camille_r_zone_frames.py [--check]

The user (2026-11-17): 「顺便查一下卡密尔的大招也有bug吧 怎么敌人走的出去？」, then 「卡密尔离开磁场后 磁场也不消失？」. The main
pack draws the arena's standing floor as one 240-tick zone (`r_floor`, tools/fix/camille_r_floor.py): a zone's picture
cannot be stopped, so when the arena ends early - she is knocked out of it, hooks out with her low-health E, dies - the
floor stays its 4 s with nobody held in it. With the add-on league_camille_wall the floor is drawn by the add-on instead,
while the arena is up (`r_on` on her): a projectile piece every 5 ticks on the arena's centre, each showing one frame
of `r_zone`'s loop (6 frames of 83 ms), so it is gone within 5 ticks of the arena's end. A projectile shows its tag
from its first frame, so each piece needs a tag of its own frame: `r_zone_<k>` is frame k of `r_zone`, `hd_r_zone_<k>`
frame k of `hd_r_zone` - the same rects and durations, no new pixels (the sheet's PNG is untouched; the repack in
tools/package_mod.py keeps identical frames shared). The main pack's own data does not use them.

Run it again after anything rewrites the sheet (import_camille.py, densify_fx.py, fx_handmade.py): it copies whatever
`r_zone` / `hd_r_zone` hold then. Idempotent; --check exits 1 when the sheet's tags are missing or differ (the add-on's
test `the_floor_pieces_are_r_zones_frames` asks the same).
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "effects", "league_camille_big#anim.fanim")
SRC = "r_zone"


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def with_frames(anims):
    """the anims with r_zone_<k> / hd_r_zone_<k> (one frame each) after hd_r_zone, the other tags as they stand"""
    for tag in (SRC, "hd_" + SRC):
        if tag not in anims:
            sys.exit(f"{PATH}: no {tag} - the sheet changed, update this script")
    if len(anims[SRC]["frames"]) != len(anims["hd_" + SRC]["frames"]):
        sys.exit(f"{SRC} and hd_{SRC} have different frame counts")
    out = {k: v for k, v in anims.items() if not (k.startswith(SRC + "_") or k.startswith("hd_" + SRC + "_"))}
    for pre in ("", "hd_"):
        for k, frame in enumerate(anims[pre + SRC]["frames"]):
            out[f"{pre}{SRC}_{k}"] = {"frames": [frame]}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 when the sheet differs; write nothing")
    a = ap.parse_args()
    with open(lp(PATH), encoding="utf-8") as f:
        raw = f.read()
    doc = json.loads(raw)
    doc["anims"] = with_frames(doc["anims"])
    # the sheet's own writer (strips.write_sheet): minified, no newline at the end
    new = json.dumps(doc, separators=(",", ":"), ensure_ascii=False)
    n = len(doc["anims"][SRC]["frames"])
    if new == raw:
        print(f"{os.path.relpath(PATH, ROOT)}: {SRC}_0..{n - 1} and hd_{SRC}_0..{n - 1} up to date")
        return
    if a.check:
        print(f"{os.path.relpath(PATH, ROOT)}: {SRC}_<k> / hd_{SRC}_<k> missing or out of date - run "
              "python tools/fix/camille_r_zone_frames.py")
        sys.exit(1)
    with open(lp(PATH), "w", encoding="utf-8", newline="") as f:
        f.write(new)
    print(f"wrote {os.path.relpath(PATH, ROOT)}: {SRC}_0..{n - 1} and hd_{SRC}_0..{n - 1}, one frame each")


if __name__ == "__main__":
    main()
