#!/usr/bin/env python3
"""Zaahen's actions (tools/art/rig_zaahen.py) beside League's own clips, one GIF for the user's review.

    python tools/art/review_zaahen_actions.py --out DIR [--lol D:/WeGameApps/lol] [--z 4] [--tags attack,skill] [--sheet]

For each tag: League's frames named in CLIPS - the very frames the poses were drawn after (pose_ref.py, Riot's model at
the pose pack's camera, his own maps: pack_zaahen_picture.LOOK; the renders stay in DIR, never committed), one beside
each of ours, next to the rig's frame at z screen px a design square, both at the tag's own frame times. The revive
(`rise`, the add-on's picture: rig_zaahen.rise_canvases) is shown against Passive_Revive by phase. Writes
<out>/zaahen_<tag>_vs_lol.gif and .png, and <out>/zaahen_all_vs_lol.gif: every tag in turn (each action played twice,
the idle and the revive once), one picture to review (memory one-gif-review). 3/4 view (yaw 35) for every tag.
--sheet: the exported sheets' hd_ frames (league/champions/league_zaahen#sheet.png and league/effects/league_zaahen_rise,
what the game draws: after ppu_restyle's outline and ppu_hd), each laid on its frame centre, instead of the rig's frames.
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
import rig_zaahen as Z  # noqa: E402
import pack_zaahen_poses as PK  # noqa: E402
import pack_zaahen_picture as ZP  # noqa: E402

# tag -> League's frames shown beside ours (clip@ms, the .anm names), one per frame of ours (the last held for the rest):
# the very frames the poses were drawn after (pack_zaahen_poses.POSES)
P = {k: v[0] for k, v in PK.POSES.items()}
IDLE = "IdleBase@0"
SPIN = "Spell1_AA1@550"          # the turn between the spin and the cut
CLIPS = {"idle": [IDLE], "run": [P["run1"], P["run2"], P["run3"], P["run4"]],
         "attack": [P["a_wind"], P["a_sweep"], IDLE],
         "skill": ["Spell1_AA1@0", P["q_cut1"], P["q_cut2"], IDLE],
         "skill_up": [P["q_crouch"], P["q_up"], IDLE],
         "skill2": ["Spell2@0", P["w_thrust"], P["w_pull"]],
         "skill2e": ["Spell2@0", P["w_thrust"], P["w_pull"], P["e_spin"], SPIN, P["q_cut1"], IDLE],
         "dash": [P["e_dash"]], "skill3": [P["e_spin"], SPIN, P["q_cut1"], IDLE],
         "ult": [P["r_crouch"], "Spell4_Intro@500", P["r_rise"], "Spell4_Dash@150", P["r_stab"]],
         "hit": [IDLE, IDLE], "dead": [P["d_fall"], P["d_fall"], P["d_down"], P["d_down"]],
         "rise": ["Passive_Revive@600", P["rv_kneel"], P["rv_kneel"], "Passive_Revive@3460"]}
BG = (96, 112, 96)


def lol_frames(lol, tag, n, out):
    want = CLIPS[tag]
    m = len(want) if tag == "rise" else n
    frames = []
    for i in range(m):
        frames += ["--frame", want[min(i, len(want) - 1)]]
    name = f"lol_{tag}"
    cmd = [sys.executable, os.path.join(R.ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Zaahen", "--hq",
           "--yaw", "35", "--mirror", "--size", "300", "--width", "2.2", "--fit", "0.35", "--no-labels", "--name", name,
           "--out", out, "--fit-all", *frames] + ZP.LOOK
    subprocess.run(cmd, check=True, capture_output=True)
    strip = Image.open(os.path.join(out, name + ".png")).convert("RGB")
    w = strip.width // m
    cells = [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(m)]
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
    if tag == "rise":                   # League's phases spread over our frames (rig_zaahen.RISE_SEQ)
        out_ = []
        for k, (_, ms) in enumerate(Z.RISE_SEQ):
            out_ += [cells[k]] * (ms // Z.GLOW_MS)
        cells = out_[:n] + [out_[-1]] * max(0, n - len(out_))
    return cells


def sheet_frames(rig):
    """{tag: [(canvas, ms)]} from the exported sheets' hd_ frames, each centred on the rig's frame centre (CX, the pivot
    FEET x PPU above the ground row) - the frame centre is the unit's position in game."""
    cx, cy = rig.CX, rig.GY - R.FEET * Z.PPU
    out = {}
    for stem, tags in ((os.path.join(R.ROOT, "league", "champions", "league_zaahen"), list(Z.MS)),
                       (os.path.join(R.ROOT, "league", "effects", "league_zaahen_rise"), ["rise_r"])):
        anims = json.load(open(R.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
        sheet = np.asarray(Image.open(R.lp(stem + "#sheet.png")).convert("RGBA"))
        for tag in tags:
            if "hd_" + tag not in anims:
                continue
            fr = []
            for f in anims["hd_" + tag]["frames"]:
                d = f["data"]
                im = sheet[int(d["y"]):int(d["y"] + d["h"]), int(d["x"]):int(d["x"] + d["w"])]
                can = np.zeros((rig.CH + 40, rig.CW, 4), np.uint8)
                y0, x0 = int(round(cy - im.shape[0] / 2)) + 40, int(round(cx - im.shape[1] / 2))
                ys, xs = max(0, y0), max(0, x0)
                sub = im[ys - y0:, xs - x0:][:can.shape[0] - ys, :can.shape[1] - xs]
                can[ys:ys + sub.shape[0], xs:xs + sub.shape[1]] = sub
                fr.append((can[40:], round(f.get("duration", 0.1) * 1000)))
            out["rise" if tag == "rise_r" else tag] = fr
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--z", type=int, default=4)
    ap.add_argument("--tags")
    ap.add_argument("--sheet", action="store_true", help="the exported sheets' hd_ frames instead of the rig's")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    C = Z.Canvas()
    rig = C.rig
    if a.sheet:
        acts = sheet_frames(rig)
    else:
        acts = Z.frames(C)
        acts["rise"] = Z.rise_canvases(C)
    tags = a.tags.split(",") if a.tags else list(acts)
    every = []
    allc = np.concatenate([np.stack([c if a.sheet else rig.finish(c) for c, _ in fr]) for fr in acts.values()])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, max(ys.max() + 3, rig.GY + 3), xs.min() - 2, xs.max() + 3
    for tag in tags:
        fr = acts[tag]
        lol = lol_frames(a.lol, tag, len(fr), a.out)
        cells = []
        for (can, ms), ref in zip(fr, lol):
            f = (can if a.sheet else rig.finish(can))[y0:y1, x0:x1]
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
            lab = CLIPS[tag][min(len(cells), len(CLIPS[tag]) - 1)] if tag != "rise" else "Passive_Revive"
            d.text((4, 3), "League " + lab, fill=(230, 230, 230))
            d.text((ref.width + 12, 3), f"ours: {tag}", fill=(230, 230, 230))
            cells.append((cell, ms))
        gif = os.path.join(a.out, f"zaahen_{tag}_vs_lol.gif")
        q = [c.quantize(255, dither=Image.Dither.NONE) for c, _ in cells]
        q[0].save(gif, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in cells], loop=0)
        w, h = cells[0][0].size
        sheet = Image.new("RGB", (w, h * min(len(cells), 12)), (40, 40, 40))
        for i, (c, _) in enumerate(cells[:12]):
            sheet.paste(c, (0, i * h))
        sheet.save(os.path.join(a.out, f"zaahen_{tag}_vs_lol.png"))
        every += cells * (1 if tag in ("idle", "rise") else 2)   # the long ones once, the actions twice
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
    path = os.path.join(a.out, "zaahen_all_vs_lol.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
