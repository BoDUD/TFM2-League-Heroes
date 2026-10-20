#!/usr/bin/env python3
"""Vel'Koz's actions (tools/art/rig_velkoz.py) beside League's own frames, one GIF of every tag for the user's review
(memory one-gif-review: League left, ours right).

    python tools/art/review_velkoz_actions.py --out DIR [--z 4] [--tags attack,skill] [--cached] [--sheet]

League's frames: for every frame of ours the moment of League's clip it follows (LOL below: "<clip>@<ms>"), rendered by
tools/lol/pose_ref.py on Riot's model at the idle's 3/4 view (yaw 35; they stay in DIR, never committed). Ours:
rig_velkoz's canvases after Rig.finish (or, with --sheet, the exported sheet's hd_ frames: what the game draws), z
screen px a design square, on the same ground line. Writes <out>/velkoz_<tag>_vs_lol.png (the frames one under the
other) and <out>/velkoz_all_vs_lol.gif (every tag in turn, each played twice).
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_velkoz as V  # noqa: E402

BG = (96, 112, 96)
# tag -> League's moment for each of our frames (clips named in Velkoz.bin's animation graph, tools/lol/anim_graph.py)
LOL = {
    "idle": [f"velkoz_idle1v2@{t}" for t in range(0, 8000, 1000)],
    "run": [f"velkoz_run@{t}" for t in range(0, 1000, 125)],
    "attack": [f"velkoz_attack1@{t}" for t in (0, 200, 300, 400, 600, 900)],
    "skill": [f"velkoz_spell1@{t}" for t in (0, 167, 333, 500, 700, 1000)],
    "skill2": [f"velkoz_spell3@{t}" for t in (0, 250, 500, 625, 875)],
    "ult": [f"velkoz_spell4_in@{t}" for t in (0, 100, 200)],
    "ult_loop": [f"velkoz_spell4@{t}" for t in (500, 900, 1300, 1700)],
    "hit": ["velkoz_idle1v2@0", "velkoz_idle1v2@0"],
    "dead": [f"velkoz_death@{t}" for t in (0, 400, 800, 1200, 1800, 2400)],
}


def lol_frames(lol, tag, specs, out, cached=False):
    name = f"lol_{tag}"
    path = os.path.join(out, name + ".png")
    n = len(specs)
    if not (cached and os.path.isfile(path)):
        cmd = [sys.executable, os.path.join(R.ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Velkoz",
               "--hq", "--mirror", "--yaw", "35", "--size", "700", "--width", "1.6", "--no-labels",
               "--bg", ",".join(map(str, BG)), "--name", name, "--out", out]
        for s in specs:
            cmd += ["--frame", s]
        subprocess.run(cmd, check=True, capture_output=True)
    strip = Image.open(path).convert("RGB")
    w = strip.width // n
    cells = [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(n)]
    # he floats high in League's cell and small: every frame cropped to the tag's common box (the motion kept)
    a = np.stack([np.asarray(c).astype(int) for c in cells])
    fg = (np.abs(a - np.array(BG)).sum(-1) > 24).any(0)
    ys, xs = np.nonzero(fg)
    m = 12
    box = (max(0, xs.min() - m), max(0, ys.min() - m), min(w, xs.max() + m), min(strip.height, ys.max() + m))
    return [c.crop(box) for c in cells]


def sheet_frames(rig, tags):
    """{tag: [(canvas, ms)]} from the exported sheet's hd_ frames (what the game draws: after the restyle's outline), each
    centred on the rig's frame centre (CX, the pivot FEET x PPU above the ground row) - review_zyra_actions'."""
    stem = os.path.join(R.ROOT, "league", "champions", "league_velkoz")
    anims = json.load(open(R.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = np.asarray(Image.open(R.lp(stem + "#sheet.png")).convert("RGBA"))
    cx, cy = rig.CX, rig.GY - R.FEET * V.PPU
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
            fr.append((can, round(f.get("duration", 0.1) * 1000)))
        out[tag] = fr
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
    F = V.form()
    rig = F.rig
    acts = V.frames(F)
    if a.sheet:
        acts = sheet_frames(rig, list(acts))
    tags = a.tags.split(",") if a.tags else list(acts)
    every = []
    allc = np.concatenate([np.stack([rig.finish(c) for c, _ in fr]) for fr in acts.values()])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, max(ys.max() + 3, rig.GY + 2), xs.min() - 2, xs.max() + 3
    for tag in tags:
        fr = acts[tag]
        specs = LOL[tag]
        if len(specs) != len(fr):
            sys.exit(f"{tag}: {len(specs)} League moments for {len(fr)} frames")
        lol = lol_frames(a.lol, tag, specs, a.out, a.cached)
        cells = []
        for k, ((can, ms), ref) in enumerate(zip(fr, lol)):
            f = rig.finish(can)[y0:y1, x0:x1]
            bg = Image.new("RGBA", (f.shape[1], f.shape[0]), BG + (255,))
            bg.alpha_composite(Image.fromarray(f))
            d = ImageDraw.Draw(bg)
            d.line([(0, rig.GY - y0), (bg.width, rig.GY - y0)], fill=(70, 84, 70, 255))
            ours = bg.convert("RGB").resize((f.shape[1] * a.z, f.shape[0] * a.z), Image.NEAREST)
            kk = ours.height / ref.height
            ref = ref.resize((round(ref.width * kk), ours.height), Image.LANCZOS)
            cell = Image.new("RGB", (ref.width + ours.width + 8, ours.height + 18), (40, 40, 40))
            cell.paste(ref, (0, 18))
            cell.paste(ours, (ref.width + 8, 18))
            dd = ImageDraw.Draw(cell)
            dd.text((4, 3), f"League {specs[k]}", fill=(230, 230, 230))
            dd.text((ref.width + 12, 3), f"ours: {tag} {k + 1}/{len(fr)}  {int(ms)} ms", fill=(230, 230, 230))
            cells.append((cell, ms))
        w, h = cells[0][0].size
        sheet = Image.new("RGB", (w, h * len(cells)), (40, 40, 40))
        for i, (c, _) in enumerate(cells):
            sheet.paste(c, (0, i * h))
        sheet.save(os.path.join(a.out, f"velkoz_{tag}_vs_lol.png"))
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
    path = os.path.join(a.out, "velkoz_all_vs_lol.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
