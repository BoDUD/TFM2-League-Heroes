#!/usr/bin/env python3
"""The Codex pack for league_lucian's walk while The Culling fires (`r_run`): 8 frames, his run's legs with both pistols
held forward as in his ult (assets/source/lucian/RUNSHOOT_PROMPT_PPU.md).

    python tools/art/pack_lucian_runshoot.py --out C:/t/lu_runshoot [--split 4] [--ult 3]

The user (2026-10-27): 「卢锡安的移动大招 ... 是不是少了点动作？」「加一套边走边开枪的动作」; a pose made by pasting the ult's
upper body (hd_ult frame ULT) onto each hd_run frame below SPLIT rows over the pivot was rejected (「腿都变形了」: the ult's
torso ends at the waist, so the run's hips and coat skirt went and the legs hung under a small body), then
「动作交给Codex重画」. That paste is now only the pose guide: each template cell holds it faded, at his height on the
design's grid (tools/art/pack_lucian_actions.py's cells: 7 px a design square, 93 / 46 squares an old pixel, the pivot
on the standing point), and Codex redraws the whole design in it. refs/run_<n>.png and refs/ult.png show the two poses
it was made from in colour.
Then <out>.zip. Read back like his other actions (tools/art/casts_lucian_hd.py) into assets/source/ppu/orig at 2.02,
then ppu_restyle (1.5), ppu_hd, hero_reels, and an add-on swapping `run` for `r_run` while league_lucian_r_ch is on.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import pack_lucian_actions as PA  # noqa: E402
import pack_riven_actions as PR  # noqa: E402

SHEET = os.path.join(REPO, "league", "champions", "league_lucian#sheet.png")
FANIM = os.path.join(REPO, "league", "champions", "league_lucian#anim.fanim")
HD_PPU = 1.5                     # his sheet's hd_ frames (hd.rs)
TAG = "r_run"
ACTION = ("walking while firing The Culling: his RUN's legs and stride (the legs swapping every half cycle, the body "
          "bobbing), the coat tails flowing back, but the upper body squared to the front with BOTH pistols held "
          "straight forward at shoulder height, as in his ult - he keeps shooting forward while he walks")
WEAPONS = ("Two pistols as in the design, one in EACH hand in every frame, BOTH arms extended forward and BOTH pistols "
           "pointed straight ahead (to the right), one a little above the other, as the pale figure - never one raised "
           "by the shoulder, never both in one hand, never dropped; the pistols' shape, size and colours as in the "
           "design.")


def anims():
    with open(FANIM, "rb") as f:
        return json.loads(f.read().decode("utf-8").lstrip("\ufeff"))["anims"]


def crops(a, sh, tag):
    out = []
    for f in a[tag]["frames"]:
        d = f["data"]
        x, y, w, h = (int(d[k]) for k in "xywh")
        out.append((sh[y:y + h, x:x + w].copy(), round(f["duration"] * 1000)))
    return out


def on_canvas(fr, W, H):
    c = np.zeros((H, W, 4), np.uint8)
    h, w = fr.shape[:2]
    c[(H - h) // 2:(H - h) // 2 + h, (W - w) // 2:(W - w) // 2 + w] = fr
    return c


def band(c, y0, y1, axis):
    ys, xs = np.nonzero(c[y0:y1, :, 3] > 0)
    if not len(xs):
        return c.shape[1] / 2 if axis == "x" else (y0 + y1) / 2
    return xs.mean() if axis == "x" else ys.mean() + y0


def guides(split, ult_k):
    """The pasted poses (hd frames, PPU 1.5, centred on the pivot) and the run frames they come from."""
    a = anims()
    sh = np.asarray(Image.open(PR.lp(SHEET)).convert("RGBA"))
    run = crops(a, sh, "hd_run")
    ult = crops(a, sh, "hd_ult")[ult_k][0]
    W = max(max(f.shape[1] for f, _ in run), ult.shape[1]) + 40
    H = max(max(f.shape[0] for f, _ in run), ult.shape[0]) + 40
    cut = H // 2 - split
    U = on_canvas(ult, W, H)
    ux, r0 = band(U, cut - 10, cut, "x"), band(on_canvas(run[0][0], W, H), cut - 30, cut, "y")
    out = []
    for fr, ms in run:
        R = on_canvas(fr, W, H)
        dx = round(band(R, cut - 10, cut, "x") - ux)
        dy = round(band(R, cut - 30, cut, "y") - r0)
        up = np.zeros_like(U)
        up[:cut] = U[:cut]
        up = np.roll(np.roll(up, dx, axis=1), dy, axis=0)
        low = R.copy()
        low[:cut + dy] = 0
        m = up[..., 3] > 0
        low[m] = up[m]
        out.append((low, ms))
    return out, run, ult


def as_old(frame):
    """An hd frame (PPU 1.5) at the old 1x scale pack_lucian_actions' cells expect (nearest, about its pivot)."""
    im = Image.fromarray(frame)
    w, h = round(im.width / HD_PPU), round(im.height / HD_PPU)
    w += (w + im.width) % 2                      # keep the centre on a pixel boundary like the frame's own
    h += (h + im.height) % 2
    return np.asarray(im.resize((w, h), Image.BOX))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--split", type=int, default=4, help="hd rows over the pivot where the ult's upper body starts")
    ap.add_argument("--ult", type=int, default=3, help="the hd_ult frame whose upper body is the guide")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    for d in (tpl, refs):
        os.makedirs(d, exist_ok=True)
    pasted, run, ult = guides(a.split, a.ult)
    frames = [(as_old(f), ms) for f, ms in pasted]
    des = Image.open(PR.lp(os.path.join(PA.SRC, "hd", "design.png"))).convert("RGBA")
    bg = Image.new("RGBA", (des.width + 4, des.height + 4), PA.GREY + (255,))
    bg.alpha_composite(des, (2, 2))
    bg.convert("RGB").resize((bg.width * 6, bg.height * 6), Image.NEAREST).save(os.path.join(refs, "design.png"))
    shutil.copyfile(PR.lp(os.path.join(PA.SRC, "hd", "design.png")), os.path.join(refs, "design_1x.png"))
    arr = np.asarray(des)
    PR.palette(np.unique(arr[arr[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    for k, (f, _) in enumerate(run):                                # the two poses it comes from, in colour
        Image.fromarray(f).resize((f.shape[1] * 6, f.shape[0] * 6), Image.NEAREST).save(os.path.join(refs, f"run_{k + 1}.png"))
    Image.fromarray(ult).resize((ult.shape[1] * 6, ult.shape[0] * 6), Image.NEAREST).save(os.path.join(refs, "ult.png"))
    sheets = []
    for n, (nums, part) in enumerate(PA.groups(frames, set())):
        name = f"{TAG}_{n + 1}"
        PA.template(os.path.join(tpl, name + ".png"), part, nums)
        PA.old_ref(part, nums, os.path.join(refs, f"old_{name}.png"))
        sheets.append(dict(tag=TAG, name=name, frames=nums, cells=len(part), action=ACTION, ms=[ms for _, ms in part],
                           weapons=WEAPONS))
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": PA.SQ, "sheet": [PA.SHEET_W, PA.H], "ground": PA.GROUND, "sheets": sheets}, f, indent=1,
                  ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(PA.SRC, "RUNSHOOT_PROMPT_PPU.md")), os.path.join(a.out, "RUNSHOOT_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets,", sum(len(s["frames"]) for s in sheets), "frames; written", zp)


if __name__ == "__main__":
    main()
