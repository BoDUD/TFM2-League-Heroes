#!/usr/bin/env python3
"""Swain's action review straight from tools/art/rig_swain.py's frames, at game size (PPU 1.5: a design square 1 / 1.5
game px, z screen px a game px) next to league_darius's idle, feet on one line.

    python tools/art/review_swain_actions.py --out DIR [--z 3]

Writes <out>/swain_actions_review.gif (each action in turn, its name over it, at its own frame times; the demon's tags
with the wings' aura behind him, as the game draws them while R lasts - and R's own cast from its 4th frame, when the
kit puts the aura on) and <out>/swain_frames_review.png (every frame of every tag, one row a tag).
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
import rig_swain as S  # noqa: E402

ORDER = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead", "b_idle", "b_run", "r_attack", "r_skill",
         "r_skill2", "r_flare", "b_hit"]
NAMES = {"idle": "idle", "run": "run", "attack": "attack (raven bolt from the demon hand)",
         "skill": "Q Death's Hand", "skill2": "E Nevermove", "ult": "R Demonic Ascension (wings from frame 4)",
         "hit": "hit", "dead": "dead", "b_idle": "R form: idle (add-on body; main pack: idle + wings)",
         "b_run": "R form: run (add-on body)", "r_attack": "R form: attack", "r_skill": "R form: Q",
         "r_skill2": "R form: E", "r_flare": "R form: Demonflare", "b_hit": "R form: hit"}
AURA_MS = 140
FLAP = [0, 0, -1, -1, -1, -1, 0, 0]
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
    sq = z / S.PPU                                     # screen px a design square
    ps = S.Poser()
    acts = S.frames(ps)
    rig = ps.rig
    aura = ps.aura                                     # design-sized + P padding
    aura_frames = []
    for dy in FLAP:
        can = rig.canvas()
        aura_frames.append(R.compose(rig, [(aura, dict(dy=dy))]))

    def screen(can):
        """A rig canvas at z: its ground row and standing column kept as the reference."""
        im = Image.fromarray(can)
        return im.resize((round(im.width * sq), round(im.height * sq)), Image.NEAREST)

    W, H = 190 * z, 80 * z
    ground = 70 * z
    cx_s, cx_d = 120 * z, 26 * z
    dar = darius(z)
    out, durs = [], []
    t_all = 0.0
    rows = {}
    for tag in ORDER:
        demon = tag.startswith(("b_", "r_"))
        reps = 2 if tag in ("idle", "run", "b_idle", "b_run") else 1
        rows[tag] = []
        for _ in range(reps):
            for k, (c, ms) in enumerate(acts[tag]):
                body = rig.finish(c)
                lay = np.zeros_like(body)
                if demon or (tag == "ult" and k >= 3):
                    w = aura_frames[int(t_all // AURA_MS) % len(FLAP)]
                    lay = w.copy()
                m = body[..., 3] > 0
                lay[m] = body[m]
                im = screen(lay)
                if len(rows[tag]) < len(acts[tag]):
                    rows[tag].append((im, ms))
                can = Image.new("RGB", (W, H), BG)
                dim, _ = dar[int(t_all // dar[0][1]) % len(dar)]
                can.paste(dim, (cx_d - dim.width // 2, round(ground - 11.5 * z - dim.height / 2)), dim)
                x0 = round(cx_s - rig.CX * sq)
                y0 = round(ground - rig.GY * sq)
                can.paste(im, (x0, y0), im)
                dr = ImageDraw.Draw(can)
                dr.line([(0, ground), (W, ground)], fill=(70, 84, 70))
                dr.text((6, 4), f"Swain: {NAMES[tag]}   (Darius idle for size)", fill=(240, 240, 240))
                out.append(can)
                durs.append(int(ms))
                t_all += ms
    os.makedirs(a.out, exist_ok=True)
    src = Image.new("RGB", (W, H * min(len(out), 12)))
    for i, im in enumerate(out[::max(1, len(out) // 12)][:12]):
        src.paste(im, (0, i * H))
    pal = src.quantize(255, dither=Image.Dither.NONE)
    q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in out]
    gif = os.path.join(a.out, "swain_actions_review.gif")
    q[0].save(gif, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=False)
    # every frame of every tag, cropped to what any frame of the whole set uses
    allims = [im for fr in rows.values() for im, _ in fr]
    boxes = [im.getbbox() for im in allims]
    bx0 = min(b[0] for b in boxes)
    by0 = min(b[1] for b in boxes)
    bx1 = max(b[2] for b in boxes)
    by1 = max(b[3] for b in boxes)
    cw, ch = bx1 - bx0 + 8, by1 - by0 + 18
    cols = max(len(fr) for fr in rows.values())
    sheet = Image.new("RGB", (cols * cw + 260, len(ORDER) * ch), BG)
    dr = ImageDraw.Draw(sheet)
    for r, tag in enumerate(ORDER):
        dr.text((4, r * ch + ch // 2), NAMES[tag][:40], fill=(240, 240, 240))
        for c, (im, ms) in enumerate(rows[tag]):
            sheet.paste(im.crop((bx0, by0, bx1, by1)), (260 + c * cw, r * ch + 14), im.crop((bx0, by0, bx1, by1)))
            dr.text((260 + c * cw + 2, r * ch + 2), f"{int(ms)}ms", fill=(220, 220, 220))
    png = os.path.join(a.out, "swain_frames_review.png")
    sheet.save(png)
    print(gif, len(out), "frames;", png, sheet.size)


if __name__ == "__main__":
    main()
