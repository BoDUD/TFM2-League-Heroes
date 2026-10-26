#!/usr/bin/env python3
"""Norra's delivered effects gathered for import_norra_fx.py: the pictures Wild Rift's kit plays, from Codex's two
deliveries, checked and copied to one folder.

    python tools/art/process_norra_fx.py     # writes assets/source/norra/fx_1x/norra_fx_<name>.png + manifest.json

Both deliveries (Codex 2026-10-26/new-chat-5) hold each effect as a one-row strip at game size (pixel_1x/), read by
Codex from its drafts (raw/) frame by frame: alpha 0 / 255, symmetric the way manifest.json says (a projectile top to
bottom, the rest left to right):
  assets/source/norra/codex_fx/norra_fx    the first pack (PROMPTS_FX.md, drawn for TFT's kit): the attack's bolt and
                                           hit, the memory ball and its blast and hit - Memory Surge plays them;
                                           the anvil, book, potion, shield, paint and the Book of Thresholds went with
                                           TFT's kit (the user, 2026-10-26: 「你要参照手游的技能啊」) and are left there.
  assets/source/norra/codex_fx2/norra_fx2  the second (PROMPTS_FX2.md, Wild Rift's kit): the trinkets and their burst,
                                           Journey to Nowhere's portal, Threads of Homecoming's portals and threads
                                           with the Threads' hit and mark, Portalpalooza!'s rift, yarn balls, their hit
                                           and slow, and the three skill icons. Its r_hit (a yarn ball's) replaces the
                                           first pack's.
Every frame is checked symmetric and drawn; nothing came out wrong this time (the first pack's r_book, anvil and shield
fixes went with TFT's kit).
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_norra_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "norra")
PACKS = [("codex_fx/norra_fx", ("a_bolt", "a_hit", "q_ball", "q_blast", "q_hit")),
         ("codex_fx2/norra_fx2", ("p_trinkets", "p_burst", "w_in", "w_lock", "w_out", "e_threads", "t_hit", "t_mark",
                                  "r_rift", "r_yarn", "r_hit", "r_slow"))]
OUT = os.path.join(SRC, "fx_1x")


def strip(src, it):
    a = np.asarray(Image.open(lp(os.path.join(src, it["pixel_1x"]))).convert("RGBA")).copy()
    w, h = it["cell_1x"]
    if a.shape[1] != w * it["frames"] or a.shape[0] != h:
        sys.exit(f"{it['id']}: sheet {a.shape[1]}x{a.shape[0]} is not {it['frames']} cells of {w}x{h}")
    return [a[:h, k * w:(k + 1) * w].copy() for k in range(it["frames"])]


def symmetric(c, sym):
    lr = (c == c[:, ::-1]).all()
    tb = (c == c[::-1]).all()
    return {"left-right": lr, "top-bottom": tb, "both": lr and tb}[sym]


def main():
    os.makedirs(lp(OUT), exist_ok=True)
    report = {}
    for pack, names in PACKS:
        src = os.path.join(SRC, pack)
        man = {it["id"]: it for it in json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8"))["items"]}
        for name in names:
            it = man[name]
            frames = strip(src, it)
            for k, c in enumerate(frames):
                if not symmetric(c, it["symmetry"]):
                    sys.exit(f"{name} frame {k + 1} is not {it['symmetry']} symmetric")
                if not c[..., 3].any():
                    sys.exit(f"{name} frame {k + 1} is empty")
            Image.fromarray(np.concatenate(frames, axis=1)).save(lp(os.path.join(OUT, f"norra_fx_{name}.png")))
            report[name] = dict(it, pixel_1x=f"norra_fx_{name}.png", pack=pack)
            print(f"{name:12s} {len(frames)} x {it['cell_1x'][0]}x{it['cell_1x'][1]}  ({pack})")
    left = sorted(f for f in os.listdir(lp(OUT)) if f.startswith("norra_fx_") and f[9:-4] not in report)
    for f in left:                                      # a picture the kit no longer plays
        os.remove(lp(os.path.join(OUT, f)))
        print("removed", f)
    with open(lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8") as f:
        json.dump({"items": list(report.values())}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
