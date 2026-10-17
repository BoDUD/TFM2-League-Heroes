#!/usr/bin/env python3
"""Renata's folded machine from Codex (tools/art/pack_renata_back.py's pack; the user, 2026-10-17: 「照原版大小，Codex 画
折叠的机甲，你按原版每帧的位置摆进去」「不对缩小一点」) brought to her fine squares.

    python tools/art/import_renata_back.py [--src assets/source/renata/codex_back] [--review DIR]

Codex delivers renata_machine_folded.png (the machine alone on green, on the pack's canvas: 63 x 95 squares of 8 px
round her idle) and renata_idle_machine.png (her idle with it). The machine is read back square by square on the
picture's own grid (8 px when the picture is the pack's size, else regrid's measure), every square snapped to the
nearest colour of her design and the ult machine (one palette for the whole hero), trimmed. Written:
assets/source/renata/hd/machine_folded.png and machine_folded.json - where its top-left sits from the top-left of her
trimmed hd idle frame (the pack's image 1), for tools/art/rig_renata.py, which lays it behind her in every frame but
the unfolded ult ones, moved as League moves it (assets/source/renata/machine_track.json). Her own squares in the
idle-with-machine picture are compared with image 1 (reported, never taken: she stays the approved design).
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
sys.path.insert(0, HERE)
import regrid as RG  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "renata", "codex_back")
HD = os.path.join(ROOT, "assets", "source", "renata", "hd")
CANVAS = (63, 95)                # the pack's canvas in squares (pack_renata_back.py: her idle + TOP / SIDE / BOTTOM)
HER_AT = (14, 34)                # her trimmed idle's top-left on it
SQ = 8                           # the pack's screen px a square


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def keyed(path):
    a = np.asarray(Image.open(lp(path)).convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    key = (g > 140) & (g > r + 60) & (g > b + 60)
    out = np.dstack([a, np.where(key, 0, 255)]).astype(np.uint8)
    out[key] = 0
    return out


def squares(a):
    """The picture read back one colour a square: the pack's 8-px grid when it has the pack's size, else regrid's."""
    H, W = a.shape[:2]
    if (W, H) == (CANVAS[0] * SQ, CANVAS[1] * SQ):
        d = a[SQ // 2::SQ, SQ // 2::SQ].copy()
    else:
        d, _, _ = RG.regrid(a, W / CANVAS[0])
        print(f"  {W}x{H} is not the pack's {CANVAS[0] * SQ}x{CANVAS[1] * SQ}: regrid -> {d.shape[1]}x{d.shape[0]}")
    d[..., 3] = np.where(d[..., 3] >= 128, 255, 0)
    d[d[..., 3] == 0] = 0
    return d


def palette():
    import rig_renata as R
    cols = [R.DESIGN[R.DESIGN[..., 3] > 0][:, :3], R.MACHINE[R.MACHINE[..., 3] > 0][:, :3]]
    return np.unique(np.concatenate(cols), axis=0).astype(int)


def snap(d, pal):
    op = d[..., 3] > 0
    near = np.argmin(((d[..., :3].astype(int)[..., None, :] - pal[None, None]) ** 2).sum(-1), -1)
    out = d.copy()
    out[op, :3] = pal[near[op]]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--review", help="the machine and her idle with it at 8x here")
    a = ap.parse_args()
    pal = palette()
    m = snap(squares(keyed(os.path.join(a.src, "renata_machine_folded.png"))), pal)
    ys, xs = np.nonzero(m[..., 3] > 0)
    box = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    machine = m[box[1]:box[3] + 1, box[0]:box[2] + 1]
    at = (box[0] - HER_AT[0], box[1] - HER_AT[1])
    print(f"machine {machine.shape[1]}x{machine.shape[0]} squares, {len({tuple(c) for c in machine[machine[..., 3] > 0][:, :3]})} "
          f"colours, top-left {at} from her trimmed idle's")
    with_her = os.path.join(a.src, "renata_idle_machine.png")
    pack1 = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "rn_work", "back", "renata_back_machine_pack", "1_定稿待机.png")
    if os.path.isfile(lp(with_her)) and os.path.isfile(lp(pack1)):
        both = snap(squares(keyed(with_her)), pal)
        plain = squares(keyed(pack1))
        if both.shape == plain.shape:
            hers = plain[..., 3] > 0
            moved = int((hers & np.any(both != plain, -1)).sum())
            print(f"  her squares changed in the idle-with-machine picture: {moved} of {int(hers.sum())} (not taken)")
    os.makedirs(lp(HD), exist_ok=True)
    Image.fromarray(machine).save(lp(os.path.join(HD, "machine_folded.png")))
    with open(lp(os.path.join(HD, "machine_folded.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"at_trim": list(at), "size": [machine.shape[1], machine.shape[0]],
                   "note": "top-left from the top-left of her trimmed hd idle frame (pack_renata_back.py image 1)"}, f,
                  indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        Image.fromarray(np.repeat(np.repeat(machine, 8, 0), 8, 1)).save(os.path.join(a.review, "machine_folded_8x.png"))
    print("written", os.path.join(HD, "machine_folded.png"))


if __name__ == "__main__":
    main()
