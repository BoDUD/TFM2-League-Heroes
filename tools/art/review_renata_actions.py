#!/usr/bin/env python3
"""Renata's action review from the exported sheet (so it also proves the sheet loads): every hd_ tag at game size (PPU
ppu_hd.PPU['renata'], as league.dll draws it) next to league_darius's idle, feet on one line.

    python tools/art/review_renata_actions.py --out DIR [--z 3] [--league DIR]

Writes <out>/renata_actions_review.gif (each action in turn, its name over it, played at its own frame times, Darius
breathing beside her) and <out>/renata_frames_review.png (every frame of every tag, one row a tag, z x game size; with
--league, under each row League's own clip at game size - tools/lol/native_pose.py assets/source/renata/poses.json
(the ult with the machine shown), cut to strips s_<tag>.png - for the poses).
A frame's centre is its pivot, FEET game px over the ground (rig_renata.py), for both heroes.
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
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_fling", "skill_w", "ult", "hit", "dead"]
NAMES = {"idle": "idle", "run": "run", "attack": "attack (pistol)", "skill": "E Loyalty Program",
         "skill2": "Q Handshake (thrust)", "skill2_fling": "Q Handshake (the fling)", "skill_w": "W Bailout",
         "ult": "R Hostile Takeover", "hit": "hit", "dead": "dead"}
LEAGUE = {t: t for t in ("run", "attack", "skill", "skill2", "skill2_fling", "skill_w", "ult", "dead")}
FEET = 11
PPU = ppu_hd.PPU["renata"]
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
    yu = {t: [(scaled(im, z / PPU), ms) for im, ms in frames("renata", "hd_" + t)] for t in TAGS}
    dar = [(scaled(im, z), ms) for im, ms in frames("darius", "idle")]
    W, H, ground = 220 * z, 110 * z, 100 * z
    cx_u, cx_d = 130 * z, 28 * z
    out, durs = [], []
    t_d, k_d = 0.0, 0
    for tag in TAGS:
        reps = 2 if tag in ("idle", "run") else 1
        for _ in range(reps):
            for im, ms in yu[tag]:
                can = Image.new("RGB", (W, H), BG)
                dim, dms = dar[k_d % len(dar)]
                can.paste(dim, (cx_d - dim.width // 2, ground - FEET * z - dim.height // 2), dim)
                can.paste(im, (cx_u - im.width // 2, ground - FEET * z - im.height // 2), im)
                dr = ImageDraw.Draw(can)
                dr.line([(0, ground), (W, ground)], fill=(70, 84, 70))
                dr.text((6, 4), f"Renata: {NAMES[tag]}   (Darius idle for size)", fill=(240, 240, 240))
                out.append(can)
                durs.append(int(ms))
                t_d += ms
                while t_d >= dms:
                    t_d -= dms
                    k_d += 1
                    dms = dar[k_d % len(dar)][1]
    os.makedirs(a.out, exist_ok=True)
    # one palette for every frame, from all of them (the machine's colours appear only in the ult)
    mont = Image.new("RGB", (W, H * len(out)))
    for i, im in enumerate(out):
        mont.paste(im, (0, i * H))
    pal = mont.quantize(255, dither=Image.Dither.NONE)
    q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in out]
    gif = os.path.join(a.out, "renata_actions_review.gif")
    q[0].save(gif, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=False)
    # every frame, League's same moment right under it (each tag its own cell width)
    lg = {}
    if a.league:
        for t, name in LEAGUE.items():
            p = os.path.join(a.league, f"s_{name}.png")
            if os.path.isfile(p):
                im = scaled(Image.open(p).convert("RGB"), z / 4.0)
                n = len(yu[t])
                w = im.width // n
                lg[t] = [im.crop((k * w, 0, (k + 1) * w, im.height)) for k in range(n)]
    label_w = 170
    rows = []
    for tag in TAGS:
        cw = max([im.width for im, _ in yu[tag]] + [im.width for im in lg.get(tag, [])]) + 8
        ch = max(im.height for im, _ in yu[tag]) + 18
        lh = max((im.height for im in lg.get(tag, [])), default=0)
        rows.append((tag, cw, ch, lh))
    width = max(label_w + len(yu[t]) * cw for t, cw, _, _ in rows)
    height = sum(ch + (lh + 8 if lh else 0) for _, _, ch, lh in rows)
    sheet = Image.new("RGB", (width, height), BG)
    dr = ImageDraw.Draw(sheet)
    y0 = 0
    for tag, cw, ch, lh in rows:
        dr.text((4, y0 + ch // 2), NAMES[tag], fill=(240, 240, 240))
        for c, (im, ms) in enumerate(yu[tag]):
            x = label_w + c * cw + (cw - im.width) // 2
            sheet.paste(im, (x, y0 + ch - im.height - 2), im)
            dr.text((label_w + c * cw + 2, y0 + 2), f"{c + 1}: {int(ms)}ms", fill=(220, 220, 220))
        if lh:
            dr.text((4, y0 + ch + lh // 2), "League", fill=(255, 230, 150))
            for c, im in enumerate(lg[tag]):
                sheet.paste(im, (label_w + c * cw + (cw - im.width) // 2, y0 + ch + 4))
        y0 += ch + (lh + 8 if lh else 0)
    png = os.path.join(a.out, "renata_frames_review.png")
    sheet.save(png)
    print(gif, len(out), "frames;", png, sheet.size)


if __name__ == "__main__":
    main()
