#!/usr/bin/env python3
"""Yunara's action review from the exported sheet (so it also proves the sheet loads): every hd_ tag at game size (PPU
ppu_hd.PPU['yunara'], as league.dll draws it) next to league_darius's idle, feet on one line.

    python tools/art/review_yunara_actions.py --out DIR [--z 3] [--league DIR]

Writes <out>/yunara_actions_review.gif (each action in turn, its name over it, played at its own frame times, Darius
breathing beside her) and <out>/yunara_frames_review.png (every frame of every tag, one row a tag, z x game size; with
--league, under each row League's own clip at game size - tools/lol/native_pose.py assets/source/yunara/poses.json,
cropped to strips s_<tag>.png - for the poses).
A frame's centre is its pivot, FEET game px over the ground (rig_yunara.py), for both heroes.
"""
import argparse
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_hd  # noqa: E402
ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)
CHAMPS = os.path.join(ROOT, "league", "champions")
TAGS = ["idle", "run", "attack", "skill", "skill_r", "skill2", "skill2_r", "ult", "hit", "dead", "r_idle", "r_run"]
NAMES = {"idle": "idle", "run": "run", "attack": "attack (Q on: the same)", "skill": "W Arc of Judgment (bead)",
         "skill_r": "R-W Arc of Ruin (laser)", "skill2": "E Kanmei's Steps", "skill2_r": "R-E Untouchable Shadow (flip)",
         "ult": "R Transcend One's Self", "hit": "hit", "dead": "dead", "r_idle": "add-on: R form idle",
         "r_run": "add-on: R form run"}
LEAGUE = {"run": "run", "attack": "attack", "skill": "skill", "skill_r": "skill_r", "skill2": "skill2",
          "skill2_r": "skill2_r", "ult": "ult", "dead": "dead"}
FEET = 11
PPU = ppu_hd.PPU["yunara"]
BG = (96, 112, 96)


def frames(hero, tag):
    stem = os.path.join(CHAMPS, f"league_{hero}")
    anims = json.load(open(stem + "#anim.fanim", encoding="utf-8-sig"))["anims"]
    sheet = Image.open(stem + "#sheet.png").convert("RGBA")
    out = []
    for f in anims[tag]["frames"]:
        d = f["data"]
        out.append((sheet.crop((int(d["x"]), int(d["y"]), int(d["x"] + d["w"]), int(d["y"] + d["h"]))),
                    float(f["duration"]) * 1000))   # the fanim keeps seconds
    return out


def scaled(im, k):
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--z", type=int, default=3)
    ap.add_argument("--league", help="the native_pose strips (s_<tag>.png at 4 screen px a game px) to show under ours")
    a = ap.parse_args()
    z = a.z
    yu = {t: [(scaled(im, z / PPU), ms) for im, ms in frames("yunara", "hd_" + t)] for t in TAGS}
    dar = [(scaled(im, z), ms) for im, ms in frames("darius", "idle")]
    W, H, ground = 190 * z, 92 * z, 82 * z
    cx_u, cx_d = 120 * z, 28 * z
    out, durs = [], []
    t_d, k_d = 0.0, 0
    for tag in TAGS:
        reps = 2 if tag in ("idle", "run", "r_idle", "r_run") else 1
        for _ in range(reps):
            for im, ms in yu[tag]:
                can = Image.new("RGB", (W, H), BG)
                dim, dms = dar[k_d % len(dar)]
                can.paste(dim, (cx_d - dim.width // 2, ground - FEET * z - dim.height // 2), dim)
                can.paste(im, (cx_u - im.width // 2, ground - FEET * z - im.height // 2), im)
                dr = ImageDraw.Draw(can)
                dr.line([(0, ground), (W, ground)], fill=(70, 84, 70))
                dr.text((6, 4), f"Yunara: {NAMES[tag]}   (Darius idle for size)", fill=(240, 240, 240))
                out.append(can)
                durs.append(int(ms))
                t_d += ms
                while t_d >= dms:
                    t_d -= dms
                    k_d += 1
                    dms = dar[k_d % len(dar)][1]
    os.makedirs(a.out, exist_ok=True)
    pal = out[0].quantize(255, dither=Image.Dither.NONE)
    q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in out]
    gif = os.path.join(a.out, "yunara_actions_review.gif")
    q[0].save(gif, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=False)
    # every frame (and League's under it)
    lg = {}
    if a.league:
        for t, name in LEAGUE.items():
            p = os.path.join(a.league, f"s_{name}.png")
            if os.path.isfile(p):
                im = Image.open(p).convert("RGB")
                lg[t] = scaled(im, z / 4.0)
    cell_w = max(im.width for fr in yu.values() for im, _ in fr) + 6
    cell_h = max(im.height for fr in yu.values() for im, _ in fr) + 18
    cols = max(len(fr) for fr in yu.values())
    rows_h = [cell_h + (lg[t].height + 6 if t in lg else 0) for t in TAGS]
    width = max(cols * cell_w + 170, max((im.width + 176 for im in lg.values()), default=0))
    sheet = Image.new("RGB", (width, sum(rows_h)), BG)
    dr = ImageDraw.Draw(sheet)
    y0 = 0
    for r, tag in enumerate(TAGS):
        dr.text((4, y0 + cell_h // 2), NAMES[tag], fill=(240, 240, 240))
        for c, (im, ms) in enumerate(yu[tag]):
            x = 170 + c * cell_w + (cell_w - im.width) // 2
            y = y0 + 14 + (cell_h - 18 - im.height) // 2
            sheet.paste(im, (x, y), im)
            dr.text((170 + c * cell_w + 2, y0 + 2), f"{int(ms)}ms", fill=(220, 220, 220))
        if tag in lg:
            dr.text((4, y0 + cell_h + lg[tag].height // 2), "League", fill=(255, 230, 150))
            sheet.paste(lg[tag], (170, y0 + cell_h))
        y0 += rows_h[r]
    png = os.path.join(a.out, "yunara_frames_review.png")
    sheet.save(png)
    print(gif, len(out), "frames;", png, sheet.size)


if __name__ == "__main__":
    main()
