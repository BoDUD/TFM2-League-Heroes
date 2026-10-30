#!/usr/bin/env python3
"""Shi Oh Yu's actions (tools/art/rig_shiohyu.py) beside his own TFT clips, one GIF for the user's review.

    python tools/art/review_shiohyu_actions.py --out DIR [--lol "D:/Riot Games/League of Legends"] [--z 4] [--tags ..]
                                            [--sheet]

For each tag: his TFT frames named in CLIPS - the very frames the poses were drawn after (pack_shiohyu_poses.POSES; his model from the Riot client's TFTSet7.wad.client,
his own map, mirrored to face right, as TFT has it; the renders stay in DIR, never committed), one beside each of ours,
next to the rig's frame at z screen px a design square, both at the tag's own frame times. Our run is Codex's eight frames
of TFT's run, shown beside it over the same cycle. Writes <out>/shiohyu_<tag>_vs_tft.gif and
.png, and <out>/shiohyu_all_vs_tft.gif: every tag in turn (each action played twice, the idle once), one picture to
review (memory one-gif-review).
--sheet: the exported sheet's hd_ frames (tft/champions/tft_shiohyu#sheet.png, what the game draws: after ppu_restyle's
outline and ppu_hd), each laid on its frame centre, instead of the rig's frames.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lol"))
import ppu_rig as R  # noqa: E402
import pose_ref  # noqa: E402
import rig_shiohyu as A  # noqa: E402
import pack_shiohyu_poses as PK  # noqa: E402

P = {k: (v[0], v[1], k) for k, v in PK.POSES.items()}
IDLE = (PK.DESIGN, PK.YAW, "idle")
CLIPS = {"idle": [IDLE], "run": [P[f"run{k}"] for k in range(1, 9)], "attack": [P["a1_wind"], P["a1_hit"]],
         "attack2": [P["a2_wind"], P["a2_hit"]], "attack3": [P["a3_wind"], P["a3_hit"]], "dash": [P["q_dash"]],
         "skill": [P["q_dash"]] * 4, "skill2": [P["a2_wind"], P["e_slam"]], "ult": [P["a3_wind"], P["r_roar"]],
         "r_wave": [P["a3_wind"], P["r_wave"]], "hit": [IDLE, IDLE], "dead": [P["d_fall"], P["d_fall"], P["d_down"]]}
BG = (96, 112, 96)
GREY = (150, 160, 150)


# the TFT renders all at one scale (his idle IDLE_FILL of a cell's height), the ground on one line, his root on one
# column - framing each render on its own figure made him big with the wings folded and small with them spread
IDLE_FILL = 0.5
CELL = (480, 320)


def model_scale(poser):
    pv = poser.pose(PK.DESIGN)[0]
    return CELL[1] * IDLE_FILL / np.ptp(pv[:, 1])


def tft_cell(poser, clip, yaw, name, scale):
    """His model in that frame (TFT as it is; the attack's arm turned as the pack turned it), mirrored to face right, on
    the review's grey, at `scale`, his lowest point on the cell's ground line, his root on its middle column."""
    m = poser.m
    pv = poser.pose(clip, PK.ARM.get(name))[0].copy()
    pv[:, 1] -= pv[:, 1].min()
    W, H = CELL
    big = 3 * W
    im = pose_ref.render_hq(pv, m.tris, m.v["uv"], m.tex, -yaw, PK.PITCH, (big, big), scale,
                            big * 0.75).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", (W, H), GREY + (255,))
    gx, gy = big / 2, big * 0.75
    can.alpha_composite(im.crop((round(gx - W / 2), round(gy - H * 0.9), round(gx + W / 2), round(gy + H * 0.1))))
    return can.convert("RGB")


def tft_frames(m, tag, n, cache):
    want = CLIPS[tag]
    out = []
    for i in range(n):
        clip, yaw, name = want[min(i, len(want) - 1)]
        key = (clip, yaw, name)
        if key not in cache:
            if "scale" not in cache:
                cache["scale"] = model_scale(m)
            cache[key] = tft_cell(m, clip, yaw, name, cache["scale"])
        out.append(cache[key])
    return out


def sheet_frames(rig):
    """{tag: [(canvas, ms)]} from the exported sheet's hd_ frames, each centred on the rig's frame centre (CX, the pivot
    FEET x PPU above the ground row) - the frame centre is the unit's position in game."""
    cx, cy = rig.CX, rig.GY - R.FEET * A.PPU
    out = {}
    stem = os.path.join(R.ROOT, "tft", "champions", "tft_shiohyu")
    anims = json.load(open(R.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = np.asarray(Image.open(R.lp(stem + "#sheet.png")).convert("RGBA"))
    for tag in A.MS:
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
        out[tag] = fr
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    ap.add_argument("--z", type=int, default=4)
    ap.add_argument("--tags")
    ap.add_argument("--sheet", action="store_true", help="the exported sheet's hd_ frames instead of the rig's")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    C = A.Canvas()
    rig = C.rig
    acts = sheet_frames(rig) if a.sheet else A.frames(C)
    tags = a.tags.split(",") if a.tags else list(acts)
    m = PK.Poser(a.lol)
    cache = {}
    every = []
    allc = np.concatenate([np.stack([c if a.sheet else rig.finish(c) for c, _ in fr]) for fr in acts.values()])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = max(0, ys.min() - 2), max(ys.max() + 3, rig.GY + 3), max(0, xs.min() - 2), xs.max() + 3
    for tag in tags:
        fr = acts[tag]
        tft = tft_frames(m, tag, len(fr), cache)
        cells = []
        for k, ((can, ms), ref) in enumerate(zip(fr, tft)):
            f = (can if a.sheet else rig.finish(can))[y0:y1, x0:x1]
            bg = Image.new("RGBA", (f.shape[1], f.shape[0]), BG + (255,))
            gd = ImageDraw.Draw(bg)            # the ground line and the unit's shadow under his standing point
            gx, gy = rig.CX - x0, rig.GY - y0
            gd.line([(0, gy), (f.shape[1], gy)], fill=(70, 80, 70, 255))
            gd.ellipse([gx - 9, gy - 3, gx + 9, gy + 2], fill=(52, 62, 52, 255))
            bg.alpha_composite(Image.fromarray(f))
            ours = bg.convert("RGB").resize((f.shape[1] * a.z, f.shape[0] * a.z), Image.NEAREST)
            kk = ours.height / ref.height
            ref_ = ref.resize((round(ref.width * kk), ours.height), Image.LANCZOS)
            cell = Image.new("RGB", (ref_.width + ours.width + 8, ours.height + 18), (40, 40, 40))
            cell.paste(ref_, (0, 18))
            cell.paste(ours, (ref_.width + 8, 18))
            d = ImageDraw.Draw(cell)
            clip, _, _ = CLIPS[tag][min(k, len(CLIPS[tag]) - 1)]
            d.text((4, 3), "TFT " + clip, fill=(230, 230, 230))
            d.text((ref_.width + 12, 3), f"ours: {tag}", fill=(230, 230, 230))
            cells.append((cell, ms))
        gif = os.path.join(a.out, f"shiohyu_{tag}_vs_tft.gif")
        q = [c.quantize(255, dither=Image.Dither.NONE) for c, _ in cells]
        q[0].save(gif, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in cells], loop=0)
        w, h = cells[0][0].size
        sheet = Image.new("RGB", (w, h * min(len(cells), 12)), (40, 40, 40))
        for i, (c, _) in enumerate(cells[:12]):
            sheet.paste(c, (0, i * h))
        sheet.save(os.path.join(a.out, f"shiohyu_{tag}_vs_tft.png"))
        every += cells * (1 if tag == "idle" else 2)       # the idle once, the actions twice
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
    path = os.path.join(a.out, "shiohyu_all_vs_tft.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
