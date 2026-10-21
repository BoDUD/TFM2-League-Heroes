#!/usr/bin/env python3
"""Neeko's actions (tools/art/rig_neeko.py) beside League's own frames, one GIF of every tag for the user's review
(memory one-gif-review: League left, ours right; review_naafiri_actions.py's way).

    python tools/art/review_neeko_actions.py --out DIR [--z 2] [--tags attack,ult_b] [--cached] [--sheet]

League's frames: LOL[tag] gives, for each of our frames, the clip and the time it was posed after (Neeko.wad.client, the
R bloom's petals and the disguise model hidden), rendered by tools/lol/pose_ref.py on Riot's model at the 3/4 camera
(they stay in DIR, never committed). Ours: rig_neeko's canvases (or, with --sheet, the exported sheet's hd_ frames),
z screen px a design square, on the same ground line. Writes <out>/neeko_<tag>_vs_lol.png and
<out>/neeko_all_vs_lol.gif (every tag in turn, each played twice).
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
import rig_neeko as RG  # noqa: E402

BG = (96, 112, 96)
NF = ("Neeko", 35)


def at(clip, *ms):
    return [(NF, clip, m) for m in ms]


# per tag, per frame of ours: (champion + camera, League clip, ms)
LOL = {
    "idle": at("Neeko_idle1", 0, 300, 600, 900, 1200, 1500, 1800, 2100),
    "run": at("Neeko_Run", 0, 225, 450, 675),
    "attack": at("Neeko_Attack1", 0, 338, 450, 676),
    "attack_w": at("Neeko_Passive_attack", 250, 375, 500, 875),
    "skill": at("Neeko_Spell1", 0, 71, 142, 213, 283, 425, 496, 560),
    "skill2": at("Neeko_Spell3_0", 100, 200, 400, 500, 700),
    "ult": at("Neeko_channel_wndup", 0, 317, 475, 633, 792),
    "ult_b": at("Neeko_Spell4", 0, 113, 225, 676, 788),
    "hit": at("Neeko_idle1", 0, 0),
    "dead": at("Neeko_Death", 250, 500, 1000, 1750),
}


def lol_frames(lol, tag, out, cached=False):
    """League's frames for a tag: one pose_ref call per run of frames with the same champion and camera."""
    specs = LOL[tag]
    cells = []
    i = 0
    run = 0
    while i < len(specs):
        (champ, yaw), _, _ = specs[i]
        j = i
        while j < len(specs) and specs[j][0] == (champ, yaw):
            j += 1
        name = f"lol_{tag}_{run}"
        path = os.path.join(out, name + ".png")
        if not (cached and os.path.isfile(path)):
            cmd = [sys.executable, os.path.join(R.ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
                   "--hide-submeshes", "--hq", "--mirror", "--yaw", str(yaw), "--size", "300",
                   "--width", "2.2", "--fit", "0.35", "--ground", "0.8", "--no-labels", "--bg", ",".join(map(str, BG)),
                   "--name", name, "--out", out]
            for _, clip, ms in specs[i:j]:
                cmd += ["--frame", f"{clip}@{ms}"]
            subprocess.run(cmd, check=True, capture_output=True)
        strip = Image.open(path).convert("RGB")
        n = j - i
        w = strip.width // n
        cells += [strip.crop((k * w, 0, (k + 1) * w, strip.height)) for k in range(n)]
        i = j
        run += 1
    return cells


def sheet_frames(C, tags):
    """{tag: [(canvas, ms)]} from the exported sheet's hd_ frames (after the restyle), each centred on the canvas's
    frame centre (CX, the pivot FEET x PPU above the ground row)."""
    stem = os.path.join(R.ROOT, "league", "champions", "league_neeko")
    anims = json.load(open(R.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = np.asarray(Image.open(R.lp(stem + "#sheet.png")).convert("RGBA"))
    cx, cy = C.rig.CX, C.rig.GY - R.FEET * RG.PPU
    out = {}
    for tag in tags:
        fr = []
        for f in anims["hd_" + tag]["frames"]:
            d = f["data"]
            im = sheet[int(d["y"]):int(d["y"] + d["h"]), int(d["x"]):int(d["x"] + d["w"])]
            can = C.rig.canvas()
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
    ap.add_argument("--z", type=int, default=2)
    ap.add_argument("--tags")
    ap.add_argument("--cached", action="store_true")
    ap.add_argument("--sheet", action="store_true", help="the exported sheet's hd_ frames instead of the rig's")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    C = RG.Canvas()
    acts = RG.frames(C)
    if a.sheet:
        acts = sheet_frames(C, list(acts))
    tags = a.tags.split(",") if a.tags else list(LOL)
    every = []
    for tag in tags:
        fr = acts[tag]
        lol = lol_frames(a.lol, tag, a.out, a.cached)
        # one crop for the tag's League frames (their union, a margin round it): the cells keep their motion
        boxes = [np.argwhere(np.abs(np.asarray(c).astype(int) - BG).sum(2) > 24) for c in lol]
        ys_ = np.concatenate([b[:, 0] for b in boxes if len(b)])
        xs_ = np.concatenate([b[:, 1] for b in boxes if len(b)])
        m_ = 12
        lol = [c.crop((max(0, xs_.min() - m_), max(0, ys_.min() - m_), min(c.width, xs_.max() + m_),
                       min(c.height, ys_.max() + m_))) for c in lol]
        if len(lol) != len(fr):
            sys.exit(f"{tag}: {len(lol)} League frames for {len(fr)} of ours")
        cans = [C.rig.finish(c) for c, _ in fr]
        ys, xs = np.nonzero(np.stack(cans)[..., 3].max(0) > 0)
        y0, y1 = ys.min() - 2, max(ys.max() + 3, C.rig.GY + 2)
        x0, x1 = xs.min() - 2, xs.max() + 3
        cells = []
        for k, (f, (_, ms), ref) in enumerate(zip(cans, fr, lol)):
            f = f[y0:y1, x0:x1]
            bg = Image.new("RGBA", (f.shape[1], f.shape[0]), BG + (255,))
            bg.alpha_composite(Image.fromarray(f))
            d = ImageDraw.Draw(bg)
            d.line([(0, C.rig.GY - y0), (bg.width, C.rig.GY - y0)], fill=(70, 84, 70, 255))
            ours = bg.convert("RGB").resize((f.shape[1] * a.z, f.shape[0] * a.z), Image.NEAREST)
            kk = ours.height / ref.height
            ref = ref.resize((max(1, round(ref.width * kk)), ours.height), Image.LANCZOS)
            cell = Image.new("RGB", (ref.width + ours.width + 8, ours.height + 18), (40, 40, 40))
            cell.paste(ref, (0, 18))
            cell.paste(ours, (ref.width + 8, 18))
            dd = ImageDraw.Draw(cell)
            spec = LOL[tag][k]
            dd.text((4, 3), f"League {spec[1]}@{spec[2]}", fill=(230, 230, 230))
            dd.text((ref.width + 12, 3), f"ours: {tag} {k + 1}/{len(fr)}  {int(ms)} ms", fill=(230, 230, 230))
            cells.append((cell, ms))
        w = max(c.width for c, _ in cells)
        h = max(c.height for c, _ in cells)
        sheet = Image.new("RGB", (w, h * len(cells)), (40, 40, 40))
        for i, (c, _) in enumerate(cells):
            sheet.paste(c, (0, i * h))
        sheet.save(os.path.join(a.out, f"neeko_{tag}_vs_lol.png"))
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
    path = os.path.join(a.out, "neeko_all_vs_lol.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
