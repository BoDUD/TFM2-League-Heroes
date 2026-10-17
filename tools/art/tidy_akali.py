#!/usr/bin/env python3
"""Akali's redo, step 2: Codex's strips of the design A40 into the native strips.

    python tools/art/tidy_akali.py <Codex's delivery folder (akali_strips_redo)> [--check]

The pack (assets/source/akali/MODEL_STRIPS_REDO.md) gave Codex the design A40, its head to paste, the palette, the idle
already built (the design in all six frames) and League's poses at game size; Codex drew the ten actions from them
(delivered 2026-10-01: akali_<tag>.png at 8x, native/ at 1x, akali_cells.json = the pack's). Checked here square by
square: flat 8x8 blocks, binary alpha, only the design's 18 colours, nothing under the feet line (pivot + 11), the idle
byte for byte the pack's. One square is added: the chain of the empowered attack's throw (attack_p frame 4) missed the
link between her hand and the rest (a piece of 70 squares on its own), so (58, 63) takes the chain's colour as in
frame 3. Writes assets/source/native/akali_<tag>.png and akali_cells.json, and keeps Codex's notes (HANDOFF.md,
manifest.json, validation.json, generation_prompts.json) in assets/source/akali/codex_model/strips_redo/.
--check only compares with what is there. Then tools/art/import_native.py --hero akali.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402
from native_refs import Z, layout  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
NOTES = os.path.join(ROOT, "assets", "source", "akali", "codex_model", "strips_redo")
FEET = 11
# (tag, frame from 1): squares (x, y in the cell) and the colour they take
FIX = {("attack_p", 4): [((58, 63), (0x0A, 0x0A, 0x14))]}


def blocks(path):
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    H, W = a.shape[:2]
    b = a.reshape(H // Z, Z, W // Z, Z, 4)
    if H % Z or W % Z or not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    out = b[:, 0, :, 0].copy()
    if not np.isin(out[..., 3], (0, 255)).all():
        sys.exit(f"{path}: alpha other than 0 / 255")
    out[out[..., 3] == 0] = 0
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery")
    ap.add_argument("--check", action="store_true")
    o = ap.parse_args()
    cells = json.load(open(os.path.join(o.delivery, "akali_cells.json"), encoding="utf-8"))
    CW, CH = cells["cell"]
    design = np.asarray(Image.open(G.lp(os.path.join(NATIVE, "akali_native.png"))).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
    pal = {tuple(int(v) for v in p[:3]) for p in design[design[..., 3] > 0]}
    bad = 0
    for tag, rows in cells["tags"].items():
        a = blocks(os.path.join(o.delivery, f"akali_{tag}.png"))
        cols, _ = layout(len(rows))
        off = {tuple(int(v) for v in p[:3]) for p in a[a[..., 3] > 0]} - pal
        if off:
            sys.exit(f"akali_{tag}: colours outside the design: {sorted(off)}")
        for k, r in enumerate(rows):
            y0, x0 = k // cols * CH, k % cols * CW
            f = a[y0:y0 + CH, x0:x0 + CW]
            low = int(np.nonzero((f[..., 3] > 0).any(1))[0].max())
            if low > r["pivot"][1] + FEET + (2 if tag == "dead" else 0):
                sys.exit(f"akali_{tag} {k + 1}: {low - r['pivot'][1] - FEET} rows under the feet line")
            for (x, y), c in FIX.get((tag, k + 1), []):
                a[y0 + y, x0 + x] = c + (255,)
        dst = os.path.join(NATIVE, f"akali_{tag}.png")
        if o.check:
            now = blocks(dst)
            same = now.shape == a.shape and (now == a).all()
            bad += not same
            print(f"akali_{tag}.png {'as tidied' if same else 'DIFFERENT'}")
            continue
        Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1)).save(G.lp(dst))
        print(f"akali_{tag}.png  {len(rows)} frames")
    if not o.check:
        shutil.copyfile(os.path.join(o.delivery, "akali_cells.json"), G.lp(os.path.join(NATIVE, "akali_cells.json")))
        os.makedirs(G.lp(NOTES), exist_ok=True)
        for name in ("HANDOFF.md", "manifest.json", "validation.json", "generation_prompts.json"):
            shutil.copyfile(os.path.join(o.delivery, name), G.lp(os.path.join(NOTES, name)))
        print("akali_cells.json, codex_model/strips_redo/")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
