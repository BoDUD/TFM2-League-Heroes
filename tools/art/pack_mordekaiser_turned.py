#!/usr/bin/env python3
"""Mordekaiser's step-2b pack for Codex (assets/source/mordekaiser/TURNED_PROMPTS.md): the action poses with the body
turned toward the image right (League's yaw 65), on the dense design's own grid.

    python tools/art/pack_mordekaiser_turned.py --out dist/mordekaiser_packs/mordekaiser_turned_pack [--lol D:/WeGameApps/lol]

The user, after the first frames (every action in the idle's 3/4 front): 「走路的时候腿既然是那个方向 身体也要那个方向吧？」
「四分之三左右 待机姿势和走路放技能的时候应该不一样的」, and picked C 65 degrees from League's model at 30 / 50 / 65 / 80
(dist/mordekaiser_packs/review/mordekaiser_angles.png). The idle and the card stay design A (yaw ~30); the run and
every skill are redrawn turned: first the design itself turned (mordekaiser-turned.png), then the ten poses of step 2
(assets/source/mordekaiser/codex_poses, the front versions the user saw) in that angle. The death (kneel, lying) stays.
  design/mordekaiser_front.png        the dense design (yaw ~30) at SQ px a square; _1x one pixel a square
  design/mordekaiser_palette.png      its 48 colours
  design/grid_landscape.png / grid_portrait.png (+ _empty)   the grid canvases with the horn and sole lines (step 2's)
  poses_front/<pose>.png              step 2's poses as drawn (the composition to keep)
  refs/1_league_turn.png              League's idle at yaw 30 (the design) and 65 (the angle to draw)
  refs/2_league_attack_65.png ...     League's moments of each pose at yaw 65 (local renders, mirrored to face right)
Renders are Riot's models: local only, never committed.
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_mordekaiser_poses as P  # noqa: E402

SRC = P.SRC
YAW = 65
POSES = ["walk-1", "walk-2", "walk-3", "walk-4", "attack-raise", "attack-strike", "q-raise", "q-slam", "e-grasp",
         "r-point"]
REFS = {
    "1_league_turn": (["idle@0"], None),
    "2_league_attack_65": (["autoattack1@0", "autoattack1@400", "autoattack1@600"], YAW),
    "3_league_q_65": (["spell_1@550", "spell_1@650", "spell_1@840"], YAW),
    "4_league_e_65": (["spell3_cast@0", "spell3_cast@400"], YAW),
    "5_league_r_65": (["spell_4_cast@0", "spell_4_cast@300"], YAW),
    "6_league_walk_65": (["walk@0", "walk@250", "walk@500", "walk@750"], YAW),
}


def turn_ref(lol, out):
    """League's idle at yaw 30 and 65 side by side."""
    tiles = []
    for yaw in (30, YAW):
        name = f"_turn{yaw}"
        P.render(lol, name, ["idle@0"], yaw, out)
        tiles.append(Image.open(os.path.join(out, name + ".png")).convert("RGB"))
        os.remove(os.path.join(out, name + ".png"))
    img = Image.new("RGB", (sum(t.width for t in tiles), max(t.height for t in tiles)), (225, 225, 225))
    x = 0
    for t in tiles:
        img.paste(t, (x, 0))
        x += t.width
    img.save(os.path.join(out, "1_league_turn.png"))
    print("1_league_turn", img.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    des, refs, fr = (os.path.join(a.out, d) for d in ("design", "refs", "poses_front"))
    for d in (des, refs, fr):
        os.makedirs(d, exist_ok=True)
    # the design files of step 2 (the same grid, palette, lines)
    front = np.asarray(Image.open(P.FRONT).convert("RGBA"))
    Image.fromarray(P.up(front, P.SQ)).save(os.path.join(des, "mordekaiser_front.png"))
    Image.fromarray(front).save(os.path.join(des, "mordekaiser_front_1x.png"))
    for kind in P.CANVASES:
        P.canvas(kind, front).convert("RGB").save(os.path.join(des, f"grid_{kind}.png"))
        P.canvas(kind).convert("RGB").save(os.path.join(des, f"grid_{kind}_empty.png"))
    cols = np.unique(front[front[..., 3] > 0][:, :3], axis=0)
    pal = Image.new("RGB", (8 * 40, ((len(cols) + 7) // 8) * 40), (255, 255, 255))
    d = ImageDraw.Draw(pal)
    for i, c in enumerate(cols):
        d.rectangle([(i % 8) * 40, (i // 8) * 40, (i % 8) * 40 + 39, (i // 8) * 40 + 39], fill=tuple(int(v) for v in c))
    pal.save(os.path.join(des, "mordekaiser_palette.png"))
    for p in POSES:
        shutil.copyfile(os.path.join(SRC, "codex_poses", f"mordekaiser-{p}.png"), os.path.join(fr, f"{p}.png"))
    turn_ref(a.lol, refs)
    for name, (frames, yaw) in REFS.items():
        if yaw is not None:
            P.render(a.lol, name, frames, yaw, refs)
    shutil.copyfile(os.path.join(SRC, "TURNED_PROMPTS.md"), os.path.join(a.out, "TURNED_PROMPTS.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
