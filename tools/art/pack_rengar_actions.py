"""The Codex pack for league_rengar's actions drawn whole at PPU 1.475 (assets/source/rengar/ACTIONS_PROMPT_PPU.md): every
frame of his run, attack, passive leap (leap), Savagery (skill), Bola Strike (skill2), Battle Roar (skill_w), hit and
death a new drawing of the approved design (hd/design.png: Codex's picture read on its own squares, 76 x 59 -
「设计图通过，继续做狮子狗的动作包」) in the pose of his OLD sheet's same frame, tools/art/pack_leesin_actions.py's way.

    python tools/art/pack_rengar_actions.py --out C:/t/rg_actions [--old-sheet PNG --old-fanim FANIM]

Not drawn: idle_base (3 breathing poses: the design, the rig sinks it), ult (the old frames are idle_base's sunk
frames 3 and 4 - the R crouch: the rig sinks the design), idle and bp (tools/art/hero_reels.json builds them from
attack 1-3 and skill2 1-4). Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each
cell the old 1x frame scaled to his height (PPU squares a pixel, SQ px a square), faded, as the pose to follow,
standing on the ground line at the standing point, and a bar as tall as he stands. The old sheet is main's
league/champions/league_rengar#sheet.png / #anim.fanim (copied to C:/t/rg_old before the redo replaces it). Then
<out>.zip.

Samira's, Draven's and Lee Sin's lessons are in the prompt: the head the design's size in every frame (mane to beard
spelled out), the build the design's, the run's legs alternating (his run is the trot the user picked: the lower legs
step in place, never crossing).
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

SRC = os.path.join(REPO, "assets", "source", "rengar")
TAGS = ["run", "attack", "leap", "skill", "skill2", "skill_w", "hit", "dead"]
NAMES = {"run": "running (his move loop): a hunched beast's trot, the lower legs stepping in turn in place (never "
                "crossing), the body bobbing with each step, the claw and the blade carried as the pale figure has them",
         "attack": "attack: he raises the claw, then swings it back and slashes the curved blade forward, then back "
                   "to his crouch",
         "leap": "Unseen Predator leap: he springs at the target, the claw flung back and the blade thrust forward, "
                 "and lands crouched",
         "skill": "Savagery: he rears up, the blade raised over his head, then rips it forward and down",
         "skill2": "Bola Strike: he raises the claw and throws the bola forward with it",
         "skill_w": "Battle Roar: he throws his arms wide - the claw back, the blade forward - and roars, mouth open",
         "hit": "struck, flinching back",
         "dead": "death: he staggers, falls on his back and lies on the ground, the blade dropped beside him"}
HANDS = ("The near hand (image left) is the big cream CLAW, the far hand (image right) grips the curved bone BLADE with "
         "the dark red tip. Each arm raised, swung back, thrust or hanging exactly as the pale figure has it; the claw "
         "stays the near hand, the blade stays in the far hand. The tail curls as the pale figure's.")
WEAPONS = {t: HANDS for t in NAMES}
WEAPONS["skill2"] = HANDS + " Do not draw the bola itself (it is an effect)."
WEAPONS["dead"] = ("Lying on the ground as the pale figure: the claw and the blade where the pale figure has them (the "
                   "blade dropped on the ground in the last frames). The tail lies as the pale figure's.")
SAME = {"dead": {7: 6, 8: 6}}            # old frames repeating another (checked pixel for pixel): take that drawing
SAME_DESIGN = {"attack": [6], "leap": [8], "skill": [8], "skill2": [6], "skill_w": [2, 7]}  # = his idle pose: the design
SQ = 8                                   # px a design square in the templates
PPU = 59 / 40                            # design squares an old pixel (hd/design.png: 59 rows, his 1x 40)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 59                               # design rows from his horn's tip to his soles
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
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "his height standing (tip of the horn)", fill=(120, 120, 120),
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
    ap.add_argument("--old-sheet", default="C:/t/rg_old/sheet.png")
    ap.add_argument("--old-fanim", default="C:/t/rg_old/anim.fanim")
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
