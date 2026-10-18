"""The Codex pack for league_fiora's PPU legs (assets/source/fiora/LEGS_PROMPT_PPU.md), the way league_camille's were
made (tools/art/pack_camille_legs.py): tools/art/rig_fiora_hd.py poses the upper body, the sword arm and the rapier
after League's skeleton, and Codex draws only the legs, along a guide per leg (thigh from League's hip to its knee, the
shin from the knee towards its foot, at the design's own lengths THIGH, SHIN squares; the front leg red, the back one
blue). Q's two dash frames (skill 2-3: League flies low, the body almost flat) Codex draws whole. Also one picture of
the rapier's guard turned 45 degrees (the user: 「剑别歪啊」 - the guard only takes quarter turns losslessly, so the
diagonal sword needs its own drawing).

    python tools/art/pack_fiora_legs.py --joints <dir>/fiora_joints.json --out C:/t/fi_legs [--lol D:/WeGameApps/lol]

Writes <out>/LEGS_PROMPT.md, <out>/templates/<tag>.png (each action's frames, 4 x 2 on 1536 x 1024, CELL_PX a
square, flat #00FF00, a darker green ground line, frame numbers; the legs and the blade left out, the guides drawn),
templates/guard45.png, <out>/refs/design.png (8x), refs/design_legs.png (16x, the grid), refs/guard.png (16x),
refs/lol_<tag>.png (League's frames: Riot's, kept local, never committed), <out>/layout.json, then <out>.zip.
"""
import argparse
import json
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
import rig_fiora_hd as F  # noqa: E402

