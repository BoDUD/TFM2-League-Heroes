#!/usr/bin/env python3
"""Heimerdinger's two turrets seen from the side, muzzle to the right, dense at PPU_SIDE (the user, 2026-10-21:
「炮台应该对准敌人吧？」 -> 「炮台改成侧面朝敌人 ... 附加包放炮台时朝向敌人那边；主包不知道敌人方向，保留正面朝镜头」 ->
「你直接调啊」 -> 「灵活利用PPU 炮也可以调的清晰」: made here from League's models, no Codex).

    python tools/art/design_heimerdinger_side_turrets.py [--yaw 70] [--review DIR]
        # writes hd/turret_side.png, hd/apex_side.png (PPU_SIDE squares a game pixel) and hd/side_turrets.json

League's models (HeimerTYellow, HeimerTBlue) rendered at yaw `--yaw` (tools/lol/pose_ref.py, --mirror as every
Heimerdinger render: facing right) on black and on white: the two give each pixel's alpha and colour (difference
matting, no keyed fringe). The figure goes to the user's game sizes (the Q turret 20 game px top to feet, the apex 30)
at PPU_SIDE squares a game pixel - league_zeri's density, 3: the hero's own 1.5 left the side view a smear at 30 rows
(the legs a line, the parts run together; a hand-placed drawing was no better) - by an area average, then flat pixel
art the way the PPU heroes are (pixel_down.crisp: one 16-colour palette, majority passes, a dark line on the darker
side of every edge between parts far apart in brightness) and the ink outline round it (strips.complete_outline).
The muzzle - the red ring's middle at the barrel's right end - goes to hd/side_turrets.json (dense px from the
picture's top left) for the turret lives (import_heimerdinger_fx.py) and the add-on's shots.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as V  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402

LOL = r"D:\WeGameApps\lol"
WORK = "C:/t/hd_work/side"
HD = os.path.join(ROOT, "assets", "source", "heimerdinger", "hd")
PPU_SIDE = 3.0
TRANSFER = 0.45         # how far the colours go toward the front design's (toward())
INK = (11, 3, 13)
# name -> (League character, its idle frame, game px top to feet: the user's picks, 2026-10-21)
TURRETS = {"turret": ("HeimerTYellow", "heimerturret_idle1@0", 20),
           "apex": ("HeimerTBlue", "heimerturret_mega_idle1@0", 30)}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def render(name, yaw):
    """The model on black and on white -> RGBA float (straight alpha 0..1), cropped to the figure."""
    champ, frame, _ = TURRETS[name]
    shots = {}
    for bg, s in (("0,0,0", "k"), ("255,255,255", "w")):
        stem = f"{name[0]}_{yaw}_{s}"
        path = os.path.join(WORK, stem + ".png")
        if not os.path.isfile(path):
            os.makedirs(WORK, exist_ok=True)
            subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", LOL, "--champ", champ,
                            "--wad", "Heimerdinger", "--hq", "--mirror", "--bg", bg, "--no-labels", "--size", "1600",
                            "--fit", "0.6", "--ground", "0.85", "--width", "1.3", "--yaw", str(yaw), "--name", stem,
                            "--out", WORK, "--frame", frame], check=True, capture_output=True)
        shots[s] = np.asarray(Image.open(path).convert("RGB")).astype(float) / 255.0
    k, w = shots["k"], shots["w"]
    a = np.clip(1.0 - (w - k).mean(-1), 0, 1)
    rgb = np.clip(k / np.maximum(a, 1e-3)[..., None], 0, 1)
    a[a < 0.03] = 0
    ys, xs = np.nonzero(a > 0)
    sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    return np.dstack([rgb[sl], a[sl]])


def down(fig, rows):
    """The figure `rows` squares tall: each square the area average of its pixels (premultiplied), drawn where half or
    more of it is covered."""
    H, W = fig.shape[:2]
    cols = max(1, round(W * rows / H))
    pre = np.dstack([fig[..., :3] * fig[..., 3:], fig[..., 3:]])
    chans = [np.asarray(Image.fromarray(pre[..., c].astype(np.float32), "F").resize((cols, rows), Image.BOX))
             for c in range(4)]
    a = chans[3]
    rgb = np.dstack(chans[:3]) / np.maximum(a, 1e-4)[..., None]
    out = np.zeros((rows, cols, 4), np.uint8)
    keep = a >= 0.5
    out[keep, :3] = np.clip(rgb[keep] * 255, 0, 255).round().astype(np.uint8)
    out[keep, 3] = 255
    return out


def muzzle(side):
    """The muzzle: the middle of the red ring's rightmost columns (dense px from the top left)."""
    a = side.astype(int)
    red = (a[..., 3] > 0) & (a[..., 0] > 110) & (a[..., 0] > a[..., 1] * 2) & (a[..., 0] > a[..., 2] * 2)
    ys, xs = np.nonzero(red)
    right = xs >= xs.max() - 2
    return int(xs.max()), float(ys[right].mean())


