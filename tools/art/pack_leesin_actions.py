"""The Codex pack for league_leesin's actions drawn whole at PPU 2.1 (assets/source/leesin/ACTIONS_PROMPT_PPU.md): every
frame of his run, attack, Sonic Wave (skill), Resonating Strike (q2), Tempest (skill2), Dragon's Rage (ult), hit and
death a new drawing of the approved design (hd/design.png: Codex's picture read on its own squares, 68 x 86 -
「通过，继续做盲僧的动作包」) in the pose of his OLD sheet's same frame, tools/art/pack_draven_actions.py's way.

    python tools/art/pack_leesin_actions.py --out C:/t/ls_actions [--old-sheet PNG --old-fanim FANIM]

q_throw is not drawn: it is Q1's frames 4-7 pixel for pixel (tools/art/leesin_throw_tag.py), so it takes skill's.
idle_base (8 breathing frames) is the design. Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or
TWO frames: in each cell the old 1x frame scaled to his height (PPU squares a pixel, SQ px a square), faded, as the pose
to follow, standing on the ground line at the standing point, and a bar as tall as he stands. The old sheet is main's
league/champions/league_leesin#sheet.png / #anim.fanim (copied to C:/t/ls_old before the redo replaces it). Then
<out>.zip.

Samira's and Draven's lessons are in the prompt: the head the design's size in every frame (crown to chin spelled out),
the build the design's, the run's legs swapping each half cycle.
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

SRC = os.path.join(REPO, "assets", "source", "leesin")
TAGS = ["run", "attack", "skill", "q2", "skill2", "ult", "hit", "dead"]
NAMES = {"run": "running (his move loop): a light martial-artist's run, fists up, the LEGS SWAPPING every half cycle "
                "(left foot forward, then right foot forward) and the body bobbing with each stride",
         "attack": "attack: a quick punch forward, then back to his guard",
         "skill": "Sonic Wave: he winds up and thrusts his far palm forward, sending a wave",
         "q2": "Resonating Strike: he leaps forward in a flying kick and lands on the target",
         "skill2": "Tempest: he jumps and slams both fists into the ground",
         "ult": "Dragon's Rage: a spinning roundhouse kick, the kicking leg swung high",
         "hit": "struck, flinching back",
         "dead": "death: he staggers back and falls, lying on the ground"}
WEAPONS = {t: "No weapon: bare hands wrapped in red-and-white bandages. Each hand, fist or open palm exactly as the pale "
              "figure has it; the far hand stays the far hand." for t in NAMES}
SAME = {}                                # no old frame repeats another (checked pixel for pixel)
SAME_DESIGN = {}                         # no old action frame is his idle pose itself
SQ = 7                                   # px a design square in the templates
PPU = 86 / 41                            # design squares an old pixel (hd/design.png: 86 rows, his 1x 41)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 86                               # design rows from his braid's tip to his soles
OLD_SOLES = 11.5                         # old frames: the soles this many pixels under the frame's centre (its pivot)
MARGIN = 30
GREY = (225, 225, 225)


def old_frames(sheet_png, fanim):
    px = np.asarray(Image.open(sheet_png).convert("RGBA"))
    with open(fanim, encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag in TAGS:
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
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "his height standing (top of the braid)", fill=(120, 120, 120),
                font=PR.font(16))
        dr.text((x0 + 14, 12), f"frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(path)


def old_ref(frames, nums, out):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for i, (fr, ms) in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
        can.alpha_composite(im, (left, top))
        dr.text((i * cw + 14, 12), f"old frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(out)


def groups(frs, skip):
    """[([numbers], [frames])] of the frames to draw (none in `skip`): two to a sheet while both fit a half."""
    todo = [(k + 1, f) for k, f in enumerate(frs) if k + 1 not in skip]
    out, k = [], 0
    while k < len(todo):
        if k + 1 < len(todo) and cell_fit(todo[k][1][0]) and cell_fit(todo[k + 1][1][0]):
            pair = todo[k:k + 2]
            k += 2
        else:
            pair = todo[k:k + 1]
            k += 1
        out.append(([n for n, _ in pair], [f for _, f in pair]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--old-sheet", default="C:/t/ls_old/sheet.png")
    ap.add_argument("--old-fanim", default="C:/t/ls_old/anim.fanim")
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
    for tag in TAGS:
        skip = set(SAME.get(tag, {})) | set(SAME_DESIGN.get(tag, []))
        for n, (nums, part) in enumerate(groups(old[tag], skip)):
            name = f"{tag}_{n + 1}"
            template(os.path.join(tpl, name + ".png"), part, nums)
            old_ref(part, nums, os.path.join(refs, f"old_{name}.png"))
            sheets.append(dict(tag=tag, name=name, frames=nums, cells=len(part), action=NAMES[tag],
                               ms=[ms for _, ms in part], weapons=WEAPONS[tag]))
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "sheet": [SHEET_W, H], "ground": GROUND, "same": SAME, "same_as_design": SAME_DESIGN,
                   "sheets": sheets}, f, indent=1, ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(SRC, "ACTIONS_PROMPT_PPU.md")), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets,", sum(len(s["frames"]) for s in sheets), "frames; written", zp)


if __name__ == "__main__":
    main()