SRC = os.path.join(REPO, "assets", "source", "fiora")
GREEN, GROUND, GREY = (0, 255, 0), (0, 128, 0), (225, 225, 225)
NEAR_C, FAR_C = (255, 0, 0), (0, 60, 255)
CANVAS, GRID = (1536, 1024), (4, 2)
CELL = (CANVAS[0] // GRID[0], CANVAS[1] // GRID[1])
SOLE_Y = 470                                  # the ground in a cell (px from the cell's top)
TAGS = F.LEG_TAGS
WHOLE = {"skill": [1, 2]}                     # frames (0-based) Codex draws whole: Q's low dash
GUARD_Z = 16


def no_blade(f):
    f = f.copy()
    for c in (F.BLADE_HI, F.BLADE_LO):
        f[(f[..., 3] > 0) & (f[..., :3] == c).all(-1)] = 0
    return f


def span(f, g):
    """A frame's columns (canvas squares): the figure and its guides, a margin round them."""
    xs = np.nonzero(f[..., 3].any(0))[0]
    gx = [p[0] for leg in g.values() for p in leg]
    return int(min(xs.min(), min(gx))) - 2, int(max(xs.max(), max(gx))) + 3


def template(rig, frames, path, z, whole=()):
    """frames: [(no-leg canvas, guides)] -> the 4 x 2 sheet, the ground line one square under the design's soles. Each
    frame is cut at its own columns (x0 in layout.json): her lunges travel further than a cell is wide."""
    w = max(b - a for a, b in (span(f, g) for f, g in frames)) * z
    can = Image.new("RGB", CANVAS, GREEN)
    dr = ImageDraw.Draw(can)
    placed = []
    for i, (f, g) in enumerate(frames):
        x0, x1 = span(f, g)
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
        dr.text((cx + 10, cy + 8), str(i + 1) + ("  WHOLE FIGURE" if i in whole else ""), fill=(0, 0, 0))
        placed.append(dict(left=int(left), top=int(top), x0=int(x0)))
    can.save(path)
    return placed


def design_png(path, z=8, rows=None, cols=None):
    d = np.asarray(Image.open(R.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA"))
    if rows is not None:
        d = d[rows[0]:rows[1]]
    if cols is not None:
        d = d[:, cols[0]:cols[1]]
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


def guard_refs(refs, tpl):
    """refs/guard.png: the glove, the guard and the blade's first squares as drawn (16x, the grid); templates/guard45.png:
    the same at the left, and on the right a 45-degree guide (the blade's line up-right, a circle on the glove) to draw
    it turned along."""
    d = np.asarray(Image.open(R.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA"))
    box = (44, 15, 64, 30)                       # design squares: glove, guard, 8 squares of blade
    sub = d[box[1]:box[3], box[0]:box[2]]
    z = GUARD_Z
    big = Image.fromarray(sub).resize((sub.shape[1] * z, sub.shape[0] * z), Image.NEAREST)
    can = Image.new("RGBA", (big.width + 2 * z, big.height + 2 * z), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for x in range(sub.shape[1] + 1):
        dr.line([(z + x * z, z), (z + x * z, z + sub.shape[0] * z)], fill=(190, 190, 190, 255))
    for y in range(sub.shape[0] + 1):
        dr.line([(z, z + y * z), (z + sub.shape[1] * z, z + y * z)], fill=(190, 190, 190, 255))
    can.alpha_composite(big, (z, z))
    can.convert("RGB").save(os.path.join(refs, "guard.png"))
    t = Image.new("RGB", CANVAS, GREEN)
    t.paste(big.convert("RGB"), (32, 32), big)
    dr = ImageDraw.Draw(t)
    gx, gy = 900, 640                            # the glove's middle in the guide
    dr.ellipse([gx - 24, gy - 24, gx + 24, gy + 24], outline=FAR_C, width=4)
    dr.line([(gx, gy), (gx + 420, gy - 420)], fill=NEAR_C, width=4)
    dr.text((40, 300), "as drawn (16 px a square)", fill=(0, 0, 0))
    dr.text((gx - 120, gy + 40), "draw it here turned 45 degrees: glove on the circle, the blade along the red line",
            fill=(0, 0, 0))
    t.save(os.path.join(tpl, "guard45.png"))
    return dict(glove=[gx, gy], z=z)


def lol_refs(lol, out, refs):
    poses = json.load(open(R.lp(os.path.join(SRC, "poses.json")), encoding="utf-8"))
    ch, cam = poses["chibi"], poses["camera"]
    for tag in TAGS:
        cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Fiora", "--hq",
               "--hide-submeshes", "--head", str(ch["head"]), "--legs", str(ch["legs"]), "--hair", str(ch["hair"]),
               "--yaw", str(cam["yaw"]), "--pitch", str(cam["pitch"]), "--size", "260", "--width", "1.4", "--fit", "0.6",
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
    D = F.design()
    rig = F.make_rig(D)
    joints = json.load(open(a.joints, encoding="utf-8"))
    drv = F.driver(rig, joints)
    sheet = R.sheet_of(F.HERO)
    frames = {}
    for tag in TAGS:
        rows = R.fit_rows(joints["tags"][tag], len(sheet[tag]))
        frames[tag] = []
        for r in rows:
            bare, g = F.leg_guides(rig, drv, joints, r["j"])
            frames[tag].append((no_blade(bare), g))
    # one square size for every template: the widest frame fits a cell
    widest = max(b - a for fr in frames.values() for a, b in (span(f, g) for f, g in fr))
    z = min(6, (CELL[0] - 8) // widest)
    print("widest frame", widest, "squares ->", z, "px a square")
    layout = {"cell_px": z}
    for tag, fr in frames.items():
        layout[tag] = template(rig, fr, os.path.join(tpl, tag + ".png"), z, WHOLE.get(tag, ()))
    layout["guard45"] = guard_refs(refs, tpl)
    json.dump(layout, open(os.path.join(a.out, "layout.json"), "w"), indent=1)
    design_png(os.path.join(refs, "design.png"))
    design_png(os.path.join(refs, "design_legs.png"), z=16, rows=(34, D.d0.shape[0]), cols=(0, 44))
    lol_refs(a.lol, a.out, refs)
    shutil.copyfile(R.lp(os.path.join(SRC, "LEGS_PROMPT_PPU.md")), os.path.join(a.out, "LEGS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
