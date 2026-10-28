"""The Codex pack for league_zed's actions drawn whole at PPU 1.62 (assets/source/zed/ACTIONS_PROMPT_PPU.md): every
frame of his run, attack, W (skill), Q (skill2), E (skill_e), R (ult), hit and death a new drawing of the approved
design (hd/design.png: Codex's zed-A read as drawn, 40 x 65 squares - the user, 2026-10-28: 「通过，用 1.62」) in the
pose of his OLD sheet's same frame, tools/art/pack_tristana_actions.py's way.

    python tools/art/pack_zed_actions.py --out C:/t/zd_actions

The wrist blades go where the old frame has them: hanging down along his legs, thrust forward, flung out to both sides.
The run's legs are named frame by frame from the start (RUN_LEGS).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from skill2 and ult),
and every old frame that is another one's picture (SAME, checked on the old sheet: skill 4 and hit 2 are his idle pose
itself -> DESIGN; skill2 6 = attack 6, skill_e 5 = skill_e 3, ult 2 = skill_e 2, ult 4 = ult 3, dead 5 = dead 4,
dead 7 and 8 = dead 6 - some of them the same picture moved: the rig places it on the old frame's own box). Nothing is
baked into his body tags (his shadows and slashes are effect strips, zed_fx_*). Each template sheet
(templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the old 1x frame scaled to his height (PPU
squares a pixel, SQ px a square), faded, as the pose to follow, standing on the ground line at the standing point, and
a bar as tall as he stands. Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "zed")
TAGS = ["run", "attack", "skill", "skill2", "skill_e", "ult", "hit", "dead"]
BAKED = []                              # (nothing baked into his body tags)
NAMES = {"run": "running (his move loop): League's ninja run, leaning forward, both arms low with the wrist blades "
                "trailing, the LEGS STEPPING IN TURN, the body bobbing with each step",
         "attack": "attack: he coils, steps in and stabs forward to the right with the wrist blades of one arm, then "
                   "pulls back to his stance",
         "skill": "Living Shadow (W): he raises one arm with its blades up, then flings it forward to the right to "
                  "send his shadow out",
         "skill2": "Razor Shuriken (Q): he raises one arm, rears up with both (frames 2-3: his face turned toward the "
                   "viewer's left, as the pale figure), crouches and whips both arms out low to throw, then "
                   "straightens",
         "skill_e": "Shadow Slash (E): he pulls his arms in, then spins and flings BOTH arms straight out to the "
                    "left and right, his blades slashing all round (frame 4: his front to the viewer mid-spin, as the "
                    "pale figure), and settles",
         "ult": "Death Mark (R): he crouches, springs and dashes forward low to the right with his blades thrust "
                "out, cuts, and lands low with his arms out",
         "hit": "struck: jolted back, one arm flung out",
         "dead": "death: struck back, he sinks to his knees, then falls flat on his front, lying on the ground"}
BLADES = ("THE WRIST BLADES go where the pale figure has them, frame by frame (image 3 shows them in colour): each "
          "forearm a gold bracer with two or three long silver blades; hanging DOWN along his legs unless the pale "
          "figure raises, thrusts or flings that arm - then the blades point where that forearm points. Only his own "
          "two sets of blades (no extra weapons); the big SHURIKEN stays on his back in every frame.")
WEAPONS = {t: BLADES for t in NAMES}
WEAPONS["dead"] = BLADES + " Lying on the ground he lies on his front as the pale figure, the blades with him."
WEAPONS["skill2"] = BLADES + (" The thrown shuriken is an effect: do not draw one in his hand or flying - the one on "
                              "his back stays where it is.")
# The run's legs frame by frame, read off the old run (the pale figures: the bottom rows of each old frame) - named
# from the start (Akali's first run kept the legs stretched apart in every frame); he runs to the right, "back" is the
# picture's left
RUN_LEGS = {
    1: "one foot planted on the ground AHEAD of his hips (right); the other leg kicked up BEHIND him (left), its foot "
       "off the ground",
    2: "the front foot still planted, now nearer under him; the back leg still up behind, its foot off the ground, "
       "starting to come forward",
    3: "PASSING: the planted foot right under his hips; the other leg comes through in front of it, its KNEE LIFTED, "
       "its foot off the ground (the legs cross)",
    4: "PASSING: the same, the planted foot under his hips, the lifted knee in front a little higher",
    5: "the planted foot now BEHIND his hips (left); the other leg reaching forward (right), its foot just off the "
       "ground",
    6: "the reaching foot coming down ahead (right) while the back foot is still on the ground",
    7: "the OTHER foot now planted AHEAD (right); the first leg kicked up behind (left), its foot off the ground",
    8: "the same, the back foot kicked up higher behind him",
}
RUN_SWAP = ("The two legs TAKE TURNS: the foot planted in frames 1-6 is the one kicked up behind in frames 7-8. Follow "
            "the pale figure's LEGS exactly - frames 1, 2, 3, 4, 5, 7 and 8 have a foot off the ground; never the "
            "same leg pose in every frame.")
# old frames that are another frame pixel for pixel (checked on the old sheet / the native cells, cropped to the
# figure): drawn once, here (tag, frame), 1-based; DESIGN: his idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
SAME = {"skill": {4: DESIGN}, "hit": {2: DESIGN}, "skill2": {6: ("attack", 6)}, "skill_e": {5: ("skill_e", 3)},
        "ult": {2: ("skill_e", 2), 4: ("ult", 3)}, "dead": {5: ("dead", 4), 7: ("dead", 6), 8: ("dead", 6)}}
SQ = 8                                   # px a design square in the templates (two run frames a sheet)
PPU = 65 / 40                            # design squares an old pixel (hd/design.png: 65 rows, his 1x 40)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 65                               # design rows from the shuriken's top point to his soles
OLD_SOLES = 11.5                         # old frames: the soles this many pixels under the frame's centre (its pivot)
MARGIN = 30
GREY = (225, 225, 225)


def old_frames(sheet_png, fanim):
    """{tag: [(frame, ms, (pivot x, soles y))]}: the old sheet's frames (pivot: the frame's centre, the soles OLD_SOLES
    under it)."""
    px = np.asarray(Image.open(sheet_png).convert("RGBA"))
    with open(fanim, encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag in TAGS:
        fr = []
        for f_ in anims[tag]["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            fr.append((px[y:y + h, x:x + w].copy(), round(f_["duration"] * 1000), (w / 2, h / 2 + OLD_SOLES)))
        out[tag] = fr
    return out


def cell_fit(frame):
    xs = np.nonzero(frame[0][..., 3].any(0))[0]
    return (xs.max() + 1 - xs.min()) * PPU * SQ + 2 * MARGIN <= SHEET_W / 2


def placed(frame, x0, cw):
    """The old frame scaled to his height in a cell [x0, x0 + cw): its pivot on the standing point (the cell's middle),
    its soles on the ground line, kept inside the cell. -> (RGBA image, left, top)."""
    a, _, (pvx, pvy) = frame
    k = PPU * SQ
    h, w = a.shape[:2]
    im = Image.fromarray(a).resize((round(w * k), round(h * k)), Image.NEAREST)
    left = round(x0 + cw / 2 - pvx * k)
    top = round(GROUND - pvy * k)
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
    for i, fr in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
        a = np.asarray(im).astype(float)
        faded = a.copy()
        faded[..., :3] = a[..., :3] * 0.35 + 255 * 0.65                  # a pale picture of the pose
        can.alpha_composite(Image.fromarray(faded.astype(np.uint8)), (left, top))
    dr = ImageDraw.Draw(can)
    for i in range(len(frames)):
        x0 = i * cw
        cx = x0 + cw / 2
        dr.rectangle([x0, 0, x0 + cw - 1, H - 1], outline=(60, 60, 60), width=2)
        dr.line([(x0, GROUND), (x0 + cw - 1, GROUND)], fill=(90, 90, 90), width=3)
        dr.line([(cx, GROUND - 12), (cx, GROUND + 12)], fill=(90, 90, 90), width=3)
        bx = x0 + 16
        dr.line([(bx, GROUND), (bx, GROUND - STAND * SQ)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "his height standing (the shuriken's top point)",
                fill=(120, 120, 120), font=PR.font(16))
        dr.text((x0 + 14, 12), f"frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(path)


def old_ref(frames, nums, out):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for i, fr in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
        can.alpha_composite(im, (left, top))
        dr.text((i * cw + 14, 12), f"old frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(out)


def groups(frs, skip):
    """[([numbers], [frames])] of the frames to draw (none in `skip`): two to a sheet while both fit a half."""
    todo = [(k + 1, f) for k, f in enumerate(frs) if k + 1 not in skip]
    out, k = [], 0
    while k < len(todo):
        if k + 1 < len(todo) and cell_fit(todo[k][1]) and cell_fit(todo[k + 1][1]):
            pair = todo[k:k + 2]
            k += 2
        else:
            pair = todo[k:k + 1]
            k += 1
        out.append(([n for n, _ in pair], [f for _, f in pair]))
    return out


def figure(a):
    ys, xs = np.nonzero(a[..., 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def idle_sheet():
    """His idle pose on the old sheet: idle_base 1."""
    px = np.asarray(Image.open(PR.lp(os.path.join(SRC, "hd", "old", "sheet.png"))).convert("RGBA"))
    with open(PR.lp(os.path.join(SRC, "hd", "old", "anim.fanim")), encoding="utf-8-sig") as f:
        d = json.load(f)["anims"]["idle_base"]["frames"][0]["data"]
    x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
    return px[y:y + h, x:x + w]


def check_same(old):
    """Every SAME pair is the same picture on the old sheet (a later edit of SAME must not join two poses)."""
    for tag, m in SAME.items():
        for k, (t2, k2) in m.items():
            a = figure(old[tag][k - 1][0])
            bs = [figure(idle_sheet())] if (t2, k2) == DESIGN else [figure(old[t2][k2 - 1][0])]
            if not any(a.shape == b.shape and (a == b).all() for b in bs):
                sys.exit(f"SAME {tag} {k} = {t2} {k2}: not the same old frame")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--old-sheet", default=os.path.join(SRC, "hd", "old", "sheet.png"))
    ap.add_argument("--old-fanim", default=os.path.join(SRC, "hd", "old", "anim.fanim"))
    ap.add_argument("--only", help="tags to pack, comma-separated (the redo of one action: --only run)")
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/zed")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    for d in (tpl, refs):
        os.makedirs(d, exist_ok=True)
    old = old_frames(PR.lp(a.old_sheet), PR.lp(a.old_fanim))
    check_same(old)
    des = Image.open(PR.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")
    bg = Image.new("RGBA", (des.width + 4, des.height + 4), GREY + (255,))
    bg.alpha_composite(des, (2, 2))
    bg.convert("RGB").resize((bg.width * 6, bg.height * 6), Image.NEAREST).save(os.path.join(refs, "design.png"))
    shutil.copyfile(PR.lp(os.path.join(SRC, "hd", "design.png")), os.path.join(refs, "design_1x.png"))
    a_ = np.asarray(des)
    PR.palette(np.unique(a_[a_[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    sheets = []
    for tag in (a.only.split(",") if a.only else TAGS):
        for n, (nums, part) in enumerate(groups(old[tag], set(SAME.get(tag, {})))):
            name = f"{tag}_{n + 1}"
            template(os.path.join(tpl, name + ".png"), part, nums)
            old_ref(part, nums, os.path.join(refs, f"old_{name}.png"))
            sheets.append(dict(tag=tag, name=name, frames=nums, cells=len(part), action=NAMES[tag],
                               ms=[ms for _, ms, _ in part], weapons=WEAPONS[tag]))
            if tag == "run":
                sheets[-1]["legs"] = " ".join(f"Frame {k}: {RUN_LEGS[k]}." for k in nums) + " " + RUN_SWAP
    same = {t: {str(k): f"{t2} {k2}" for k, (t2, k2) in m.items()} for t, m in SAME.items()}
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "sheet": [SHEET_W, H], "ground": GROUND, "same": same, "baked_body_frames": BAKED,
                   "sheets": sheets}, f, indent=1, ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(SRC, a.prompt)), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets,", sum(len(s["frames"]) for s in sheets), "frames; written", zp)


if __name__ == "__main__":
    main()
