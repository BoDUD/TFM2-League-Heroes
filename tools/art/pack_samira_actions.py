"""The Codex pack for league_samira's actions drawn whole at PPU 2.84 (assets/source/samira/ACTIONS_PROMPT_PPU.md): every
frame of her run, gun attack, sword attack (attack_m), Flair gun / sword (skill / skill_m), Wild Rush + Blade Whirl
(skill2), Inferno Trigger (ult), hit and death a new drawing of the approved design (hd/design.png: Codex's v3 picture
read at PPU 2.84, 77 x 105 squares, the greatsword straightened - the user, 2026-10-25: 「通过，继续做动作包」) in the pose
of her OLD sheet's same frame (the timing the kit casts on) - tools/art/pack_gwen_actions.py's way. Her old frames'
baked effects (muzzle flashes, red slashes, the dash's dust) are not drawn: the prompt says so.

    python tools/art/pack_samira_actions.py --out C:/t/sm_actions [--old-sheet PNG --old-fanim FANIM]

A frame holding the same pose as an earlier one (SAME, measured on the old frames with their effects left out) is not
drawn again. Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: two cells of
768 x 1024 when both frames' old pictures fit one (CELL_FIT), else one cell 1536 wide. In each cell the old 1x frame
scaled to her height (PPU squares a pixel, SQ px a square), faded, as the pose to follow, standing on the ground line at
the standing point, and a bar as tall as she stands. refs/: the design at 6x and 1x, its palette, each sheet's old
frames in colour. The old sheet is main's league/champions/league_samira#sheet.png / #anim.fanim (copied to
C:/t/sm_old before the redo replaces it). Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "samira")
TAGS = ["run", "attack", "attack_m", "skill", "skill_m", "skill2", "ult", "hit", "dead"]
NAMES = {"run": "running (her move loop): a quick run, the greatsword on her back, the LEGS SWAPPING every half cycle "
                 "(left foot forward, then right foot forward) and the body bobbing up and down with each stride",
         "attack": "gun attack: her far hand (image right) raises her pistol and fires forward, then lowers it",
         "attack_m": "sword attack: she draws the greatsword from her back, swings it down in front of her and puts it "
                     "back on her back",
         "skill": "Flair (gun): her far hand fires the pistol forward",
         "skill_m": "Flair (sword): the greatsword raised and slashed across in front of her, then back on her back",
         "skill2": "Wild Rush then Blade Whirl: she dashes forward with the greatsword held out in front, then whirls the "
                   "sword round herself, then stands",
         "ult": "Inferno Trigger: a pistol in EACH hand, firing to both sides in turn",
         "hit": "struck, flinching back",
         "dead": "death: she falls back and lies down, the greatsword dropping to the ground beside her"}
# what her weapons do in each sheet (the old frames draw her OLD costume: never copy it)
WEAPONS = {"run": "The greatsword stays on her back as in image 1 (hilt with the red tassel up at the upper left), the pistol "
                  "in its gold holster on her near hip.",
           "attack": "The pistol is in her FAR hand (image right) every frame; the greatsword stays on her back.",
           "attack_m": "The greatsword is in ONE hand all through the swing - the same hand in every frame, where the pale "
                       "figure holds it; between swings it is back on her back. The pistol stays in its holster.",
           "skill": "The pistol is in her FAR hand (image right) every frame; the greatsword stays on her back.",
           "skill_m": "The greatsword is in ONE hand all through the slash - the same hand in every frame, where the pale "
                      "figure holds it; at the end it is back on her back.",
           "skill2": "The greatsword in ONE hand all through (the same hand every frame), held forward in the dash, whirled "
                     "round her after it, then on her back.",
           "ult": "A pistol in EACH hand, pointing out to each side as the pale figure; the greatsword stays on her back.",
           "hit": "The greatsword stays on her back, the pistol in its holster.",
           "dead_1": "The greatsword still on her back as she starts to fall.",
           "dead": "The greatsword lies on the ground beside her, still (where the pale figure has it)."}
# old frames that hold the same pose as an earlier one (their pixels differ only by the old baked effects; measured
# square by square with the effects left out): drawn once, the later frame takes the earlier's drawing (1-based)
SAME = {"attack": {5: 4, 6: 3, 7: 3},
        "attack_m": {7: 6},
        "skill": {4: 3, 5: 3, 8: 1},
        "skill_m": {3: 1, 9: 8},
        "skill2": {12: 8, 13: 9, 14: 10, 15: 11},
        "ult": {3: 2, 4: 2, 6: 5, 7: 5, 8: 2, 9: 2, 10: 2, 12: 11, 13: 11, 14: 2, 15: 2, 16: 2, 17: 5, 18: 5, 19: 5, 20: 2,
                21: 2, 22: 2, 23: 11, 24: 11, 25: 11},
        "dead": {6: 5, 7: 5, 8: 5}}
RELEASE = {"attack": 3, "attack_m": 3, "skill": 2, "skill_m": 4, "ult": 1}   # the frame the hit / shot lands on (0-based)
SQ = 5.5                                 # px a design square in the templates
PPU = 2.84                               # design squares an old pixel
H = 1024
SHEET_W = 1536
GROUND = H - 120
STAND = 105                              # design rows from her crown to her soles
OLD_SOLES = 11.5                         # old frames: the soles this many pixels under the frame's centre (its pivot)
MARGIN = 40
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


def span(frame):
    """Scaled width the old frame's drawing needs."""
    xs = np.nonzero(frame[..., 3].any(0))[0]
    return (xs.max() + 1 - xs.min()) * PPU * SQ


