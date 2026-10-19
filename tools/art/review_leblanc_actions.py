#!/usr/bin/env python3
"""LeBlanc's PPU actions (tools/art/rig_leblanc_hd.py) beside League's own clips: one GIF for the user's review
(memory one-gif-review: every tag in turn, played twice, League's clip on the left, ours on the right).

    python tools/art/review_leblanc_actions.py --joints <dir>/leblanc_joints.json --out DIR [--lol D:/WeGameApps/lol]

For each tag: League's clip (pose_ref.py with poses.json's chibi head and legs, Riot's model - the renders stay in DIR,
never committed) sampled at as many frames as the tag has, spread over the clip's part named in CLIPS, next to the
rig's frame (with the effects the bake laid in) at z screen px a design square, both at the tag's own frame times.
Writes <out>/leblanc_all_vs_lol.gif.
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
import rig_leblanc_hd as L  # noqa: E402

# tag -> (League's clip, from s, to s) - the part of the clip the tag shows
CLIPS = {"idle": ("Idle1", 0, 2.0), "run": ("Run1", 0, 1.13), "attack": ("Attack1", 0, 0.6),
         "skill": ("Spell1", 0, 0.5), "ult": ("Spell1", 0, 0.5), "skill2": ("Spell2", 0, 0.5),
         "skill2_back": ("Spell2_Recast", 0, 0.5), "e": ("Spell3", 0, 0.8), "hit": ("Idle1", 0, 0.1),
         "dead": ("Death", 0, 1.5)}
BG = (96, 112, 96)


def lol_frames(lol, tag, n, out):
    clip, t0, t1 = CLIPS[tag]
    sub = os.path.join(out, "lol_" + tag)
    os.makedirs(sub, exist_ok=True)
    cmd = [sys.executable, os.path.join(R.ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Leblanc",
           "--anim", clip, "--frames", str(n), "--t0", str(t0), "--t1", str(t1), "--head", "2.3", "--legs", "0.8",
           "--submesh-texture", "Weapon=Weapon_TX", "--yaw", "45", "--pitch", "20", "--size", "300", "--no-labels",
           "--out", sub]
    subprocess.run(cmd, check=True, capture_output=True)
    png = [f for f in os.listdir(sub) if f.lower().endswith(".png")][0]
    strip = Image.open(os.path.join(sub, png)).convert("RGB")
    w = strip.width // n
    return [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(n)]


def flat(rig, lay):
    """A frame (a canvas, or the bake's {body, over, under}) as one RGBA canvas after the rig's finish."""
    if not isinstance(lay, dict):
        return rig.finish(lay)
    out = rig.finish(lay["body"])
    for fx, top in ((lay.get("under"), False), (lay.get("over"), True)):
        if fx is not None:
            m = fx[..., 3] > 0
            if not top:
                m &= out[..., 3] == 0
            out[m] = fx[m]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--z", type=int, default=3)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    with open(a.joints, encoding="utf-8") as f:
        joints = json.load(f)
    rig = L.make_rig(L.design())
    acts = L.frames(rig, joints)
    tags = [t for t in CLIPS if t in acts]
    flats = {t: [(flat(rig, c), ms) for c, ms in acts[t]] for t in tags}
    allc = np.concatenate([np.stack([c for c, _ in fr]) for fr in flats.values()])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3
    every = []
    for tag in tags:
        fr = flats[tag]
        lol = lol_frames(a.lol, tag, len(fr), a.out)
        for (can, ms), ref in zip(fr, lol):
            f = can[y0:y1, x0:x1]
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
            every.append((cell, ms))
        every += every[-len(fr):]
        print(tag, len(fr))
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
    path = os.path.join(a.out, "leblanc_all_vs_lol.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[max(20, int(ms)) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
