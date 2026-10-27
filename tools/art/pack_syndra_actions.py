"""The Codex pack for league_syndra's actions at PPU 1.86 (assets/source/syndra/ACTIONS_PROMPT_PPU.md) - the user, 2026-10-27:
「就用原样 1.86，继续做辛德拉的动作包」.

Her old sheet is a rig of her idle drawing (checked frame by frame against idle 1 after lining up a shift): every frame
is the idle moved whole (her hover bob up 1-2 px, R's lift, the hit's 1-2 px back, the death's 3 px down) with only
two places drawn again - the far forearm and hand (four poses, A-D, reused by the attack, Q, W, E, R and the hover's
peak) and the legs (the run's three bends, the death's crumple). Redrawn whole 41 times, her face and body would
differ a little from frame to frame and flicker in so quiet an animation; so Codex draws only the NINE distinct poses
(POSES), each a whole picture of her in that old frame's pose, and tools/art/rig_syndra_hd.py builds every frame from
the approved design: the old frame's shift x PPU, the changed region (the hand or the legs, from the old frame's
difference to idle 1) taken from Codex's drawing of that pose.

    python tools/art/pack_syndra_actions.py --out C:/t/sy_actions [--old-sheet PNG --old-fanim FANIM]

Each template sheet (templates/pose_<k>.png, 1536 x 1024) holds two poses: in each cell the old 1x frame scaled to her
height (PPU squares a pixel, SQ px a square), faded, as the pose to follow, her lower toe on the ground line at the
standing point, and a bar as tall as she is (horn tips to toe). The old sheet is main's league_syndra#sheet.png /
#anim.fanim (copied to C:/t/sy_old and assets/source/syndra/hd/old before the redo replaces it). Then <out>.zip.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import pack_riven_actions as PR  # noqa: E402

SRC = os.path.join(REPO, "assets", "source", "syndra")
# (label, old tag, old frame (1-based), what changes from her idle) - the nine distinct poses of the old sheet
POSES = [
    ("A", "idle_base", 4, "her far hand (image right) a little lower and turned, the hover's top"),
    ("B", "attack", 2, "her far hand (image right) raised to her shoulder, the palm out"),
    ("C", "attack", 3, "her far hand (image right) pushed out to the right at waist height"),
    ("D", "skill", 1, "her far hand (image right) raised higher, over her shoulder"),
    ("E", "run", 2, "gliding: her lower leg bent back a little"),
    ("F", "run", 3, "gliding: her lower leg swung, her far hand out"),
    ("G", "run", 4, "gliding: her legs coming back, her far hand out"),
    ("H", "dead", 4, "dying: her legs giving way, she sinks a little"),
    ("I", "dead", 5, "dying: she sinks onto her bent legs, slumped"),
]
SQ = 8                                   # px a design square in the templates
PPU = 78 / 42                            # design squares an old pixel (hd/design.png: 78 rows, her 1x 42)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 78                               # design rows from her horn tips to her lower toe
OLD_SOLES = 11.5                         # old frames: the toe this many pixels under the frame's centre (its pivot)
MARGIN = 30
GREY = (225, 225, 225)


def old_frames(sheet_png, fanim):
    px = np.asarray(Image.open(sheet_png).convert("RGBA"))
    with open(fanim, encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag in anims:
        fr = []
        for f_ in anims[tag]["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            fr.append((px[y:y + h, x:x + w].copy(), round(f_["duration"] * 1000)))
        out[tag] = fr
    return out


def cell_fit(frame):
    xs = np.nonzero(frame[..., 3].any(0))[0]
    return (xs.max() + 1 - xs.min()) * PPU * SQ + 2 * MARGIN <= SHEET_W / 2


def placed(frame, x0, cw):
    """The old frame scaled to his height in a cell [x0, x0 + cw): its pivot (the frame's centre) on the standing point
    (the cell's middle), kept inside the cell. -> (RGBA image, left, top)."""
    k = PPU * SQ
    h, w = frame.shape[:2]
    im = Image.fromarray(frame).resize((round(w * k), round(h * k)), Image.NEAREST)
    left = round(x0 + cw / 2 - (w / 2) * k)
    top = round(GROUND - OLD_SOLES * k - (h / 2) * k)
    bb = im.getbbox()
    if bb:
        lo, hi = left + bb[0], left + bb[2]
        if lo < x0 + MARGIN:
            left += x0 + MARGIN - lo
        elif hi > x0 + cw - 14:
            left -= hi - (x0 + cw - 14)
        if top + bb[1] < 8:
            raise SystemExit(f"a frame reaches {8 - top - bb[1]} px over the template's top: lower SQ")
    return im, left, top


def template(path, frames, nums):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), (255, 255, 255, 255))
    for i, (fr, ms) in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
        a = np.asarray(im).astype(float)
        faded = a.copy()
        faded[..., :3] = a[..., :3] * 0.35 + 255 * 0.65                  # a pale picture of the pose
        can.alpha_composite(Image.fromarray(faded.astype(np.uint8)), (left, top))
    dr = ImageDraw.Draw(can)
    for i, (fr, ms) in enumerate(frames):
        x0 = i * cw
        cx = x0 + cw / 2
        dr.rectangle([x0, 0, x0 + cw - 1, H - 1], outline=(60, 60, 60), width=2)
        dr.line([(x0, GROUND), (x0 + cw - 1, GROUND)], fill=(90, 90, 90), width=3)
        dr.line([(cx, GROUND - 12), (cx, GROUND + 12)], fill=(90, 90, 90), width=3)
        bx = x0 + 16
        dr.line([(bx, GROUND), (bx, GROUND - STAND * SQ)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "her height (horn tips to toe)", fill=(120, 120, 120),
                font=PR.font(16))
        dr.text((x0 + 14, 12), f"pose {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(path)


def old_ref(frames, nums, out):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for i, (fr, ms) in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
        can.alpha_composite(im, (left, top))
        dr.text((i * cw + 14, 12), f"old pose {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--old-sheet", default="C:/t/sy_old/sheet.png")
    ap.add_argument("--old-fanim", default="C:/t/sy_old/anim.fanim")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    for d in (tpl, refs):
        os.makedirs(d, exist_ok=True)
    old = old_frames(a.old_sheet, a.old_fanim)
    des = Image.open(PR.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")
    bg = Image.new("RGBA", (des.width + 4, des.height + 4), GREY + (255,))
    bg.alpha_composite(des, (2, 2))
    bg.convert("RGB").resize((bg.width * 6, bg.height * 6), Image.NEAREST).save(os.path.join(refs, "design.png"))
    shutil.copyfile(PR.lp(os.path.join(SRC, "hd", "design.png")), os.path.join(refs, "design_1x.png"))
    a_ = np.asarray(des)
    PR.palette(np.unique(a_[a_[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    sheets = []
    for k in range(0, len(POSES), 2):
        pair = POSES[k:k + 2]
        name = f"pose_{k // 2 + 1}"
        part = [old[tag][n - 1] for _, tag, n, _ in pair]
        labels = [lab for lab, _, _, _ in pair]
        template(os.path.join(tpl, name + ".png"), part, labels)
        old_ref(part, labels, os.path.join(refs, f"old_{name}.png"))
        sheets.append(dict(name=name, cells=len(pair), poses=[dict(pose=lab, old=f"{tag} {n}", change=what)
                                                              for lab, tag, n, what in pair]))
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "sheet": [SHEET_W, H], "ground": GROUND, "sheets": sheets}, f, indent=1,
                  ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(SRC, "ACTIONS_PROMPT_PPU.md")), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets,", sum(s["cells"] for s in sheets), "poses; written", zp)


if __name__ == "__main__":
    main()
