#!/usr/bin/env python3
"""league_caitlyn redone at PPU 1.45 (the user, 2026-10-23: 「设计通过，用 PPU 1.45（和现在一样高）」): her idle is the approved
design (tools/art/design_caitlyn_hd.py), every other action Codex's whole-frame redraw of that design in League's pose
of the frame (tools/art/pack_caitlyn_actions.py), read back with the rifle drawn straight
(tools/art/actions_caitlyn_hd.py), each stood on her ground by its pivot. The effects stay baked as before
(assets/source/native/caitlyn_bake.json, Rig.bake).

    python tools/art/rig_caitlyn_hd.py --review DIR      # every tag at 3x + GIFs
    python tools/art/rig_caitlyn_hd.py                   # orig strips + the 1x sheet
    python tools/art/hero_reels.py --hero caitlyn        # then: the idle / ban-pick reels from idle_base

League's frames of a tag (poses.json) are spread over the sheet's frame count the way ppu_rig.fit_rows does.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "caitlyn"
PPU = 1.45
DESIGN_ROWS = 65
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
LEAD = 0.6                               # a flash's centre this share of its half width past the muzzle
REELS = {"idle", "bp"}                   # tools/art/hero_reels.py's tags: rebuilt after the export


def lp(path):
    return R.lp(path)


def picture():
    d = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(lp(os.path.join(HD, "picture.png")))
    return d


def design():
    want = picture()
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != want.shape or (D.d != want).any():
        sys.exit("hd/picture.png does not read back as hd/design.png")
    D.d0 = D.d.copy()
    return D


MUZZLES = {}                             # id(canvas) -> (muzzle (x, y) on the canvas, the rifle's direction)


def muzzle_of(rf):
    """The straight rifle's muzzle in its frame and its direction (actions.json's rifle: the way, the grip)."""
    import rifle_caitlyn as RC
    a = np.radians(rf["way"])
    u = np.array((np.cos(a), -np.sin(a)))
    return np.array(rf["grip"], float) + u * RC.LENGTH * (1 - RC.GRIP), u


def placed(rig, img, pivot, rf=None):
    """A canvas with img's pivot on the standing point (the design's soles' middle on the ground)."""
    can = rig.canvas()
    h, w = img.shape[:2]
    x0 = int(round(rig.CX - pivot[0]))
    y0 = int(round(rig.GY - pivot[1]))
    ys, xs = np.nonzero(img[..., 3] > 0)
    Y, X = ys + y0, xs + x0
    ok = (Y >= 0) & (Y < can.shape[0]) & (X >= 0) & (X < can.shape[1])
    can[Y[ok], X[ok]] = img[ys[ok], xs[ok]]
    can[rig.GY:] = 0
    if rf is not None:
        m, u = muzzle_of(rf)
        MUZZLES[id(can)] = (m + (x0, y0), u)
    return can


def muzzle_cfg():
    """caitlyn_bake.json with every item's offset cleared: its flashes are laid on the pivot, then at_muzzles moves
    each frame's to that frame's muzzle (the old offsets were the 1x sprite's muzzle)."""
    with open(lp(os.path.join(R.ROOT, "assets", "source", "native", f"{HERO}_bake.json")), encoding="utf-8") as f:
        cfg = json.load(f)
    for e in cfg["items"]:
        e.pop("dx", None)
        e.pop("dy", None)
    return cfg


def at_muzzles(rig, acts):
    """Each frame's flash (its "over" layer, laid on the pivot) moved so its centre sits LEAD squares past that
    frame's muzzle along the rifle."""
    for tag, fr in acts.items():
        for lay, _ in fr:
            if not isinstance(lay, dict) or lay.get("over") is None:
                continue
            m = MUZZLES.get(id(lay["body"]))
            if m is None:
                continue
            (mx, my), u = m
            ov = lay["over"]
            ys, xs = np.nonzero(ov[..., 3] > 0)
            if not len(ys):
                continue
            # the flash's own middle (its picture is not centred in the effect frame) to just past the muzzle
            half = (xs.max() - xs.min() + 1) / 2
            cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
            dx = int(round(mx + u[0] * (half * LEAD) - cx))
            dy = int(round(my + u[1] * (half * LEAD) - cy))
            new = np.zeros_like(ov)
            Y, X = ys + dy, xs + dx
            ok = (Y >= 0) & (Y < ov.shape[0]) & (X >= 0) & (X < ov.shape[1])
            new[Y[ok], X[ok]] = ov[ys[ok], xs[ok]]
            lay["over"] = new
    return acts


def frames(rig):
    D = rig.D
    with open(lp(os.path.join(HD, "actions", "actions.json")), encoding="utf-8") as f:
        info = json.load(f)
    acts_img = {k: np.asarray(Image.open(lp(os.path.join(HD, "actions", k + ".png"))).convert("RGBA")) for k in info}
    sheet = R.sheet_of(HERO)
    bake = json.load(open(lp(os.path.join(R.ROOT, "assets", "source", "native", f"{HERO}_bake.json")), encoding="utf-8"))
    baked = {e["into"] for e in bake["items"] if "from" in e}
    # the design's standing point: its soles' middle (the rig's CX / GY)
    idle = placed(rig, D.d0, (D.px, D.ground))
    out = {}
    for tag in sheet:
        if tag in baked or tag in REELS:
            continue
        ms = [m for _, m in sheet[tag]]
        if tag == "idle_base":
            fr = [idle.copy() for _ in ms]
        else:
            n = len([k for k in info if k.rsplit("_", 1)[0] == tag])
            if not n:
                sys.exit(f"{tag}: no redrawn frames")
            idx = [min(n - 1, int(i * n / len(ms))) for i in range(len(ms))]
            fr = [placed(rig, acts_img[f"{tag}_{k + 1}"], info[f"{tag}_{k + 1}"]["pivot"], info[f"{tag}_{k + 1}"]["rifle"])
                  for k in idx]
        if tag == "hit":
            m = MUZZLES.get(id(fr[0]))
            fr[0] = R.flash(fr[0])
            if m:
                MUZZLES[id(fr[0])] = m
        out[tag] = list(zip(fr, ms))
    # the reels (tools/art/hero_reels.py rebuilds them from idle_base and the actions): the drawn idle for now
    out["idle"] = [(idle.copy(), m) for _, m in out["idle_base"]]
    acts = at_muzzles(rig, rig.bake(out, cfg=muzzle_cfg()))
    for t in sheet:
        if t in REELS:
            continue
        if t not in acts or len(acts[t]) != len(sheet[t]):
            sys.exit(f"{t}: frames differ from the sheet")
    return {t: acts[t] for t in sheet if t in acts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    rig = R.Rig(D, pad=(90, 90, 90, 30))
    acts = frames(rig)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
