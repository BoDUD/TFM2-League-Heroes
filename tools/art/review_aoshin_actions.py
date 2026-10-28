#!/usr/bin/env python3
"""Ao Shin's actions (tools/art/rig_aoshin.py) beside his own TFT clips, one GIF for the user's review.

    python tools/art/review_aoshin_actions.py --out DIR [--lol "D:/Riot Games/League of Legends"] [--z 4] [--tags ..]
                                           [--sheet]

For each tag: his TFT frames named in CLIPS - the very frames the poses were drawn after (pack_aoshin_poses.POSES; his
model from the Riot client's TFTSet7.wad.client, his own map, mirrored to face right; the renders stay in DIR, never
committed), one beside each of ours, next to the rig's frame at z screen px a design square, both at the tag's own
frame times. Writes <out>/aoshin_<tag>_vs_tft.gif and .png, and <out>/aoshin_all_vs_tft.gif: every tag in turn (each
action played twice, the idle once), one picture to review (memory one-gif-review).
--sheet: the exported sheet's hd_ frames (tft/champions/tft_aoshin#sheet.png, what the game draws: after ppu_restyle's
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
import rig_aoshin as A  # noqa: E402
import pack_aoshin_poses as PK  # noqa: E402
from pack_aoshin_picture import Model  # noqa: E402

P = {k: (v[0], v[1]) for k, v in PK.POSES.items()}
IDLE = (PK.DESIGN, PK.YAW)
CLIPS = {"idle": [IDLE, IDLE], "run": [P["run1"], P["run2"], P["run3"], P["run4"]],
         "attack": [P["a_coil"], P["a_lunge"], P["a_back"]], "skill": [P["q_rear"], P["q_breath"], P["a_back"]],
         "skill2": [P["a_back"], P["e_rise"]], "ult": [P["r_call"]] + [P["r_storm"]] * 4, "hit": [IDLE, IDLE],
         "dead": [P["d_hit"], P["d_hit"], P["d_back"], P["d_away"]]}
BG = (96, 112, 96)
GREY = (150, 160, 150)


def tft_cell(m, clip, yaw, size=320):
    """His model in that frame (no grown head: TFT as it is), mirrored to face right, on the review's grey, framed on
    his body."""
    pv = m.posed(clip).copy()
    pv[:, 1] -= pv[:, 1].min()
    tris = body = m.tris
    big = size * 3

    def shot(t, scale):
        return pose_ref.render_hq(pv, t, m.v["uv"], m.tex, -yaw, PK.PITCH, (big, big), scale,
                                  big * 0.75).transpose(Image.FLIP_LEFT_RIGHT)
    s0 = size * 0.5 / pv[:, 1].max()
    x0, y0, x1, y1 = shot(body, s0).getbbox()
    k = size * 0.86 / max(x1 - x0, y1 - y0)
    im = shot(tris, s0 * k)
    x0, y0, x1, y1 = shot(body, s0 * k).getbbox()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    can = Image.new("RGBA", (size, size), GREY + (255,))
    can.alpha_composite(im.crop((round(cx - size / 2), round(cy - size / 2), round(cx + size / 2),
                                 round(cy + size / 2))))
    return can.convert("RGB")


def tft_frames(m, tag, n, cache):
    want = CLIPS[tag]
    out = []
    for i in range(n):
        clip, yaw = want[min(i, len(want) - 1)]
        key = (clip, yaw)
        if key not in cache:
            cache[key] = tft_cell(m, clip, yaw)
        out.append(cache[key])
    return out


def sheet_frames(rig):
    """{tag: [(canvas, ms)]} from the exported sheet's hd_ frames, each centred on the rig's frame centre (CX, the pivot
    FEET x PPU above the ground row) - the frame centre is the unit's position in game."""
    cx, cy = rig.CX, rig.GY - R.FEET * A.PPU
    out = {}
    stem = os.path.join(R.ROOT, "tft", "champions", "tft_aoshin")
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
    m = Model(a.lol)
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
            clip, _ = CLIPS[tag][min(k, len(CLIPS[tag]) - 1)]
            d.text((4, 3), "TFT " + clip, fill=(230, 230, 230))
            d.text((ref_.width + 12, 3), f"ours: {tag}", fill=(230, 230, 230))
            cells.append((cell, ms))
        gif = os.path.join(a.out, f"aoshin_{tag}_vs_tft.gif")
        q = [c.quantize(255, dither=Image.Dither.NONE) for c, _ in cells]
        q[0].save(gif, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in cells], loop=0)
        w, h = cells[0][0].size
        sheet = Image.new("RGB", (w, h * min(len(cells), 12)), (40, 40, 40))
        for i, (c, _) in enumerate(cells[:12]):
            sheet.paste(c, (0, i * h))
        sheet.save(os.path.join(a.out, f"aoshin_{tag}_vs_tft.png"))
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
    path = os.path.join(a.out, "aoshin_all_vs_tft.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in frames], loop=0)
    print(path)


if __name__ == "__main__":
    main()
