#!/usr/bin/env python3
"""Rek'Sai's action review from the exported sheet (so it also proves the sheet loads): every hd_ tag at game size (PPU
1.58, as league.dll draws it) next to league_darius's idle, feet on one line.

    python tools/art/review_reksai_actions.py --out DIR [--z 3]

Writes <out>/reksai_actions_review.gif (each action in turn, its name over it, played at its own frame times, Darius
breathing beside her; Burrow runs on into Unburrow and Void Rush into its leap, as the kit plays them) and
<out>/reksai_frames_review.png (every frame of every tag, one row a tag, z x game size).
A frame's centre is its pivot, FEET game px over the ground (rig_reksai.py), for both heroes.
"""
import argparse
import json
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)
CHAMPS = os.path.join(ROOT, "league", "champions")
TAGS = ["idle", "run", "attack", "skill", "skill_q2", "bite", "skill2", "skill2_up", "ult", "ult_hit", "hit", "dead",
        "b_idle", "b_run"]
NAMES = {"idle": "idle", "run": "run", "attack": "attack", "skill": "Q Queen's Wrath", "skill_q2": "Q Prey Seeker",
         "bite": "E Furious Bite (full Fury)", "skill2": "W Burrow (tunnelling)", "skill2_up": "W Unburrow",
         "ult": "R Void Rush (under)", "ult_hit": "R the lunge", "hit": "hit", "dead": "dead",
         "b_idle": "add-on: burrowed idle", "b_run": "add-on: burrowed run"}
FEET = 11
PPU = 1.58
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
    a = ap.parse_args()
    z = a.z
    rk = {t: [(scaled(im, z / PPU), ms) for im, ms in frames("reksai", "hd_" + t)] for t in TAGS}
    dar = [(scaled(im, z), ms) for im, ms in frames("darius", "idle")]
    W, H, ground = 160 * z, 72 * z, 64 * z
    cx_u, cx_d = 104 * z, 28 * z
    out, durs = [], []
    t_d, k_d = 0.0, 0
    for tag in TAGS:
        reps = 2 if tag in ("idle", "run", "b_idle", "b_run") else 1
        for _ in range(reps):
            for im, ms in rk[tag]:
                can = Image.new("RGB", (W, H), BG)
                dim, dms = dar[k_d % len(dar)]
                can.paste(dim, (cx_d - dim.width // 2, ground - FEET * z - dim.height // 2), dim)
                can.paste(im, (cx_u - im.width // 2, ground - FEET * z - im.height // 2), im)
                dr = ImageDraw.Draw(can)
                dr.line([(0, ground), (W, ground)], fill=(70, 84, 70))
                dr.text((6, 4), f"Rek'Sai: {NAMES[tag]}   (Darius idle for size)", fill=(240, 240, 240))
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
    gif = os.path.join(a.out, "reksai_actions_review.gif")
    q[0].save(gif, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=False)
    # every frame
    cell_w = max(im.width for fr in rk.values() for im, _ in fr) + 6
    cell_h = max(im.height for fr in rk.values() for im, _ in fr) + 18
    cols = max(len(fr) for fr in rk.values())
    sheet = Image.new("RGB", (cols * cell_w + 150, len(TAGS) * cell_h), BG)
    dr = ImageDraw.Draw(sheet)
    for r, tag in enumerate(TAGS):
        dr.text((4, r * cell_h + cell_h // 2), NAMES[tag], fill=(240, 240, 240))
        for c, (im, ms) in enumerate(rk[tag]):
            x = 150 + c * cell_w + (cell_w - im.width) // 2
            y = r * cell_h + 14 + (cell_h - 18 - im.height) // 2
            sheet.paste(im, (x, y), im)
            dr.text((150 + c * cell_w + 2, r * cell_h + 2), f"{int(ms)}ms", fill=(220, 220, 220))
    png = os.path.join(a.out, "reksai_frames_review.png")
    sheet.save(png)
    print(gif, len(out), "frames;", png, sheet.size)


if __name__ == "__main__":
    main()
