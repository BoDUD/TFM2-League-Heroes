"""The Codex pack for league_camille's PPU legs (assets/source/camille/LEGS_PROMPT_PPU.md): her actions are League's
full-body kicks, flips and leaps, which the design's rigid blade legs cannot pose losslessly (league_kaisa's walk:
every slid, cut or row-swung leg read as 「变形」), so tools/art/rig_camille_hd.py poses the upper body and the arms after
League's skeleton and Codex draws only the legs, along a guide per leg: thigh from League's hip to its knee, the blade
from the knee towards its foot, at the design's own lengths (THIGH, BLADE squares), the near leg red, the far one blue.

    python tools/art/pack_camille_legs.py --joints <dir>/camille_joints.json --out C:/t/cm_legs [--lol D:/WeGameApps/lol]

Writes <out>/LEGS_PROMPT.md, <out>/templates/<tag>.png (each action's frames, 4 x 2 on 1536 x 1024, CELL_PX a square,
flat #00FF00, a darker green ground line, frame numbers; the legs left out, their guides drawn), <out>/refs/design.png
(8x), refs/design_legs.png (16x, the grid), refs/lol_<tag>.png (League's frames: Riot's, kept local, never committed),
then <out>.zip. tools/art/import_camille_legs.py reads the delivery back.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_camille_hd as C  # noqa: E402

SRC = os.path.join(REPO, "assets", "source", "camille")
GREEN, GROUND, GREY = (0, 255, 0), (0, 128, 0), (225, 225, 225)
NEAR_C, FAR_C = (255, 0, 0), (0, 60, 255)
CANVAS, GRID, CELL_PX = (1536, 1024), (4, 2), 6
CELL = (CANVAS[0] // GRID[0], CANVAS[1] // GRID[1])
SOLE_Y = 470                                  # the ground in a cell (px from the cell's top)
TAGS = C.LEG_TAGS


def template(rig, frames, path, z=CELL_PX):
    """frames: [(no-leg canvas, guides)] -> the 4 x 2 sheet, the ground line one square under the design's soles."""
    xs = np.concatenate([np.nonzero(f[..., 3].any(0))[0] for f, _ in frames])
    gx = [p[0] for _, g in frames for leg in g.values() for p in leg]
    x0 = int(min(xs.min(), min(gx))) - 2
    x1 = int(max(xs.max(), max(gx))) + 3
    w = (x1 - x0) * z
    can = Image.new("RGB", CANVAS, GREEN)
    dr = ImageDraw.Draw(can)
    placed = []
    for i, (f, g) in enumerate(frames):
        cx, cy = (i % GRID[0]) * CELL[0], (i // GRID[0]) * CELL[1]
        left = cx + max(0, (CELL[0] - w) // 2 // z * z)
        top = cy + SOLE_Y - rig.GY * z
        sub = f[:, x0:x1]
        im = Image.fromarray(sub).resize((sub.shape[1] * z, sub.shape[0] * z), Image.NEAREST)
        dr.rectangle([cx + 8, cy + SOLE_Y, cx + CELL[0] - 9, cy + SOLE_Y + z - 1], fill=GROUND)
        for side, col in (("far", FAR_C), ("near", NEAR_C)):
            pts = [(left + (p[0] - x0) * z, top + p[1] * z) for p in g[side]]
            dr.line(pts, fill=col, width=z)
            kx, ky = pts[1]
            dr.ellipse([kx - z, ky - z, kx + z, ky + z], outline=col, width=2)
        can.paste(im, (left, top), im)
        dr.text((cx + 10, cy + 8), str(i + 1), fill=(0, 0, 0))
        placed.append(dict(left=int(left), top=int(top), x0=int(x0)))
    can.save(path)
    return placed


def design_png(path, z=8, rows=None):
    d = np.asarray(Image.open(R.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA"))
    if rows is not None:
        d = d[rows[0]:rows[1]]
    big = Image.fromarray(d).resize((d.shape[1] * z, d.shape[0] * z), Image.NEAREST)
    can = Image.new("RGBA", (big.width + 2 * z, big.height + 2 * z), GREY + (255,))
    if rows is not None:
        dr = ImageDraw.Draw(can)
        for x in range(d.shape[1] + 1):
            dr.line([(z + x * z, z), (z + x * z, z + d.shape[0] * z)], fill=(190, 190, 190, 255))
        for y in range(d.shape[0] + 1):
            dr.line([(z, z + y * z), (z + d.shape[1] * z, z + y * z)], fill=(190, 190, 190, 255))
    can.alpha_composite(big, (z, z))
    can.convert("RGB").save(path)


def lol_refs(lol, out, refs):
    poses = json.load(open(R.lp(os.path.join(SRC, "poses_hd.json")), encoding="utf-8"))
    ch, cam = poses["chibi"], poses["camera"]
    for tag in TAGS:
        cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Camille", "--hq",
               "--hide-submeshes", "--head", str(ch["head"]), "--legs", str(ch["legs"]), "--hair", str(ch["hair"]),
               "--yaw", str(cam["yaw"]), "--pitch", str(cam["pitch"]), "--size", "260", "--width", "1.0", "--fit", "0.6",
               "--ground", "0.9", "--no-labels", "--bg", ",".join(map(str, GREY)), "--name", "lol_" + tag, "--out", out]
        if cam.get("mirror"):
            cmd.append("--mirror")
        for name, _ in poses["tags"][tag]["frames"]:
            cmd += ["--frame", name]
        subprocess.run(cmd, check=True, capture_output=True)
        shutil.move(os.path.join(out, "lol_" + tag + ".png"), os.path.join(refs, "lol_" + tag + ".png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    os.makedirs(tpl, exist_ok=True)
    os.makedirs(refs, exist_ok=True)
    D = C.design()
    rig = C.make_rig(D)
    joints = json.load(open(a.joints, encoding="utf-8"))
    drv = C.driver(rig, joints)
    sheet = R.sheet_of(C.HERO)
    layout = {}
    for tag in TAGS:
        rows = R.fit_rows(joints["tags"][tag], len(sheet[tag]))
        fr = []
        for r in rows:
            fr.append(C.leg_guides(rig, drv, joints, r["j"]))
        layout[tag] = template(rig, fr, os.path.join(tpl, tag + ".png"))
    json.dump(layout, open(os.path.join(a.out, "layout.json"), "w"), indent=1)
    design_png(os.path.join(refs, "design.png"))
    design_png(os.path.join(refs, "design_legs.png"), z=16, rows=(40, D.d0.shape[0]))
    lol_refs(a.lol, a.out, refs)
    shutil.copyfile(R.lp(os.path.join(SRC, "LEGS_PROMPT_PPU.md")), os.path.join(a.out, "LEGS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
