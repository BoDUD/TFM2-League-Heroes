#!/usr/bin/env python3
"""Mordekaiser's step-2 pack for Codex (assets/source/mordekaiser/POSE_PROMPTS.md): the key poses of his actions,
drawn on the dense design's own grid.

    python tools/art/pack_mordekaiser_poses.py --out dist/mordekaiser_packs/mordekaiser_pose_pack [--lol D:/WeGameApps/lol]

The dense design is Codex's raw picture A read back on its own grid (tools/art/design_mordekaiser_hd.py ->
assets/source/mordekaiser/hd/front.png, 166 x 246 squares, 48 colours; PPU 5 in league.dll, shown 110% with a thicker
outline - the user's pick C). Every action is posed from the 3/4 front design (the user: 「侧面只要四分之三那种就行
参考卡萨丁」). His mace rests on his shoulder behind the helm and the pauldron, so a swing cannot be cut out of the design
(the haft behind the helm, the head's lower half behind the pauldron and the shoulder under the hand were never drawn):
the user chose 「交给 Codex 画姿势」. The pack asks for the key poses on the same grid (one drawn square = one dense
pixel, SQ px a square); the import keeps the design's helm square for square in every frame (memory one-face-all-frames)
and the design's own parts wherever a pose leaves them where they were.
  design/mordekaiser_front.png        the dense design at SQ px a square (transparent); _1x one pixel a square
  design/mordekaiser_palette.png      its 48 colours
  design/grid_landscape.png           the design on the 1536 x 1024 grid canvas (384 x 256 squares) with the lines
                                      every pose keeps (the horns' tips, the soles), and _empty
  design/grid_portrait.png            the same on 1024 x 1536 (256 x 384 squares: room above for a raised mace)
  refs/1_picture_A.png                Codex's step-0 picture A (the look)
  refs/2_league_attack.png ...        League's own moments of each pose (local renders, mirrored to face right)
Renders are Riot's models: local only, never committed.
"""
import argparse
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "mordekaiser")
FRONT = os.path.join(SRC, "hd", "front.png")
PICTURE = os.path.join(SRC, "codex_picture", "raw", "mordekaiser-model-A.png")
SQ = 4                           # pixels a square in the pack
HORNS = 30                       # the design's row of the helm's horn tips
CANVASES = {                     # name -> (columns, rows, the design's left column, the design's top row)
    "landscape": (384, 256, 60, 6),
    "portrait": (256, 384, 40, 134),
}
# ref name -> (frames, yaw); League's clip names (mirrored to face right)
REFS = {
    "2_league_attack": (["autoattack1@0", "autoattack1@400", "autoattack1@600"], 40),
    "3_league_q": (["spell_1@550", "spell_1@650", "spell_1@840"], 40),
    "4_league_e": (["spell3_cast@0", "spell3_cast@400"], 40),
    "5_league_r": (["spell_4_cast@0", "spell_4_cast@300"], 40),
    "6_league_walk": (["walk@0", "walk@250", "walk@500", "walk@750"], 40),
    "7_league_death": (["death@0", "death@1667", "death@2222", "death@2778"], 40),
}
SUBMESH = ["--hide-submesh", "Guitar", "--hide-submesh", "Poro_ShadowIsles_Mat", "--hide-submesh", "Crown",
           "--submesh-texture", "Mace=Mace"]


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def canvas(kind, design=None):
    cols, rows, x0, y0 = CANVASES[kind]
    can = np.zeros((rows, cols, 4), np.uint8)
    if design is not None:
        h, w = design.shape[:2]
        can[y0:y0 + h, x0:x0 + w] = design
    img = Image.new("RGBA", (cols * SQ, rows * SQ), (255, 255, 255, 255))
    img.alpha_composite(Image.fromarray(up(can, SQ)))
    d = ImageDraw.Draw(img)
    for c in range(0, cols + 1, 10):
        d.line([(c * SQ, 0), (c * SQ, rows * SQ)], fill=(240, 210, 60, 255), width=1)
    for r in range(0, rows + 1, 10):
        d.line([(0, r * SQ), (cols * SQ, r * SQ)], fill=(240, 210, 60, 255), width=1)
    h = 246 if design is None else design.shape[0]
    d.line([(0, (y0 + HORNS) * SQ), (cols * SQ, (y0 + HORNS) * SQ)], fill=(40, 200, 60, 255), width=3)
    d.line([(0, (y0 + h) * SQ), (cols * SQ, (y0 + h) * SQ)], fill=(230, 40, 40, 255), width=3)
    return img


def render(lol, name, frames, yaw, out):
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Mordekaiser",
           "--hq", "--bg", "225,225,225", "--no-labels", "--size", "800", "--fit", "0.62", "--ground", "0.8",
           "--width", "1.4", "--yaw", str(yaw), "--mirror", "--name", name, "--out", out] + SUBMESH
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    print(name, Image.open(os.path.join(out, name + ".png")).size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    des, refs = os.path.join(a.out, "design"), os.path.join(a.out, "refs")
    os.makedirs(des, exist_ok=True)
    os.makedirs(refs, exist_ok=True)
    front = np.asarray(Image.open(FRONT).convert("RGBA"))
    Image.fromarray(up(front, SQ)).save(os.path.join(des, "mordekaiser_front.png"))
    Image.fromarray(front).save(os.path.join(des, "mordekaiser_front_1x.png"))
    cols = np.unique(front[front[..., 3] > 0][:, :3], axis=0)
    pal = Image.new("RGB", (8 * 40, ((len(cols) + 7) // 8) * 40), (255, 255, 255))
    d = ImageDraw.Draw(pal)
    for i, c in enumerate(cols):
        d.rectangle([(i % 8) * 40, (i // 8) * 40, (i % 8) * 40 + 39, (i // 8) * 40 + 39], fill=tuple(int(v) for v in c))
    pal.save(os.path.join(des, "mordekaiser_palette.png"))
    for kind in CANVASES:
        canvas(kind, front).convert("RGB").save(os.path.join(des, f"grid_{kind}.png"))
        canvas(kind).convert("RGB").save(os.path.join(des, f"grid_{kind}_empty.png"))
    shutil.copyfile(PICTURE, os.path.join(refs, "1_picture_A.png"))
    for name, (frames, yaw) in REFS.items():
        render(a.lol, name, frames, yaw, refs)
    shutil.copyfile(os.path.join(SRC, "POSE_PROMPTS.md"), os.path.join(a.out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
