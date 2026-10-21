#!/usr/bin/env python3
"""Orianna's actions as the game shows them (the sheet's hd_ frames: tools/art/rig_orianna.py -> ppu_restyle.py ->
ppu_hd.py) beside League's own clips, in ONE GIF for the user's review (memory one-gif-review), then the showcase
(tools/art/preview_orianna.py: the Ball and the effects in a scripted fight).

    python tools/art/review_orianna_actions.py --out DIR [--z 3]

League's frames are the strips pack's skeletons (tools/art/pack_orianna_strips.py --render: League's clips at chibi
proportions on the design's grid, Riot's model - local only, never committed), one per action frame. Every tag plays
twice, its name over it; idle and hit have no League clip (ours alone). Writes DIR/orianna_review.gif.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rig_orianna as R  # noqa: E402

STEM = os.path.join(ROOT, "league", "champions", "league_orianna")
SHOWCASE = os.path.join(ROOT, "docs", "preview", "league_orianna_showcase.gif")
NAMES = {"idle": "待机", "run": "跑步", "attack": "普攻", "skill": "Q 指令：攻击", "skill_w": "W 指令：杂音",
         "skill_e": "E 指令：防卫", "ult": "R 指令：冲击波", "hit": "受击", "dead": "死亡"}
BOX = (-58, -112, 58, 6)            # squares round the standing point / the row under the soles
BG = (92, 98, 86)


def hd_frames(tag):
    anims = json.load(open(R.lp(STEM + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = Image.open(R.lp(STEM + "#sheet.png")).convert("RGBA")
    out = []
    for f in anims["hd_" + tag]["frames"]:
        d = f["data"]
        out.append((sheet.crop((int(d["x"]), int(d["y"]), int(d["x"] + d["w"]), int(d["y"] + d["h"]))),
                    int(round(f["duration"] * 1000))))
    return out


def ours(frame, z):
    """An hd frame (its pivot at its middle, the soles' bottom edge FEET x PPU under it) on the review box."""
    x0, y0, x1, y1 = BOX
    can = Image.new("RGBA", ((x1 - x0) * z, (y1 - y0) * z), (*BG, 255))
    big = frame.resize((frame.width * z, frame.height * z), Image.NEAREST)
    px = (-x0) * z - frame.width / 2 * z
    py = (-y0) * z - (frame.height / 2 + R.FEET * R.PPU) * z
    can.alpha_composite(big, (int(round(px)), int(round(py))))
    return can.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--z", type=int, default=3)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    z = a.z
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
    small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    frames, durs = [], []
    w = (BOX[2] - BOX[0]) * z
    h = (BOX[3] - BOX[1]) * z
    W, H = 2 * w + 12, h + 44
    for tag in R.ORDER:
        hd = hd_frames(tag)
        lol = tag not in ("idle", "hit")
        for rep in range(2):
            for i, (fr, ms) in enumerate(hd):
                im = Image.new("RGB", (W, H), (30, 30, 30))
                if lol:
                    im.paste(R.lol_tile(tag, i, z, BOX), (0, 44))
                else:
                    ImageDraw.Draw(im).text((20, 44 + h // 2), "（英雄联盟没有对应动作）", fill=(170, 170, 170), font=small)
                im.paste(ours(fr, z), (w + 12, 44))
                d = ImageDraw.Draw(im)
                d.text((12, 8), f"{NAMES[tag]}  {i + 1}/{len(hd)}", fill=(255, 240, 160), font=font)
                d.text((w + 24, 12), "我们的（游戏里的高清帧）", fill=(200, 200, 200), font=small)
                d.text((w - 130, 12), "英雄联盟", fill=(200, 200, 200), font=small)
                frames.append(im)
                durs.append(max(20, ms))
    # the showcase, scaled to the same width, after a title card
    sc = Image.open(R.lp(SHOWCASE))
    k = W / sc.width
    title = Image.new("RGB", (W, H), (30, 30, 30))
    ImageDraw.Draw(title).text((20, H // 2 - 20), "实战演示：新的球和特效", fill=(255, 240, 160), font=font)
    frames.append(title)
    durs.append(1200)
    for i in range(sc.n_frames):
        sc.seek(i)
        f = sc.convert("RGB").resize((W, int(round(sc.height * k))), Image.NEAREST)
        im = Image.new("RGB", (W, max(H, f.height)), (30, 30, 30))
        im.paste(f, (0, (im.height - f.height) // 2))
        frames.append(im.crop((0, 0, W, H)) if im.height > H else im)
        durs.append(sc.info.get("duration", 60))
    pal = [f.quantize(255, dither=Image.Dither.NONE) for f in frames]
    path = os.path.join(a.out, "orianna_review.gif")
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=durs, loop=0)
    print(path, len(frames), "frames")


if __name__ == "__main__":
    main()
