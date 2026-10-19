#!/usr/bin/env python3
"""Vex's actions (tools/art/rig_vex.py) beside League's own clips, one GIF per tag for the user's review.

    python tools/art/review_vex_actions.py --out DIR [--lol D:/WeGameApps/lol] [--z 4] [--tags attack,skill]

For each tag: League's clip (pose_ref.py, Riot's model - the renders stay in DIR, never committed) sampled at as many
frames as the tag has, spread over the clip's part named in CLIPS, next to the rig's frame at z screen px a design
square, both at the tag's own frame times. Writes <out>/vex_<tag>_vs_lol.gif and <out>/vex_<tag>_vs_lol.png,
and <out>/vex_all_vs_lol.gif: every tag in turn (each played twice), one picture to review (memory one-gif-review).
League's renders leave out the Shadow decal, the ult's hands and the spare eye shapes (her Shadow standing up is
particles in League); the side view is yaw 75 on her model (35 for the 3/4 idle).
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
import rig_vex as Z  # noqa: E402

# tag -> (League's clip, from s, to s) - the part of the clip the tag shows
CLIPS = {"idle": ("Idle", 0, 2.0), "run": ("Run", 0, 0.8), "attack": ("Attack_1", 0, 0.3),
         "skill": ("Spell1", 0, 1.0), "skill_w": ("Spell2", 0, 0.8), "skill2": ("Spell3", 0, 0.75),
         "ult": ("Spell4_Cast", 0, 0.75), "ult_dash": ("Spell4_Dash", 0, 0.65), "ult_hit": ("Spell4_Attack", 0, 0.8),
         "hit": ("Idle", 0, 0.1), "dead": ("Death", 0, 2.3)}
YAW = {"idle": 35}
HIDE = ["--hide-submesh", "Ult", "--hide-submesh", "Shadow", *[x for e in ("EyeCross", "EyeWink", "EyeClose", "EyeOpen",
        "EyeLaugh") for x in ("--hide-submesh", e)], "--hide-joints", r"^(L_|R_)?Shadow|^VFXUlt"]
BG = (96, 112, 96)


def lol_frames(lol, tag, n, out, cached=False):
    clip, t0, t1 = CLIPS[tag]
    name = f"lol_{tag}"
    path = os.path.join(out, name + ".png")
    if cached and os.path.isfile(path):
        strip = Image.open(path).convert("RGB")
        w = strip.width // n
        return [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(n)]
    cmd = [sys.executable, os.path.join(R.ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Vex",
           "--anim", clip, "--frames", str(n), "--t0", str(t0), "--t1", str(t1), "--mirror",
           *HIDE, "--yaw", str(YAW.get(tag, 75)), "--size", "300", "--width", "1.3", "--no-labels", "--out", out]
    subprocess.run(cmd, check=True, capture_output=True)
    strip = Image.open(os.path.join(out, clip + ".png")).convert("RGB")
    os.replace(os.path.join(out, clip + ".png"), os.path.join(out, name + ".png"))
    w = strip.width // n
    return [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(n)]


def sheet_frames(F):
    """{tag: [(canvas, ms)]} from the exported sheet's hd_ frames (what the game draws: after the restyle's outline), each
    centred on the rig's frame centre (CX, the pivot FEET x PPU above the ground row) - review_chogath_actions'."""
    import json
    stem = os.path.join(R.ROOT, "league", "champions", "league_vex")
    anims = json.load(open(R.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = np.asarray(Image.open(R.lp(stem + "#sheet.png")).convert("RGBA"))
    rig = F.rig
    cx, cy = rig.CX, rig.GY - R.FEET * Z.PPU
    out = {}
    for tag in Z.MS:
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
    ap.add_argument("--cached", action="store_true", help="reuse League's renders already in --out")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    F = Z.form()
    acts = sheet_frames(F) if a.sheet else Z.frames(F)
    tags = a.tags.split(",") if a.tags else list(acts)
    every = []
    allc = np.concatenate([np.stack([F.rig.finish(c) for c, _ in fr]) for fr in acts.values()])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3
    for tag in tags:
        fr = acts[tag]
        lol = lol_frames(a.lol, tag, len(fr), a.out, a.cached)
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
        gif = os.path.join(a.out, f"vex_{tag}_vs_lol.gif")
        q = [c.quantize(255, dither=Image.Dither.NONE) for c, _ in cells]
        q[0].save(gif, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in cells], loop=0)
        w, h = cells[0][0].size
        sheet = Image.new("RGB", (w, h * len(cells)), (40, 40, 40))
        for i, (c, _) in enumerate(cells):
            sheet.paste(c, (0, i * h))
        sheet.save(os.path.join(a.out, f"vex_{tag}_vs_lol.png"))
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
    path = os.path.join(a.out, "vex_all_vs_lol.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
