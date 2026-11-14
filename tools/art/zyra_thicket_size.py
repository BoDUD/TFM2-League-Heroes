#!/usr/bin/env python3
"""Zyra's R thicket (league/effects/league_zyra_thicket) drawn at the size of R's radius, crisp, with dense twins.

    python -I tools/art/zyra_thicket_size.py           # write the sheet for build_zyra.P["r_r"]
    python -I tools/art/zyra_thicket_size.py --check   # fail unless the sheet is what this writes

The user, 2026-11-14: 「婕拉的大招范围大小改了没有 我记得我之前想让扩大点的 按照联盟的比例缩小点扩大 … 没改的话也顺手改了」,
「记得扩大后不要太糊 特效」, 「还有哪些技能没高清化的也高清化一下」. R's radius went 32000 -> 38000 (League's 575 against
Neeko's 600 = our 40000). Codex drew the thicket's ring 58 squares wide for a radius of 32000 (a game px a square;
tools/art/import_zyra_fx.py). On 2026-10-20 it was blown up 1.5 times for 44000 - squares of 1.5 game px, blurred in game
(「婕拉的大招特效局内怎么这么模糊」) - and went back to 32000 and Codex's own squares. So here the picture is not stretched:
every frame (Codex's cells 1:1 at 32000, import_zyra_fx.thicket_tags) is redrawn eight times finer by
tools/art/fx_vector.redraw_tag (its boundaries traced and smoothed, the same drawing - the tool of the 553 effect redraws
the user took on 11-14), and that picture is read back one sample a square at the new size (r_r / 32000 times bigger):
the 1x frame - a square a game px, nothing blurred - and the hd_ frame at twice that (PPU 2, a square half a game px,
exactly twice the 1x frame). Every frame stays centred on the pivot (the ring's middle on the ground) as Codex's are.
tools/art/fx_ppu_table.py then lists the sheet in league_main's fx_ppu.rs (dense since it has hd_ twins).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import import_zyra_fx as Z  # noqa: E402
import fx_vector as V  # noqa: E402
import densify_fx as D  # noqa: E402
import build_zyra as K  # noqa: E402

BASE_R = 32000            # the radius Codex's ring (58 squares) was drawn for
FINE = 8                  # fx_vector's redraw this many times finer before the picture is read back
STEM = os.path.join(ROOT, "league", "effects", "league_zyra_thicket")


def codex_frames():
    """league_zyra_thicket's idle at 32000 as import_zyra_fx makes it: [(canvas, ms)]"""
    man = json.load(open(Z.lp(os.path.join(Z.SRC, "manifest.json")), encoding="utf-8-sig"))
    for e in man.get("effects") or man.get("assets") or man["entries"]:
        name = e.get("name") or e.get("id") or e["file"][len("zyra_fx_"):-len(".png")]
        if name == "r_thicket":
            meta = dict(e, pixel_1x=os.path.join(Z.SRC, "pixel_1x", e["file"]))
            break
    else:
        sys.exit("no r_thicket in the Codex manifest")
    cs = Z.cells("r_thicket", meta)
    return [(a, round(ms, 3)) for a, ms in Z.thicket_tags(cs, Z.FX["r_thicket"][1])["idle"]]   # ms as a .fanim keeps them


def resample(fine, w, h, s, out_w, out_h, k):
    """read `fine` (a frame w x h redrawn FINE times finer) back at s times its 1x size, k samples a game px, out_w x out_h
    game px, both centred: one nearest sample a square (no blending)"""
    H, W = fine.shape[:2]
    oy = (np.arange(out_h * k) + 0.5) / k - out_h / 2      # game px from the centre, the output's square middles
    ox = (np.arange(out_w * k) + 0.5) / k - out_w / 2
    sy = (oy / s + h / 2) * FINE                           # back in the fine picture
    sx = (ox / s + w / 2) * FINE
    iy = np.floor(sy).astype(int)
    ix = np.floor(sx).astype(int)
    out = np.zeros((out_h * k, out_w * k, 4), np.uint8)
    vy = (iy >= 0) & (iy < H)
    vx = (ix >= 0) & (ix < W)
    out[np.ix_(vy, vx)] = fine[np.ix_(iy[vy], ix[vx])]
    return out


def even(n):
    return int(2 * round(n / 2))


def frames_for(r_r):
    src = codex_frames()
    s = r_r / BASE_R
    fine = V.redraw_tag([a for a, _ in src], P=FINE)
    h, w = src[0][0].shape[:2]
    out_w, out_h = even(w * s), even(h * s)
    one = [(resample(f, w, h, s, out_w, out_h, 1), ms) for f, (_, ms) in zip(fine, src)]
    dense = [(resample(f, w, h, s, out_w, out_h, 2), ms) for f, (_, ms) in zip(fine, src)]
    return {"idle": one, "hd_idle": dense}, s


def same(a, b):
    return list(a) == list(b) and all(len(a[t]) == len(b[t]) and all(
        x.shape == y.shape and np.array_equal(x, y) and mx == my for (x, mx), (y, my) in zip(a[t], b[t])) for t in a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    r_r = K.P["r_r"]
    tags, s = frames_for(r_r)
    now = D.load_sheet(STEM)
    if same(tags, now):
        print(f"league_zyra_thicket: up to date (R radius {r_r}, x{s:.4f})")
        return
    if a.check:
        sys.exit(f"league_zyra_thicket: not the sheet for R radius {r_r} - run tools/art/zyra_thicket_size.py")
    D.G.write_sheet(D.G.lp(STEM), tags, share=True)
    print(f"league_zyra_thicket: written for R radius {r_r} (x{s:.4f}): 1x {tags['idle'][0][0].shape[1]}x"
          f"{tags['idle'][0][0].shape[0]}, hd {tags['hd_idle'][0][0].shape[1]}x{tags['hd_idle'][0][0].shape[0]}")


if __name__ == "__main__":
    main()
