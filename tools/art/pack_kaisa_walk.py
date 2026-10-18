"""The Codex pack for league_kaisa's PPU walk (assets/source/kaisa/WALK_PROMPT_PPU.md): Codex redraws only the two legs
of the 8 run frames tools/art/rig_kaisa_hd.py poses (their feet, crossing steps and upper body kept), in the design's
own leg widths, plates and boots, bending at the knee - the user, 2026-10-18, at the legs swung by whole rows:
「有点变形啊 让codex帮忙把」.

    python tools/art/pack_kaisa_walk.py --joints <dir>/kaisa_joints.json --out C:/t/ks_walk [--lol D:/WeGameApps/lol]

Writes <out>/WALK_PROMPT.md and <out>/refs/1_walk_template.png (the 8 frames 4 x 2 on 1536 x 1024, CELL_PX a square,
flat #00FF00, a darker green ground line under each), 2_design.png (8x), 3_design_legs.png (16x, the grid drawn),
4_lol_run.png (League's kaisa_run at yaw 45 through tools/lol/pose_ref.py: Riot's, kept local, never committed),
5_old_walk.png (the approved 1x run on origin/main, 8x), then <out>.zip. Render into a short folder.
"""
import argparse
import io
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
import rig_kaisa_hd as K  # noqa: E402

SRC = os.path.join(REPO, "assets", "source", "kaisa")
GREEN, GROUND, GREY = (0, 255, 0), (0, 128, 0), (225, 225, 225)
CANVAS, GRID, CELL_PX = (1536, 1024), (4, 2), 6
CELL = (CANVAS[0] // GRID[0], CANVAS[1] // GRID[1])
SOLE_Y = 470                                  # the soles' bottom in a cell (px from the cell's top)
LEGS_FROM = 44                                # design row: the hip plates' lowest rows and the legs (the 16x close-up)


def lp(path):
    return K.lp(path)


def template(frames, path):
    """The run frames 4 x 2, CELL_PX a square, the ground line one square under the soles, frame numbers on top."""
    D_rows = [np.nonzero(f[..., 3].any(1))[0] for f in frames]
    ys = np.concatenate(D_rows)
    xs = np.concatenate([np.nonzero(f[..., 3].any(0))[0] for f in frames])
    x0, x1 = xs.min() - 2, xs.max() + 3
    gy = frames[0].shape[0]                      # canvas row under the soles of a standing frame
    rig_gy = None
    can = Image.new("RGB", CANVAS, GREEN)
    dr = ImageDraw.Draw(can)
    for i, f in enumerate(frames):
        cx, cy = (i % GRID[0]) * CELL[0], (i // GRID[0]) * CELL[1]
        sub = f[:, x0:x1]
        im = Image.fromarray(sub).resize((sub.shape[1] * CELL_PX, sub.shape[0] * CELL_PX), Image.NEAREST)
        left = cx + (CELL[0] - im.width) // 2 // CELL_PX * CELL_PX
        top = cy + SOLE_Y - GY * CELL_PX
        can.paste(im, (left, top), im)
        dr.rectangle([cx + 8, cy + SOLE_Y, cx + CELL[0] - 9, cy + SOLE_Y + CELL_PX - 1], fill=GROUND)
        dr.text((cx + 10, cy + 8), str(i + 1), fill=(0, 0, 0))
    can.save(path)
    return x0, x1, rig_gy


def design_png(path, z=8, rows=None):
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA"))
    if rows is not None:
        d = d[rows[0]:rows[1]]
    big = Image.fromarray(d).resize((d.shape[1] * z, d.shape[0] * z), Image.NEAREST)
    can = Image.new("RGBA", (big.width + 2 * z, big.height + 2 * z), GREY + (255,))
    can.alpha_composite(big, (z, z))
    if rows is not None:
        dr = ImageDraw.Draw(can)
        for x in range(d.shape[1] + 1):
            dr.line([(z + x * z, z), (z + x * z, z + d.shape[0] * z)], fill=(190, 190, 190, 255))
        for y in range(d.shape[0] + 1):
            dr.line([(z, z + y * z), (z + d.shape[1] * z, z + y * z)], fill=(190, 190, 190, 255))
        can.alpha_composite(big, (z, z))
    can.convert("RGB").save(path)


def old_walk(path, z=8):
    """origin/main's 1x run (the walk the user approved 2026-10-02), each frame centred as the game draws it."""
    stem = "league/champions/league_kaisa"

    def show(p):
        return subprocess.run(["git", "show", f"origin/main:{p}"], cwd=REPO, capture_output=True, check=True).stdout
    sheet = Image.open(io.BytesIO(show(stem + "#sheet.png"))).convert("RGBA")
    frames = json.loads(show(stem + "#anim.fanim").decode("utf-8-sig"))["anims"]["run"]["frames"]
    ims = []
    for f in frames:
        d = f["data"]
        ims.append(sheet.crop((int(d["x"]), int(d["y"]), int(d["x"] + d["w"]), int(d["y"] + d["h"]))))
    W, H = max(i.width for i in ims), max(i.height for i in ims)
    can = Image.new("RGBA", (len(ims) * (W + 2) * z, (H + 2) * z), GREY + (255,))
    for k, im in enumerate(ims):
        c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        c.alpha_composite(im, ((W - im.width) // 2, (H - im.height) // 2))
        can.alpha_composite(c.resize((W * z, H * z), Image.NEAREST), (k * (W + 2) * z + z, z))
    can.convert("RGB").save(path)


def lol_run(lol, out, path):
    poses = json.load(open(lp(os.path.join(SRC, "poses_hd.json")), encoding="utf-8"))
    ch, cam = poses["chibi"], poses["camera"]
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Kaisa", "--hq",
           "--hide-submeshes", "--head", str(ch["head"]), "--legs", str(ch["legs"]), "--hair", str(ch["hair"]),
           "--yaw", str(cam["yaw"]), "--pitch", str(cam["pitch"]), "--size", "300", "--width", "1.0", "--fit", "0.75",
           "--ground", "0.92", "--no-labels", "--bg", ",".join(map(str, GREY)), "--name", "lol_run", "--out", out]
    if cam.get("mirror"):
        cmd.append("--mirror")
    for name, _ in poses["tags"]["run"]["frames"]:
        cmd += ["--frame", name]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.move(os.path.join(out, "lol_run.png"), path)


GY = None


def main():
    global GY
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    refs = os.path.join(a.out, "refs")
    os.makedirs(refs, exist_ok=True)
    D = K.design()
    rig = K.make_rig(D)
    GY = rig.GY
    joints = json.load(open(a.joints, encoding="utf-8"))
    frames = K.run_frames(rig, joints["tags"]["run"])
    template(frames, os.path.join(refs, "1_walk_template.png"))
    design_png(os.path.join(refs, "2_design.png"))
    design_png(os.path.join(refs, "3_design_legs.png"), z=16, rows=(LEGS_FROM, D.d0.shape[0]))
    lol_run(a.lol, a.out, os.path.join(refs, "4_lol_run.png"))
    old_walk(os.path.join(refs, "5_old_walk.png"))
    shutil.copyfile(lp(os.path.join(SRC, "WALK_PROMPT_PPU.md")), os.path.join(a.out, "WALK_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