def cell_fit(frame):
    return span(frame) + 2 * MARGIN <= SHEET_W / 2


def placed(frame, x0, cw):
    """The old frame scaled to her height in a cell [x0, x0 + cw): its pivot (the frame's centre) on the standing point
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
    return im, left, top


def template(path, frames, nums, release, also):
    """One or two frames (their 1-based numbers nums): per cell the old frame faded as the pose, ground, standing point,
    her height."""
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
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "her height standing (crown)", fill=(120, 120, 120),
                font=PR.font(16))
        note = "  (the hit / cast lands now)" if nums[i] - 1 == release else ""
        dr.text((x0 + 14, 12), f"frame {nums[i]}{note}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(path)


def old_ref(frames, nums, out):
    """The sheet's old frames in colour at the same scale and place."""
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for i, (fr, ms) in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
        can.alpha_composite(im, (left, top))
        dr.text((i * cw + 14, 12), f"old frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(out)


def groups(frs, same):
    """[([numbers], [frames])] of the frames to draw (none in `same`): two to a sheet while both fit a half, else one."""
    todo = [(k + 1, f) for k, f in enumerate(frs) if k + 1 not in same]
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
    ap.add_argument("--old-sheet", default="C:/t/sm_old/sheet.png")
    ap.add_argument("--old-fanim", default="C:/t/sm_old/anim.fanim")
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
        same = SAME.get(tag, {})
        for n, (nums, part) in enumerate(groups(old[tag], same)):
            name = f"{tag}_{n + 1}"
            template(os.path.join(tpl, name + ".png"), part, nums, RELEASE.get(tag, -1), same)
            old_ref(part, nums, os.path.join(refs, f"old_{name}.png"))
            sheets.append(dict(tag=tag, name=name, frames=nums,
                               cells=len(part), action=NAMES[tag], ms=[ms for _, ms in part],
                               weapons=WEAPONS.get(name, WEAPONS[tag])))
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "sheet": [SHEET_W, H], "ground": GROUND, "same": SAME, "sheets": sheets}, f, indent=1,
                  ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(SRC, "ACTIONS_PROMPT_PPU.md")), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets,", sum(len(s["frames"]) for s in sheets), "frames; written", zp)


if __name__ == "__main__":
    main()
