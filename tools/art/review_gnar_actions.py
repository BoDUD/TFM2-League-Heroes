#!/usr/bin/env python3
"""Gnar's actions (tools/art/rig_gnar.py) beside League's own frames, one GIF of every tag for the user's review (memory
one-gif-review: League left, ours right).

    python tools/art/review_gnar_actions.py --out DIR [--z 4] [--tags attack,m_skill] [--cached] [--sheet]

League's frames: LOL[tag] gives, for each of our frames, the clip and the time it was posed after (Mini = Gnar, Mega =
GnarBig in Gnar.wad.client), rendered by tools/lol/pose_ref.py on Riot's model (they stay in DIR, never committed) -
Mini and Mega's idle at the 3/4 camera (yaw 35), Mega's actions side-on (yaw 75). Ours: rig_gnar's canvases (or, with
--sheet, the exported sheet's hd_ frames: what the game draws after the restyle), z screen px a design square, on the
same ground line. Writes <out>/gnar_<tag>_vs_lol.png (the frames one under the other) and <out>/gnar_all_vs_lol.gif
(every tag in turn, each played twice).
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
import rig_gnar as RG  # noqa: E402

BG = (96, 112, 96)
MINI, MEGA = ("Gnar", 35), ("GnarBig", 75)
MEGA34 = ("GnarBig", 35)


def at(form, clip, *ms):
    return [(form, clip, m) for m in ms]


# per tag, per frame of ours: (champion + camera, League clip, ms)
LOL = {
    "idle": at(MINI, "gnar_idle1", 0, 500, 1000, 1500, 2000, 2500, 3000, 3500),
    "run": at(MINI, "gnar_run1", 0, 200, 400, 600, 800, 1000, 1200, 1400),
    "attack": at(MINI, "gnar_attack1", 0, 250, 450, 650, 900),
    "skill": at(MINI, "gnar_spell1_0", 0, 120, 200, 308, 463, 700, 925),
    "skill2": at(MINI, "gnar_spell3_jump", 0, 70, 133, 267, 400, 600, 800, 933),
    "hit": at(MINI, "gnar_idle1", 0, 0),
    "dead": at(MINI, "gnar_death", 0, 167, 667, 1000, 1300),
    "transform": at(MINI, "gnar_idlerage", 0, 300, 600, 900) + at(MEGA34, "gnarbig_rage_stop", 0, 600),
    "revert": at(MEGA34, "gnarbig_idle1_base", 0, 0) + at(MINI, "gnar_revert", 300, 700, 1100),
    "m_idle": at(MEGA34, "gnarbig_idle1_base", 0, 166, 333, 500, 666, 833, 1000, 1166),
    "m_run": at(MEGA, "gnarbig_run", 0, 125, 250, 375, 500, 625, 750, 875),
    "m_hit": at(MEGA34, "gnarbig_idle1_base", 0, 0),
    "m_dead": at(MEGA, "gnarbig_death", 0, 200) + at(MINI, "gnar_death", 167, 667, 1000, 1300),
    "m_attack": at(MEGA, "gnarbig_attack1", 0, 135, 271, 542, 700, 1000),
    "m_skill": at(MEGA, "gnarbig_spell1", 125, 375, 500, 625, 750, 875),
    "m_skill2": at(MEGA, "gnarbig_spell3", 0, 146, 292, 438, 583, 729, 875, 1021),
    "m_wallop": at(MEGA, "gnarbig_spell2", 150, 300, 450, 600, 750, 1050),
    "ult": at(MEGA, "gnarbig_spell4", 0, 217, 325, 433, 650, 800),
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
                   "--wad", "Gnar", "--hq", "--mirror", "--yaw", str(yaw), "--size", "300",
                   "--width", "1.3" if yaw == 35 else "1.7", "--no-labels", "--bg", ",".join(map(str, BG)),
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
    stem = os.path.join(R.ROOT, "league", "champions", "league_gnar")
    anims = json.load(open(R.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = np.asarray(Image.open(R.lp(stem + "#sheet.png")).convert("RGBA"))
    cx, cy = C.rig.CX, C.rig.GY - R.FEET * RG.PPU
    out = {}
    for tag in tags:
        fr = []
        for f in anims["hd_" + tag]["frames"]:
            d = f["data"]
            im = sheet[int(d["y"]):int(d["y"] + d["h"]), int(d["x"]):int(d["x"] + d["w"])]
            can = C.blank()
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
    C = RG.Canvas()
    acts = RG.frames(C)
    if a.sheet:
        acts = sheet_frames(C, list(acts))
    tags = a.tags.split(",") if a.tags else list(acts)
    every = []
    for tag in tags:
        fr = acts[tag]
        lol = lol_frames(a.lol, tag, a.out, a.cached)
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
        sheet.save(os.path.join(a.out, f"gnar_{tag}_vs_lol.png"))
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
    path = os.path.join(a.out, "gnar_all_vs_lol.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
