#!/usr/bin/env python3
"""Twitch's actions (tools/art/rig_twitch_hd.py) beside League's own clips, one GIF for the user's review.

    python tools/art/review_twitch_actions.py --out DIR [--lol D:/WeGameApps/lol] [--z 4] [--tags attack,skill]

For each tag: League's frames of assets/source/twitch/poses.json (the clips the old sheet was drawn after; pose_ref.py,
Riot's model - the renders stay in DIR, never committed), one beside each of ours, both at the tag's own frame times;
ours are the exported sheet's hd_ frames (league/champions/league_twitch#sheet.png: what the game draws), each laid on
its frame centre, the idle as hero_reels' reel and the ban/pick card's reel (bp) too. Writes
<out>/twitch_<tag>_vs_lol.gif and .png, and <out>/twitch_all_vs_lol.gif: every tag in turn (each action played twice,
the idle and card reels once), one picture to review (memory one-gif-review).
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
import rig_twitch_hd as T  # noqa: E402

POSES = os.path.join(R.ROOT, "assets", "source", "twitch", "poses.json")
STEM = os.path.join(R.ROOT, "league", "champions", "league_twitch")
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_e", "ult", "hit", "dead", "bp"]
BG = (96, 112, 96)


def clips(tag, ms):
    """League's frame (clip@ms) for each of our frames: poses.json's frame of the time our frame starts at (the attack's
    bake split its frames at the flash's times)."""
    spec = json.load(open(R.lp(POSES), encoding="utf-8"))["tags"]
    src = spec.get(tag if tag not in ("bp", "idle") else "idle")["frames"]
    out, t = [], 0
    for m in ms:
        acc, pick = 0, src[-1][0]
        for clip, d in src:
            if acc <= t < acc + d:
                pick = clip
                break
            acc += d
        out.append(pick)
        t += m
    return out


def lol_frames(lol, tag, want, out):
    spec = json.load(open(R.lp(POSES), encoding="utf-8"))
    cam = spec["camera"]
    name = f"lol_{tag}"
    cmd = [sys.executable, os.path.join(R.ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Twitch", "--hq",
           "--yaw", str(cam["yaw"]), "--pitch", str(cam["pitch"]), "--head", str(spec["chibi"]["head"]),
           "--hide-submeshes", "--size", "300", "--width", "1.6", "--fit", "0.5", "--no-labels", "--name", name,
           "--out", out, "--fit-all"]
    if cam.get("mirror"):
        cmd.append("--mirror")
    if tag == "dead":
        cmd += ["--fit", "0.35", "--width", "2.2"]
    for f in want:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    strip = Image.open(os.path.join(out, name + ".png")).convert("RGB")
    n = len(want)
    w = strip.width // n
    cells = [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(n)]
    bg = np.asarray(cells[0]).astype(int)[2, 2]
    boxes = []
    for c in cells:
        a = np.asarray(c).astype(int)
        ys, xs = np.nonzero(np.abs(a - bg).sum(-1) > 30)
        if len(ys):
            boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
    if boxes:
        x0, y0 = min(b[0] for b in boxes) - 6, min(b[1] for b in boxes) - 6
        x1, y1 = max(b[2] for b in boxes) + 6, max(b[3] for b in boxes) + 6
        cells = [c.crop((max(0, x0), max(0, y0), min(c.width, x1), min(c.height, y1))) for c in cells]
    return cells


def sheet_frames(rig):
    """{tag: [(canvas, ms)]} from the exported sheet's hd_ frames, each centred on the rig's frame centre (CX, the pivot
    FEET x PPU above the ground row) - the frame centre is the unit's position in game."""
    anims = json.load(open(R.lp(STEM + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = np.asarray(Image.open(R.lp(STEM + "#sheet.png")).convert("RGBA"))
    cx, cy = rig.CX, rig.GY - R.FEET * T.PPU
    out = {}
    for tag in TAGS:
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
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rig = T.make_rig(T.Design())
    acts = sheet_frames(rig)
    tags = a.tags.split(",") if a.tags else TAGS
    every = []
    allc = np.concatenate([np.stack([c for c, _ in fr]) for fr in acts.values()])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3
    for tag in tags:
        fr = acts[tag]
        want = clips(tag, [ms for _, ms in fr])
        lol = lol_frames(a.lol, tag, want, a.out)
        cells = []
        for i, ((can, ms), ref) in enumerate(zip(fr, lol)):
            f = can[y0:y1, x0:x1]
            bg = Image.new("RGBA", (f.shape[1], f.shape[0]), BG + (255,))
            gd = ImageDraw.Draw(bg)            # the ground line and the unit's shadow under his standing point
            gx, gy = rig.CX - x0, rig.GY - y0
            gd.line([(0, gy), (f.shape[1], gy)], fill=(70, 80, 70, 255))
            gd.ellipse([gx - 9, gy - 3, gx + 9, gy + 2], fill=(52, 62, 52, 255))
            bg.alpha_composite(Image.fromarray(f))
            ours = bg.convert("RGB").resize((f.shape[1] * a.z, f.shape[0] * a.z), Image.NEAREST)
            k = ours.height / ref.height
            ref = ref.resize((round(ref.width * k), ours.height), Image.LANCZOS)
            cell = Image.new("RGB", (ref.width + ours.width + 8, ours.height + 18), (40, 40, 40))
            cell.paste(ref, (0, 18))
            cell.paste(ours, (ref.width + 8, 18))
            d = ImageDraw.Draw(cell)
            d.text((4, 3), "League " + want[i], fill=(230, 230, 230))
            d.text((ref.width + 12, 3), f"ours: {tag} {i + 1}/{len(fr)}", fill=(230, 230, 230))
            cells.append((cell, ms))
        gif = os.path.join(a.out, f"twitch_{tag}_vs_lol.gif")
        q = [c.quantize(255, dither=Image.Dither.NONE) for c, _ in cells]
        q[0].save(gif, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in cells], loop=0)
        w, h = cells[0][0].size
        sheet = Image.new("RGB", (w, h * len(cells)), (40, 40, 40))
        for i, (c, _) in enumerate(cells):
            sheet.paste(c, (0, i * h))
        sheet.save(os.path.join(a.out, f"twitch_{tag}_vs_lol.png"))
        every += cells * (1 if tag in ("idle", "bp") else 2)   # the long reels once, the actions twice
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
    path = os.path.join(a.out, "twitch_all_vs_lol.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
