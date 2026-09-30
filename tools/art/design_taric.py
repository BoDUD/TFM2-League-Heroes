#!/usr/bin/env python3
"""Taric's design (assets/source/native/taric_native.png) from Codex's game-size drawing.

    python tools/art/design_taric.py [--check]

Step 1 of the user's order (sprite -> strips -> effects): Codex drew a picture from League's renders
(assets/source/taric/codex_model/picture_generation_prompts.txt; the user picked picture A, the mace-axe hanging at
his side), then the sprite at game size, 40 rows from the top of the hair to the soles, A (head 13 rows) and B
(head 15 rows) - assets/source/taric/MODEL_PROMPTS.md, codex_model/design_HANDOFF.md. The user took neither: "脸和头发
不像"; Codex redrew only the heads inside a box (HEAD_REDO.md, codex_model/head_redo_HANDOFF.md, not a square
outside it changed) and the user picked B2 (codex_model/taric_design_B2_1x.png, 128x128, 26 colours, soles on row
99). Here:
  1. the outline closed (the skill's strips.complete_outline: a clear square next to a light edge square takes the
     commonest dark edge colour, nothing drawn repainted, nothing added under the soles);
  2. shown at 8x on the 1024 canvas, like the other *_native.png.
--check compares the result with the committed taric_native.png instead of writing it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402

DRAFT = os.path.join(ROOT, "assets", "source", "taric", "codex_model", "taric_design_B2_1x.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "taric_native.png")
FEET = 99


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def build():
    a = np.asarray(Image.open(lp(DRAFT)).convert("RGBA")).copy()
    assert a.shape[:2] == (128, 128), a.shape
    ys, _ = np.nonzero(a[..., 3])
    assert ys.max() == FEET, ys.max()
    out, added, darkened = strips.complete_outline(a, feet=FEET)
    return out, added, darkened


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    out, added, darkened = build()
    big = Image.fromarray(out).resize((1024, 1024), Image.NEAREST)
    if args.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        same = np.array_equal(old, np.asarray(big))
        print("identical" if same else "DIFFERENT")
        sys.exit(0 if same else 1)
    big.save(lp(OUT))
    ys, xs = np.nonzero(out[..., 3])
    cols = len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))
    print(f"{OUT}: outline +{added} squares, {darkened} darkened; rows {ys.min()}-{ys.max()} ({ys.max() - ys.min() + 1}), "
          f"cols {xs.min()}-{xs.max()}, {cols} colours")


if __name__ == "__main__":
    main()
