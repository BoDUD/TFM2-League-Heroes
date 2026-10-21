#!/usr/bin/env python3
"""Xerath's actions (tools/art/rig_xerath_hd.py) beside League's own frames, one GIF of every tag for the user's review
(memory one-gif-review: League left, ours right) - review_velkoz_actions' way.

    python tools/art/review_xerath_actions.py --out DIR [--z 4] [--tags attack,ult] [--cached] [--sheet]

League's frames: for every frame of ours the moment of League's clip it follows (LOL below, one per frame before the
bake splits a tag at its effect's times: a split frame shows its frame's moment), rendered by tools/lol/pose_ref.py on
Riot's model at poses.json's 3/4 view (yaw 45, mirrored; they stay in DIR, never committed). Ours: the rig's canvases
after Rig.finish with the baked effects on (or, with --sheet, the exported sheet's hd_ frames: what the game draws, after
ppu_restyle's outline), z screen px a design square, on the same ground line. Writes
<out>/xerath_<tag>_vs_lol.png and <out>/xerath_all_vs_lol.gif (every tag in turn, each played twice). The _fx copies
the bake makes (attack_fx1, skill_fx1) are left out: cut from attack and skill.
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_xerath_hd as X  # noqa: E402

BG = (96, 112, 96)
# tag -> League's moment for each of our frames before the bake's split (clips: tools/lol/anim_graph.py Xerath)
LOL = {
    "idle": [f"Xerath_Idle1@{t}" for t in range(0, 6400, 800)],
    "run": [f"Xerath_run@{t}" for t in range(0, 968, 121)],
    "attack": [f"Xerath_Attack1@{t}" for t in (0, 121, 242, 363, 484, 726)],
    "skill": ["Xerath_channel_windup@0", "Xerath_channel_windup@300", "Xerath_channel@0", "Xerath_channel@300",
              "Xerath_channel@600", "Xerath_Spell1@700", "Xerath_Spell1@1050"],
    "skill_quick": ["Xerath_channel_windup@0", "Xerath_channel@0", "Xerath_channel@400", "Xerath_Spell1@700",
                    "Xerath_Spell1@1050"],
    "skill2": ["Xerath_Spell3@0", "Xerath_Spell3@150", "Xerath_Spell3@300", "Xerath_Spell3@450", "Xerath_Spell2@129",
               "Xerath_Spell2@323"],
    "ult": [f"Spell5Start@{t}" for t in (0, 183, 367, 550, 642)],
    "ult_loop": [f"Spell5Loop@{t}" for t in (0, 388, 777, 1166, 1555, 1944)],
    "ult_shot": [f"Spell5_Fast@{t}" for t in (0, 288, 575)],
    "hit": ["Xerath_Idle1@0>Xerath_Death@300:0.3", "Xerath_Idle1@0"],
    "dead": [f"Xerath_Death@{t}" for t in (0, 300, 625, 1000, 1500, 2500, 3500, 4375)],
}


def lol_frames(lol, tag, specs, out, cached=False):
    name = f"lol_{tag}"
    path = os.path.join(out, name + ".png")
    n = len(specs)
    if not (cached and os.path.isfile(path)):
        cmd = [sys.executable, os.path.join(R.ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Xerath",
               "--hq", "--mirror", "--yaw", "45", "--size", "700", "--width", "1.6", "--no-labels",
               "--bg", ",".join(map(str, BG)), "--name", name, "--out", out]
        for s in specs:
            cmd += ["--frame", s]
        subprocess.run(cmd, check=True, capture_output=True)
    strip = Image.open(path).convert("RGB")
    w = strip.width // n
    cells = [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(n)]
    a = np.stack([np.asarray(c).astype(int) for c in cells])
    fg = (np.abs(a - np.array(BG)).sum(-1) > 24).any(0)
    ys, xs = np.nonzero(fg)
    m = 12
    box = (max(0, xs.min() - m), max(0, ys.min() - m), min(w, xs.max() + m), min(strip.height, ys.max() + m))
    return [c.crop(box) for c in cells]


def sheet_frames(rig, tags):
    """{tag: [(canvas, ms)]} from the exported sheet's hd_ frames, each centred on the rig's frame centre (CX, the pivot
    FEET x PPU above the ground row) - review_velkoz_actions'."""
    import json
    stem = os.path.join(R.ROOT, "league", "champions", "league_xerath")
    anims = json.load(open(R.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = np.asarray(Image.open(R.lp(stem + "#sheet.png")).convert("RGBA"))
    cx, cy = rig.CX, rig.GY - R.FEET * X.PPU
    out = {}
    for tag in tags:
        fr = []
        for f in anims["hd_" + tag]["frames"]:
            d = f["data"]
            im = sheet[int(d["y"]):int(d["y"] + d["h"]), int(d["x"]):int(d["x"] + d["w"])]
            can = rig.canvas()
            y0, x0 = int(round(cy - im.shape[0] / 2)), int(round(cx - im.shape[1] / 2))
            ys, xs = max(0, y0), max(0, x0)
            sub = im[ys - y0:, xs - x0:][:can.shape[0] - ys, :can.shape[1] - xs]
            can[ys:ys + sub.shape[0], xs:xs + sub.shape[1]] = sub
            fr.append((can, f.get("duration", 0.1) * 1000))
        out[tag] = fr
    return out


def flat(rig, c):
    if not isinstance(c, dict):
        return c if getattr(rig, "as_drawn", False) else rig.finish(c)
    full = rig.finish(c["body"])
    for fx_, top in ((c.get("under"), False), (c.get("over"), True)):
        if fx_ is not None:
            m = fx_[..., 3] > 0
            if not top:
                m &= full[..., 3] == 0
            full[m] = fx_[m]
    return full


def base_index(tag, fr):
    """For every (split) frame the index of its frame before the split, by start time."""
    import json
    native = os.path.join(R.ROOT, "assets", "source", "native")
    with open(R.lp(os.path.join(native, "xerath_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)["tags"]
    with open(R.lp(os.path.join(native, "xerath_bake.json")), encoding="utf-8") as f:
        laid_in = {e["into"] for e in json.load(f)["items"] if "from" not in e}
    base = [r["ms"] for r in cells[tag]] if tag in laid_in else [ms for _, ms in fr]
    starts = np.cumsum([0] + base[:-1])
    out, t = [], 0
    for _, ms in fr:
        out.append(int(np.searchsorted(starts, t + 0.5) - 1))
        t += ms
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--z", type=int, default=4)
    ap.add_argument("--tags")
    ap.add_argument("--cached", action="store_true")
    ap.add_argument("--sheet", action="store_true", help="the exported sheet's hd_ frames instead of the rig's")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rig = X.make_rig(X.Design())
    acts = X.frames(rig)
    tags = a.tags.split(",") if a.tags else [t for t in acts if not t.endswith("_fx1")]
    if a.sheet:
        acts = sheet_frames(rig, tags)
        rig.as_drawn = True                       # the sheet's frames are final: no tidy / crack fill again
    every = []
    allc = np.concatenate([np.stack([flat(rig, c) for c, _ in acts[t]]) for t in tags])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, max(ys.max() + 3, rig.GY + 2), xs.min() - 2, xs.max() + 3
    for tag in tags:
        fr = acts[tag]
        specs = LOL[tag]
        idx = base_index(tag, fr)
        if max(idx) + 1 != len(specs):
            sys.exit(f"{tag}: {len(specs)} League moments for {max(idx) + 1} frames")
        lol = lol_frames(a.lol, tag, specs, a.out, a.cached)
        cells = []
        for k, (can, ms) in enumerate(fr):
            ref = lol[idx[k]]
            f = flat(rig, can)[y0:y1, x0:x1]
            bg = Image.new("RGBA", (f.shape[1], f.shape[0]), BG + (255,))
            d = ImageDraw.Draw(bg)
            d.line([(0, rig.GY - y0), (bg.width, rig.GY - y0)], fill=(70, 84, 70, 255))
            bg.alpha_composite(Image.fromarray(f))
            ours = bg.convert("RGB").resize((f.shape[1] * a.z, f.shape[0] * a.z), Image.NEAREST)
            kk = ours.height / ref.height
            ref = ref.resize((round(ref.width * kk), ours.height), Image.LANCZOS)
            cell = Image.new("RGB", (ref.width + ours.width + 8, ours.height + 18), (40, 40, 40))
            cell.paste(ref, (0, 18))
            cell.paste(ours, (ref.width + 8, 18))
            dd = ImageDraw.Draw(cell)
            dd.text((4, 3), f"League {specs[idx[k]]}", fill=(230, 230, 230))
            dd.text((ref.width + 12, 3), f"ours: {tag} {k + 1}/{len(fr)}  {int(round(ms))} ms", fill=(230, 230, 230))
            cells.append((cell, ms))
        w = max(c.width for c, _ in cells)
        h = cells[0][0].height
        sheet = Image.new("RGB", (w, h * len(cells)), (40, 40, 40))
        for i, (c, _) in enumerate(cells):
            sheet.paste(c, (0, i * h))
        sheet.save(os.path.join(a.out, f"xerath_{tag}_vs_lol.png"))
        every += cells * 2
        print(tag, len(cells))
    W = max(c.width for c, _ in every)
    H = max(c.height for c, _ in every)
    frames = []
    for c, ms in every:
        full = Image.new("RGB", (W, H), (40, 40, 40))
        full.paste(c, (0, 0))
        frames.append((full, ms))
    pal = Image.new("RGB", (W, H * 4))
    for i, (c, _) in enumerate(frames[::max(1, len(frames) // 4)][:4]):
        pal.paste(c, (0, i * H))
    pal = pal.quantize(255, dither=Image.Dither.NONE)
    q = [c.quantize(palette=pal, dither=Image.Dither.NONE) for c, _ in frames]
    path = os.path.join(a.out, "xerath_all_vs_lol.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[max(20, int(round(ms))) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
