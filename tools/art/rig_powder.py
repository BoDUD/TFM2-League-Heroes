#!/usr/bin/env python3
"""tft_powder's action frames from the approved pieces: the idle design (hd/idle.png, A-2) and the poses Codex drew on
skeletons (hd/poses/*.png, read back by design_powder_poses.py with the one clean head) - every frame a whole picture
moved by whole squares, quarter turns or a white flash, nothing redrawn.

    python tools/art/rig_powder.py --review DIR [--lol D:/WeGameApps/lol]   # one GIF: every tag, TFT's clip left
    python tools/art/rig_powder.py --frames DIR                            # every tag's frames at 8x (self-review)

Tags (the kit's actions, tools/kit/build_powder.py): idle (the idle design breathing a row), run (the 8 run frames, the
head held on one column), attack (the firecracker: wind, throw), skill (Monkey Bomb: crouch, the underhand toss), skill2
(Run, Powder!: the slam at her feet, a hop up in place - the game's MoveBack carries her back), ult (the Hex Crystal
Bomb: a long wind-up, the throw), hit (knocked back, the first frame flashed white), dead (8 frames: knocked back, a
quarter turn backwards in the air, down on her back, a bounce, still).
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "powder", "hd")
W, H, GROUND, STAND = 72, 72, 66, 36     # the canvas, the soles' row + 1, the standing column
IDLE_LEG_ROW = 40                        # the idle design's legs: rows from here down stay while the body breathes


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(name):
    return np.asarray(Image.open(lp(os.path.join(HD, name))).convert("RGBA")).copy()


def sole_mid(d, rows=2):
    op = d[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    xs = np.nonzero(op[ys.max() - rows + 1:ys.max() + 1].any(0))[0]
    return (xs.min() + xs.max() + 1) / 2, ys.max() + 1


def head_col(d, head):
    """The column of the clean head's left edge in a pose (it was pasted unchanged: an exact match of its rows)."""
    core = head[:21]
    m = core[..., 3] > 0
    hh, hw = core.shape[:2]
    best = (-1, 0, 0)
    pad = np.zeros((d.shape[0] + 2 * hh, d.shape[1] + 2 * hw, 4), np.uint8)
    pad[hh:hh + d.shape[0], hw:hw + d.shape[1]] = d
    for y in range(0, pad.shape[0] - hh + 1):
        for x in range(0, pad.shape[1] - hw + 1):
            n = int((pad[y:y + hh, x:x + hw][m] == core[m]).all(-1).sum())
            if n > best[0]:
                best = (n, x - hw, y - hh)
    if best[0] < 0.9 * m.sum():                  # a few crumbs may have gone with the head swap's cleanup
        raise SystemExit(f"head not found ({best[0]} of {int(m.sum())})")
    return best[1], best[2]


def place(d, x, bottom):
    """d on a fresh canvas with its column x at STAND... (x = the picture's anchor column), its last row at bottom."""
    can = np.zeros((H, W, 4), np.uint8)
    ox = int(round(STAND - x))
    oy = int(bottom - d.shape[0])
    ys, xs = np.nonzero(d[..., 3])
    ok = (ys + oy >= 0) & (ys + oy < H) & (xs + ox >= 0) & (xs + ox < W)
    can[ys[ok] + oy, xs[ok] + ox] = d[ys[ok], xs[ok]]
    return can


def on_feet(d, up=0, dx=0):
    x, _ = sole_mid(d)
    return place(d, x - dx, GROUND - up)


def flash(can, k=0.55):
    out = can.copy()
    op = out[..., 3] > 0
    out[op, :3] = (out[op, :3] * (1 - k) + 255 * k).astype(np.uint8)
    return out


def lying(d, up=0, dx=0):
    """Turned a quarter backwards (the head to the left), on the ground."""
    r = np.rot90(d, 1).copy()
    return place(r, r.shape[1] / 2 - dx, GROUND - up)


# ms per frame; the kit's ticks come from these (the release frame of each throw)
MS = {"idle": [150] * 8, "run": [100] * 8,
      "attack": [90, 90, 80, 120], "skill": [100, 100, 80, 100, 100], "skill2": [70, 80, 80, 80, 90],
      "ult": [100, 100, 100, 80, 120, 120], "hit": [100, 100], "dead": [100, 110, 120, 150, 60, 60, 100, 500]}


