#!/usr/bin/env python3
"""Wukong's W clone pictures in the new design (tools/art/pack_wukong_clone.py; Codex's delivery in
assets/source/wukong/codex_clone/, 8 px a square, each frame mirrored left to right by Codex) brought to 1x and written
over the first FX pack's 1x sheets (assets/source/wukong/codex_fx/pixel_1x/wukong_fx_w_clone*.png, the same cells), so
tools/art/import_wukong_fx.py builds them into league_wukong_big.

    python tools/art/import_wukong_clone.py && python tools/art/import_wukong_fx.py

Only the exact key (#00FF00) is cleared: the eyes are a green (19, 197, 11) close to it. Colours snapped to the action
frames' palette (tools/art/palette_act_1018.py) plus the whirl's gold and the eye green; symmetry checked.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "wukong")
Z = 8


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def main():
    act = os.path.join(SRC, "hd", "act")
    px = np.concatenate([np.asarray(Image.open(lp(os.path.join(act, n))).convert("RGBA")).reshape(-1, 4)
                         for n in os.listdir(lp(act))])
    pal = np.unique(px[px[:, 3] > 0][:, :3], axis=0).astype(int)
    for name in ("w_clone", "w_clone_atk", "w_clone_spin"):
        a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_clone", f"wukong-{name}.png"))).convert("RGB")).astype(int)
        s = a[Z // 2::Z, Z // 2::Z]
        key = (s[..., 1] > 240) & (s[..., 0] < 16) & (s[..., 2] < 16)
        op = ~key
        # the whirl's golds / whites and the eye green are kept as drawn; the body snapped to the action palette
        c = s[op]
        keep = (c[:, 1] > c[:, 0] + 100) | ((c[:, 0] > 230) & (c[:, 1] > 200))
        idx = np.argmin(((c[:, None, :] - pal[None]) ** 2).sum(-1), 1)
        c2 = np.where(keep[:, None], c, pal[idx])
        out = np.zeros(s.shape[:2] + (4,), np.uint8)
        out[op, :3] = c2
        out[op, 3] = 255
        dst = os.path.join(SRC, "codex_fx", "pixel_1x", f"wukong_fx_{name}.png")
        old = Image.open(lp(dst))
        if old.size != (out.shape[1], out.shape[0]):
            raise SystemExit(f"{name}: {out.shape[1]}x{out.shape[0]} against the old {old.size}")
        n = 4
        w = out.shape[1] // n
        for k in range(n):
            cell = out[:, k * w:(k + 1) * w]
            half = w // 2
            cell[:, w - half:] = cell[:, :half][:, ::-1]                   # exact symmetry (the red side)
        Image.fromarray(out).save(lp(dst))
        print(name, out.shape[1], "x", out.shape[0])


if __name__ == "__main__":
    main()
