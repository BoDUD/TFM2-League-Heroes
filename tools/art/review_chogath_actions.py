#!/usr/bin/env python3
"""Cho'Gath's actions (tools/art/rig_chogath.py) beside League's own clips, one GIF per tag for the user's review.

    python tools/art/review_chogath_actions.py --out DIR [--lol D:/WeGameApps/lol] [--z 4] [--tags attack,skill]

For each tag: League's clip (pose_ref.py, Riot's model - the renders stay in DIR, never committed) sampled at as many
frames as the tag has, spread over the clip's part named in CLIPS, next to the rig's frame at z screen px a design
square, both at the tag's own frame times. Writes <out>/chogath_<tag>_vs_lol.gif and <out>/chogath_<tag>_vs_lol.png,
and <out>/chogath_all_vs_lol.gif: every tag in turn (each played twice), one picture to review. League's death walks
its root out of a normal cell: it is rendered in a wide cell (WIDE) and cropped to the model.
--sheet: ours are the exported sheet's hd_ frames (league/champions/league_chogath#sheet.png, what the game draws: after
ppu_restyle's outline and ppu_hd), each laid on its frame centre, instead of the rig's frames.
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
import rig_chogath as V  # noqa: E402

# tag -> (League's clip, from s, to s) - the part of the clip the tag shows
CLIPS = {"idle": ("chogath_idle1", 0, 2.0), "run": ("chogath_run", 0, 0.75), "attack": ("chogath_attack2", 0, 0.7),
         "attack_e": ("chogath_crit", 0, 0.7), "skill": ("chogath_spell4", 0, 0.9), "skill2": ("chogath_spell1", 0, 1.0),
         "ult": ("chogath_spell2", 0, 1.3), "hit": ("chogath_idle1", 0, 0.1), "dead": ("chogath_death", 0, 2.5)}
WIDE = {"dead"}
BG = (96, 112, 96)


def lol_frames(lol, tag, n, out):
    clip, t0, t1 = CLIPS[tag]
    name = f"lol_{tag}"
    wide = ["--width", "3", "--fit", "0.3"] if tag in WIDE else []
    cmd = [sys.executable, os.path.join(R.ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Chogath",
           "--anim", clip, "--frames", str(n), "--t0", str(t0), "--t1", str(t1), "--mirror",
           "--yaw", "75", "--size", "300", "--no-labels", "--out", out] + wide
    subprocess.run(cmd, check=True, capture_output=True)
    strip = Image.open(os.path.join(out, clip + ".png")).convert("RGB")
    os.replace(os.path.join(out, clip + ".png"), os.path.join(out, name + ".png"))
    w = strip.width // n
    tiles = [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(n)]
    if tag in WIDE:
        # every tile cropped to the box the model takes over the whole clip
        a = np.stack([np.asarray(t).astype(int) for t in tiles])
        bg = a[0, 0, 0]
        fg = (np.abs(a - bg).sum(-1) > 30).any(0)
        ys, xs = np.nonzero(fg)
        m = 10
        box = (max(0, xs.min() - m), max(0, ys.min() - m), min(w, xs.max() + m), min(strip.height, ys.max() + m))
        tiles = [t.crop(box) for t in tiles]
    return tiles


def sheet_frames(F):
    """{tag: [(canvas, ms)]} from the exported sheet's hd_ frames, each centred on the rig's frame centre (CX, the
    pivot FEET x PPU above the ground row) - the frame centre is the unit's position in game."""
    import json
    stem = os.path.join(R.ROOT, "league", "champions", "league_chogath")
    anims = json.load(open(R.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = np.asarray(Image.open(R.lp(stem + "#sheet.png")).convert("RGBA"))
    rig = F.rig
    cx, cy = rig.CX, rig.GY - R.FEET * V.PPU
    out = {}
    for tag in V.MS:
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
    ap.add_argument("--sheet", action="store_true", help="the exported sheet's hd_ frames instead of the rig's")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    F = V.form()
    acts = V.frames(F)
    if a.sheet:
        acts = sheet_frames(F)
    tags = a.tags.split(",") if a.tags else list(acts)
    every = []
    allc = np.concatenate([np.stack([F.rig.finish(c) for c, _ in fr]) for fr in acts.values()])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3
    for tag in tags:
        fr = acts[tag]
        lol = lol_frames(a.lol, tag, len(fr), a.out)
        cells = []
        for (can, ms), ref in zip(fr, lol):
            f = F.rig.finish(can)[y0:y1, x0:x1]
            bg = Image.new("RGBA", (f.shape[1], f.shape[0]), BG + (255,))
            bg.alpha_composite(Image.fromarray(f))
            ours = bg.convert("RGB").resize((f.shape[1] * a.z, f.shape[0] * a.z), Image.NEAREST)
            k = ours.height / ref.height
            ref = ref.resize((round(ref.width * k), ours.height), Image.LANCZOS)
            cell = Image.new("RGB", (ref.width + ours.width + 8, ours.height + 18), (40, 40, 40))
            cell.paste(ref, (0, 18))
            cell.paste(ours, (ref.width + 8, 18))
            d = ImageDraw.Draw(cell)
            d.text((4, 3), f"League {CLIPS[tag][0]}", fill=(230, 230, 230))
            d.text((ref.width + 12, 3), f"ours: {tag}", fill=(230, 230, 230))
            cells.append((cell, ms))
        gif = os.path.join(a.out, f"chogath_{tag}_vs_lol.gif")
        q = [c.quantize(255, dither=Image.Dither.NONE) for c, _ in cells]
        q[0].save(gif, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in cells], loop=0)
        w, h = cells[0][0].size
        sheet = Image.new("RGB", (w, h * len(cells)), (40, 40, 40))
        for i, (c, _) in enumerate(cells):
            sheet.paste(c, (0, i * h))
        sheet.save(os.path.join(a.out, f"chogath_{tag}_vs_lol.png"))
        every += cells * 2
        print(gif)
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
    path = os.path.join(a.out, "chogath_all_vs_lol.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
