#!/usr/bin/env python3
"""Yuumi's actions (tools/art/rig_yuumi.py) beside League's own clips, one GIF per tag for the user's review.

    python tools/art/review_yuumi_actions.py --out DIR [--lol D:/WeGameApps/lol] [--z 4] [--tags attack,skill]

For each tag: League's clip (pose_ref.py, Riot's model - the renders stay in DIR, never committed) sampled at as many
frames as the tag has, spread over the clip's part named in CLIPS, next to the rig's frame at z screen px a design
square, both at the tag's own frame times. Writes <out>/yuumi_<tag>_vs_lol.gif and <out>/yuumi_<tag>_vs_lol.png,
and <out>/yuumi_all_vs_lol.gif: every tag in turn (each played twice), one picture to review (memory one-gif-review).
League's renders use pack_yuumi_picture.LOOK (the base skin's tint maps, the spiky fur / dilated eyes / props hidden);
the side view is yaw 70 on her model (45 for the 3/4 idle and the hit).
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
import rig_yuumi as Z  # noqa: E402
from pack_yuumi_picture import LOOK  # noqa: E402

# tag -> (League's clip, from s, to s) - the part of the clip the tag shows
CLIPS = {"idle": ("Yuumi_Idle01", 0, 2.0), "run": ("Yuumi_Run01", 0, 1.33), "attack": ("Yuumi_Attack01", 0, 0.9),
         "skill": ("Yuumi_Spell1_detached", 0, 1.8), "skill2": ("Yuumi_Spell2_Attach_in", 0, 0.6),
         "w_off": ("Yuumi_Spell2_Detach_out", 0.8, 1.9), "ult": ("Yuumi_Spell4_in", 0, 1.25),
         "hit": ("Yuumi_Idle01", 0, 0.1), "dead": ("Yuumi_Death01", 0, 3.0)}
YAW = {"idle": 45, "hit": 45}
BG = (96, 112, 96)


def lol_frames(lol, tag, n, out):
    clip, t0, t1 = CLIPS[tag]
    name = f"lol_{tag}"
    cmd = [sys.executable, os.path.join(R.ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Yuumi",
           "--anim", clip, "--frames", str(n), "--t0", str(t0), "--t1", str(t1), "--mirror",
           *LOOK, "--yaw", str(YAW.get(tag, 70)), "--size", "300", "--fit", "0.5", "--no-labels", "--out", out]
    subprocess.run(cmd, check=True, capture_output=True)
    strip = Image.open(os.path.join(out, clip + ".png")).convert("RGB")
    os.replace(os.path.join(out, clip + ".png"), os.path.join(out, name + ".png"))
    w = strip.width // n
    return [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--z", type=int, default=4)
    ap.add_argument("--tags")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    F = Z.form()
    acts = Z.frames(F)
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
        gif = os.path.join(a.out, f"yuumi_{tag}_vs_lol.gif")
        q = [c.quantize(255, dither=Image.Dither.NONE) for c, _ in cells]
        q[0].save(gif, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in cells], loop=0)
        w, h = cells[0][0].size
        sheet = Image.new("RGB", (w, h * len(cells)), (40, 40, 40))
        for i, (c, _) in enumerate(cells):
            sheet.paste(c, (0, i * h))
        sheet.save(os.path.join(a.out, f"yuumi_{tag}_vs_lol.png"))
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
    path = os.path.join(a.out, "yuumi_all_vs_lol.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
