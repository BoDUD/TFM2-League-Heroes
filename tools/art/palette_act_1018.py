#!/usr/bin/env python3
"""One palette for all of a hero's Codex action frames (assets/source/<hero>/hd/act/*.png).

    python tools/art/palette_act_1018.py wukong [--colours 48]

The user, 2026-10-18: 「猴子gif图里面怎么一直变色？」 - Wukong's skin-swap frames came back unpalettised (1000-2000 colours a
frame, 64 000 over the 61 frames: Codex's export kept the generator's shading noise; Akshan's were snapped to his design's
40 colours), and ppu_restyle's pixelate snaps each frame to its OWN commonest colours, so the shading shifted from frame
to frame. Here every opaque square of every frame goes into one median-cut palette (the eye green kept exact) and each
frame is snapped to it, in place.
"""
import argparse
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KEEP = {"wukong": [(70, 215, 90)]}


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hero")
    ap.add_argument("--colours", type=int, default=48)
    a = ap.parse_args()
    act = os.path.join(ROOT, "assets", "source", a.hero, "hd", "act")
    names = sorted(os.listdir(lp(act)))
    frames = [np.asarray(Image.open(lp(os.path.join(act, n))).convert("RGBA")).copy() for n in names]
    keep = np.array(KEEP.get(a.hero, []), int).reshape(-1, 3)
    px = np.concatenate([f[f[..., 3] > 0][:, :3] for f in frames])
    if len(keep):
        px = px[np.abs(px[:, None, :].astype(int) - keep[None]).sum(-1).min(1) > 0]
    strip = Image.fromarray(px.reshape(1, -1, 3).astype(np.uint8))
    q = strip.quantize(colors=a.colours, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = np.array(q.getpalette()[:3 * a.colours], int).reshape(-1, 3)
    pal = np.unique(np.concatenate([pal, keep]), axis=0)
    before = len(np.unique(np.concatenate([f[f[..., 3] > 0][:, :3] for f in frames]), axis=0))
    for n, f in zip(names, frames):
        op = f[..., 3] > 0
        c = f[op][:, :3].astype(int)
        idx = np.empty(len(c), int)
        for s in range(0, len(c), 4096):
            idx[s:s + 4096] = np.argmin(((c[s:s + 4096, None, :] - pal[None]) ** 2).sum(-1), 1)
        f[op, :3] = pal[idx]
        Image.fromarray(f).save(lp(os.path.join(act, n)))
    print(f"{a.hero}: {len(frames)} frames, {before} colours -> {len(pal)}")


if __name__ == "__main__":
    main()
