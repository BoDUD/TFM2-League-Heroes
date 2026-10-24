#!/usr/bin/env python3
"""Bel'Veth's actions (tools/art/rig_belveth.py) beside League's own clips, one GIF for the user's review.

    python tools/art/review_belveth_actions.py --out DIR [--lol D:/WeGameApps/lol] [--z 4] [--tags attack,skill] [--sheet]

For each tag: League's frames named in CLIPS - the very frames the poses were drawn after (pose_ref.py, Riot's model; the
renders stay in DIR, never committed), one beside each of ours, next to the rig's frame at z screen px a design square,
both at the tag's own frame times. Writes <out>/belveth_<tag>_vs_lol.gif and .png, and <out>/belveth_all_vs_lol.gif:
every tag in turn (each action played twice, the idle and card reels once, last preview_belveth.py's fight with the
effects in play when it has been written), one picture to review (memory one-gif-review). 3/4 view (yaw 35) for every
tag (the user's pick: 3/4 only); the idle beside League's relaxed idle (the design's folded wings), the glide beside
RunClosed.
--sheet: the exported sheet's hd_ frames (league/champions/league_belveth#sheet.png, what the game draws: after
ppu_restyle's outline and ppu_hd), each laid on its frame centre, instead of the rig's frames - the idle as hero_reels'
reel and the ban/pick card's reel (bp) too.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageSequence

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_belveth as Z  # noqa: E402
import pack_belveth_poses as PK  # noqa: E402

# tag -> League's frames shown beside ours (clip@ms, the .anm names), one per frame of ours (the last held for the rest):
# the very frames the poses were drawn after (pack_belveth_poses.POSES); the glide is League's RunClosed at our 6 steps
P = {k: v[0] for k, v in PK.POSES.items()}
IDLE = "idle1_relaxed_base@0"
CLIPS = {"idle": [IDLE], "run": [f"runclosed@{t}" for t in range(0, 660, 110)],
         "attack": [P["a_wind"], P["a_slash"], IDLE],
         "skill": [P["q_dash"], IDLE],
         "skill2": [P["w_coil"], P["w_slam"]],
         "skill_e": [P["e_spin1"], P["e_spin2"], P["e_spin1"], P["e_spin2"]],
         "ult": [P["r_curl"], P["r_rise"]],
         "hit": [IDLE], "dead": [P["d_reel"], P["d_reel"], P["d_down"]],
         "bp": [IDLE]}           # the ban/pick card's reel (hero_reels; --sheet only)
BG = (96, 112, 96)
SHOWCASE = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs", "preview", "league_belveth_showcase.gif")


def lol_frames(lol, tag, n, out):
    want = CLIPS[tag]
    frames = []
    for i in range(n):
        frames += ["--frame", want[min(i, len(want) - 1)]]
    name = f"lol_{tag}"
    cmd = [sys.executable, os.path.join(R.ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Belveth", "--hq",
           "--yaw", "35", "--mirror", "--size", "300", "--width", "1.6", "--fit", "0.5", "--no-labels", "--name", name,
           "--out", out, *frames]
    if tag in ("dead", "skill"):                        # she sinks flat / dashes level: room along the ground
        cmd += ["--fit", "0.35", "--width", "2.2"]
    subprocess.run(cmd, check=True, capture_output=True)
    strip = Image.open(os.path.join(out, name + ".png")).convert("RGB")
    w = strip.width // n
    cells = [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(n)]
    # one box round him in every frame (the clip's own ground kept): League's figure fills its side of the cell
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
    stem = os.path.join(R.ROOT, "league", "champions", "league_belveth")
    anims = json.load(open(R.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = np.asarray(Image.open(R.lp(stem + "#sheet.png")).convert("RGBA"))
    cx, cy = rig.CX, rig.GY - R.FEET * Z.PPU
    out = {}
    for tag in list(Z.MS) + ["bp"]:                      # idle is hero_reels' reel here, bp the card's
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


def flat(fr):
    """A frame of the rig (a canvas or a baked {"body", "over", "under"}) as one canvas."""
    if not isinstance(fr, dict):
        return fr
    full = fr["body"].copy()
    for fx, top in ((fr.get("under"), False), (fr.get("over"), True)):
        if fx is not None:
            m = fx[..., 3] > 0
            if not top:
                m &= full[..., 3] == 0
            full[m] = fx[m]
    return full


def showcase():
    """preview_belveth.py's fight, labelled: the effects in play, on their layers, and the combos (none before
    preview_belveth.py has written it)."""
    if not os.path.exists(SHOWCASE):
        return []
    cells = []
    for f in ImageSequence.Iterator(Image.open(SHOWCASE)):
        cell = Image.new("RGB", (f.width, f.height + 18), (40, 40, 40))
        cell.paste(f.convert("RGB"), (0, 18))
        ImageDraw.Draw(cell).text((4, 3), "in play: W -> Q, Q -> W, coral, the true form", fill=(230, 230, 230))
        cells.append((cell, f.info.get("duration", 40)))
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--z", type=int, default=4)
    ap.add_argument("--tags")
    ap.add_argument("--sheet", action="store_true", help="the exported sheet's hd_ frames instead of the rig's")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    F = Z.Form(Z.design())
    F.rig.idle_canvas = F.pose()
    acts = Z.frames(F)
    rig = F.rig
    if a.sheet:
        acts = sheet_frames(rig)
    tags = a.tags.split(",") if a.tags else list(acts)
    every = []
    allc = np.concatenate([np.stack([rig.finish(flat(c)) for c, _ in fr]) for fr in acts.values()])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3
    for tag in tags:
        fr = acts[tag]
        lol = lol_frames(a.lol, tag, len(fr), a.out)
        cells = []
        for (can, ms), ref in zip(fr, lol):
            f = rig.finish(flat(can))[y0:y1, x0:x1]
            bg = Image.new("RGBA", (f.shape[1], f.shape[0]), BG + (255,))
            gd = ImageDraw.Draw(bg)            # the ground line and the unit's shadow under her standing point
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
            d.text((4, 3), "League " + CLIPS[tag][min(len(cells), len(CLIPS[tag]) - 1)], fill=(230, 230, 230))
            d.text((ref.width + 12, 3), f"ours: {tag}", fill=(230, 230, 230))
            cells.append((cell, ms))
        gif = os.path.join(a.out, f"belveth_{tag}_vs_lol.gif")
        q = [c.quantize(255, dither=Image.Dither.NONE) for c, _ in cells]
        q[0].save(gif, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in cells], loop=0)
        w, h = cells[0][0].size
        sheet = Image.new("RGB", (w, h * len(cells)), (40, 40, 40))
        for i, (c, _) in enumerate(cells):
            sheet.paste(c, (0, i * h))
        sheet.save(os.path.join(a.out, f"belveth_{tag}_vs_lol.png"))
        every += cells * (1 if tag in ("idle", "bp") else 2)   # the long reels once, the actions twice
        print(gif)
    if not a.tags:
        every += showcase()
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
    path = os.path.join(a.out, "belveth_all_vs_lol.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
