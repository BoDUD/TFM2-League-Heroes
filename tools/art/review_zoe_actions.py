#!/usr/bin/env python3
"""Zoe's actions as the game shows them (the sheet's hd_ frames: tools/art/rig_zoe.py -> ppu_restyle.py -> ppu_hd.py)
beside League's own clips, in ONE GIF for the user's review (memory one-gif-review), then the showcase
(tools/art/preview_zoe.py: the stars, the bubble, the portals in a scripted fight).

    python tools/art/review_zoe_actions.py --out DIR [--z 3]

League's frames are rig_zoe.lol_strip's: her clip at the very beat each of our frames stands for (rig_zoe.LOL;
pose_ref.py, Riot's model - local only, never committed), side-on (yaw +15, mirrored) at chibi proportions, her props
left out. Every tag plays twice with its name over it; the hit has no League clip (ours alone). Writes
DIR/zoe_review.gif.
"""
import argparse
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rig_zoe as Z  # noqa: E402

STEM = os.path.join(ROOT, "league", "champions", "league_zoe")
SHOWCASE = os.path.join(ROOT, "docs", "preview", "league_zoe_showcase.gif")
BOX = (-45, -88, 45, 4)                 # squares round the standing point / the row under the soles
BG = (92, 98, 86)


def hd_frames(tag):
    anims = json.load(open(Z.lp(STEM + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = Image.open(Z.lp(STEM + "#sheet.png")).convert("RGBA")
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
    py = (-y0) * z - (frame.height / 2 + 11.5 * Z.PPU) * z
    can.alpha_composite(big, (int(round(px)), int(round(py))))
    return can.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--z", type=int, default=3)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    z = a.z
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
    small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 15)
    w, h = (BOX[2] - BOX[0]) * z, (BOX[3] - BOX[1]) * z
    frames, durs = [], []
    for tag in Z.TAGS:
        hd = hd_frames(tag)
        lol = [im.resize((w, int(im.height * w / im.width))) for im in Z.lol_strip(tag)] if tag in Z.LOL else None
        for rep in range(2):
            for i, (fr, ms) in enumerate(hd):
                im = Image.new("RGB", (2 * w + 12, h + 58), (30, 30, 30))
                if lol:
                    t = lol[i]
                    im.paste(t.crop((0, max(0, t.height - h), w, t.height)), (0, 58 + max(0, h - t.height)))
                else:
                    ImageDraw.Draw(im).text((20, 58 + h // 2), "（英雄联盟没有对应动作）", fill=(170, 170, 170), font=small)
                im.paste(ours(fr, z), (w + 12, 58))
                d = ImageDraw.Draw(im)
                d.text((12, 8), f"{Z.NAMES[tag]}  {i + 1}/{len(hd)}", fill=(255, 240, 160), font=font)
                d.text((12, 34), "英雄联盟", fill=(200, 200, 200), font=small)
                d.text((w + 24, 34), "我们的（游戏里的高清帧）", fill=(200, 200, 200), font=small)
                frames.append(im)
                durs.append(max(20, ms))
    sc = Image.open(Z.lp(SHOWCASE))
    W, H = frames[0].size
    title = Image.new("RGB", (W, H), (30, 30, 30))
    ImageDraw.Draw(title).text((20, H // 2 - 20), "实战演示：特效没动，换上新的动作帧", fill=(255, 240, 160), font=font)
    frames.append(title)
    durs.append(1200)
    k = W / sc.width
    for i in range(sc.n_frames):
        sc.seek(i)
        f = sc.convert("RGB").resize((W, int(round(sc.height * k))), Image.NEAREST)
        im = Image.new("RGB", (W, H), (30, 30, 30))
        im.paste(f, (0, (H - f.height) // 2))
        frames.append(im)
        durs.append(sc.info.get("duration", 60))
    pal = [f.quantize(255, dither=Image.Dither.NONE) for f in frames]
    path = os.path.join(a.out, "zoe_review.gif")
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=durs, loop=0)
    print(path, len(frames), "frames")


if __name__ == "__main__":
    main()
