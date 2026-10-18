#!/usr/bin/env python3
"""Maokai's action review straight from tools/art/rig_maokai.py's frames, at game size (PPU 1.5: a design square 1 / 1.5
game px, z screen px a game px) next to league_darius's idle, feet on one line.

    python tools/art/review_maokai_actions.py --out DIR [--z 3]

Writes <out>/maokai_actions_review.gif (each action in turn, its name over it, at its own frame times) and
<out>/maokai_frames_review.png (every frame of every tag, one row a tag).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_maokai as N  # noqa: E402

ORDER = ["idle", "run", "attack", "skill", "skill2", "skill2_land", "skill_e", "ult", "hit", "dead"]
NAMES = {"idle": "idle", "run": "run", "attack": "attack (the huge arm)", "skill": "Q Bramble Smash",
         "skill2": "W Twisted Advance (down)", "skill2_land": "W Twisted Advance (up at the target)",
         "skill_e": "E Sapling Toss", "ult": "R Nature's Grasp", "hit": "hit", "dead": "dead"}
BG = (96, 112, 96)


def darius(z):
    stem = os.path.join(R.MOD, "champions", "league_darius")
    anims = json.load(open(R.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = Image.open(R.lp(stem + "#sheet.png")).convert("RGBA")
    out = []
    for f in anims["idle"]["frames"]:
        d = f["data"]
        im = sheet.crop((int(d["x"]), int(d["y"]), int(d["x"] + d["w"]), int(d["y"] + d["h"])))
        out.append((im.resize((im.width * z, im.height * z), Image.NEAREST), float(f["duration"]) * 1000))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--z", type=int, default=3)
    a = ap.parse_args()
    z = a.z
    sq = z / N.PPU                                     # screen px a design square
    fa = N.form()
    acts = N.frames(fa)
    rig = fa.rig
    fin = {tag: [(rig.finish(c), ms) for c, ms in fr] for tag, fr in acts.items()}
    allc = np.stack([c for fr in fin.values() for c, _ in fr])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    top, left, right = (rig.GY - ys.min()) * sq, (rig.CX - xs.min()) * sq, (xs.max() + 1 - rig.CX) * sq

    def screen(can):
        im = Image.fromarray(can)
        return im.resize((round(im.width * sq), round(im.height * sq)), Image.NEAREST)

    cx_d = 26 * z
    cx_s = round(60 * z + left)
    W = round(cx_s + right + 8 * z)
    ground = round(top + 14 * z)
    H = ground + 6 * z
    dar = darius(z)
    out, durs = [], []
    t_all = 0.0
    rows = {}
    for tag in ORDER:
        reps = 2 if tag in ("idle", "run") else 1
        rows[tag] = []
        for _ in range(reps):
            for c, ms in fin[tag]:
                im = screen(c)
                if len(rows[tag]) < len(fin[tag]):
                    rows[tag].append((im, ms))
                can = Image.new("RGB", (W, H), BG)
                dim, _ = dar[int(t_all // dar[0][1]) % len(dar)]
                can.paste(dim, (cx_d - dim.width // 2, round(ground - 11.5 * z - dim.height / 2)), dim)
                x0 = round(cx_s - rig.CX * sq)
                y0 = round(ground - rig.GY * sq)
                can.paste(im, (x0, y0), im)
                dr = ImageDraw.Draw(can)
                dr.line([(0, ground), (W, ground)], fill=(70, 84, 70))
                dr.text((6, 4), f"Maokai: {NAMES[tag]}   (Darius idle for size)", fill=(240, 240, 240))
                out.append(can)
                durs.append(int(ms))
                t_all += ms
    os.makedirs(a.out, exist_ok=True)
    src = Image.new("RGB", (W, H * min(len(out), 12)))
    for i, im in enumerate(out[::max(1, len(out) // 12)][:12]):
        src.paste(im, (0, i * H))
    pal = src.quantize(255, dither=Image.Dither.NONE)
    q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in out]
    gif = os.path.join(a.out, "maokai_actions_review.gif")
    q[0].save(gif, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=False)
    allims = [im for fr in rows.values() for im, _ in fr]
    boxes = [im.getbbox() for im in allims]
    bx0 = min(b[0] for b in boxes)
    bx1 = max(b[2] for b in boxes)
    by1 = max(b[3] for b in boxes)
    cw = bx1 - bx0 + 8
    tops = {tag: min(im.getbbox()[1] for im, _ in rows[tag]) for tag in ORDER}     # each row as tall as it needs
    hs = {tag: by1 - tops[tag] + 18 for tag in ORDER}
    cols = max(len(fr) for fr in rows.values())
    sheet = Image.new("RGB", (cols * cw + 260, sum(hs.values())), BG)
    dr = ImageDraw.Draw(sheet)
    y = 0
    for tag in ORDER:
        dr.text((4, y + hs[tag] // 2), NAMES[tag][:40], fill=(240, 240, 240))
        for c, (im, ms) in enumerate(rows[tag]):
            crop = im.crop((bx0, tops[tag], bx1, by1))
            sheet.paste(crop, (260 + c * cw, y + 14), crop)
            dr.text((260 + c * cw + 2, y + 2), f"{int(ms)}ms", fill=(220, 220, 220))
        y += hs[tag]
    png = os.path.join(a.out, "maokai_frames_review.png")
    sheet.save(png)
    print(gif, len(out), "frames;", png, sheet.size)


if __name__ == "__main__":
    main()