def lab_stats(img):
    px = img[img[..., 3] > 0][:, :3].astype(float)
    lab = V.srgb2lab(px[px.sum(-1) >= PD.DARK_SUM])
    return lab.mean(0), lab.std(0)


def lab2srgb(lab):
    """design_varus.srgb2lab's inverse."""
    fy = (lab[..., 0] + 16) / 116
    f = np.stack([fy + lab[..., 1] / 500, fy, fy - lab[..., 2] / 200], -1)
    xyz = np.where(f ** 3 > 0.008856, f ** 3, (f - 16 / 116) / 7.787) * np.array([0.95047, 1.0, 1.08883])
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    c = np.clip(xyz @ np.linalg.inv(m).T, 0, 1)
    return np.where(c > 0.0031308, 1.055 * c ** (1 / 2.4) - 0.055, 12.92 * c) * 255


def toward(img, src, dst, k=TRANSFER):
    """img's colours moved `k` of the way the front render (src) differs from the front design (dst): Lab mean and
    spread per channel (the design's lighting and saturation; League's lit render is darker and greyer)."""
    (ms, ss), (md, sd) = src, dst
    out = img.copy()
    m = (img[..., 3] > 0) & (img[..., :3].astype(int).sum(-1) >= PD.DARK_SUM)
    lab = V.srgb2lab(img[m][:, :3].astype(float))
    moved = (lab - ms) * (sd / np.maximum(ss, 1e-3)) + md
    out[m, :3] = np.clip(lab2srgb(lab + k * (moved - lab)), 0, 255).round().astype(np.uint8)
    return out


def build(name, yaw):
    rows = round(TURRETS[name][2] * PPU_SIDE) - 2              # the ink outline adds a row each end
    g = down(render(name, yaw), rows)
    front = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g = toward(g, lab_stats(down(render(name, 0), rows)), lab_stats(front))
    g = PD.crisp([g], n=16, passes=2, contrast=1.2, lines=True)[0]
    pad = np.pad(g, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=INK, feet=pad.shape[0] - 1)
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yaw", type=int, default=70)
    ap.add_argument("--review")
    a = ap.parse_args()
    meta, cells = {"ppu": PPU_SIDE, "yaw": a.yaw}, []
    for name in TURRETS:
        side = build(name, a.yaw)
        Image.fromarray(side).save(lp(os.path.join(HD, f"{name}_side.png")))
        mx, my = muzzle(side)
        meta[name] = {"size": [side.shape[1], side.shape[0]], "muzzle": [mx, round(my, 1)]}
        print(name, "side", side.shape[1], "x", side.shape[0], "muzzle", meta[name]["muzzle"])
        front = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
        cells.append((front, side))
    with open(lp(os.path.join(HD, "side_turrets.json")), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    if a.review:
        # each at game size x 12: the front design (PPU 1.5) beside the side (PPU_SIDE)
        Z, gap = 12, 30
        tiles = []
        for front, side in cells:
            for pic, ppu in ((front, 1.5), (side, PPU_SIDE)):
                k = Z / ppu
                tiles.append(Image.fromarray(pic).resize((round(pic.shape[1] * k), round(pic.shape[0] * k)), Image.NEAREST))
        W = sum(t.width + gap for t in tiles)
        H = max(t.height for t in tiles)
        sheet = Image.new("RGB", (W, H), (96, 112, 96))
        x = 0
        for t in tiles:
            sheet.paste(t, (x, H - t.height), t)
            x += t.width + gap
        os.makedirs(a.review, exist_ok=True)
        out = os.path.join(a.review, f"side_turrets_yaw{a.yaw}.png")
        sheet.save(out)
        print(out, sheet.size)


if __name__ == "__main__":
    main()
