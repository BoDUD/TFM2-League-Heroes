#!/usr/bin/env python3
"""league_milio's run from Codex's leg redo (tools/art/pack_milio_run.py -> outputs/milio-run, 2026-10-15).

    python tools/art/import_milio_run.py --prepare <delivery>/raw      (once: the raws -> codex_run/)
    python tools/art/import_milio_run.py [--review DIR]

Codex's own finished frames are NOT used: it took the near leg of its first draft and bent it bone by bone onto every
frame's guide lines (its HANDOFF: 「按大腿、小腿、脚分段重映射」) - the warped bone legs this user calls deformed (memory
run-legs-caitlyn-way). Its eight raw drafts are the model's own legs, and they are read here: each raw lies on the
pack's canvas within a square of the upper body it was given (the design head matched at scale 1.0, 0.975 once), so
  * the raw, snapped to the design's colours, is voted down at 6 px a square (block_vote) at the offset its head match
    gives;
  * its legs - everything under its own kilt's hem (the kilt-and-sash piece, import_milio_strips.KILT) - go under the
    upper body the pack gave it (Codex's step-2 run frame, its legs cut, at the frame's bob: pack_milio_run.legless),
    which stays square for square (one face, the same arms);
  * the eight are played in the order of a stride (ORDER): Codex drew the light near leg in front in all eight again,
    but in three kinds of pose - A the light leg planted ahead and the dark one kicked up behind (raws 1, 2, 5, 6), B
    the dark leg planted under the hips and the light one swinging forward past it, knee up (3, 7), C a wide stride,
    both feet down (4, 8) - so the loop is C A A B* C* A* A* B (raws 4 1 2 7 4 1 2 7), the * frames with the two
    legs' skins swapped in place (the dark leg then lands ahead and the light one kicks up behind): each leg goes
    landing ahead - under the body - pushing off - kicked up - swinging forward past the other (the cross step, frames
    4 and 8) - landing again;
  * grounded (the lowest square on SOLE), small holes and the outline closed (import_milio_strips.final_clean).
Writes assets/source/milio/frames/run_<n>.png and frames.json "run_redo" (per frame: the raw, the upper body's source,
the bob, the swap, the head's top-left), which rig_milio.py reads.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import import_milio_strips as I  # noqa: E402
import pack_milio_run as R  # noqa: E402

CODEX = os.path.join(I.SRC, "codex_run")
# the two half strides drawn alike: C (raw 4), A (raws 1, 2), then B (raw 7: the knee swinging forward past the planted
# leg - its raw 3 swung the heel up behind under the kilt instead); the second half the same four with the skins swapped,
# so the body bobs alike in both (heads on rows 59, 62, 63, 61; with raws 8, 5, 6, 3 for the second half they went
# 62, 60, 60, 58 - a hitch every other step)
ORDER = [(4, False), (1, False), (2, False), (7, True), (4, True), (1, True), (2, True), (7, False)]
PX = R.PX


def prepare(raw):
    """The raws snapped to the design's colours, as indexed crops (codex_run/<name>.png + crops.json)."""
    os.makedirs(CODEX, exist_ok=True)
    crops = {}
    flat = [0, 0, 0] + [int(v) for c in I.PAL for v in c]
    for k in range(1, 9):
        name = f"milio_run_{k}"
        a = np.asarray(Image.open(os.path.join(raw, name + ".png")).convert("RGBA"))
        op = a[..., 3] >= I.ALPHA
        ys, xs = np.nonzero(op)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        idx = np.zeros(op.shape, np.uint8)
        idx[op] = I.snap(a[op][:, :3]) + 1
        im = Image.fromarray(idx[y0:y1, x0:x1], "P")
        im.putpalette(flat + [0] * (768 - len(flat)))
        im.save(os.path.join(CODEX, name + ".png"), transparency=0)
        crops[name] = [int(x0), int(y0)]
        print(name, (x1 - x0, y1 - y0))
    with open(os.path.join(CODEX, "crops.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(crops, f, indent=1)


def load_raw(k):
    crops = json.load(open(os.path.join(CODEX, "crops.json"), encoding="utf-8"))
    name = f"milio_run_{k}"
    p = np.asarray(Image.open(os.path.join(CODEX, name + ".png")))
    x0, y0 = crops[name]
    out = np.full(I.CANVAS, -1, int)
    out[y0:y0 + p.shape[0], x0:x0 + p.shape[1]] = p.astype(int) - 1
    return out


def upper_of(k):
    """The upper body the pack gave raw k, on the frame canvas: Codex's step-2 run frame SOURCE[k], legs cut, BOB rows
    down; and its head's top-left there."""
    meta = json.load(open(os.path.join(I.OUT, "frames.json"), encoding="utf-8"))
    src = R.SOURCE[k - 1]
    a = np.asarray(Image.open(os.path.join(I.OUT, f"codex_run_{src}.png")).convert("RGBA"))
    up, _ = R.legless(a)
    bob = R.BOB[k - 1]
    out = np.zeros_like(up)
    out[bob:] = up[:up.shape[0] - bob] if bob >= 0 else 0
    if bob < 0:
        out[:bob] = up[-bob:]
    hr, hc = meta["heads"][f"run_{src}"]["at"]
    return out, (hr + bob, hc)


def head_offset(idx, up_pack, head_pack):
    """The raw's offset (dx, dy in draft px) from where the pack put the head: the design head matched at scale 1 in a
    window of +-30 px round it."""
    hr, hc = head_pack
    tpl = I.HEAD
    t = np.repeat(np.repeat(tpl, PX, 0), PX, 1)
    T = I.dv.srgb2lab(t[..., :3].astype(float))
    M = t[..., 3] > 0
    y0, x0 = hr * PX, hc * PX
    pad = 30
    ya, xa = max(0, y0 - pad), max(0, x0 - pad)
    sub = I.lab_image(idx)[ya:y0 + t.shape[0] + pad, xa:x0 + t.shape[1] + pad]
    e = I.masked_ssd(sub, T, M)
    j = np.unravel_index(np.argmin(e), e.shape)
    return xa + j[1] - x0, ya + j[0] - y0


def legs_of(k, up, head):
    """Raw k's legs on the frame canvas: the raw voted down at 6 px a square at its head's offset, everything under its
    kilt's hem."""
    idx = load_raw(k)
    pack_head = (head[0] - I.SOLE + R.SOLE, head[1] - I.PIV + R.PIV_X)
    dx, dy = head_offset(idx, up, pack_head)
    # pack square (r, c) <- draft px (r * 6 + dy, c * 6 + dx); frame canvas = pack - (pack origin)
    oy, ox = R.SOLE - I.SOLE, R.PIV_X - I.PIV
    # block_vote's square (0, 0) starts at draft (x, y): the frame canvas's (0, 0) is pack square (oy, ox), draft
    # (ox * 6, oy * 6), moved by the raw's offset
    can = I.block_vote(idx, float(PX), ox * PX + dx, oy * PX + dy, 0, 0)
    kilt = np.isin(can, R.KILT)
    lbl, n = ndimage.label(kilt, structure=np.ones((3, 3)))
    sizes = ndimage.sum(kilt, lbl, range(1, n + 1))
    body = lbl == (int(np.argmax(sizes)) + 1)
    ys, _ = np.nonzero(body)
    top = ys.min()
    below = np.zeros(can.shape, bool)
    for c in range(can.shape[1]):
        col = np.nonzero(body[:, c])[0]
        if len(col):
            below[col.max() + 1:, c] = True
        else:
            below[top + 8:, c] = True
    legs = np.where(below & (can >= 0), can, -1)
    # keep the legs' pieces only (the raw's back fist or a stray square under the hem line goes)
    lbl, n = ndimage.label(legs >= 0, structure=np.ones((3, 3)))
    if n:
        sz = ndimage.sum(legs >= 0, lbl, range(1, n + 1))
        keep = [i + 1 for i in range(n) if sz[i] >= 25]
        legs[~np.isin(lbl, keep)] = -1
    return legs, (dx, dy)


def swap(can, legs):
    """The two legs' skins swapped in place: the lighter leg's skin pieces darkened (TO_FAR), the darker's lightened
    (TO_NEAR) - shapes untouched."""
    skin = (legs >= 0) & np.isin(can, I.LEG_SKIN)
    lbl, n = ndimage.label(skin, structure=np.ones((3, 3)))
    pieces = []
    for j in range(1, n + 1):
        m = lbl == j
        if m.sum() < 6:
            continue
        lum = I.PAL[can[m]].astype(int).sum(1).mean()
        pieces.append((lum, m))
    if len(pieces) < 2:
        return can
    pieces.sort(key=lambda t: t[0])
    lums = [p[0] for p in pieces]
    split = (max(lums) + min(lums)) / 2
    out = can.copy()
    for lum, m in pieces:
        cmap = I.TO_FAR if lum >= split else I.TO_NEAR
        ys, xs = np.nonzero(m)
        for y, x in zip(ys, xs):
            out[y, x] = cmap.get(int(can[y, x]), int(can[y, x]))
    return out


def stray_lines(can):
    """Outline squares with no coloured square next to them (8 ways), peeled until none is left: Codex's raws carry a
    thin dark arc or two of their own (run_2 / run_6: the back fist's old outline hanging under it)."""
    out = can.copy()
    for _ in range(20):
        drawn = out >= 0
        dark = drawn & np.isin(out, [I.OUTLINE, 1])
        lit = drawn & ~dark
        lone = dark & ~ndimage.binary_dilation(lit, structure=np.ones((3, 3)))
        if not lone.any():
            break
        out[lone] = -1
    return out


def run(a):
    os.makedirs(I.OUT, exist_ok=True)
    meta_path = os.path.join(I.OUT, "frames.json")
    meta = json.load(open(meta_path, encoding="utf-8"))
    redo = []
    row = []
    for n_out, (k, swapped) in enumerate(ORDER, 1):
        up, head = upper_of(k)
        legs, off = legs_of(k, up, head)
        upi = I.to_idx(up)
        can = np.where(upi >= 0, upi, legs)              # the upper body over the legs
        if swapped:
            can = swap(can, np.where(upi >= 0, -1, legs))
        ys = np.nonzero((can >= 0).any(1))[0]
        dr = I.SOLE - ys.max()
        can = I.shift(can, dr, 0)
        head = (head[0] + dr, head[1])
        can = stray_lines(can)
        can = I.final_clean(can)
        can = I.close_outline(can)
        can = I.final_clean(can)
        rgba = I.to_rgba(can)
        Image.fromarray(rgba).save(os.path.join(I.OUT, f"run_{n_out}.png"))
        redo.append({"raw": k, "source": R.SOURCE[k - 1], "bob": R.BOB[k - 1], "swapped": swapped,
                     "offset": [int(off[0]), int(off[1])], "head_at": [int(head[0]), int(head[1])]})
        print(f"run_{n_out}: raw {k}{' swapped' if swapped else ''}, upper body codex_run_{R.SOURCE[k - 1]} "
              f"bob {R.BOB[k - 1]}, raw offset {off}, grounded {dr:+d}")
        row.append(rgba)
    meta["run_redo"] = redo
    with open(meta_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        I.review_strip(os.path.join(a.review, "run.png"), row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", metavar="RAW_DIR")
    ap.add_argument("--review")
    a = ap.parse_args()
    if a.prepare:
        prepare(a.prepare)
        return
    run(a)


if __name__ == "__main__":
    main()