def frames():
    idle = load("idle.png")
    P = {n: load(f"poses/{n}.png") for n in ("wind", "throw", "crouch", "toss", "slam", "hop", "hit")}
    runs = [load(f"poses/run{k}.png") for k in range(1, 9)]
    head = load("head.png")
    out = {}

    def breathe(c):
        legs, top = idle.copy(), idle.copy()
        legs[:IDLE_LEG_ROW] = 0
        top[IDLE_LEG_ROW:] = 0
        can = on_feet(legs)
        x, _ = sole_mid(idle)
        body = place(top, x, GROUND - (idle.shape[0] - IDLE_LEG_ROW) + c + (idle.shape[0] - IDLE_LEG_ROW))
        m = body[..., 3] > 0
        can[m] = body[m]
        return can
    out["idle"] = [breathe(c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    # the run: the head on one column (the legs swing under it), the soles on the ground
    hx = [head_col(r, head)[0] for r in runs]
    out["run"] = [place(r, x + 12, GROUND) for r, x in zip(runs, hx)]
    out["attack"] = [on_feet(P["wind"]), on_feet(P["wind"]), on_feet(P["throw"]), on_feet(P["throw"])]
    out["skill"] = [on_feet(P["crouch"]), on_feet(P["crouch"]), on_feet(P["toss"]), on_feet(P["toss"]),
                    on_feet(P["toss"])]
    out["skill2"] = [on_feet(P["slam"]), on_feet(P["slam"]), on_feet(P["hop"], up=5), on_feet(P["hop"], up=3),
                     on_feet(P["crouch"])]
    out["ult"] = [on_feet(P["wind"]), on_feet(P["wind"]), on_feet(P["wind"]), on_feet(P["throw"]),
                  on_feet(P["throw"]), on_feet(P["throw"])]
    out["hit"] = [flash(on_feet(P["hit"], dx=-1)), on_feet(P["hit"])]
    out["dead"] = [on_feet(P["hit"], dx=-1), on_feet(P["hit"], dx=-2), lying(P["hit"], up=6, dx=-4), lying(P["hit"], dx=-6),
                   lying(P["hit"], up=2, dx=-6), lying(P["hit"], dx=-6), lying(P["hit"], dx=-6), lying(P["hit"], dx=-6)]
    for tag, cans in out.items():
        if len(cans) != len(MS[tag]):
            sys.exit(f"{tag}: {len(cans)} frames for {len(MS[tag])}")
    return {tag: list(zip(cans, MS[tag])) for tag, cans in out.items()}


# tag -> (TFT's clip, from s, to s) for the review
CLIPS = {"idle": ("Idle", 0, 2.6), "run": ("Run", 0, 0.8), "attack": ("attack_1", 0, 0.7),
         "skill": ("attack_2", 0, 0.7), "skill2": ("attack_1", 0.4, 1.0), "ult": ("Spell", 0, 1.2),
         "hit": ("Death", 0, 0.1), "dead": ("Death", 0, 1.0)}
BG = (96, 112, 96)


def tft_frames(lol, tag, n, out):
    clip, t0, t1 = CLIPS[tag]
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "TFT13_Blue",
           "--wad-file", "TFTSet13.wad.client", "--hide-submesh", "Bomb", "--hide-submesh", "Monkey", "--anim", clip,
           "--frames", str(n), "--t0", str(t0), "--t1", str(t1), "--mirror", "--yaw", "70", "--size", "300",
           "--no-labels", "--out", out]
    subprocess.run(cmd, check=True, capture_output=True)
    strip = Image.open(os.path.join(out, clip + ".png")).convert("RGB")
    w = strip.width // n
    return [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(n)]


def review(acts, out, lol, z=5):
    os.makedirs(out, exist_ok=True)
    every = []
    allc = np.stack([c for fr in acts.values() for c, _ in fr])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3
    for tag, fr in acts.items():
        refs = tft_frames(lol, tag, len(fr), out)
        for (can, ms), ref in zip(fr, refs):
            f = can[y0:y1, x0:x1]
            bg = Image.new("RGBA", (f.shape[1], f.shape[0]), BG + (255,))
            bg.alpha_composite(Image.fromarray(f))
            ours = bg.convert("RGB").resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST)
            k = ours.height / ref.height
            ref = ref.resize((round(ref.width * k), ours.height), Image.LANCZOS)
            cell = Image.new("RGB", (ref.width + ours.width + 8, ours.height + 18), (40, 40, 40))
            cell.paste(ref, (0, 18))
            cell.paste(ours, (ref.width + 8, 18))
            d = ImageDraw.Draw(cell)
            d.text((4, 3), f"TFT {CLIPS[tag][0]}", fill=(230, 230, 230))
            d.text((ref.width + 12, 3), f"ours: {tag}", fill=(230, 230, 230))
            every.append((cell, ms))
        every += every[-len(fr):]          # each tag played twice
    Wm = max(c.width for c, _ in every)
    Hm = max(c.height for c, _ in every)
    fr_all = []
    for c, ms in every:
        full = Image.new("RGB", (Wm, Hm), (40, 40, 40))
        full.paste(c, (0, 0))
        fr_all.append((full, ms))
    pal = Image.new("RGB", (Wm, Hm * 4))
    for i, (c, _) in enumerate(fr_all[::max(1, len(fr_all) // 4)][:4]):
        pal.paste(c, (0, i * Hm))
    pal = pal.quantize(255, dither=Image.Dither.NONE)
    q = [c.quantize(palette=pal, dither=Image.Dither.NONE) for c, _ in fr_all]
    path = os.path.join(out, "powder_all_vs_tft.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in fr_all], loop=0)
    print(path)


def dump(acts, out, z=8):
    os.makedirs(out, exist_ok=True)
    for tag, fr in acts.items():
        sheet = Image.new("RGBA", (len(fr) * (W * z + 8), H * z), (200, 205, 195, 255))
        for i, (c, _) in enumerate(fr):
            sheet.alpha_composite(Image.fromarray(np.repeat(np.repeat(c, z, 0), z, 1)), (i * (W * z + 8), 0))
        sheet.convert("RGB").save(os.path.join(out, f"powder_{tag}_8x.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--frames")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    acts = frames()
    if a.frames:
        dump(acts, a.frames)
    if a.review:
        review(acts, a.review, a.lol)


if __name__ == "__main__":
    main()
